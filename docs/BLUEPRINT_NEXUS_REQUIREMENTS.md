# NEXUS Requirements — Blueprint de Arquitectura

**Proyecto:** QASL NEXUS LLM — MS-01 NEXUS Requirements (rediseño de punta a punta)
**Autor:** Elyer Gregorio Maldonado
**Versión:** 1.1 — Borrador para revisión (integra la revisión completa de `templates/`: guías 05_Guias, escala VCR oficial 1–3, rúbrica A5 desde checklist §5)
**Fecha:** 2026-07-24
**Base normativa:** QASL Shift-Left Testing Framework (https://e-gregorio.github.io/qa-shiftleft-methodology/) · ISTQB CTFL v4 · ISO/IEC/IEEE 29119 · ISO/IEC/IEEE 29148:2018 · IEEE 1028 · ISO/IEC 25010 · OWASP Top 10 · WCAG 2.2

**Nomenclatura oficial del ecosistema:** *QASL Shift-Left Testing Framework* = la norma (plantillas + guías + Catálogo NX). *NEXUS Requirements* = el motor que la ejecuta. *QASL Ecosystem* = las herramientas que consumen la trazabilidad. Lema: **el framework define la norma; NEXUS la ejecuta; el ecosistema la consume.**

---

## 1. Visión y problema

Las herramientas de testing de la industria (Playwright, Cypress, Postman, JMeter, K6, Grafana) operan en las etapas donde el defecto **ya existe**. Nadie ataca la etapa donde el defecto **nace**: el requerimiento.

El escenario real que NEXUS resuelve: el equipo desarrolla sobre HUs ambiguas, los bugs aparecen en ambiente QA, el cliente presiona, y los defectos se pasan a staging/UAT como "bugs conocidos" para no perder el negocio. El proyecto se vuelve reactivo.

**NEXUS Requirements interviene antes de que la HU llegue a desarrollo:** analiza la HU contra una norma pública, detecta gaps, genera la HU ideal corregida con informe estático y justificación, el analista la revisa y la presenta al cliente. La HU aprobada entra a desarrollo con la trazabilidad completa (Epic → HU → Test Suite → Precondición → Test Case) **ya lista antes del primer despliegue**.

Consecuencias medibles:

- Los defectos posteriores son atribuibles: error de codificación (barato) o cambio de alcance (se cobra). La zona gris "desarrollamos algo que no existía" desaparece.
- El "bug conocido" deja de ser una erosión silenciosa: pasar con gaps abiertos se convierte en una aceptación de riesgo explícita, documentada y firmada.
- QA recibe el primer build con el arsenal completo: smoke derivado por regla, TCs con datos frontera, precondiciones con setup.
- El DoD del analista funcional se convierte en el DoR de QA/desarrollo, materializado en un artefacto: **el Certificado**.

> **El éxito no se mide por los bugs que encuentras, sino por los bugs que impides que existan.**
> Métricas proxy: tasa de escape de defectos por causa raíz (requerimiento vs. código), retrabajo por HU, cobertura inicial → final (ej. 25% → 100% antes de la primera línea de código).

---

## 2. Principios de diseño

1. **La norma es el producto.** NEXUS no opina: certifica contra un catálogo de reglas versionado (Catálogo NX) derivado de la metodología publicada y sus plantillas. El dictamen es incumplimiento verificable de reglas numeradas, no juicio de una IA.
2. **El LLM decide, el código ejecuta.** Los agentes hacen solo lo que requiere juicio semántico. Toda aritmética (RHI, VCR, cobertura), clasificación derivable y renderizado es código determinista. Nunca un agente re-decide lo que otro ya decidió.
3. **Prohibido inventar.** Lo que el documento fuente no dice se marca `NO_ESPECIFICADO` y genera un gap. Un motor de calidad que alucina requerimientos es el peor bug posible.
4. **Contratos entre etapas.** Cada agente recibe y entrega JSON validado contra esquema (structured outputs). Una falla de API o de validación detiene la etapa con error visible — jamás un fallback silencioso que se disfrace de análisis válido.
5. **Single Source of Truth.** MS-12 PostgreSQL es el único origen. Reportes, HU Ideal, Certificado y CSVs son **renderizados/exportaciones** de la BD, nunca caminos de autoría paralelos.
6. **Idempotencia real.** IDs deterministas derivados del contenido (`HU_REG_01_TC_E1`), no secuencias globales. Re-analizar una HU actualiza, nunca duplica.
7. **Los humanos firman.** NEXUS prepara la evidencia; el analista revisa lo normalizado y el cliente aprueba la HU corregida. Las compuertas humanas son parte explícita del flujo.
8. **Trazabilidad ejecutable.** Cada entidad enlaza a la siguiente en la BD. Un TC que falla en smoke apunta a su escenario, su BR y su HU aprobada: el reporte de defecto se escribe solo.

---

## 3. Base normativa: plantillas y Catálogo NX

### 3.1 Las plantillas HTML como formatos canónicos

Las 8 plantillas de la metodología **ya existen en HTML y se integran al proyecto tal cual** (carpeta `templates/`). No se rediseñan: se convierten en los formatos de entrada/salida oficiales del motor.

| Plantilla | Rol en NEXUS |
|---|---|
| `plantillaUS_ISQTB.html` (16 campos) | **Define el esquema de la HU Canónica.** Es la salida del Normalizador y el formato de render de la HU Ideal. |
| `checklist-revision.html` (IEEE 1028 / ISO 20246) | **Embrión del Catálogo NX** (su Sección 2 de especificación de requisitos son las primeras 6 reglas) y **formato de salida del Certificador**: el informe estático es este checklist completado automáticamente. NEXUS = inspección IEEE 1028 automatizada. |
| `plantillaTestPlan.html` (29119-3) | Consumidor downstream: secciones de alcance, trazabilidad y métricas se llenan por consulta a MS-12. |
| `plantillaMasterTestPlan.html` | Ídem, a nivel release. |
| `informe-avance-prueba.html` | Render de MS-09 sobre vistas de MS-12 (fases posteriores). |
| `metricas-calidad.html` (IEEE 1061 / ISO 25023) | Define los KPIs oficiales (ejecución, tasa de éxito, densidad de defectos, **tasa de escape**, % automatización, ROI) que MS-09/MS-11 calculan desde MS-12. |
| `calendario-pruebas.html` | Plantilla de cronograma para los Test Plans derivados. |
| `reporte-defectos.html` / `reporte-defecto-individual.html` (IEEE 1044) | La sección de trazabilidad del defecto individual (HU/TC/build) se autocompleta desde la cadena Epic→HU→TS→TC. |
| `informe-cierre-prueba.html` (29119-3) | Render final de MS-09; la decisión de release consume las métricas acumuladas. |

### 3.1b Las guías (05_Guias) como base de conocimiento de los agentes

La carpeta `templates/05_Guias/` no contiene formatos de salida sino **conocimiento metodológico** que los agentes consultan (se inyecta como contexto en sus prompts, versionado junto al catálogo):

| Guía | Consumidor | Uso |
|---|---|---|
| `guia-estimacion-vcr.html` | Política VCR (`vcr_policy.yaml`) | Escalas oficiales, tabla SP↔horas, anclas, Planning Poker |
| `checklist-revision.html` §2 (6 criterios de requisitos) | A2 Certificador | Semilla literal de NX-020..NX-025 |
| `checklist-revision.html` §5 (7 criterios de diseño de TCs) | **A5 Verificador** | La rúbrica adversarial de los activos generados ya existe: trazabilidad, pasos reproducibles, datos especificados, resultados verificables, positivos+negativos, límites, prioridad |
| `guia-estrategia-pruebas.html` | A4 Generador | Niveles, técnicas, priorización por riesgo |
| `guia-gestion-riesgos.html` | A2/A3 | Escalas P×I y tratamiento de riesgos |
| `guia-devsecops-security.html` (OWASP/ASVS/STRIDE) | A3/A4 | Escenarios y TCs de seguridad |
| `guia-testing-db-sql.html` (Data Contract, DQFI) | Contratos JSON + MS-12 | El "Data Contract como DoR" de la guía = los JSON Schemas de este blueprint |
| `guia-testing-ia-llm.html` (evals, golden sets, OWASP LLM Top 10, NIST AI RMF) | **El propio NEXUS** | La metodología ordena cómo probar aplicaciones LLM → NEXUS se certifica con su propia norma (ver §8) |
| `marco-normativo-estandares.html` | Todo el sistema | Fuente única de referencias normativas (ya migrado a 29119/29148; el código actual aún cita IEEE 829/830 y debe alinearse) |

### 3.2 Catálogo NX — la norma ejecutable

Archivo `catalog/nx_rules.yaml`, versionado (SemVer). Cada regla:

```yaml
- id: NX-020
  nombre: Sin ambigüedad léxica
  criterio: >
    Ninguna BR ni escenario contiene términos no verificables
    (rápido, adecuado, amigable, fácil, eficiente, etc.)
    sin cuantificación asociada.
  severidad: ALTO
  fase: redaccion
  referencia: "ISO/IEC/IEEE 29148 §5.2.5; checklist-revision §2.1"
  evaluador: llm          # llm | codigo | mixto
```

**Catálogo inicial propuesto (v0.1) — 28 reglas en 4 familias:**

**Familia Estructura (¿está completa según la plantilla US ISTQB?)** — evaluador mayormente código:

| ID | Regla | Severidad |
|---|---|---|
| NX-001 | ID único con formato del proyecto (HU_XXX_NN) | CRÍTICO |
| NX-002 | Descripción con estructura Como / Quiero / Para | CRÍTICO |
| NX-003 | Épica vinculada con ID (EP-NNN) | ALTO |
| NX-004 | Prioridad declarada | MEDIO |
| NX-005 | Reglas de negocio identificadas y numeradas (BRn) | CRÍTICO |
| NX-006 | Escenarios en Gherkin (DADO/CUANDO/ENTONCES) numerados (En) | CRÍTICO |
| NX-007 | Precondiciones declaradas | ALTO |
| NX-008 | Dependencias declaradas (o "Ninguna" explícito) | MEDIO |
| NX-009 | Estimaciones VCR completas (SP, V, C, P, I) en escala oficial | ALTO |
| NX-010 | Alcance: sección "Dentro del alcance" presente | ALTO |
| NX-011 | Fuera de alcance con referencia cruzada a la HU que lo cubre | MEDIO |
| NX-012 | Usuarios/Roles identificados | ALTO |
| NX-013 | Referencias documentales (CU, normativa aplicable) | BAJO |

**Familia Redacción (¿es un buen requerimiento según 29148?)** — evaluador LLM:

| ID | Regla | Severidad |
|---|---|---|
| NX-020 | Sin términos ambiguos no cuantificados | ALTO |
| NX-021 | Toda BR es verificable/testeable (se puede diseñar una prueba que la refute) | CRÍTICO |
| NX-022 | Sin contradicciones internas entre BRs, escenarios y alcance | CRÍTICO |
| NX-023 | HU atómica: una sola funcionalidad (si mezcla, se recomienda split) | ALTO |
| NX-024 | Valores cuantificados: límites, tiempos y umbrales con número y unidad | ALTO |
| NX-025 | Vocabulario consistente (mismo concepto, mismo término en todo el documento) | MEDIO |

**Familia Testabilidad (¿se puede probar completa?)** — evaluador mixto (mapeo LLM + conteo código):

| ID | Regla | Severidad |
|---|---|---|
| NX-030 | Cada BR con ≥1 escenario positivo | CRÍTICO |
| NX-031 | Cada BR con ≥1 escenario negativo | CRÍTICO |
| NX-032 | BRs con valores numéricos tienen escenarios de valores límite | ALTO |
| NX-033 | BRs de autenticación/permisos/datos sensibles tienen escenario de seguridad (ref. OWASP) | CRÍTICO |
| NX-034 | Mensajes de error esperados especificados textualmente | MEDIO |
| NX-035 | Datos de prueba derivables de la HU (ejemplos concretos o derivables por regla) | MEDIO |

**Familia No Funcional / Compliance** — evaluador LLM:

| ID | Regla | Severidad |
|---|---|---|
| NX-040 | NFRs declarados o marcados N/A explícitamente (performance, volumen) | MEDIO |
| NX-041 | Si hay UI: consideración de accesibilidad (WCAG 2.2) declarada o N/A | MEDIO |
| NX-042 | Si maneja datos sensibles: requisito de auditoría/logging presente | ALTO |
| NX-043 | Cumplimiento regulatorio aplicable identificado o N/A | BAJO |

### 3.3 RHI — Requirement Health Index (aritmética, no opinión)

```
RHI = 100 × Σ(peso_regla × cumplida) / Σ(peso_regla)
Pesos: CRÍTICO=5, ALTO=3, MEDIO=2, BAJO=1
```

**Dictamen (calculado por código):**

| Dictamen | Condición |
|---|---|
| CERTIFICADO | RHI = 100 (todas las reglas aplicables cumplidas) |
| APTO PARA DESARROLLO | RHI ≥ 90 y cero CRÍTICOS incumplidos |
| REQUIERE REVISIÓN | RHI ≥ 60 y cero CRÍTICOS incumplidos |
| NO APTO | RHI < 60 o ≥1 CRÍTICO incumplido |

Las reglas no aplicables (ej. NX-041 en una HU sin UI) se excluyen del denominador y quedan registradas como `N/A` con justificación.

---

## 4. Arquitectura del pipeline

```
  Documento fuente (Word, Jira, HTML, PDF, correo, HU a medias)
        │
        ▼
┌────────────────────── ORQUESTADOR (código Python, máquina de estados) ─────────────────────┐
│                                                                                            │
│  [A1] AGENTE NORMALIZADOR ──► HU Canónica (JSON validado contra schema)                    │
│        · Transforma cualquier formato al esquema de la plantilla US ISTQB                  │
│        · Campo ausente = NO_ESPECIFICADO (nunca inventa)                                   │
│        ▼                                                                                   │
│  ── Compuerta humana #1: el analista revisa la normalización ──                            │
│        ▼                                                                                   │
│  [A2] AGENTE CERTIFICADOR ──► Evaluación NX regla por regla (veredicto + evidencia)        │
│        · Código calcula RHI y dictamen                                                     │
│        · Render: checklist-revision.html completado + Certificado                          │
│        ▼                                                                                   │
│  [A3] AGENTE DE COBERTURA (RTM) ──► Mapeo semántico BR↔Escenario, gaps, sugeridos          │
│        · Cobertura global = promedio de cobertura real por BR                              │
│        ▼                                                                                   │
│  [A4] AGENTE GENERADOR DE ACTIVOS ──► Suites + Precondiciones + TCs                        │
│        · Estándar de calidad: golden CSVs (datos frontera, técnicas ISTQB,                 │
│          payloads OWASP, PRCs con setup, es_smoke por regla)                               │
│        ▼                                                                                   │
│  [A5·opcional] AGENTE VERIFICADOR ──► Revisión adversarial de los activos vs. la HU        │
│                                                                                            │
│  PERSISTENCIA (código puro) ──► MS-12 PostgreSQL (SSOT, transaccional, idempotente)        │
│        ▼                                                                                   │
│  RENDERIZADORES (código puro, desde la BD):                                                │
│        · Informe estático (checklist IEEE 1028)   · HU Ideal (plantilla US ISTQB)          │
│        · CERTIFICADO (DoD→DoR)                    · CSVs de trazabilidad (export)          │
│        · Dashboard / métricas                                                              │
└────────────────────────────────────────────────────────────────────────────────────────────┘
        │
        ▼
  ── Compuerta humana #2: analista presenta, cliente aprueba la HU corregida ──
        │
        ▼
  HU certificada + trazabilidad lista ──► Sprint backlog ──► Planning Poker (VCR con anclas)
        │                                                       │
        ▼                                                       ▼
  Primer despliegue: smoke derivado (v_smoke_suite)      VCR ≥ 9 → deuda técnica →
  valida la HU aprobada contra el sistema real           candidata a automatizar (MS-03/04)
```

**Reglas del orquestador:**

- Es código determinista (no un LLM): pipeline con estados por etapa (`PENDIENTE → EN_PROCESO → OK / FALLIDO`), reintentos con backoff, y validación de esquema a la salida de cada agente.
- Si un agente falla tras N reintentos, la corrida queda `FALLIDA` y visible. Prohibido el fallback silencioso.
- Cada corrida registra: versión del catálogo NX, versión de prompts, modelo LLM usado, timestamps. Reproducibilidad y auditoría.
- La HU nunca se sobreescribe: cada análisis crea versión N+1 con historial (Requirement Evolution).

### 4.1 Qué es agente y qué es código (decisión por etapa)

| Etapa | Tipo | Justificación |
|---|---|---|
| Normalización | **Agente LLM** | Interpretar formatos arbitrarios requiere juicio semántico |
| Certificación NX (reglas familia Redacción/NFR) | **Agente LLM** | Detectar ambigüedad y contradicción es semántico |
| Certificación NX (reglas familia Estructura) | **Código** | Presencia/formato de campos es determinista |
| RHI, dictamen, cobertura %, VCR | **Código** | Aritmética — reproducible siempre |
| Mapeo BR↔Escenario, gaps, escenarios sugeridos | **Agente LLM** | Correspondencia semántica |
| Clasificación de suite de cada escenario | **Agente LLM (en A3/A4)** | Se decide una vez, con contexto; el código la consume |
| Generación de TCs, PRCs, datos de prueba | **Agente LLM** | Diseño de pruebas con técnicas |
| Marca `es_smoke` | **Código (regla)** | Escenarios positivos de BRs CRÍTICAS + integración core |
| Escritura a BD, renders, exports CSV | **Código** | Mecánica pura |

---

## 5. Contratos JSON entre etapas

Todos en `schemas/`, validados con JSON Schema en el orquestador y forzados con structured outputs en la API de Anthropic (se elimina el parseo de markdown con `split`).

**5.1 `hu_canonica.schema.json`** — espejo de los 16 campos de la plantilla US ISTQB:

```json
{
  "id": "HU_REG_01",
  "nombre": "...", "epica": {"id": "EP-001", "nombre": "..."},
  "prioridad": "...", "estado": "...",
  "descripcion": {"como": "...", "quiero": "...", "para": "..."},
  "usuarios_roles": ["..."],
  "reglas_negocio": [{"id": "BR1", "descripcion": "...", "tipo": "acceso|visualizacion|funcionalidad|datos"}],
  "precondiciones": ["..."], "dependencias": ["..."],
  "estimaciones": {"sp": 5, "valor": 3, "costo": 2, "probabilidad": 2, "impacto": 3},
  "escenarios": [{"id": "E1", "titulo": "...", "pasos": [{"tipo": "DADO|CUANDO|ENTONCES|Y", "texto": "..."}]}],
  "dentro_alcance": ["..."], "fuera_alcance": [{"item": "...", "cubierto_por": "HU_XXX"}],
  "referencias": ["..."], "notas": "...",
  "_meta": {"campos_no_especificados": ["estimaciones.probabilidad"], "fuente": "...", "version": 2}
}
```

Nota: `escenarios.pasos` es una **lista ordenada de pasos tipados** — soporta múltiples Y, varios CUANDO y Scenario Outlines; se elimina la rigidez DADO=1/CUANDO=2/ENTONCES=3.

**5.2 `certificacion.schema.json`** — salida de A2:

```json
{
  "hu_id": "HU_REG_01", "version_hu": 2, "version_catalogo": "0.1.0",
  "evaluaciones": [
    {"regla": "NX-021", "veredicto": "INCUMPLE", "evidencia": "BR4 'mensaje visible' no define criterio de visibilidad", "recomendacion": "..."},
    {"regla": "NX-041", "veredicto": "NO_APLICA", "justificacion": "..."}
  ],
  "rhi": 78.4, "dictamen": "REQUIERE_REVISION",
  "criticos_incumplidos": ["NX-030"]
}
```

**5.3 `cobertura.schema.json`** — salida de A3 (evolución del actual): mapeos BR↔escenario con tipo de validación y justificación, gaps con severidad ISTQB + referencia OWASP + escenario sugerido en pasos tipados, y resumen con cobertura por BR.

**5.4 `activos.schema.json`** — salida de A4: suites (con técnica y framework), precondiciones (con pasos de setup, datos requeridos, categoría, reutilizable), test cases (con datos de entrada concretos, resultado esperado, técnica, trazabilidad a E y BR, `es_smoke`, tiempo estimado, complejidad).

---

## 6. Especificación VCR (política oficial en `catalog/vcr_policy.yaml`)

Fuente oficial: `templates/05_Guias/guia-estimacion-vcr.html`.

| Métrica | Qué mide | Escala |
|---|---|---|
| Story Points (SP) | Esfuerzo relativo (con tabla orientativa SP↔horas: 1≈4h … 13>96h) | 1,2,3,5,8,13 |
| Valor (V) | Beneficio de negocio | 1–3 |
| Costo (C) | **Costo de ejecutar las pruebas manuales en cada ciclo** (datos, ambientes, repetición — a mayor costo manual, más conviene automatizar) | 1–3 |
| Probabilidad (P) | Probabilidad de falla en producción | 1–3 |
| Impacto (I) | Gravedad si ocurre (legal, reputacional, negocio) | 1–3 |
| Riesgo (R) | R = P × I | 1–9 |
| **VCR Total** | V + C + R | 3–15 |

**Decisión:** VCR ≥ 9 → deuda técnica: se automatiza obligatoriamente, va a regresión, prioridad alta. VCR < 9 → manual, revisable en sprints futuros si cambia el riesgo.

**Momento:** ceremonia Planning Poker (primera del sprint), todo el equipo, solo US refinadas en backlog — en el flujo NEXUS, la US llega a esta ceremonia ya certificada y con activos generados.

**Anclas de referencia:** cada equipo define ejemplos ancla por puntuación (qué es un V=3, qué es un P=2) al inicio del proyecto para puntuar consistente. Se guardan en `vcr_policy.yaml`.

> ✅ **Decisión D1 resuelta por evidencia:** la guía oficial de estimación VCR, la plantilla US ISTQB y la HU_LOGIN_01 de ejemplo usan consistentemente P/I en **1–3** (VCR 3–15). El único artefacto divergente es la página web de Fase 4 (escala 1–5, VCR 3–31). Escala oficial adoptada: **1–3**; corregir la página de Fase 4 del sitio. La regla NX-009 valida contra esta escala. *(Pendiente solo la confirmación de Elyer.)*

**Flujo del dato VCR (corrige el bug actual):** el Normalizador extrae Estimaciones a `hu_canonica.estimaciones` → el código calcula R y VCR total → se persiste en `user_story` y `vcr_score` → el trigger de PostgreSQL sigue siendo la autoridad de cálculo en BD. El VCR de la HU nunca más se pierde en el camino.

---

## 7. Persistencia MS-12 — correcciones de diseño

Hereda el esquema actual de 9 tablas con estos cambios obligatorios:

1. **IDs deterministas en todo:** `{HU}_TC_{E}` para test cases (ej. `HU_REG_01_TC_E4`), `{HU}_PRC{NN}`, `{HU}_TS{NN}`. Elimina la secuencia global `TC-NNN` que rompe la idempotencia (hoy re-analizar duplica TCs). Si se necesita un ID corto para mostrar, es una columna de presentación, no la clave.
2. **`db_writer` no re-decide:** consume la clasificación de suites, el mapeo BR↔TC y el tipo positivo/negativo directamente del JSON de A3/A4. Mueren `_es_escenario_negativo` (keywords) y `_detectar_br_cubierta` (overlap de palabras).
3. **Severidad sin colapso:** `static_analysis_gap.severidad` guarda los 4 niveles (CRÍTICO/ALTO/MEDIO/BAJO), no el mapeo a 3 que pierde información.
4. **Steps reales:** `test_case_step` guarda la lista ordenada de pasos tipados (soporta N pasos), no un único step con todo embutido.
5. **Cobertura honesta:** la métrica global persistida es el promedio de cobertura por BR según el mapeo semántico, no `escenarios_documentados / (BRs × 2)`.
6. **Columnas nuevas:** `test_case.es_smoke BOOLEAN`, `user_story.version INT` + tabla `user_story_version` (historial Requirement Evolution), `analysis_run` (corrida: versión catálogo, prompts, modelo, estado, RHI, dictamen).
7. **Vistas nuevas:** `v_smoke_suite`, `v_certification_status`, `v_requirement_evolution`, y las existentes (`v_traceability`, `v_pending_gaps`, etc.).
8. **CSVs = export:** comando `nexus export csv HU_REG_01` genera los 4 CSVs desde vistas. El prompt manual de Fase 2 queda obsoleto — su contenido se convierte en el prompt de A4.

---

## 8. Golden set y evals — QA del motor de QA

El criterio de aceptación del motor es de la propia metodología: **el requerimiento del sistema, certificado antes de construirlo.**

- `goldens/HU_REG_01/`: los 4 CSVs existentes (User Stories, Test Suites, Preconditions, Test Cases) — estándar de calidad de A4.
- `goldens/HU_LOGIN_01/`: HU original + reporte + HU actualizada — regresión de A3.
- `goldens/hus_horribles/`: colección de HUs reales mal escritas (anonimizadas) — casos de prueba de A1 y A2.
- `evals/run_evals.py`: corre el pipeline sobre los goldens y compara salidas contra lo esperado (estructura exacta por código; calidad semántica con LLM-as-judge). Se ejecuta ante cada cambio de prompt o de catálogo. Ningún cambio se integra si degrada el golden set.

**Definición de terminado del motor:** su salida automática es indistinguible de los golden CSVs generados manualmente.

**Base normativa de esta sección:** la propia `guia-testing-ia-llm.html` de la metodología (evals, golden sets, detección de alucinación, OWASP LLM Top 10, NIST AI RMF, promptfoo/garak). NEXUS es una aplicación LLM → **NEXUS se prueba según la guía IA/LLM de la metodología que implementa.** Adicionalmente, el A5 Verificador aplica la Sección 5 del `checklist-revision.html` (los 7 criterios de diseño de TCs) como rúbrica sobre los activos generados — la rúbrica adversarial ya existe en la norma.

---

## 9. El Certificado — artefacto DoD → DoR

Una página (HTML con el estilo de las plantillas, exportable a PDF), generada desde la BD:

1. **Identificación:** HU, versión, épica, fecha, versión del catálogo NX aplicado.
2. **Dictamen** destacado: CERTIFICADO / APTO / REQUIERE REVISIÓN / NO APTO + RHI.
3. **Resumen de certificación:** reglas evaluadas, cumplidas, incumplidas por severidad (con IDs NX).
4. **Cobertura:** % por BR antes → después, gaps cerrados con los escenarios agregados.
5. **Activos generados:** conteo de suites, PRCs, TCs, marca smoke, estimación de esfuerzo de ejecución.
6. **VCR:** puntuación, decisión automatizar/manual.
7. **Riesgos aceptados:** gaps que se decidió no cerrar, con justificación de negocio y firma del responsable (aquí muere el "bug conocido" silencioso).
8. **Aprobaciones:** Analista Funcional (DoD) · QA Lead · Cliente/PO (habilita DoR de desarrollo). Nombre, fecha, firma.

---

## 10. Roadmap

**Fase 0 — Cimientos (diseño, poco código):**
Catálogo NX v0.1 en YAML · política VCR con decisión de escala tomada · 4 JSON Schemas · golden set armado (incluye recolectar HUs horribles reales) · plantillas HTML integradas a `templates/`.

**Fase 1 — Certificación (lo nuevo, el diferencial):**
A1 Normalizador + A2 Certificador · orquestador mínimo (2 etapas, estados, reintentos, validación de esquemas) · render del checklist IEEE 1028 completado + Certificado v1 · evals de A1/A2 contra HUs horribles.

**Fase 2 — Cobertura y generación al estándar golden:**
A3 (migración del `rtm_analyzer_ai` actual con fórmula de cobertura corregida y pasos tipados) · A4 (el prompt de Fase 2 manual convertido en agente, con datos frontera, técnicas, OWASP, `es_smoke`) · evals contra golden CSVs.

**Fase 3 — Persistencia y ciclo completo:**
`db_writer` v2 (IDs deterministas, sin re-decisiones, steps reales, columnas y vistas nuevas) · export CSV por comando · versionado de HU (`analysis_run`, `user_story_version`) · orquestador de punta a punta.

**Fase 4 — Arma laboral:**
Dashboard sobre las vistas · README de portada (problema → demo → métricas → arquitectura) · demo guionada de 5 minutos: HU horrible en vivo → Certificado + HU Ideal + 20 TCs · video corto · caso antes/después con métricas del proyecto real (defectos UAT por causa raíz).

---

## 11. Estructura de proyecto propuesta

```
ms-01-nexus-requirements/
├── orchestrator/            # máquina de estados, reintentos, validación de contratos
├── agents/
│   ├── normalizer/          # A1 + prompt versionado
│   ├── certifier/           # A2 + prompt versionado
│   ├── coverage/            # A3 (evolución de rtm_analyzer_ai)
│   ├── generator/           # A4 (evolución del prompt Fase 2)
│   └── verifier/            # A5 opcional
├── catalog/
│   ├── nx_rules.yaml        # la norma ejecutable (versionada)
│   └── vcr_policy.yaml      # escalas, umbral, anclas
├── schemas/                 # hu_canonica, certificacion, cobertura, activos
├── templates/               # las 8 plantillas HTML de la metodología (tal cual)
├── renderers/               # informe, hu_ideal, certificado, dashboard
├── db/                      # writer v2, migraciones, vistas, export CSV
├── goldens/                 # HU_REG_01, HU_LOGIN_01, hus_horribles/
├── evals/                   # run_evals.py, jueces, resultados
├── cli/                     # nexus analyze | certify | export | evals
└── docs/                    # este blueprint, decisiones (ADRs), guía de demo
```

---

## 12. Registro de decisiones abiertas

| # | Decisión | Estado |
|---|---|---|
| D1 | Escala oficial P/I | **Resuelta por evidencia: 1–3** (guía VCR + plantilla US + ejemplos consistentes; corregir página Fase 4 del sitio que dice 1–5) — confirmar |
| D2 | ¿A5 Verificador adversarial en v1 o se pospone a v2? | Propuesto: posponer a v2, pero su rúbrica ya está definida (checklist §5) |
| D3 | Umbral RHI de APTO (90) y REVISIÓN (60) | Propuestos — calibrar con las primeras 10 HUs reales |
| D4 | Regla `es_smoke`: positivos de BRs CRÍTICAS + integración core | Propuesta — validar contra criterio de QA en proyecto real |
| D5 | Nombre del MS: MS-01 NEXUS Requirements (upstream de MS-02) vs reemplazo de MS-02 | Propuesto: MS-01 nuevo; MS-02 actual se absorbe en A3/A4 |
| D6 | Rebranding: "QA Shift-Left Methodology" → **QASL Shift-Left Testing Framework** | **Decidido** (alineado al CV) — actualizar título del sitio y README del repo; los links/URLs pueden permanecer |

---

*QASL NEXUS LLM — NEXUS Requirements Blueprint v1.0 · Metodología QA Shift-Left · La norma es el producto.*
