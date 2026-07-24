# -*- coding: utf-8 -*-
"""Agentes del pipeline NEXUS (A1 Normalizador, A2 Certificador,
A3 Cobertura, A4 Generador).

Cada agente construye su prompt, exige JSON y valida el contrato.
El código nunca re-decide lo que un agente ya decidió (principio 2),
y toda aritmética (RHI, VCR, IDs, es_smoke) es determinista.
"""
import json

from nexus import NexusPipelineError
from nexus.catalog import compute_rhi, evaluate_structural
from nexus.contracts import validate

MARCA_PROPUESTO = "[PROPUESTO"  # los valores propuestos llevan '[PROPUESTO...]'

# Clave que identifica la raíz correcta de cada contrato (para desenvolver
# respuestas que el modelo envuelve en una clave contenedora)
_MARCADOR_RAIZ = {"hu_canonica": "id", "cobertura": "coberturas", "activos": "test_cases"}


def _limpiar_nulos(obj):
    """Elimina recursivamente claves con valor null: en campos opcionales,
    null significa 'ausente' (los modelos suelen emitirlo así)."""
    if isinstance(obj, dict):
        return {k: _limpiar_nulos(v) for k, v in obj.items() if v is not None}
    if isinstance(obj, list):
        return [_limpiar_nulos(x) for x in obj]
    return obj


_RE_PASO = None  # compilado perezoso


def _coerce_pasos(pasos):
    """Convierte pasos Gherkin en string ('DADO que...', 'DADOque...') a objetos
    tipados {tipo, texto}. Conversión de formato pura — no interpreta contenido."""
    import re
    global _RE_PASO
    if _RE_PASO is None:
        _RE_PASO = re.compile(r"^\s*(DADO|CUANDO|ENTONCES|Y)\s*(.*)$", re.IGNORECASE)
    if not isinstance(pasos, list):
        return pasos
    resultado = []
    for p in pasos:
        if isinstance(p, dict):
            resultado.append(p)
            continue
        if isinstance(p, str):
            m = _RE_PASO.match(p)
            if m and m.group(2).strip():
                resultado.append({"tipo": m.group(1).upper(), "texto": m.group(2).strip()})
            elif resultado:  # línea sin keyword: se anexa como Y
                resultado.append({"tipo": "Y", "texto": p.strip()})
            else:
                resultado.append({"tipo": "DADO", "texto": p.strip()})
    return resultado


def _inferir_tipo_gap(gap: dict) -> str:
    """Si el modelo omitió tipo_gap, se infiere del propio texto del gap
    (precedencia: seguridad > límite > negativo > positivo)."""
    texto = f"{gap.get('descripcion','')} {gap.get('escenario_sugerido',{}).get('titulo','')}".lower()
    if gap.get("owasp") or any(k in texto for k in ("seguridad", "owasp", "token", "auditor", "enumera")):
        return "falta_seguridad"
    if any(k in texto for k in ("límite", "limite", "frontera", "borde")):
        return "falta_limite"
    if "negativ" in texto:
        return "falta_negativo"
    if "positiv" in texto:
        return "falta_positivo"
    return "sin_escenarios"


def _coercionar(data: dict, contrato: str) -> dict:
    """Coerciones deterministas para variaciones inofensivas de formato que los
    modelos producen: lista de notas → texto unido; 'NO_ESPECIFICADO' en campos
    que el contrato exige como lista → lista vacía. Nunca cambia el significado."""
    if not isinstance(data, dict):
        return data
    if contrato == "hu_canonica":
        if isinstance(data.get("notas"), list):
            data["notas"] = " | ".join(str(n) for n in data["notas"])
        for campo in ("escenarios", "reglas_negocio"):
            if data.get(campo) == "NO_ESPECIFICADO":
                data[campo] = []
                nolist = data.get("_meta", {}).get("campos_no_especificados")
                if isinstance(nolist, list) and campo not in nolist:
                    nolist.append(campo)
        desc = data.get("descripcion")
        if isinstance(desc, dict):
            for k, v in list(desc.items()):
                if isinstance(v, list):
                    desc[k] = " ".join(str(x) for x in v)
        for esc in data.get("escenarios", []) or []:
            if isinstance(esc, dict):
                esc["pasos"] = _coerce_pasos(esc.get("pasos", []))
    if contrato == "cobertura":
        for gap in data.get("gaps", []) or []:
            if not isinstance(gap, dict):
                continue
            if "tipo_gap" not in gap:
                gap["tipo_gap"] = _inferir_tipo_gap(gap)
            sug = gap.get("escenario_sugerido")
            if isinstance(sug, dict):
                sug["pasos"] = _coerce_pasos(sug.get("pasos", []))
    if contrato == "activos":
        data = _coercionar_activos(data)
    return data


