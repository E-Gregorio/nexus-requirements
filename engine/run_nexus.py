# -*- coding: utf-8 -*-
"""
NEXUS Requirements — Orquestador
================================
QASL Shift-Left Testing Framework
"El framework define la norma; NEXUS la ejecuta; el ecosistema la consume."

Uso:
    python run_nexus.py <ruta_a_la_HU> [--out DIR]

Acepta .md, .txt, .html — cualquier formato: el Normalizador lo convierte
a HU Canónica. Salidas en outputs/<HU_ID>/ (o --out):

    01_hu_canonica.json      02_certificacion_nx.json   03_cobertura_gaps.json
    04_activos.json          05_CERTIFICADO_<HU>.md     <HU>_IDEAL.html
    csv/1..4_*.csv           run_manifest.json
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from nexus import NexusPipelineError, __version__
from nexus.config import OUTPUTS_DIR, load_env
from nexus.catalog import compute_vcr, load_catalog, load_vcr_policy
from nexus.contracts import validate
from nexus.llm_client import LLMClient
from nexus.agents import analizar_cobertura, certificar, generar_activos, normalizar
from nexus.renderers import render_certificado, render_csvs, render_hu_ideal


def _leer_fuente(ruta: Path) -> str:
    if not ruta.exists():
        raise NexusPipelineError("entrada", f"Archivo no encontrado: {ruta}")
    return ruta.read_text(encoding="utf-8", errors="replace")


def _guardar(directorio: Path, nombre: str, contenido):
    directorio.mkdir(parents=True, exist_ok=True)
    ruta = directorio / nombre
    if isinstance(contenido, (dict, list)):
        ruta.write_text(json.dumps(contenido, ensure_ascii=False, indent=2), encoding="utf-8")
    else:
        ruta.write_text(contenido, encoding="utf-8")
    return ruta


def ejecutar_pipeline(ruta_hu: Path, out_dir: Path = None, llm=None) -> dict:
    """Pipeline completo. `llm` inyectable para tests offline."""
    print("=" * 62)
    print(f"  NEXUS Requirements v{__version__} — QASL Shift-Left Testing Framework")
    print("=" * 62)

    catalogo = load_catalog()
    vcr_policy = load_vcr_policy()
    print(f"  Catálogo NX v{catalogo['meta']['version']} · {len(catalogo['reglas'])} reglas")

    if llm is None:
        llm = LLMClient()

    fuente = _leer_fuente(ruta_hu)

    # [1/6] Normalización
    print("\n[1/6] Normalizando documento fuente → HU Canónica...")
    hu = normalizar(llm, fuente, ruta_hu.name)
    hu_id = hu["id"]
    destino = out_dir or (OUTPUTS_DIR / hu_id)
    _guardar(destino, "01_hu_canonica.json", hu)
    print(f"      HU: {hu_id} — {hu['nombre']} · "
          f"{len(hu['reglas_negocio'])} BRs · {len(hu['escenarios'])} escenarios · "
          f"{len(hu['_meta']['campos_no_especificados'])} campos NO_ESPECIFICADO")

    # [2/6] Certificación NX
    print("[2/6] Certificando contra el Catálogo NX...")
    cert = certificar(llm, hu, catalogo)
    _guardar(destino, "02_certificacion_nx.json", cert)
    print(f"      RHI: {cert['rhi']}/100 → {cert['dictamen']} · "
          f"críticos incumplidos: {len(cert['criticos_incumplidos'])}")

    # [3/6] Cobertura RTM
    print("[3/6] Analizando cobertura BR ↔ Escenario (RTM)...")
    cob = analizar_cobertura(llm, hu)
    _guardar(destino, "03_cobertura_gaps.json", cob)
    res = cob["resumen"]
    print(f"      Cobertura: {res['cobertura_inicial_promedio']}% → "
          f"{res['cobertura_proyectada']}% proyectada · gaps: {res['total_gaps']}")

    # [4/6] Generación de activos
    print("[4/6] Generando activos de prueba (suites, PRCs, TCs)...")
    activos = generar_activos(llm, hu, cob, vcr_policy)
    _guardar(destino, "04_activos.json", activos)
    smoke = [t["tc_id"] for t in activos["test_cases"] if t.get("es_smoke")]
    print(f"      Suites: {len(activos['suites'])} · PRCs: {len(activos['precondiciones'])} · "
          f"TCs: {len(activos['test_cases'])} · smoke: {len(smoke)}")

    # VCR (código puro): HU si trae; si no, propuesto del generador
    vcr = None
    if isinstance(hu.get("estimaciones"), dict):
        vcr = compute_vcr(hu["estimaciones"], vcr_policy)
        vcr["origen"] = "declarado en la HU"
    elif isinstance(activos.get("vcr_propuesto"), dict):
        vcr = compute_vcr(activos["vcr_propuesto"], vcr_policy)
        vcr["origen"] = "PROPUESTO — ratificar en Planning Poker"

    # [5/6] Renderizado
    print("[5/6] Renderizando Certificado, HU Ideal y CSVs...")
    _guardar(destino, f"05_CERTIFICADO_{hu_id}.md",
             render_certificado(hu, cert, cob, activos, vcr))
    _guardar(destino, f"{hu_id}_IDEAL.html", render_hu_ideal(hu, cert, cob, vcr))
    for nombre, contenido in render_csvs(hu, cert, cob, activos, vcr).items():
        _guardar(destino / "csv", nombre, contenido)

    # [6/6] Manifiesto de la corrida (reproducibilidad y auditoría)
    print("[6/6] Registrando manifiesto de la corrida...")
    manifest = {
        "hu_id": hu_id,
        "fuente": str(ruta_hu),
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "engine_version": __version__,
        "catalogo_version": catalogo["meta"]["version"],
        "modelo": getattr(llm, "model", "offline"),
        "rhi": cert["rhi"],
        "dictamen": cert["dictamen"],
        "gaps": res["total_gaps"],
        "test_cases": len(activos["test_cases"]),
        "vcr": vcr,
    }
    _guardar(destino, "run_manifest.json", manifest)

    print("\n" + "=" * 62)
    print(f"  [OK] ANÁLISIS COMPLETADO — {destino}")
    print("=" * 62)
    return manifest


def main():
    parser = argparse.ArgumentParser(description="NEXUS Requirements — análisis estático de HUs")
    parser.add_argument("hu", help="Ruta al documento de la HU (.md, .txt, .html)")
    parser.add_argument("--out", help="Directorio de salida (default: outputs/<HU_ID>)")
    args = parser.parse_args()

    load_env()
    try:
        ejecutar_pipeline(Path(args.hu), Path(args.out) if args.out else None)
    except NexusPipelineError as e:
        print(f"\n[FALLO DEL PIPELINE] {e}", file=sys.stderr)
        print("La corrida queda marcada como FALLIDA — ningún artefacto parcial "
              "debe tratarse como análisis válido.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
