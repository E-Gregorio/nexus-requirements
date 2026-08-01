<div align="center">

# 🛡️ NEXUS Requirements

### Motor de Certificación de Requerimientos con IA · Calidad Predictiva

**El framework define la norma; NEXUS la ejecuta; el ecosistema la consume.**

[![Engine](https://img.shields.io/badge/engine-v1.0-blue)]()
[![Python](https://img.shields.io/badge/python-3.10%2B-3776AB?logo=python&logoColor=white)]()
[![Claude](https://img.shields.io/badge/AI-Claude%20Sonnet-D4A574)]()
[![ISTQB](https://img.shields.io/badge/ISTQB-CTFL%20v4-success)]()
[![ISO](https://img.shields.io/badge/ISO%2FIEC%2FIEEE-29119%20·%2029148-success)]()
[![OWASP](https://img.shields.io/badge/OWASP-Top%2010%3A2021-red)]()
[![Framework](https://img.shields.io/badge/QASL-Shift--Left%20Testing%20Framework-2563EB)](https://e-gregorio.github.io/qa-shiftleft-methodology/)

*Parte del ecosistema **QASL** · Implementación ejecutable del [QASL Shift-Left Testing Framework](https://e-gregorio.github.io/qa-shiftleft-methodology/)*

</div>

---

## 💡 El problema que nadie ataca

Las herramientas de testing de la industria — Playwright, Cypress, Postman, JMeter, K6 — operan donde el defecto **ya existe**. Pero los defectos más caros no nacen en el código: nacen en el **requerimiento**. Una Historia de Usuario que dice *"el link expira rápido"* o *"la contraseña debe ser segura"* es intesteable, y su ambigüedad se convierte en bugs de QA, presión del cliente y "bugs conocidos" pasando a producción.

**NEXUS Requirements interviene antes de la primera línea de código:** certifica la HU contra una norma pública, detecta los gaps de cobertura, genera la HU ideal corregida y deja los casos de prueba listos para el primer despliegue.

```
Reactivo:    Requerimiento ambiguo → Código → Bugs en QA → Presión → "Bugs conocidos" en UAT
Predictivo:  Requerimiento CERTIFICADO → Código → Los bugs de requerimiento nunca existieron
```

---

## 🔬 Resultado real (corrida verificada del motor)

Entrada: una HU de **3 viñetas ambiguas** (`demo/HU_PASS_01_original.md`). Salida, sin intervención humana, en ~6 minutos y centavos de dólar de API:

| Artefacto | Resultado |
|---|---|
| 📋 **Dictamen normativo** | `NO_APTO` · **RHI 23.7/100** (22/93 puntos ponderados, cálculo auditable) |
| 🚨 **Reglas críticas violadas** | 6 — BRs sin numerar, sin Gherkin, no verificables, 0% cobertura, sin seguridad |
| 🔍 **Gaps detectados** | **13** con severidad y referencia OWASP (A07 anti-enumeración · A09 auditoría) |
| ➕ **BRs nuevas propuestas** | 2 — rate limiting por IP (anti fuerza bruta) y retención de logs 90 días |
| 🧪 **Test Cases generados** | **13** con datos frontera reales (token 29'/30'/31' · password 11/12 chars · timing ±50ms) |
| 🗂️ **Suites / Precondiciones** | 3 suites (Positivos · Negativos · Seguridad-OWASP) · 5 PRCs con setup ejecutable |
| ⚖️ **VCR** | V3+C2+R9 = **14 → AUTOMATIZAR** (propuesto, ratificable en Planning Poker) |
| ✅ **Trazabilidad** | **22/22 verificaciones de integridad referencial** — IDs deterministas e idempotentes |
| 📜 **Certificado DoD→DoR** | Dictamen + decisiones de negocio + bloque de aprobaciones (Analista · QA Lead · Cliente) |

> Cobertura de prueba: **0% → 100% proyectada, antes de escribir una sola línea de código.**

---

## 🔁 Dos corridas reales sobre el mismo SUT — la base para QDF y el orquestador

A diferencia del golden set (`demo/`, fijo, para evals offline), estas dos corridas son
**100% reales**, contra el mismo sistema bajo prueba público
(`https://the-internet.herokuapp.com/login`), pensadas como el par de referencia que
alimenta el resto del ecosistema QASL: [QDF](https://e-gregorio.github.io/qasl-quality-decision-framework/)
toma el VCR propuesto y lo ratifica en Planning Poker con el equipo; el orquestador
ejecuta los Test Cases una vez el VCR decide `AUTOMATIZAR`.

| | `input/HU_LOGIN_01_original.md` → **HU-001** | `input/HU_LOGIN_02_original.md` → **HU-002** |
|---|---|---|
| Estilo de la HU original | Deliberadamente incompleta (3 BRs sin numerar, sin escenarios Gherkin, campos clave vacíos) | Completa: 5 BRs, 4 escenarios Gherkin, alcance y referencias explícitos |
| RHI | **19.4/100** → `NO_APTO` | **64.4/100** → `NO_APTO` |
| Críticos incumplidos | 7 | 4 |
| Gaps detectados | 15 | 9 |
| Cobertura inicial → proyectada | 0% → 100% | 40% → 100% |
| Reglas de negocio (originales → con propuestas de NEXUS) | 3 → 7 | 5 → 7 |
| Suites / Precondiciones / Test Cases | 3 / 5 / 15 | 3 / 5 / 13 |
| VCR | Sin datos — la HU original no trae estimaciones y el modelo no propuso `vcr_propuesto` en esa corrida | **V3+C2+R9 = 14 → AUTOMATIZAR** (propuesto, a ratificar en QDF) |

Ambas quedan en `outputs/HU-001/` y `outputs/HU-002/`, con IDs estables — `catalog/id_registry.json`
garantiza que volver a analizar la misma fuente nunca cambia el `HU_ID` — y trazabilidad exacta
`HU-00N | TS-0N | TC-0N` en las cuatro pestañas CSV (que ahora incluyen los 16 campos completos
de la plantilla ISTQB, no solo un resumen), listas para mapear 1:1 a Jira/Azure DevOps.

---

## ⚙️ El pipeline

```mermaid
flowchart TD
    A["📄 Documento fuente<br/><i>Word · Jira · HTML · Markdown<br/>(cualquier formato, incluso HUs horribles)</i>"] --> B

    subgraph NEXUS ["🛡️ NEXUS Requirements — Orquestador determinista"]
        B["🤖 A1 · NORMALIZADOR<br/>→ HU Canónica ISTQB<br/><i>lo ausente = NO_ESPECIFICADO, cero invención</i>"]
        B --> C["🤖 A2 · CERTIFICADOR<br/>29 reglas del Catálogo NX<br/><i>RHI + dictamen calculados por código</i>"]
        C --> D["🤖 A3 · COBERTURA RTM<br/>Mapeo semántico BR ↔ Escenario<br/><i>gaps + escenarios sugeridos + OWASP</i>"]
        D --> E["🤖 A4 · GENERADOR<br/>Suites · Precondiciones · Test Cases<br/><i>datos frontera + técnicas ISTQB</i>"]
        E --> F["⚙️ RENDERIZADORES<br/><i>código puro, cero LLM</i>"]
    end

    F --> G["📜 Certificado<br/>DoD → DoR"]
    F --> H["📄 HU Ideal<br/>plantilla ISTQB"]
    F --> I["🗂️ CSVs de<br/>trazabilidad"]
    F --> J["🧾 Manifiesto<br/>de auditoría"]

    G --> K["👤 Analista revisa →<br/>🤝 Cliente aprueba"]
    K --> L["🚀 Desarrollo construye<br/>QA ejecuta desde el día 1<br/><i>Playwright · Newman · K6 · ZAP</i>"]

    style NEXUS fill:#0f172a,color:#fff,stroke:#2563EB,stroke-width:2px
    style A fill:#f1f5f9,stroke:#334155,color:#000
    style G fill:#dcfce7,stroke:#16a34a,color:#000
    style H fill:#dbeafe,stroke:#1d4ed8,color:#000
    style I fill:#f1f5f9,stroke:#334155,color:#000
    style J fill:#f1f5f9,stroke:#334155,color:#000
    style K fill:#fef3c7,stroke:#d97706,color:#000
    style L fill:#dcfce7,stroke:#16a34a,color:#000
```

### Principios de diseño no negociables

| Principio | Implementación |
|---|---|
| 🧠 **El LLM decide, el código ejecuta** | RHI, VCR, dictamen, IDs y regla smoke: aritmética pura, jamás el modelo |
| 🚫 **Prohibido inventar** | Campos ausentes = `NO_ESPECIFICADO`; todo valor propuesto marcado `[PROPUESTO]` para confirmación del negocio |
| 📜 **Contratos entre etapas** | JSON Schema valida la salida de cada agente; coerciones deterministas + reintento con feedback |
| 🔊 **Sin fallback silencioso** | Falla de API o contrato = corrida `FALLIDA` visible; nunca un análisis vacío disfrazado de válido |
| 🔁 **Idempotencia por diseño** | IDs limpios y secuenciales (`HU-001`, `TS-01`, `PRC-01`, `TC-01`) con registro persistente (`catalog/id_registry.json`): re-analizar la misma fuente siempre devuelve el mismo `HU_ID` — trazabilidad estable para Jira/Azure DevOps |
| ✍️ **Los humanos firman** | NEXUS prepara la evidencia; Analista, QA Lead y Cliente aprueban |

---

## 🔗 Trazabilidad completa antes del primer despliegue

```mermaid
flowchart TD
    EP["🏛️ ÉPICA<br/>EP-001"] --> HU["📘 USER STORY<br/>HU-NNN<br/><i>RHI · dictamen · VCR</i>"]
    HU --> BR["📐 BUSINESS RULES<br/>BR1..BR5<br/><i>incluye propuestas por NEXUS</i>"]
    BR --> GAP["🚨 GAPS<br/>severidad + OWASP"]
    GAP --> ESC["📝 ESCENARIOS<br/>E1..EN · Gherkin"]
    ESC --> TC["🧪 TEST CASES<br/>TC-01..TC-NN<br/><i>traza a HU-NNN · TS-0N · TC-0N</i>"]
    TC --> TS["🗂️ TEST SUITES<br/>TS-01 Positivos · TS-02 Negativos · TS-03 Seguridad-OWASP"]
    TC --> PRC["🔧 PRECONDICIONES (M2M)<br/>PRC-01..0N · setup ejecutable"]
    TC --> SMK["🔥 SMOKE SUITE<br/>derivada por regla"]

    style EP fill:#e0e7ff,stroke:#4338ca,color:#000
    style HU fill:#dbeafe,stroke:#1d4ed8,color:#000
    style BR fill:#f1f5f9,stroke:#334155,color:#000
    style GAP fill:#fee2e2,stroke:#dc2626,color:#000
    style ESC fill:#f1f5f9,stroke:#334155,color:#000
    style TC fill:#dcfce7,stroke:#16a34a,color:#000
    style TS fill:#f1f5f9,stroke:#334155,color:#000
    style PRC fill:#f1f5f9,stroke:#334155,color:#000
    style SMK fill:#ffedd5,stroke:#ea580c,color:#000
```

Cuando un TC falla en ejecución, el diagnóstico viene incluido: el TC traza a su escenario, el escenario a su BR, la BR a la HU **certificada y aprobada por el cliente**. El reporte de defecto se escribe solo — y la discusión "¿esto era un bug o nunca se especificó?" desaparece.

**Integridad verificada en la corrida real: 22/22 checks** — formato de IDs, referencias TC→Suite/PRC/Escenario/BR, consistencia bidireccional Suite↔TC y PRC↔TC, cadena vertical completa.

---

## 📏 La norma ejecutable: Catálogo NX

La base normativa no es un prompt: es un **catálogo versionado de 29 reglas verificables** (`catalog/nx_rules.yaml`), derivado del [QASL Shift-Left Testing Framework](https://e-gregorio.github.io/qa-shiftleft-methodology/) y sus estándares:

| Familia | Reglas | Evalúa | Evaluador |
|---|---|---|---|
| 🏗️ **Estructura** | NX-001..013 | Los 16 campos de la plantilla US ISTQB | Código (determinista) |
| ✍️ **Redacción** | NX-020..025 | Ambigüedad, verificabilidad, contradicciones (ISO 29148) | LLM |
| 🧪 **Testabilidad** | NX-030..035 | 1 BR = positivo + negativo · límites · seguridad OWASP | Mixto |
| 🔒 **NFR/Compliance** | NX-040..043 | Performance, WCAG, auditoría, regulatorio | LLM |

```
RHI = 100 × Σ(peso × cumplida) / Σ(peso)        pesos: CRÍTICO=5 · ALTO=3 · MEDIO=2 · BAJO=1

CERTIFICADO (100) · APTO (≥90, sin críticos) · REQUIERE REVISIÓN (≥60) · NO APTO (<60 o críticos)
```

El dictamen no es la opinión de una IA: es el **incumplimiento verificable de reglas numeradas** — como un linter, pero de requerimientos.

---

## 🚀 Quickstart

```bash
cd engine
pip install -r requirements.txt
copy .env.example .env            # completar ANTHROPIC_API_KEY

# Verificación offline (sin API — evals contra el golden set)
python tests/test_offline.py      # → TODOS LOS CHECKS PASARON ✔

# Análisis de una HU real — las HUs a analizar viven en input/, nunca en demo/
# (demo/ es el golden set fijo de referencia, no se toca)
python run_nexus.py ..\input\HU_LOGIN_01_original.md
```

Salidas en `outputs/<HU_ID>/`: HU canónica → certificación NX → gaps → activos → **Certificado** + **HU Ideal** + **CSVs** + manifiesto de auditoría — esto es lo que consume QDF para la ceremonia de estimación y, más adelante, el orquestador.

---

## 🧪 QA del motor de QA

El motor se certifica con la propia metodología que implementa (guía de Testing IA/LLM del framework):

- **Golden set** (`demo/`): corrida de referencia certificada a mano — el estándar que la salida automática debe igualar.
- **Evals offline** (`tests/test_offline.py`): sin consumir API, verifica que la evaluación estructural, el RHI (23.9 → NO_APTO), el VCR, los IDs deterministas, la regla smoke y los 11 artefactos reproducen el golden set exactamente.
- **Eval online verificado**: el motor en vivo reprodujo el dictamen del golden (RHI 23.7 vs 23.9, mismos 6 críticos) y detectó *más* gaps que el análisis manual — incluyendo timing attacks y rate limiting que ningún analista escribe espontáneamente.

---

## 📂 Estructura del proyecto

```
nexus-requirements/
├── catalog/          # La norma ejecutable: nx_rules.yaml (29 reglas) · vcr_policy.yaml · id_registry.json (IDs estables entre corridas)
├── schemas/          # Contratos JSON entre etapas (4 schemas)
├── engine/           # El motor: orquestador + 4 agentes + renderizadores + evals
├── input/            # HUs originales reales a analizar — el comando apunta aquí
├── demo/             # Golden set fijo de referencia: HU horrible → todos los artefactos certificados (no se toca)
├── outputs/          # Resultado de cada corrida — esto es lo que consumen QDF y el orquestador
└── docs/             # Blueprint de arquitectura completo
```

---

## 🗺️ Roadmap

- [x] **Fase 0** — Catálogo NX · política VCR · JSON Schemas · golden set
- [x] **Fase 1-2** — Motor completo (A1-A4) · renderizadores · evals offline · **primera corrida real certificada**
- [ ] **Fase 3** — Persistencia en PostgreSQL (MS-12, single source of truth) · export CSV por vistas · versionado de HU
- [ ] **Fase 4** — Dashboard de métricas · integración con motores de ejecución (Playwright/Newman/K6/ZAP)

---

<div align="center">

## 👤 Autor

**Elyer Gregorio Maldonado** · Senior QA Automation Lead

Creador del [QASL Shift-Left Testing Framework](https://e-gregorio.github.io/qa-shiftleft-methodology/) y del ecosistema QASL

[![LinkedIn](https://img.shields.io/badge/LinkedIn-elyergregorio-0A66C2?logo=linkedin)](https://linkedin.com/in/elyergregorio)
[![GitHub](https://img.shields.io/badge/GitHub-E--Gregorio-181717?logo=github)](https://github.com/E-Gregorio)
[![Portfolio](https://img.shields.io/badge/Portafolio-e--gregorio.github.io-2563EB)](https://e-gregorio.github.io/mi-portafolio)

*"El éxito de QA no se mide solo por los bugs que encuentra, sino por los que impide que existan."*

</div>

---

## 📄 Licencia

**© 2026 Elyer Gregorio Maldonado — Todos los derechos reservados.**

Este repositorio es *source-available* con fines de **evaluación profesional** (reclutadores, hiring managers, evaluadores técnicos). No se permite su uso, copia, modificación ni redistribución sin permiso escrito del autor. Ver [LICENSE](LICENSE) para los términos completos (EN/ES). La metodología [QASL Shift-Left Testing Framework](https://e-gregorio.github.io/qa-shiftleft-methodology/) se publica por separado bajo CC BY-NC-ND 4.0.