def _alias(obj: dict, destino: str, *alias):
    """Renombra el primer alias presente al nombre canónico del contrato."""
    if destino not in obj:
        for a in alias:
            if a in obj:
                obj[destino] = obj.pop(a)
                break


def _coerce_categoria_suite(cat: str) -> str:
    c = (cat or "").lower()
    if "owasp" in c or "seguridad" in c:
        return "Seguridad - OWASP"
    if "negativ" in c:
        return "Funcional - Negativa"
    if "integra" in c:
        return "Integracion"
    return "Funcional"


def _coercionar_activos(data: dict) -> dict:
    """Alias y defaults deterministas para el contrato de activos."""
    for i, prc in enumerate(data.get("precondiciones", []) or [], start=1):
        if not isinstance(prc, dict):
            continue
        _alias(prc, "titulo", "nombre", "title", "titulo_prc")
        _alias(prc, "categoria", "tipo", "category")
        _alias(prc, "pasos_setup", "pasos", "setup", "pasos_precondicion")
        _alias(prc, "datos_requeridos", "datos")
        if "titulo" not in prc:
            prc["titulo"] = (prc.get("descripcion") or f"Precondición {i}")[:80]
        if "categoria" not in prc:
            prc["categoria"] = "General"
        if isinstance(prc.get("pasos_setup"), str):
            prc["pasos_setup"] = [prc["pasos_setup"]]

    for s in data.get("suites", []) or []:
        if not isinstance(s, dict):
            continue
        _alias(s, "nombre", "titulo", "nombre_suite")
        _alias(s, "categoria", "tipo", "category")
        s["categoria"] = _coerce_categoria_suite(s.get("categoria", ""))

    for tc in data.get("test_cases", []) or []:
        if not isinstance(tc, dict):
            continue
        _alias(tc, "titulo", "nombre", "titulo_tc", "title")
        _alias(tc, "escenario_id", "escenario", "e_id")
        _alias(tc, "brs_cubiertas", "br_cubiertas", "brs", "cobertura_br", "br_afectada")
        _alias(tc, "prcs_asociadas", "precondiciones", "prc_asociadas", "prcs")
        if isinstance(tc.get("brs_cubiertas"), str):
            tc["brs_cubiertas"] = [b.strip() for b in tc["brs_cubiertas"].split(",") if b.strip()]
        if "brs_cubiertas" not in tc:
            tc["brs_cubiertas"] = []
        if isinstance(tc.get("prcs_asociadas"), str):
            tc["prcs_asociadas"] = [p.strip() for p in tc["prcs_asociadas"].split(",") if p.strip()]
        pasos = tc.get("pasos")
        if isinstance(pasos, list):
            nuevos = []
            for j, p in enumerate(pasos, start=1):
                if isinstance(p, str):
                    p = {"accion": p}
                if isinstance(p, dict):
                    _alias(p, "accion", "paso_accion", "paso")
                    _alias(p, "resultado_esperado", "resultado", "esperado")
                    _alias(p, "datos", "datos_entrada")
                    p.setdefault("numero", j)
                    p.setdefault("accion", "Ejecutar el paso del escenario")
                    p.setdefault("resultado_esperado", tc.get("resultado_esperado", ""))
                    nuevos.append(p)
            tc["pasos"] = nuevos
        if not tc.get("pasos"):
            tc["pasos"] = [{
                "numero": 1,
                "accion": tc.get("datos_entrada", "Ejecutar el escenario"),
                "datos": tc.get("datos_entrada", ""),
                "resultado_esperado": tc.get("resultado_esperado", ""),
            }]
    return data


def _desenvolver(data: dict, contrato: str) -> dict:
    """Si el modelo envolvió la respuesta ({"hu_canonica": {...}}), la desenvuelve."""
    marcador = _MARCADOR_RAIZ.get(contrato)
    for _ in range(2):  # hasta 2 niveles de envoltura
        if not isinstance(data, dict) or marcador in data:
            break
        if len(data) == 1:
            unico = next(iter(data.values()))
            if isinstance(unico, dict):
                data = unico
                continue
        break
    return data


