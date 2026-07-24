# NEXUS Requirements — Motor de Certificación de Requerimientos

**QASL Shift-Left Testing Framework** · *El framework define la norma; NEXUS la ejecuta; el ecosistema la consume.*

Motor de análisis estático de Historias de Usuario: recibe cualquier documento
(Markdown, HTML, texto), lo normaliza a la HU Canónica ISTQB, lo certifica
contra el **Catálogo NX** (RHI + dictamen auditable), detecta gaps de cobertura
con referencia OWASP y genera los activos de prueba completos — suites,
precondiciones y test cases con datos frontera — listos antes de la primera
línea de código.

## Instalación

```bash
cd nexus-requirements/engine
pip install -r requirements.txt
copy .env.example .env      # y completar ANTHROPIC_API_KEY
```

## Uso

```bash
python run_nexus.py ../demo/HU_PASS_01_original.md
python run_nexus.py C:\ruta\a\mi_hu.html --out C:\salidas\mi_hu
```

Salidas en `outputs/<HU_ID>/`:

| Artefacto | Contenido |
|---|---|
| `01_hu_canonica.json` | HU normalizada (campos ausentes = `NO_ESPECIFICADO`, cero invención) |
| `02_certificacion_nx.json` | Evaluación de las 29 reglas NX + RHI + dictamen |
| `03_cobertura_gaps.json` | Mapeo BR↔Escenario, gaps con OWASP, escenarios sugeridos |
| `04_activos.json` | Suites, precondiciones y TCs con IDs deterministas |
| `05_CERTIFICADO_<HU>.md` | El artefacto DoD→DoR con firmas |
| `<HU>_IDEAL.html` | HU corregida en plantilla ISTQB (AGREGADO / PROPUESTO) |
| `csv/1..4_*.csv` | Trazabilidad exportada (formato QASL) |
| `run_manifest.json` | Auditoría de la corrida (versiones, modelo, resultados) |

## Arquitectura (blueprint §4)

```
run_nexus.py (orquestador — código determinista, máquina de 6 pasos)
 ├── A1 normalizar()        agente LLM → HU Canónica          [contrato hu_canonica]
 ├── A2 certificar()        estructura=CÓDIGO + semántica=LLM  [contrato certificacion]
 │        └── RHI y dictamen: aritmética pura (catalog.py)
 ├── A3 analizar_cobertura() agente LLM → gaps + sugeridos     [contrato cobertura]
 ├── A4 generar_activos()   agente LLM → suites/PRCs/TCs      [contrato activos]
 │        └── IDs deterministas + regla es_smoke: CÓDIGO
 └── renderers.py           certificado, HU Ideal, CSVs: CÓDIGO puro
```

Principios no negociables implementados:

- **El LLM decide, el código ejecuta** — RHI, VCR, dictamen, IDs y smoke jamás los calcula el modelo.
- **Prohibido inventar** — lo ausente es `NO_ESPECIFICADO`; los valores que el motor propone van marcados `[PROPUESTO — confirmar con negocio]`.
- **Sin fallback silencioso** — una falla de API o de contrato aborta la corrida con `NexusPipelineError`; nunca produce un "análisis vacío" que parezca válido.
- **Idempotencia** — IDs `HU_X_TC_E1` derivados del contenido: re-analizar actualiza, no duplica.
- **Contratos validados** — JSON Schema en la salida de cada agente.

## Verificación (QA del motor de QA)

```bash
python tests/test_offline.py
```

Test offline contra el **golden set** de `demo/HU_PASS_01`: sin llamar a la API,
verifica que la evaluación estructural, el RHI (23.9 → NO_APTO), el VCR
(11 → AUTOMATIZAR), los IDs deterministas, la regla smoke y los 11 artefactos
renderizados reproducen exactamente los valores certificados. Conforme a la
guía de Testing IA/LLM del propio framework (evals + golden sets).

## Roadmap (blueprint §10)

- [x] Fase 0: Catálogo NX · política VCR · schemas · golden set
- [x] Fase 1-2: motor completo A1-A4 + renderizadores + evals offline
- [ ] Fase 3: `db_writer` v2 → MS-12 PostgreSQL (SSOT) + export CSV por vista
- [ ] Fase 4: dashboard, demo guionada, eval online contra golden set con API
