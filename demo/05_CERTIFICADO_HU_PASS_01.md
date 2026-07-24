# 🛡️ CERTIFICADO DE REQUERIMIENTO — NEXUS Requirements

**QASL Shift-Left Testing Framework** · Inspección estática automatizada (IEEE 1028 / ISO 20246 / ISO 29148)

| Campo | Valor |
|---|---|
| Historia de Usuario | **HU_PASS_01 — Recuperación de Contraseña** |
| Épica | EP-001: Autenticación y Control de Acceso *(PROPUESTA — confirmar)* |
| Versión analizada | v1 (documento original) → v2 (HU Ideal generada) |
| Catálogo normativo | NX v0.1.0 (28 reglas) |
| Fecha de análisis | 2026-07-24 |
| Analizado por | NEXUS Requirements · revisión humana pendiente |

---

## DICTAMEN

| Versión | RHI | Dictamen |
|---|---|---|
| **v1 — original** | **23.9 / 100** | 🔴 **NO APTO PARA DESARROLLO** |
| **v2 — HU Ideal (proyectada)** | **100 / 100*** | 🟢 **APTO — pendiente de aprobación del cliente** |

\* *La v2 alcanza 100 solo si el negocio confirma los 2 valores PROPUESTOS (expiración 30 min; política de contraseña 8+/May/min/núm) y el equipo completa el VCR en Planning Poker.*

**Motivo del NO APTO (v1):** 6 reglas CRÍTICAS incumplidas — NX-005 (BRs sin numerar), NX-006 (sin escenarios Gherkin), NX-021 (BRs no verificables: "rápido", "segura"), NX-030/NX-031 (0% cobertura positiva y negativa), NX-033 (credenciales sin escenarios de seguridad).

---

## RESUMEN DE CERTIFICACIÓN (v1)

| Severidad | Evaluadas | Cumple | Incumple | N/A |
|---|---|---|---|---|
| CRÍTICO | 9 | 3 | **6** | 0 |
| ALTO | 10 | 1 | **9** | 0 |
| MEDIO | 8 | 2 | 6 | 0 |
| BAJO | 2 | 0 | 1 | 1 |
| **Total** | **29** | **6** | **22** | **1** |

RHI = 100 × 22/92 puntos ponderados (C=5 · A=3 · M=2 · B=1) = **23.9**

## COBERTURA DE REGLAS DE NEGOCIO

| BR | Descripción (normalizada) | Cobertura v1 | Cobertura v2 |
|---|---|---|---|
| BR1 | Solicitud de restablecimiento vía correo con link | 🔴 0% | 🟢 100% (E1 + E2) |
| BR2 | Expiración del link *(30 min PROPUESTO)* | 🔴 0% | 🟢 100% (E3 + E4 + E5 límite + E8 seguridad) |
| BR3 | Política de nueva contraseña *(8+/May/min/núm PROPUESTO)* | 🔴 0% | 🟢 100% (E6 + E7) |

**Gaps detectados: 9** (5 CRÍTICOS · 4 ALTOS) — todos cerrados con los escenarios E1–E9 de la HU Ideal.

## ACTIVOS DE PRUEBA GENERADOS

3 Test Suites (Positivos / Negativos / Seguridad-OWASP) · 4 Precondiciones con setup ejecutable · **9 Test Cases** con datos frontera (29:59/30:01 · password de 8 exactos/7/vacía) y referencias OWASP A07/A09 · Suite smoke derivada: **TC_E1 + TC_E3** (~50 min de ejecución manual) · IDs deterministas e idempotentes (`HU_PASS_01_TC_E1`…)

## VCR (PROPUESTO — ratificar en Planning Poker)

V=3 (acceso al sistema) · C=2 (datos de token, correo de prueba) · P=2 · I=3 (credenciales) → R=6 → **VCR = 11 ≥ 9 → AUTOMATIZAR** (deuda técnica → regresión)

## DECISIONES DE NEGOCIO REQUERIDAS

1. ⏱️ Confirmar tiempo de expiración del link (propuesto: **30 minutos**)
2. 🔑 Confirmar política de contraseña (propuesta: **mín. 8, mayúscula, minúscula, número**)
3. 📋 Confirmar épica asignada y completar VCR en ceremonia

## RIESGOS ACEPTADOS

*Ninguno registrado. Todo gap no cerrado antes de desarrollo deberá registrarse aquí con justificación y firma del responsable.*

---

## APROBACIONES (DoD del Analista → DoR de Desarrollo/QA)

| Rol | Nombre | Decisión | Fecha | Firma |
|---|---|---|---|---|
| Analista Funcional (DoD) | ______________ | ☐ Aprueba v2 | ______ | ______ |
| QA Lead | ______________ | ☐ Valida activos | ______ | ______ |
| Cliente / Product Owner (habilita DoR) | ______________ | ☐ Aprueba valores propuestos | ______ | ______ |

*Generado por NEXUS Requirements — QASL Shift-Left Testing Framework. El framework define la norma; NEXUS la ejecuta; el ecosistema la consume.*
