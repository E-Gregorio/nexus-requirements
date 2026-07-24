# -*- coding: utf-8 -*-
"""Renderizadores (código puro, cero LLM): certificado, HU Ideal HTML y CSVs.
Todos leen los JSON validados del pipeline — un origen, N formatos."""
import csv
import io
from datetime import date

MARK = "[PROPUESTO"


def _tiene_propuestos(texto: str) -> bool:
    return MARK in (texto or "")


# ---------------------------------------------------------------------------
# Certificado (DoD del analista → DoR de desarrollo/QA)
# ---------------------------------------------------------------------------

def render_certificado(hu, cert, cob, activos, vcr) -> str:
    r = cert["resumen_por_severidad"]
    dictamen_map = {
        "CERTIFICADO": "🟢 CERTIFICADO",
        "APTO_PARA_DESARROLLO": "🟢 APTO PARA DESARROLLO",
        "REQUIERE_REVISION": "🟡 REQUIERE REVISIÓN",
        "NO_APTO": "🔴 NO APTO PARA DESARROLLO",
    }
    brs_mejoradas = cob.get("brs_mejoradas", [])
    decisiones = [
        b["descripcion"] for b in brs_mejoradas if _tiene_propuestos(b.get("descripcion"))
    ]
    smoke = [t["tc_id"] for t in activos["test_cases"] if t.get("es_smoke")]
    total_eval = sum(v["cumple"] + v["incumple"] + v["no_aplica"] for v in r.values())

    lineas = [
        "# 🛡️ CERTIFICADO DE REQUERIMIENTO — NEXUS Requirements",
        "",
        "**QASL Shift-Left Testing Framework** · Inspección estática automatizada (IEEE 1028 / ISO 20246 / ISO 29148)",
        "",
        "| Campo | Valor |",
        "|---|---|",
        f"| Historia de Usuario | **{hu['id']} — {hu['nombre']}** |",
        f"| Versión analizada | v{cert['version_hu']} |",
        f"| Catálogo normativo | NX v{cert['version_catalogo']} |",
        f"| Fecha de análisis | {date.today().isoformat()} |",
        "| Analizado por | NEXUS Requirements · revisión humana pendiente |",
        "",
        "---",
        "",
        "## DICTAMEN",
        "",
        f"### {dictamen_map[cert['dictamen']]} — RHI {cert['rhi']} / 100",
        "",
        f"Cálculo auditable: {cert['puntos_obtenidos']}/{cert['puntos_totales']} puntos ponderados "
        "(CRÍTICO=5 · ALTO=3 · MEDIO=2 · BAJO=1).",
        "",
    ]
    if cert["criticos_incumplidos"]:
        lineas.append(f"**Reglas CRÍTICAS incumplidas:** {', '.join(cert['criticos_incumplidos'])}")
        lineas.append("")

    lineas += [
        "## RESUMEN DE CERTIFICACIÓN",
        "",
        "| Severidad | Cumple | Incumple | N/A |",
        "|---|---|---|---|",
    ]
    for s in ("CRITICO", "ALTO", "MEDIO", "BAJO"):
        lineas.append(f"| {s} | {r[s]['cumple']} | {r[s]['incumple']} | {r[s]['no_aplica']} |")
    lineas.append(f"| **Total ({total_eval} reglas)** | | | |")

    lineas += [
        "",
        "## COBERTURA DE REGLAS DE NEGOCIO",
        "",
        "| BR | Cobertura actual | Justificación |",
        "|---|---|---|",
    ]
    for c in cob["coberturas"]:
        pct = c["cobertura_porcentaje"]
        icono = "🟢" if pct == 100 else ("🟡" if pct > 0 else "🔴")
        lineas.append(f"| {c['br_id']} | {icono} {pct}% | {c.get('justificacion','')} |")

    res = cob["resumen"]
    lineas += [
        "",
        f"**Cobertura inicial promedio:** {res['cobertura_inicial_promedio']}% → "
        f"**proyectada con escenarios sugeridos:** {res['cobertura_proyectada']}%",
        f"**Gaps detectados:** {res['total_gaps']} — {res.get('gaps_por_severidad', {})}",
        "",
        "## ACTIVOS DE PRUEBA GENERADOS",
        "",
        f"- Suites: {len(activos['suites'])} · Precondiciones: {len(activos['precondiciones'])} · "
        f"Test Cases: {len(activos['test_cases'])}",
        f"- Suite smoke derivada: {', '.join(smoke) if smoke else '—'}",
        "- IDs deterministas e idempotentes (re-analizar no duplica).",
        "",
        "## VCR",
        "",
    ]
    if vcr:
        origen = vcr.get("origen", "HU")
        lineas.append(
            f"V={vcr['valor']} · C={vcr['costo']} · P={vcr['probabilidad']} · I={vcr['impacto']} → "
            f"R={vcr['riesgo']} → **VCR = {vcr['vcr_total']} → {vcr['decision']}** ({origen})"
        )
    else:
        lineas.append("*Sin estimaciones — completar en Planning Poker.*")

    if decisiones:
        lineas += ["", "## DECISIONES DE NEGOCIO REQUERIDAS", ""]
        for i, d in enumerate(decisiones, 1):
            lineas.append(f"{i}. {d}")

    lineas += [
        "",
        "## RIESGOS ACEPTADOS",
        "",
        "*Ninguno registrado. Todo gap no cerrado antes de desarrollo debe registrarse aquí "
        "con justificación y firma del responsable.*",
        "",
        "---",
        "",
        "## APROBACIONES (DoD del Analista → DoR de Desarrollo/QA)",
        "",
        "| Rol | Nombre | Decisión | Fecha | Firma |",
        "|---|---|---|---|---|",
        "| Analista Funcional (DoD) | ______ | ☐ Aprueba | ______ | ______ |",
        "| QA Lead | ______ | ☐ Valida activos | ______ | ______ |",
        "| Cliente / Product Owner (DoR) | ______ | ☐ Aprueba propuestos | ______ | ______ |",
        "",
        "*Generado por NEXUS Requirements. El framework define la norma; NEXUS la ejecuta; "
        "el ecosistema la consume.*",
    ]
    return "\n".join(lineas)


