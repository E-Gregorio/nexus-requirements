# 🛡️ CERTIFICADO DE REQUERIMIENTO — NEXUS Requirements

**QASL Shift-Left Testing Framework** · Inspección estática automatizada (IEEE 1028 / ISO 20246 / ISO 29148)

| Campo | Valor |
|---|---|
| Historia de Usuario | **HU-001 — Inicio de sesión** |
| Versión analizada | v1 |
| Catálogo normativo | NX v0.1.0 |
| Fecha de análisis | 2026-08-01 |
| Analizado por | NEXUS Requirements · revisión humana pendiente |

---

## DICTAMEN

### 🔴 NO APTO PARA DESARROLLO — RHI 19.4 / 100

Cálculo auditable: 18/93 puntos ponderados (CRÍTICO=5 · ALTO=3 · MEDIO=2 · BAJO=1).

**Reglas CRÍTICAS incumplidas:** NX-001, NX-005, NX-006, NX-021, NX-030, NX-031, NX-033

## RESUMEN DE CERTIFICACIÓN

| Severidad | Cumple | Incumple | N/A |
|---|---|---|---|
| CRITICO | 2 | 7 | 0 |
| ALTO | 2 | 8 | 0 |
| MEDIO | 1 | 7 | 0 |
| BAJO | 0 | 2 | 0 |
| **Total (29 reglas)** | | | |

## COBERTURA DE REGLAS DE NEGOCIO

| BR | Cobertura actual | Justificación |
|---|---|---|
| BR1 | 🔴 0% |  |
| BR2 | 🔴 0% |  |
| BR3 | 🔴 0% |  |
| BR4 | 🔴 0% |  |
| BR5 | 🔴 0% |  |
| BR6 | 🔴 0% |  |
| BR7 | 🔴 0% |  |

**Cobertura inicial promedio:** 0% → **proyectada con escenarios sugeridos:** 100%
**Gaps detectados:** 15 — {}

## ACTIVOS DE PRUEBA GENERADOS

- Suites: 3 · Precondiciones: 5 · Test Cases: 15
- Suite smoke derivada: TC-01
- IDs deterministas e idempotentes (re-analizar no duplica).

## VCR

*Sin estimaciones — completar en Planning Poker.*

## DECISIONES DE NEGOCIO REQUERIDAS

1. [NUEVA - PROPUESTA] Después de [PROPUESTO: 3] intentos fallidos consecutivos desde la misma IP en [PROPUESTO: 15 minutos], el sistema bloquea temporalmente la cuenta por [PROPUESTO: 30 minutos] y registra el evento en el log de auditoría (OWASP A07:2021, A09:2021) [VALOR PROPUESTO — confirmar con negocio]
2. [NUEVA - PROPUESTA] El sistema registra en el log de auditoría cada intento de inicio de sesión (exitoso y fallido) incluyendo timestamp, IP de origen, usuario intentado y resultado, cumpliendo OWASP A09:2021 (Security Logging and Monitoring Failures) [PROPUESTO]
3. [NUEVA - PROPUESTA] La contraseña debe transmitirse mediante HTTPS y almacenarse con hash criptográfico fuerte (ej. bcrypt, Argon2) con salt único, nunca en texto plano (OWASP A02:2021, A04:2021) [PROPUESTO]
4. [NUEVA - PROPUESTA] El token de sesión debe ser un UUID v4 de un solo uso, con tiempo de expiración de [PROPUESTO: 30 minutos] de inactividad, y se invalida completamente al cerrar sesión (OWASP A07:2021) [VALOR PROPUESTO — confirmar con negocio]

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