# 🛡️ CERTIFICADO DE REQUERIMIENTO — NEXUS Requirements

**QASL Shift-Left Testing Framework** · Inspección estática automatizada (IEEE 1028 / ISO 20246 / ISO 29148)

| Campo | Valor |
|---|---|
| Historia de Usuario | **HU_PASS_01 — Recuperar contraseña** |
| Versión analizada | v1 |
| Catálogo normativo | NX v0.1.0 |
| Fecha de análisis | 2026-07-24 |
| Analizado por | NEXUS Requirements · revisión humana pendiente |

---

## DICTAMEN

### 🔴 NO APTO PARA DESARROLLO — RHI 23.7 / 100

Cálculo auditable: 22/93 puntos ponderados (CRÍTICO=5 · ALTO=3 · MEDIO=2 · BAJO=1).

**Reglas CRÍTICAS incumplidas:** NX-005, NX-006, NX-021, NX-030, NX-031, NX-033

## RESUMEN DE CERTIFICACIÓN

| Severidad | Cumple | Incumple | N/A |
|---|---|---|---|
| CRITICO | 3 | 6 | 0 |
| ALTO | 1 | 9 | 0 |
| MEDIO | 2 | 6 | 0 |
| BAJO | 0 | 2 | 0 |
| **Total (29 reglas)** | | | |

## COBERTURA DE REGLAS DE NEGOCIO

| BR | Cobertura actual | Justificación |
|---|---|---|
| BR1 | 🔴 0% |  |
| BR2 | 🔴 0% |  |
| BR3 | 🔴 0% |  |

**Cobertura inicial promedio:** 0% → **proyectada con escenarios sugeridos:** 100%
**Gaps detectados:** 13 — {}

## ACTIVOS DE PRUEBA GENERADOS

- Suites: 3 · Precondiciones: 5 · Test Cases: 13
- Suite smoke derivada: HU_PASS_01_TC_E1
- IDs deterministas e idempotentes (re-analizar no duplica).

## VCR

V=3 · C=2 · P=3 · I=3 → R=9 → **VCR = 14 → AUTOMATIZAR** (PROPUESTO — ratificar en Planning Poker)

## DECISIONES DE NEGOCIO REQUERIDAS

1. El link de restablecimiento de contraseña expira después de 30 minutos [PROPUESTO] desde su generación por razones de seguridad. Después de este tiempo, el link es inválido y el usuario debe solicitar uno nuevo. El link también se invalida inmediatamente después de su primer uso exitoso (un solo uso).
2. La nueva contraseña debe cumplir los siguientes requisitos de seguridad: mínimo 12 caracteres [PROPUESTO], incluir al menos una letra mayúscula, una letra minúscula, un número y un carácter especial [PROPUESTO]. El usuario debe confirmar la contraseña ingresándola dos veces y ambas deben coincidir.
3. [NUEVA - PROPUESTA] El sistema debe limitar el número de solicitudes de restablecimiento de contraseña a un máximo de 5 intentos por dirección IP en un período de 15 minutos [PROPUESTO] para prevenir abuso y ataques de fuerza bruta (OWASP A07:2021). Después de exceder el límite, el usuario debe esperar 30 minutos [PROPUESTO] antes de poder realizar una nueva solicitud.
4. [NUEVA - PROPUESTA] El sistema debe registrar en logs de auditoría todos los eventos relacionados con el restablecimiento de contraseña, incluyendo: solicitudes de restablecimiento (exitosas y bloqueadas), accesos a links (válidos, expirados, ya usados), cambios de contraseña exitosos y rechazados, con información de timestamp, usuario/correo, IP origen y resultado. Los logs deben conservarse por un mínimo de 90 días [PROPUESTO] para cumplir con requisitos de auditoría de seguridad (OWASP A09:2021).

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