# ---------------------------------------------------------------------------
# HU Ideal (HTML — plantilla US ISTQB)
# ---------------------------------------------------------------------------

_CSS = """
  body { font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }
  .us-container { max-width: 900px; margin: 0 auto; }
  .us-header { background: #5C85D6; color: white; padding: 15px; text-align: center; font-weight: bold; font-size: 20px; }
  .version-banner { background: #e8f5e8; border: 1px solid #4caf50; padding: 8px 15px; font-size: 13px; }
  .us-table { width: 100%; border-collapse: collapse; }
  .us-table td { border: 1px solid #000; padding: 12px; vertical-align: top; }
  .label { background: #5C85D6; color: white; font-weight: bold; width: 200px; }
  .scenario-title { font-weight: bold; margin-top: 10px; }
  .scenario-content { margin-bottom: 10px; font-family: 'Courier New', monospace; background: #f5f5f5; padding: 10px; border-left: 3px solid #5C85D6; }
  .scenario-content.sugerido { border-left: 3px solid #4caf50; }
  .tag-sugerido { background: #4caf50; color: white; font-size: 10px; padding: 1px 6px; border-radius: 8px; margin-left: 6px; }
  .tag-propuesto { background: #F59E0B; color: white; font-size: 10px; padding: 1px 6px; border-radius: 8px; }
"""


def _campo(valor, vacio="—"):
    if valor == "NO_ESPECIFICADO" or valor is None:
        return vacio
    if isinstance(valor, list):
        return "<br>".join(f"&bull; {v}" for v in valor)
    return str(valor)


def _marcar_propuestos(texto: str) -> str:
    return (texto or "").replace(MARK, '<span class="tag-propuesto">PROPUESTO</span> [')


def _render_escenario(titulo, pasos, sugerido: bool, extra_tag: str = "") -> str:
    clase = "scenario-content sugerido" if sugerido else "scenario-content"
    tag = f'<span class="tag-sugerido">AGREGADO{extra_tag}</span>' if sugerido else ""
    cuerpo = "<br>".join(
        f"<strong>{p['tipo']}</strong> {_marcar_propuestos(p['texto'])}" for p in pasos
    )
    return (f'<div class="scenario-title">{titulo} {tag}</div>'
            f'<div class="{clase}">{cuerpo}</div>')