def _call_validado(llm, etapa: str, prompt: str, contrato: str,
                   max_tokens: int = 8000, postproc=None, reintentos: int = 2) -> dict:
    """Llama al agente, desenvuelve, postprocesa y valida contra el contrato.
    Si el contrato se viola, reintenta con el detalle del error como feedback.
    Agotados los reintentos, falla ruidosamente (sin fallback silencioso)."""
    ultimo_error = None
    p = prompt
    for _ in range(reintentos + 1):
        data = _limpiar_nulos(_desenvolver(llm.call_json(etapa, p, max_tokens=max_tokens), contrato))
        data = _coercionar(data, contrato)
        if postproc:
            data = postproc(data)
        try:
            return validate(contrato, data, etapa)
        except NexusPipelineError as e:
            ultimo_error = e
            print(f"      [{etapa}] la respuesta violó el contrato — reenviando con "
                  f"el detalle del error para autocorrección...", flush=True)
            p = (prompt + "\n\nCORRECCIÓN REQUERIDA: tu respuesta anterior violó el "
                 f"contrato JSON ({e.mensaje}). Devuelve el objeto con la estructura "
                 "EXACTA pedida EN EL NIVEL RAÍZ del JSON, sin envolverlo en ninguna "
                 "clave contenedora y con todos los campos requeridos.")
    raise ultimo_error


# ---------------------------------------------------------------------------
# A1 — NORMALIZADOR
# ---------------------------------------------------------------------------

def normalizar(llm, texto_fuente: str, nombre_fuente: str) -> dict:
    prompt = f"""FASE: NORMALIZACIÓN DE REQUERIMIENTO (A1)

Transforma el documento fuente (cualquier formato: Markdown, HTML, texto de Jira,
correo) a la HU Canónica del QASL Shift-Left Testing Framework.

REGLAS ESTRICTAS:
1. PROHIBIDO INVENTAR: todo campo ausente en la fuente se marca con el string "NO_ESPECIFICADO".
   No completes épica, escenarios, estimaciones ni alcance si el documento no los trae.
2. Si el documento trae reglas de negocio SIN numerar (viñetas, párrafos), normalízalas como
   BR1, BR2... con "origen": "inferida_de_texto". Si ya vienen numeradas, "origen": "explicita".
3. Los escenarios solo se registran si están realmente en la fuente con estructura Gherkin
   (aunque sea informal). Un criterio vago tipo "funciona sin problemas" NO es un escenario:
   va en "notas" como criterio no verificable.
4. Cada escenario se descompone en pasos tipados: lista ordenada de objetos
   {{"tipo": "DADO|CUANDO|ENTONCES|Y", "texto": "..."}}. Soporta múltiples Y y CUANDO.
5. En _meta declara: "campos_no_especificados" (lista de campos marcados),
   "supuestos_normalizacion" (todo lo que inferiste y por qué), "fuente": "{nombre_fuente}", "version": 1.
6. "fuera_alcance", si existe, es lista de objetos {{"item": "...", "cubierto_por": "HU_XXX o 'sin cobertura planificada'"}}.
7. "epica", si existe, es objeto {{"id": "EP-NNN", "nombre": "..."}}.
8. "estimaciones", si existe, es objeto con sp, valor, costo, probabilidad, impacto (enteros).

DOCUMENTO FUENTE ({nombre_fuente}):
---------------------------------
{texto_fuente}
---------------------------------

Responde SOLO el JSON de la HU Canónica, con "id", "nombre", "descripcion", etc.
DIRECTAMENTE en el nivel raíz del objeto (NO lo envuelvas en una clave como "hu_canonica")."""
    return _call_validado(llm, "normalizador", prompt, "hu_canonica")


# ---------------------------------------------------------------------------
# A2 — CERTIFICADOR
# ---------------------------------------------------------------------------

