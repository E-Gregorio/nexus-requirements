# 🛡️ CERTIFICADO DE REQUERIMIENTO — NEXUS Requirements

**QASL Shift-Left Testing Framework** · Inspección estática automatizada (IEEE 1028 / ISO 20246 / ISO 29148)

| Campo | Valor |
|---|---|
| Historia de Usuario | **HU-002 — Autenticación de Usuario en Formulario de Login** |
| Versión analizada | v1 |
| Catálogo normativo | NX v0.1.0 |
| Fecha de análisis | 2026-08-01 |
| Analizado por | NEXUS Requirements · revisión humana pendiente |

---

## DICTAMEN

### 🔴 NO APTO PARA DESARROLLO — RHI 64.4 / 100

Cálculo auditable: 56/87 puntos ponderados (CRÍTICO=5 · ALTO=3 · MEDIO=2 · BAJO=1).

**Reglas CRÍTICAS incumplidas:** NX-001, NX-022, NX-031, NX-033

## RESUMEN DE CERTIFICACIÓN

| Severidad | Cumple | Incumple | N/A |
|---|---|---|---|
| CRITICO | 5 | 4 | 0 |
| ALTO | 6 | 2 | 2 |
| MEDIO | 6 | 2 | 0 |
| BAJO | 1 | 1 | 0 |
| **Total (29 reglas)** | | | |

## COBERTURA DE REGLAS DE NEGOCIO

| BR | Cobertura actual | Justificación |
|---|---|---|
| BR1 | 🟢 100% |  |
| BR2 | 🔴 0% |  |
| BR3 | 🟡 50% |  |
| BR4 | 🔴 0% |  |
| BR5 | 🟡 50% |  |

**Cobertura inicial promedio:** 40% → **proyectada con escenarios sugeridos:** 100%
**Gaps detectados:** 9 — {}

## ACTIVOS DE PRUEBA GENERADOS

- Suites: 3 · Precondiciones: 5 · Test Cases: 13
- Suite smoke derivada: TC-01
- IDs deterministas e idempotentes (re-analizar no duplica).

## VCR

V=3 · C=2 · P=3 · I=3 → R=9 → **VCR = 14 → AUTOMATIZAR** (PROPUESTO — ratificar en Planning Poker)

## DECISIONES DE NEGOCIO REQUERIDAS

1. Si el usuario o la contraseña son incorrectos, el sistema debe mostrar un mensaje de error ÚNICO 'Invalid credentials' [PROPUESTO — actualmente muestra mensajes diferenciados], sin indicar cuál de los dos campos falló (control anti-enumeración de usuarios según OWASP A01:2021)
2. Tras un login exitoso, el sistema debe redirigir al usuario a la página segura (`/secure`) y mostrar un mensaje de confirmación 'You logged into a secure area!'. Los intentos de acceso directo a `/secure` sin sesión válida deben redirigir a `/login` [PROPUESTO — verificar comportamiento actual]

## RIESGOS ACEPTADOS

*Ninguno registrado. Todo gap no cerrado antes de desarrollo debe registrarse aquí con justificación y firma del responsable.*

---

## APROBACIONES (DoD del Analista → DoR de Desarrollo/QA)

| Rol | Nombre | Decisión | Fecha | Firma |
|---|---|---|---|---|
| Analista Funcional (DoD) | ______ | ☐ Aprueba | ______ | ______ |
| QA Lead | ______ | ☐ Valida activos | ______ | ______ |
| Cliente / Product Owner (DoR) | ______ | ☐ Aprueba propuestos | ______ | ______ |

*Generado por NEXUS Requirements. El framework define la norma; NEXUS la ejecuta; el ecosistema la consume.*