def render_hu_ideal(hu, cert, cob) -> str:
    brs_mejoradas = cob.get("brs_mejoradas") or [
        {"id": b["id"], "descripcion": b["descripcion"]} for b in hu["reglas_negocio"]
    ]
    brs_html = "<br>".join(
        f"{b['id']}: {_marcar_propuestos(b['descripcion'])}" for b in brs_mejoradas
    )

    escenarios_html = []
    for e in hu.get("escenarios", []):
        escenarios_html.append(_render_escenario(f"{e['id']}: {e['titulo']}", e["pasos"], sugerido=False))
    for g in cob.get("gaps", []):
        sug = g.get("escenario_sugerido")
        if sug and sug.get("pasos"):
            extra = f" · OWASP {g['owasp']}" if g.get("owasp") else ""
            escenarios_html.append(_render_escenario(sug.get("titulo", g["id"]), sug["pasos"], True, extra))

    epica = hu.get("epica")
    epica_txt = f"{epica['id']}: {epica['nombre']}" if isinstance(epica, dict) else "— (definir)"
    fa = hu.get("fuera_alcance")
    fa_txt = ("<br>".join(f"&bull; {i['item']} — <em>{i.get('cubierto_por','')}</em>" for i in fa)
              if isinstance(fa, list) else "—")

    return f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="UTF-8">
<title>HU Ideal — {hu['id']} (v{cert['version_hu'] + 1})</title>
<style>{_CSS}</style></head><body>
<div class="us-container">
  <div class="us-header">HISTORIA DE USUARIO — HU IDEAL (v{cert['version_hu'] + 1})</div>
  <div class="version-banner">✅ Generada por <strong>NEXUS Requirements</strong> desde la
  v{cert['version_hu']} (RHI {cert['rhi']} · {cert['dictamen'].replace('_',' ')}).
  Los valores <span class="tag-propuesto">PROPUESTO</span> requieren confirmación del negocio.</div>
  <table class="us-table">
    <tr><td class="label">ID</td><td>{hu['id']}</td></tr>
    <tr><td class="label">Nombre</td><td>{hu['nombre']}</td></tr>
    <tr><td class="label">Épica</td><td>{epica_txt}</td></tr>
    <tr><td class="label">Prioridad</td><td>{_campo(hu.get('prioridad'))}</td></tr>
    <tr><td class="label">Descripción</td><td><strong>Como</strong> {hu['descripcion']['como']}<br>
      <strong>Quiero</strong> {hu['descripcion']['quiero']}<br>
      <strong>Para</strong> {hu['descripcion']['para']}</td></tr>
    <tr><td class="label">Usuarios / Roles</td><td>{_campo(hu.get('usuarios_roles'))}</td></tr>
    <tr><td class="label">Reglas de Negocio</td><td>{brs_html}</td></tr>
    <tr><td class="label">Precondiciones</td><td>{_campo(hu.get('precondiciones'))}</td></tr>
    <tr><td class="label">Dependencias</td><td>{_campo(hu.get('dependencias'))}</td></tr>
    <tr><td class="label">Escenarios de Prueba (Criterios de Aceptación)</td>
        <td>{''.join(escenarios_html)}</td></tr>
    <tr><td class="label">Dentro del Alcance</td><td>{_campo(hu.get('dentro_alcance'))}</td></tr>
    <tr><td class="label">Fuera del Alcance</td><td>{fa_txt}</td></tr>
    <tr><td class="label">Referencias</td><td>{_campo(hu.get('referencias'))}</td></tr>
    <tr><td class="label">Notas</td><td>{_campo(hu.get('notas'), '')}</td></tr>
  </table>