def certificar(llm, hu: dict, catalogo: dict, version_hu: int = 1) -> dict:
    # 1) Reglas estructurales: código puro
    ev_estructura = evaluate_structural(hu, catalogo)

    # 2) Reglas semánticas: LLM (familias redaccion, testabilidad, nfr)
    reglas_llm = [r for r in catalogo["reglas"] if r["familia"] != "estructura"]
    listado = "\n".join(
        f'- {r["id"]} ({r["severidad"]}, familia {r["familia"]}): {r["nombre"]} — {r["criterio"]}'
        for r in reglas_llm
    )
    prompt = f"""FASE: CERTIFICACIÓN NORMATIVA (A2) — Inspección estática IEEE 1028 automatizada

Evalúa la HU Canónica contra las siguientes reglas del Catálogo NX. Para CADA regla
emite un objeto con: "regla" (id), "veredicto" ("CUMPLE" | "INCUMPLE" | "NO_APLICA"),
"evidencia" (cita concreta del texto que sustenta el veredicto) y, si INCUMPLE,
"recomendacion" accionable. Si NO_APLICA, incluye "justificacion_na".

CRITERIOS DE EXIGENCIA:
- Sé estricto: ante la duda, INCUMPLE. Un requerimiento ambiguo que llega a desarrollo
  es el defecto más caro del proyecto.
- NX-021 (verificabilidad): una BR con términos como "rápido", "seguro" o "adecuado"
  sin cuantificar NO es verificable.
- NX-030/031: revisa BR por BR si existe escenario positivo/negativo que la valide
  semánticamente (no por palabras iguales, por significado).
- NX-033: si la HU toca autenticación, permisos o datos sensibles y no tiene escenarios
  de seguridad, INCUMPLE con referencia OWASP.
- NO_APLICA solo con justificación real (ej. NX-041 en una HU sin interfaz de usuario).

REGLAS A EVALUAR:
{listado}

HU CANÓNICA:
{json.dumps(hu, ensure_ascii=False, indent=2)}

Responde SOLO: {{"evaluaciones": [ ... una entrada por CADA regla listada ... ]}}"""
    resp = llm.call_json("certificador", prompt)
    while isinstance(resp, dict) and "evaluaciones" not in resp and len(resp) == 1:
        resp = next(iter(resp.values()))  # desenvolver si vino envuelto
    ev_semantica = _limpiar_nulos(resp.get("evaluaciones", [])) if isinstance(resp, dict) else []

    ids_esperadas = {r["id"] for r in reglas_llm}
    ids_recibidas = {e.get("regla") for e in ev_semantica}
    if ids_esperadas != ids_recibidas:
        faltan = ids_esperadas - ids_recibidas
        sobran = ids_recibidas - ids_esperadas
        raise NexusPipelineError(
            "certificador",
            f"El agente no evaluó el catálogo completo. Faltan: {sorted(faltan)}; sobran: {sorted(sobran)}"
        )

    evaluaciones = ev_estructura + ev_semantica

    # 3) RHI y dictamen: aritmética pura
    resultado = compute_rhi(evaluaciones, catalogo)
    cert = {
        "hu_id": hu["id"],
        "version_hu": version_hu,
        "version_catalogo": catalogo["meta"]["version"],
        "evaluaciones": evaluaciones,
        **resultado,
    }
    return validate("certificacion", cert, "certificador")


# ---------------------------------------------------------------------------
# A3 — COBERTURA (RTM)
# ---------------------------------------------------------------------------

