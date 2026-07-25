# HISTORIA DE USUARIO

**ID:** HU_TRANSF_01
**Nombre:** Transferencia entre cuentas propias
**Épica:** EP-002: Gestión de Fondos
**Prioridad:** Alta
**Estado:** Refinada

## Descripción

**Como** cliente del banco con cuentas activas
**Quiero** transferir dinero entre mis propias cuentas
**Para** administrar mis fondos sin ir a la sucursal

**Usuarios / Roles:** Cliente bancario autenticado

## Reglas de Negocio

BR1: El cliente solo puede transferir entre cuentas propias que estén activas.
BR2: El monto máximo por transferencia debe ser razonable según el perfil del cliente.
BR3: La transferencia debe reflejarse rápidamente en ambas cuentas.
BR4: Si la cuenta origen no tiene fondos suficientes, la transferencia se rechaza.

## Escenarios (Criterios de Aceptación)

**E1 - Transferencia exitosa:**
DADO que el cliente tiene dos cuentas activas y saldo suficiente en la cuenta origen
CUANDO ingresa el monto, selecciona las cuentas y confirma la operación
ENTONCES el sistema debita la cuenta origen, acredita la cuenta destino y muestra el comprobante

**E2 - Selección de cuentas:**
DADO que el cliente accede al módulo de transferencias
CUANDO abre el formulario
ENTONCES ve listadas únicamente sus cuentas propias activas

**E3 - Pantalla de confirmación:**
DADO que el cliente ingresó los datos de la transferencia
CUANDO presiona Continuar
ENTONCES ve una pantalla de confirmación con monto, cuentas seleccionadas y comisión aplicable

**E4 - Comprobante descargable:**
DADO que la transferencia fue exitosa
CUANDO finaliza la operación
ENTONCES puede descargar el comprobante en formato PDF

**E5 - Fondos insuficientes:**
DADO que el saldo de la cuenta origen es menor al monto ingresado
CUANDO confirma la operación
ENTONCES el sistema muestra el mensaje "Fondos insuficientes" y no ejecuta la transferencia

## Dentro del Alcance

- Transferencias inmediatas entre cuentas propias en la misma moneda
- Visualización y descarga de comprobante
- Validación de fondos antes de ejecutar

**Mockup:** Figma — pantalla Transferencias v3 (enlace interno del proyecto)
