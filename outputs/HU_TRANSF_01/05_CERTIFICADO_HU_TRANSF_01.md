# 🛡️ CERTIFICADO DE REQUERIMIENTO — NEXUS Requirements

**QASL Shift-Left Testing Framework** · Inspección estática automatizada (IEEE 1028 / ISO 20246 / ISO 29148)

| Campo | Valor |
|---|---|
| Historia de Usuario | **HU_TRANSF_01 — Transferencia entre cuentas propias** |
| Versión analizada | v1 |
| Catálogo normativo | NX v0.1.0 |
| Fecha de análisis | 2026-07-25 |
| Analizado por | NEXUS Requirements · revisión humana pendiente |

---

## DICTAMEN

### 🔴 NO APTO PARA DESARROLLO — RHI 44.1 / 100

Cálculo auditable: 41/93 puntos ponderados (CRÍTICO=5 · ALTO=3 · MEDIO=2 · BAJO=1).

**Reglas CRÍTICAS incumplidas:** NX-021, NX-030, NX-031, NX-033

## RESUMEN DE CERTIFICACIÓN

| Severidad | Cumple | Incumple | N/A |
|---|---|---|---|
| CRITICO | 5 | 4 | 0 |
| ALTO | 4 | 6 | 0 |
| MEDIO | 2 | 6 | 0 |
| BAJO | 0 | 2 | 0 |
| **Total (29 reglas)** | | | |

## COBERTURA DE REGLAS DE NEGOCIO

| BR | Cobertura actual | Justificación |
|---|---|---|
| BR1 | 🟡 50% |  |
| BR2 | 🔴 0% |  |
| BR3 | 🟡 50% |  |
| BR4 | 🟢 100% |  |

**Cobertura inicial promedio:** 50% → **proyectada con escenarios sugeridos:** 100%
**Gaps detectados:** 13 — {}

## ACTIVOS DE PRUEBA GENERADOS

- Suites: 3 · Precondiciones: 5 · Test Cases: 18
- Suite smoke derivada: HU_TRANSF_01_TC_E1
- IDs deterministas e idempotentes (re-analizar no duplica).

## VCR

V=3 · C=2 · P=3 · I=3 → R=9 → **VCR = 14 → AUTOMATIZAR** (PROPUESTO — ratificar en Planning Poker)

## DECISIONES DE NEGOCIO REQUERIDAS

1. El monto máximo por transferencia es de $50,000 [PROPUESTO] para perfil estándar, $200,000 [PROPUESTO] para perfil premium, y $1,000,000 [PROPUESTO] para perfil corporativo. El monto mínimo es $1 [PROPUESTO]. Acumulado diario no debe exceder 3x el límite individual [PROPUESTO]. Confirmar valores con negocio
2. La transferencia debe reflejarse en ambas cuentas (débito en origen y crédito en destino) en un tiempo máximo de 5 segundos [PROPUESTO]. Si el proceso excede este SLA o falla parcialmente, el sistema debe ejecutar rollback automático y notificar al usuario. Confirmar SLA con negocio
3. [PROPUESTO] La sesión del usuario debe estar activa al momento de confirmar la transferencia. Timeout de sesión: 15 minutos de inactividad [PROPUESTO]. Si la sesión expiró, se rechaza la operación y se redirige a login. Confirmar timeout con políticas de seguridad
4. [PROPUESTO] Toda transferencia requiere autenticación de segundo factor (OTP vía SMS o app, biometría o token). El código OTP expira en 3 minutos [PROPUESTO] y permite máximo 3 intentos de validación. Basado en OWASP A07:2021. Confirmar método 2FA con negocio
5. [PROPUESTO] El sistema debe registrar en log de auditoría cada operación de transferencia (exitosa o fallida) incluyendo: timestamp, ID de usuario, cuentas origen/destino, monto, resultado, IP de origen y geolocalización. Retención mínima 7 años según regulación bancaria. Basado en OWASP A09:2021
6. [PROPUESTO] Después de 3 intentos fallidos de transferencia (cualquier causa) en ventana de 5 minutos [PROPUESTO], el sistema bloquea temporalmente la funcionalidad por 30 minutos [PROPUESTO] y envía notificación al email registrado del cliente. Basado en OWASP A07:2021 para prevenir ataques automatizados. Confirmar valores con seguridad

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