def analizar_cobertura(llm, hu: dict) -> dict:
    prompt = f"""FASE: ANÁLISIS DE COBERTURA RTM (A3)

Analiza semánticamente qué escenarios cubren cada Regla de Negocio (BR) y detecta gaps.

METODOLOGÍA:
1. Regla fundamental: 1 BR = mínimo 1 escenario POSITIVO + 1 NEGATIVO.
2. Mapeo por SIGNIFICADO, no por palabras iguales. Un escenario puede cubrir varias BRs.
3. cobertura_porcentaje por BR: 100 (positivo Y negativo), 50 (solo uno), 0 (ninguno).
4. Gaps adicionales obligatorios cuando apliquen:
   - falta_limite: BRs con valores numéricos sin escenario de frontera (valor exacto, -1, +1).
   - falta_seguridad: BRs de autenticación/permisos/credenciales sin escenario de seguridad
     (referencia OWASP Top 10:2021: A01, A03, A07, A09...). Incluye anti-enumeración de
     usuarios, tokens de un solo uso y auditoría de eventos donde corresponda.
5. Cada gap incluye "id", "br_id", "tipo_gap", "severidad", "descripcion" y
   "escenario_sugerido" ESPECÍFICO al contexto de la HU (no genérico).
   FORMATO OBLIGATORIO de pasos — lista de OBJETOS, nunca strings:
   "escenario_sugerido": {{"titulo": "E4 - ...", "pasos": [
     {{"tipo": "DADO", "texto": "que el link fue generado hace más de 30 minutos"}},
     {{"tipo": "CUANDO", "texto": "el usuario accede al link"}},
     {{"tipo": "ENTONCES", "texto": "el sistema muestra 'El enlace ha expirado'"}}
   ]}}
6. Si la HU tiene valores sin cuantificar (ej. "expira rápido"), tus escenarios sugeridos
   DEBEN proponer un valor concreto marcándolo "[VALOR PROPUESTO — confirmar con negocio]".
7. Además del contrato, agrega el campo "brs_mejoradas": lista de
   {{"id": "BRn", "descripcion": "BR reescrita, cuantificada y verificable (valores nuevos marcados [PROPUESTO])"}} —
   incluye BRs NUEVAS si detectas requisitos implícitos obligatorios (ej. auditoría por OWASP A09).
8. Severidades de gaps: CRITICO (seguridad/permisos/credenciales, BR sin negativo de auth),
   ALTO (funcionalidad principal, límites), MEDIO (visualización), BAJO (formato).
9. resumen.cobertura_inicial_promedio = promedio de cobertura_porcentaje por BR.
   resumen.cobertura_proyectada = cobertura si se agregan todos los sugeridos.
10. IDs de gaps: GAP-001, GAP-002... IDs de escenarios sugeridos: continúa la numeración
    existente (si la HU tiene E1-E3, sugeridos desde E4; si no tiene, desde E1).

HU CANÓNICA:
{json.dumps(hu, ensure_ascii=False, indent=2)}

Responde SOLO el JSON del contrato de cobertura (con brs_mejoradas incluido),
con "hu_id", "coberturas", "gaps" y "resumen" DIRECTAMENTE en el nivel raíz."""
    return _call_validado(llm, "cobertura", prompt, "cobertura", max_tokens=12000)


# ---------------------------------------------------------------------------
# A4 — GENERADOR DE ACTIVOS
# ---------------------------------------------------------------------------

