# -*- coding: utf-8 -*-
"""Catálogo NX: carga de la norma, evaluación estructural por código,
cálculo determinista del RHI y dictamen.

Principio 2 del blueprint: el LLM decide lo semántico; la aritmética y las
verificaciones de presencia/formato son SIEMPRE código reproducible.
"""
import re

import yaml

from nexus import NexusPipelineError
from nexus.config import NX_RULES_FILE, VCR_POLICY_FILE

DICTAMENES = ("CERTIFICADO", "APTO_PARA_DESARROLLO", "REQUIERE_REVISION", "NO_APTO")


def load_catalog() -> dict:
    with open(NX_RULES_FILE, "r", encoding="utf-8") as f:
        cat = yaml.safe_load(f)
    if not cat or "reglas" not in cat:
        raise NexusPipelineError("catalogo", f"Catálogo inválido o vacío: {NX_RULES_FILE}")
    return cat


def load_vcr_policy() -> dict:
    with open(VCR_POLICY_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# ---------------------------------------------------------------------------
# Evaluación estructural (familia 'estructura') — 100% código
# ---------------------------------------------------------------------------

def _es_lista(valor) -> bool:
    return isinstance(valor, list) and len(valor) > 0


def _check_nx001(hu):
    ok = bool(re.match(r"^HU_[A-Z0-9]+_\d{2}$", str(hu.get("id", ""))))
    return ok, f"ID '{hu.get('id')}' {'con formato válido' if ok else 'no cumple HU_<MODULO>_<NN>'}"


def _check_nx002(hu):
    d = hu.get("descripcion") or {}
    ok = all(isinstance(d.get(k), str) and d.get(k).strip() for k in ("como", "quiero", "para"))
    return ok, "Como/Quiero/Para completos" if ok else "Descripción sin estructura Como/Quiero/Para completa"


def _check_nx003(hu):
    e = hu.get("epica")
    ok = isinstance(e, dict) and re.match(r"^EP-\d{3}$", str(e.get("id", "")))
    return ok, f"Épica: {e}" if ok else "Sin épica referenciada con ID EP-NNN"


def _check_nx004(hu):
    p = hu.get("prioridad")
    ok = isinstance(p, str) and p != "NO_ESPECIFICADO" and p.strip() != ""
    return ok, f"Prioridad: {p}" if ok else "Prioridad no declarada"


def _check_nx005(hu):
    brs = hu.get("reglas_negocio") or []
    if not brs:
        return False, "Sin reglas de negocio identificables"
    inferidas = [b["id"] for b in brs if b.get("origen") == "inferida_de_texto"]
    if inferidas:
        return False, f"BRs sin numerar en el documento fuente (inferidas en normalización: {', '.join(inferidas)})"
    return True, f"{len(brs)} BRs numeradas explícitamente"


def _check_nx006(hu):
    escs = hu.get("escenarios") or []
    if not escs:
        return False, "Cero escenarios Gherkin documentados"
    tipos_requeridos = {"DADO", "CUANDO", "ENTONCES"}
    incompletos = [
        e["id"] for e in escs
        if not tipos_requeridos.issubset({p.get("tipo") for p in e.get("pasos", [])})
    ]
    if incompletos:
        return False, f"Escenarios sin DADO/CUANDO/ENTONCES completos: {', '.join(incompletos)}"
    return True, f"{len(escs)} escenarios Gherkin completos"


def _check_nx007(hu):
    ok = _es_lista(hu.get("precondiciones"))
    return ok, "Precondiciones declaradas" if ok else "Sin precondiciones declaradas"


def _check_nx008(hu):
    ok = _es_lista(hu.get("dependencias"))
    return ok, "Dependencias declaradas" if ok else "Sin dependencias declaradas (ni 'Ninguna' explícito)"


def _check_nx009(hu):
    est = hu.get("estimaciones")
    if not isinstance(est, dict):
        return False, "Sin estimaciones VCR"
    claves = ("valor", "costo", "probabilidad", "impacto")
    faltan = [k for k in claves if not isinstance(est.get(k), int)]
    if faltan:
        return False, f"Estimaciones incompletas, faltan: {', '.join(faltan)}"
    fuera = [k for k in claves if not (1 <= est[k] <= 3)]
    if fuera:
        return False, f"Valores fuera de la escala oficial 1-3: {', '.join(fuera)}"
    return True, "Estimaciones VCR completas en escala oficial"


def _check_nx010(hu):
    ok = _es_lista(hu.get("dentro_alcance"))
    return ok, "Alcance declarado" if ok else "Sin sección Dentro del Alcance"


def _check_nx011(hu):
    fa = hu.get("fuera_alcance")
    if not _es_lista(fa):
        return False, "Sin sección Fuera del Alcance"
    sin_ref = [i.get("item", "?") for i in fa
               if not (i.get("cubierto_por") or "").strip()]
    if sin_ref:
        return False, f"Exclusiones sin referencia cruzada: {', '.join(sin_ref)}"
    return True, "Fuera de alcance con referencias cruzadas"


def _check_nx012(hu):
    ok = _es_lista(hu.get("usuarios_roles"))
    return ok, "Roles identificados" if ok else "Usuarios/Roles no identificados"


def _check_nx013(hu):
    ok = _es_lista(hu.get("referencias"))
    return ok, "Referencias presentes" if ok else "Sin referencias documentales"


_CHECKS = {
    "NX-001": _check_nx001, "NX-002": _check_nx002, "NX-003": _check_nx003,
    "NX-004": _check_nx004, "NX-005": _check_nx005, "NX-006": _check_nx006,
    "NX-007": _check_nx007, "NX-008": _check_nx008, "NX-009": _check_nx009,
    "NX-010": _check_nx010, "NX-011": _check_nx011, "NX-012": _check_nx012,
    "NX-013": _check_nx013,
}


def evaluate_structural(hu: dict, catalogo: dict) -> list:
    """Evalúa las reglas de familia 'estructura' por código puro."""
    evaluaciones = []
    for regla in catalogo["reglas"]:
        if regla["familia"] != "estructura":
            continue
        check = _CHECKS.get(regla["id"])
        if check is None:
            raise NexusPipelineError("certificador", f"Regla estructural sin check implementado: {regla['id']}")
        ok, evidencia = check(hu)
        evaluaciones.append({
            "regla": regla["id"],
            "veredicto": "CUMPLE" if ok else "INCUMPLE",
            "evidencia": evidencia,
        })
    return evaluaciones


# ---------------------------------------------------------------------------
# RHI y dictamen — aritmética pura
# ---------------------------------------------------------------------------

def compute_rhi(evaluaciones: list, catalogo: dict) -> dict:
    pesos = catalogo["meta"]["pesos"]
    sev = {r["id"]: r["severidad"] for r in catalogo["reglas"]}

    ids_evaluadas = {e["regla"] for e in evaluaciones}
    faltantes = [r["id"] for r in catalogo["reglas"] if r["id"] not in ids_evaluadas]
    if faltantes:
        raise NexusPipelineError("certificador", f"Reglas del catálogo sin evaluar: {', '.join(faltantes)}")

    obtenidos = totales = 0
    criticos_incumplidos = []
    resumen = {s: {"cumple": 0, "incumple": 0, "no_aplica": 0} for s in ("CRITICO", "ALTO", "MEDIO", "BAJO")}

    for ev in evaluaciones:
        s = sev.get(ev["regla"])
        if s is None:
            raise NexusPipelineError("certificador", f"Evaluación de regla desconocida: {ev['regla']}")
        v = ev["veredicto"]
        if v == "NO_APLICA":
            resumen[s]["no_aplica"] += 1
            continue
        peso = pesos[s]
        totales += peso
        if v == "CUMPLE":
            obtenidos += peso
            resumen[s]["cumple"] += 1
        else:
            resumen[s]["incumple"] += 1
            if s == "CRITICO":
                criticos_incumplidos.append(ev["regla"])

    rhi = round(100.0 * obtenidos / totales, 1) if totales else 0.0

    if rhi == 100.0 and not criticos_incumplidos:
        dictamen = "CERTIFICADO"
    elif rhi >= 90.0 and not criticos_incumplidos:
        dictamen = "APTO_PARA_DESARROLLO"
    elif rhi >= 60.0 and not criticos_incumplidos:
        dictamen = "REQUIERE_REVISION"
    else:
        dictamen = "NO_APTO"

    return {
        "puntos_obtenidos": obtenidos,
        "puntos_totales": totales,
        "rhi": rhi,
        "dictamen": dictamen,
        "criticos_incumplidos": sorted(criticos_incumplidos),
        "resumen_por_severidad": resumen,
    }


def compute_vcr(est: dict, policy: dict) -> dict:
    """R = P×I; VCR = V+C+R; decisión según umbral de la política."""
    v, c, p, i = est["valor"], est["costo"], est["probabilidad"], est["impacto"]
    r = p * i
    total = v + c + r
    umbral = int(policy["decision"]["automatizar_si"].split(">=")[1])
    return {
        "valor": v, "costo": c, "probabilidad": p, "impacto": i,
        "riesgo": r, "vcr_total": total,
        "decision": "AUTOMATIZAR" if total >= umbral else "MANUAL",
    }