</div></body></html>"""


# ---------------------------------------------------------------------------
# Export CSV (formato QASL Shift-Left)
# ---------------------------------------------------------------------------

def _csv_string(headers, rows) -> str:
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(headers)
    w.writerows(rows)
    return buf.getvalue()


def render_csvs(hu, cert, cob, activos, vcr) -> dict:
    """Devuelve {nombre_archivo: contenido_csv}."""
    epica = hu.get("epica")
    epic_id = epica["id"] if isinstance(epica, dict) else "EP-000"
    epic_txt = f"{epica['id']}: {epica['nombre']}" if isinstance(epica, dict) else "NO_ESPECIFICADO"

    brs = cob.get("brs_mejoradas") or hu["reglas_negocio"]
    brs_txt = " | ".join(f"{b['id']}: {b['descripcion']}" for b in brs)
    escenarios_txt = " | ".join(
        f"{t['escenario_id']}: {t['titulo']}" for t in activos["test_cases"]
    )
    res = cob["resumen"]

    us = _csv_string(
        ["EPIC_ID", "ID_HU", "Nombre_HU", "Epica", "Estado", "Prioridad",
         "VCR_Valor", "VCR_Costo", "VCR_Riesgo", "VCR_Total", "Requiere_Regresion",
         "Es_Deuda_Tecnica", "Cobertura_Inicial", "Cobertura_Proyectada",
         "Dictamen_NX", "RHI", "Criterios_Aceptacion", "Reglas_Negocio"],
        [[epic_id, hu["id"], hu["nombre"], epic_txt,
          "Analisis Estatico Completado", _campo(hu.get("prioridad")),
          vcr["valor"] if vcr else "", vcr["costo"] if vcr else "",
          vcr["riesgo"] if vcr else "", vcr["vcr_total"] if vcr else "",
          "Si" if (vcr and vcr["decision"] == "AUTOMATIZAR") else "No",
          "Si" if (vcr and vcr["decision"] == "AUTOMATIZAR") else "No",
          f"{res['cobertura_inicial_promedio']}%", f"{res['cobertura_proyectada']}%",
          cert["dictamen"], cert["rhi"], escenarios_txt, brs_txt]],
    )

    suites_rows = []
    for s in activos["suites"]:
        tcs = [t for t in activos["test_cases"] if t["ts_id"] == s["ts_id"]]
        suites_rows.append([
            epic_id, hu["id"], s["ts_id"], s["nombre"], s.get("descripcion", ""),
            s.get("prioridad", "Alta"), s["categoria"], s.get("tecnica", ""),
            " | ".join(f"{t['tc_id']}: {t['titulo']}" for t in tcs),
            "Planning", s.get("framework_sugerido", "Playwright + Newman"), "QA", len(tcs),
        ])
    ts = _csv_string(
        ["EPIC_ID", "US_ID", "TS_ID", "Nombre_Suite", "Descripcion_Suite", "Prioridad",
         "Categoria", "Tecnica_Aplicada", "TC_Generados", "Estado", "QA_Framework",
         "Ambiente_Testing", "Total_TC"], suites_rows)

    prc_rows = []
    for p in activos["precondiciones"]:
        tcs_asoc = [t["tc_id"] for t in activos["test_cases"]
                    if p["prc_id"] in t.get("prcs_asociadas", [])]
        prc_rows.append([
            p["prc_id"], p["titulo"], p.get("descripcion", ""),
            " | ".join(p.get("pasos_setup", [])), p.get("datos_requeridos", ""),
            p.get("estado_sistema", ""), p.get("categoria", ""),
            "Si" if p.get("reutilizable", True) else "No", ", ".join(tcs_asoc),
        ])
    prc = _csv_string(
        ["PRC_ID", "Titulo_PRC", "Descripcion", "Pasos_Precondicion", "Datos_Requeridos",
         "Estado_Sistema", "Categoria", "Reutilizable", "TC_Asociados"], prc_rows)

    tc_rows = []
    for t in activos["test_cases"]:
        tc_rows.append([
            t["tc_id"], hu["id"], t["ts_id"], t["titulo"], t.get("tipo_prueba", "Funcional"),
            ", ".join(t.get("prcs_asociadas", [])), t.get("datos_entrada", ""),
            t.get("resultado_esperado", ""), t.get("prioridad", "Alta"),
            t.get("complejidad", "Media"), "Diseñando",
            "Si" if t.get("es_smoke") else "No", t.get("tiempo_estimado", ""),
            "NEXUS Requirements", t["escenario_id"], ", ".join(t.get("brs_cubiertas", [])),
            t.get("tecnica", ""), t.get("origen", ""),
        ])
    tc = _csv_string(
        ["TC_ID", "US_ID", "TS_ID", "Titulo_TC", "Tipo_Prueba", "PRC_Asociadas",
         "Datos_Entrada", "Resultado_Esperado", "Prioridad", "Complejidad", "Estado",
         "Es_Smoke", "Tiempo_Estimado", "Creado_Por", "Cobertura_Escenario",
         "Cobertura_BR", "Tecnica_Aplicada", "Origen"], tc_rows)

    return {
        "1_User_Storie.csv": us,
        "2_Test_Suite.csv": ts,
        "3_Precondition.csv": prc,
        "4_Test_Case.csv": tc,
    }