def generar_activos(llm, hu: dict, cobertura: dict, vcr_policy: dict) -> dict:
    prompt = f"""FASE: GENERACIÓN DE ACTIVOS DE PRUEBA (A4)

Genera los activos ejecutables a partir de la HU y su análisis de cobertura
(escenarios originales + sugeridos). Estándar de calidad: casos listos para que
un automatizador escriba el script sin preguntar nada.

REGLAS:
1. SUITES (2-3): TS de Flujos Positivos (Funcional), TS de Flujos Negativos
   (Funcional - Negativa) y, si hay escenarios de seguridad, TS Seguridad - OWASP.
   Declara técnica ISTQB por suite y framework sugerido (Playwright + Newman [+ ZAP]).
2. PRECONDICIONES (3-5): específicas de ESTA HU (no genéricas). Cada una con
   pasos_setup ejecutables, datos_requeridos concretos y estado_sistema.
   Incluye precondiciones de datos en estados especiales si los flujos negativos
   los requieren (ej. tokens expirados/usados pre-generados).
3. SÉ COMPACTO — tu respuesta debe caber en el límite de tokens:
   textos breves y precisos, sin párrafos largos ni repeticiones; máximo 3 pasos
   por TC (los simples con 1 paso); no repitas la descripción del escenario en
   el título ni en los pasos.
4. TEST CASES: exactamente 1 por escenario (originales y sugeridos).
   - datos_entrada CONCRETOS con valores frontera reales (no "datos válidos":
     valores exactos en el límite, límite-1, límite+1, vacío).
   - resultado_esperado preciso y verificable, con mensajes textuales.
   - pasos: lista numerada accion/datos/resultado (mínimo 1, los complejos más).
   - tecnica ISTQB por TC (Partición de Equivalencia, Valores Límite,
     Tabla de Decisión, Análisis Causa-Efecto, Análisis de Riesgos OWASP).
   - "origen": "original" si el escenario estaba en la HU, "gap_sugerido" si viene del análisis.
   - "es_smoke": true SOLO para escenarios positivos del flujo principal (regla: se ajusta por código después).
5. Los tc_id/ts_id/prc_id que propongas serán REEMPLAZADOS por IDs deterministas
   por código — usa placeholders con el id del escenario (ej. "TC_E1").
6. Si la HU no trae estimaciones VCR, agrega "vcr_propuesto":
   {{"valor": 1-3, "costo": 1-3, "probabilidad": 1-3, "impacto": 1-3, "justificacion": "..."}}
   según la política: Valor=beneficio negocio; Costo=costo de la prueba MANUAL por ciclo;
   escala oficial 1-3.

HU CANÓNICA:
{json.dumps(hu, ensure_ascii=False, indent=2)}

ANÁLISIS DE COBERTURA (gaps + escenarios sugeridos + brs_mejoradas):
{json.dumps(cobertura, ensure_ascii=False, indent=2)}

FORMATO OBLIGATORIO (nombres de campos EXACTOS):
- precondiciones: [{{"prc_id": "PRC_1", "titulo": "...", "descripcion": "...",
  "pasos_setup": ["..."], "datos_requeridos": "...", "estado_sistema": "...",
  "categoria": "Datos de Prueba", "reutilizable": true}}]
- test_cases: [{{"tc_id": "TC_E1", "ts_id": "TS_POS", "titulo": "...",
  "tipo_prueba": "Funcional", "escenario_id": "E1", "brs_cubiertas": ["BR1"],
  "prcs_asociadas": ["PRC_1"], "tecnica": "...", "origen": "gap_sugerido",
  "es_smoke": false, "prioridad": "Alta", "complejidad": "Media",
  "tiempo_estimado": "20 min", "datos_entrada": "...", "resultado_esperado": "...",
  "pasos": [{{"numero": 1, "accion": "...", "datos": "...", "resultado_esperado": "..."}}]}}

Responde SOLO el JSON del contrato de activos (con vcr_propuesto si aplica),
con "hu_id", "suites", "precondiciones" y "test_cases" DIRECTAMENTE en el nivel raíz."""

    def _postproc(data):
        data = _asignar_ids_deterministas(hu["id"], data)
        return _aplicar_regla_smoke(data)

    return _call_validado(llm, "generador", prompt, "activos",
                          max_tokens=24000, postproc=_postproc)


def _asignar_ids_deterministas(hu_id: str, activos: dict) -> dict:
    """IDs idempotentes por diseño: {HU}_TS{NN}, {HU}_PRC{NN}, {HU}_TC_{E}.
    Re-analizar la misma HU produce SIEMPRE los mismos IDs (fix del bug de
    duplicación de MS-02 v3)."""
    mapa_ts = {}
    for i, suite in enumerate(activos.get("suites", []), start=1):
        nuevo = f"{hu_id}_TS{i:02d}"
        mapa_ts[suite.get("ts_id", nuevo)] = nuevo
        suite["ts_id"] = nuevo

    mapa_prc = {}
    for i, prc in enumerate(activos.get("precondiciones", []), start=1):
        nuevo = f"{hu_id}_PRC{i:02d}"
        mapa_prc[prc.get("prc_id", nuevo)] = nuevo
        prc["prc_id"] = nuevo

    for tc in activos.get("test_cases", []):
        esc = tc.get("escenario_id", "EX")
        tc["tc_id"] = f"{hu_id}_TC_{esc}"
        tc["ts_id"] = mapa_ts.get(tc.get("ts_id"), tc.get("ts_id", ""))
        tc["prcs_asociadas"] = [mapa_prc.get(p, p) for p in tc.get("prcs_asociadas", [])]

    activos["hu_id"] = hu_id
    return activos


def _aplicar_regla_smoke(activos: dict) -> dict:
    """Regla determinista (D4 del blueprint): el smoke son los TCs positivos del
    flujo principal. El código garantiza al menos 1 y que ningún negativo/seguridad
    quede marcado."""
    smoke_validos = []
    for tc in activos.get("test_cases", []):
        es_funcional_positivo = tc.get("tipo_prueba") == "Funcional"
        if not es_funcional_positivo:
            tc["es_smoke"] = False
        if tc.get("es_smoke"):
            smoke_validos.append(tc["tc_id"])
    if not smoke_validos:
        for tc in activos.get("test_cases", []):
            if tc.get("tipo_prueba") == "Funcional":
                tc["es_smoke"] = True
                break
    return activos
