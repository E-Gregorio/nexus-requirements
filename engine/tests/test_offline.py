# -*- coding: utf-8 -*-
"""Test offline del motor NEXUS contra el golden set de HU_PASS_01.

No llama a la API: inyecta las respuestas de los agentes desde los archivos
de la demo y verifica que las partes DETERMINISTAS del motor (evaluación
estructural, RHI, dictamen, VCR, IDs, regla smoke, renderizadores) reproducen
exactamente los números certificados a mano.

Ejecutar:  python tests/test_offline.py
"""
import json
import sys
import tempfile
from pathlib import Path

ENGINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ENGINE))

from nexus.catalog import compute_rhi, compute_vcr, evaluate_structural, load_catalog, load_vcr_policy  # noqa: E402

ROOT = ENGINE.parent
DEMO = ROOT / "demo"

FALLOS = []


def check(nombre, cond, detalle=""):
    estado = "OK " if cond else "FAIL"
    print(f"  [{estado}] {nombre}" + (f" — {detalle}" if detalle and not cond else ""))
    if not cond:
        FALLOS.append(nombre)


def cargar(nombre):
    with open(DEMO / nombre, "r", encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
print("\n== 1. Evaluación estructural (código) vs golden set ==")
catalogo = load_catalog()
hu = cargar("01_hu_canonica.json")
golden_cert = cargar("02_certificacion_nx.json")
golden_por_regla = {e["regla"]: e["veredicto"] for e in golden_cert["evaluaciones"]}

ev_estructura = evaluate_structural(hu, catalogo)
check("13 reglas estructurales evaluadas", len(ev_estructura) == 13, f"obtenidas: {len(ev_estructura)}")
for ev in ev_estructura:
    esperado = golden_por_regla[ev["regla"]]
    check(f"{ev['regla']} = {esperado}", ev["veredicto"] == esperado,
          f"motor dio {ev['veredicto']}")

# ---------------------------------------------------------------------------
print("\n== 2. RHI y dictamen (aritmética) vs golden set ==")
resultado = compute_rhi(golden_cert["evaluaciones"], catalogo)
check("RHI = 23.9", resultado["rhi"] == 23.9, f"motor dio {resultado['rhi']}")
check("Puntos 22/92", (resultado["puntos_obtenidos"], resultado["puntos_totales"]) == (22, 92),
      f"motor dio {resultado['puntos_obtenidos']}/{resultado['puntos_totales']}")
check("Dictamen NO_APTO", resultado["dictamen"] == "NO_APTO", resultado["dictamen"])
check("6 críticos incumplidos",
      resultado["criticos_incumplidos"] == ["NX-005", "NX-006", "NX-021", "NX-030", "NX-031", "NX-033"],
      str(resultado["criticos_incumplidos"]))

# Dictamen proyectado: todo CUMPLE → CERTIFICADO
todas_cumplen = [{"regla": r["id"], "veredicto": "CUMPLE"} for r in catalogo["reglas"]]
proyectado = compute_rhi(todas_cumplen, catalogo)
check("Proyección v2: RHI 100 → CERTIFICADO",
      proyectado["rhi"] == 100.0 and proyectado["dictamen"] == "CERTIFICADO")

# ---------------------------------------------------------------------------
print("\n== 3. VCR (política oficial 1-3) ==")
policy = load_vcr_policy()
vcr = compute_vcr({"valor": 3, "costo": 2, "probabilidad": 2, "impacto": 3}, policy)
check("V3 C2 P2 I3 → R=6, VCR=11, AUTOMATIZAR",
      vcr["riesgo"] == 6 and vcr["vcr_total"] == 11 and vcr["decision"] == "AUTOMATIZAR", str(vcr))
vcr2 = compute_vcr({"valor": 1, "costo": 1, "probabilidad": 2, "impacto": 3}, policy)
check("V1 C1 P2 I3 → VCR=8, MANUAL", vcr2["vcr_total"] == 8 and vcr2["decision"] == "MANUAL", str(vcr2))

# ---------------------------------------------------------------------------
print("\n== 4. Pipeline completo con agentes simulados (golden set) ==")
golden_cob = cargar("03_cobertura_gaps.json")

_TIPOS = {"E1": "Funcional", "E2": "Seguridad", "E3": "Funcional", "E4": "Funcional - Negativa",
          "E5": "Funcional - Negativa", "E6": "Funcional", "E7": "Funcional - Negativa",
          "E8": "Seguridad", "E9": "Seguridad"}
_SUITE = {"E1": "TS_POS", "E3": "TS_POS", "E6": "TS_POS",
          "E2": "TS_NEG", "E4": "TS_NEG", "E5": "TS_NEG", "E7": "TS_NEG",
          "E8": "TS_SEC", "E9": "TS_SEC"}


class FakeLLM:
    """Devuelve las respuestas del golden set — cero API."""
    model = "fake-golden"

    def call_json(self, etapa, prompt, max_tokens=8000, reintentos=3):
        if etapa == "normalizador":
            return cargar("01_hu_canonica.json")
        if etapa == "certificador":
            estructurales = {r["id"] for r in catalogo["reglas"] if r["familia"] == "estructura"}
            return {"evaluaciones": [e for e in golden_cert["evaluaciones"]
                                     if e["regla"] not in estructurales]}
        if etapa == "cobertura":
            return golden_cob
        if etapa == "generador":
            tcs = []
            for g in golden_cob["gaps"]:
                e_id = g["escenario_sugerido"]["titulo"].split(" ")[0]
                tcs.append({
                    "tc_id": f"TC_{e_id}", "ts_id": _SUITE[e_id],
                    "titulo": g["escenario_sugerido"]["titulo"],
                    "tipo_prueba": _TIPOS[e_id], "escenario_id": e_id,
                    "brs_cubiertas": [g["br_id"]], "prcs_asociadas": ["PRC_A"],
                    "tecnica": "Valores Limite", "origen": "gap_sugerido",
                    "es_smoke": e_id in ("E1", "E3", "E2"),  # E2 mal marcado a propósito
                    "prioridad": "Alta", "complejidad": "Media", "tiempo_estimado": "20 min",
                    "datos_entrada": "datos frontera", "resultado_esperado": "resultado verificable",
                    "pasos": [{"numero": 1, "accion": "ejecutar", "datos": "d", "resultado_esperado": "r"}],
                })
            return {
                "hu_id": "HU_PASS_01",
                "suites": [
                    {"ts_id": "TS_POS", "nombre": "Positivos", "categoria": "Funcional",
                     "tecnica": "PE", "prioridad": "Alta", "framework_sugerido": "Playwright"},
                    {"ts_id": "TS_NEG", "nombre": "Negativos", "categoria": "Funcional - Negativa",
                     "tecnica": "VL", "prioridad": "Alta", "framework_sugerido": "Playwright"},
                    {"ts_id": "TS_SEC", "nombre": "Seguridad", "categoria": "Seguridad - OWASP",
                     "tecnica": "Riesgos", "prioridad": "Muy Alta", "framework_sugerido": "ZAP"},
                ],
                "precondiciones": [
                    {"prc_id": "PRC_A", "titulo": "Usuario registrado", "categoria": "Datos",
                     "descripcion": "d", "pasos_setup": ["s"], "datos_requeridos": "x",
                     "estado_sistema": "ok", "reutilizable": True},
                ],
                "test_cases": tcs,
                "vcr_propuesto": {"valor": 3, "costo": 2, "probabilidad": 2, "impacto": 3,
                                  "justificacion": "credenciales"},
            }
        raise AssertionError(f"etapa inesperada: {etapa}")


from run_nexus import ejecutar_pipeline  # noqa: E402

with tempfile.TemporaryDirectory() as tmp:
    out = Path(tmp) / "HU_PASS_01"
    manifest = ejecutar_pipeline(DEMO / "HU_PASS_01_original.md", out_dir=out, llm=FakeLLM())

    check("Manifiesto: RHI 23.9 / NO_APTO",
          manifest["rhi"] == 23.9 and manifest["dictamen"] == "NO_APTO")
    check("Manifiesto: VCR 11 AUTOMATIZAR (propuesto)",
          manifest["vcr"]["vcr_total"] == 11 and manifest["vcr"]["decision"] == "AUTOMATIZAR")

    activos = json.loads((out / "04_activos.json").read_text(encoding="utf-8"))
    tcs = {t["escenario_id"]: t for t in activos["test_cases"]}
    check("ID determinista: HU_PASS_01_TC_E1", tcs["E1"]["tc_id"] == "HU_PASS_01_TC_E1",
          tcs["E1"]["tc_id"])
    check("Suites renombradas: HU_PASS_01_TS01..03",
          {s["ts_id"] for s in activos["suites"]} == {"HU_PASS_01_TS01", "HU_PASS_01_TS02", "HU_PASS_01_TS03"})
    check("PRC renombrada y re-asociada",
          tcs["E1"]["prcs_asociadas"] == ["HU_PASS_01_PRC01"], str(tcs["E1"]["prcs_asociadas"]))
    check("Regla smoke: E2 (Seguridad) desmarcado por código", tcs["E2"]["es_smoke"] is False)
    check("Regla smoke: E1 y E3 conservan smoke",
          tcs["E1"]["es_smoke"] and tcs["E3"]["es_smoke"])

    esperados = ["01_hu_canonica.json", "02_certificacion_nx.json", "03_cobertura_gaps.json",
                 "04_activos.json", "05_CERTIFICADO_HU_PASS_01.md", "HU_PASS_01_IDEAL.html",
                 "run_manifest.json", "csv/1_User_Storie.csv", "csv/2_Test_Suite.csv",
                 "csv/3_Precondition.csv", "csv/4_Test_Case.csv"]
    for nombre in esperados:
        check(f"Artefacto generado: {nombre}", (out / nombre).exists())

    cert_md = (out / "05_CERTIFICADO_HU_PASS_01.md").read_text(encoding="utf-8")
    check("Certificado contiene RHI y dictamen", "23.9" in cert_md and "NO APTO" in cert_md)
    html = (out / "HU_PASS_01_IDEAL.html").read_text(encoding="utf-8")
    check("HU Ideal marca PROPUESTO y AGREGADO", "PROPUESTO" in html and "AGREGADO" in html)
    csv_tc = (out / "csv/4_Test_Case.csv").read_text(encoding="utf-8")
    check("CSV TC con Es_Smoke e IDs deterministas",
          "Es_Smoke" in csv_tc and "HU_PASS_01_TC_E9" in csv_tc)

# ---------------------------------------------------------------------------
print("\n" + "=" * 50)
if FALLOS:
    print(f"RESULTADO: {len(FALLOS)} FALLOS → {FALLOS}")
    sys.exit(1)
print("RESULTADO: TODOS LOS CHECKS PASARON ✔")
