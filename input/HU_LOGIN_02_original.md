# Historia de Usuario: Autenticación de Usuario en Formulario de Login

## SUT (Sistema Bajo Prueba)
URL: https://the-internet.herokuapp.com/login
Aplicación de prueba pública (Heroku "The Internet"), módulo de Login.

## ID
PENDIENTE (lo asigna el sistema)

## Épica
EP-001: Autenticación y Gestión de Acceso

## Prioridad
Alta

## Estado
Backlog — priorizada para el próximo sprint

## Descripción
Como usuario registrado del sistema,
quiero iniciar sesión ingresando mi usuario y contraseña,
para acceder de forma segura a las funcionalidades protegidas de la aplicación.

## Usuarios / Roles
- Usuario registrado (rol estándar)
- Administrador del sistema (mismo formulario, mismas reglas de validación)

## Reglas de Negocio
BR1: El sistema debe validar usuario y contraseña contra las credenciales almacenadas antes de conceder acceso.
BR2: Si el usuario o la contraseña son incorrectos, el sistema debe mostrar un mensaje de error genérico, sin indicar cuál de los dos campos falló (control anti-enumeración de usuarios).
BR3: Tras un login exitoso, el sistema debe redirigir al usuario a la página segura (`/secure`) y mostrar un mensaje de confirmación.
BR4: El campo contraseña debe ocultar el texto ingresado (tipo password) en todo momento.
BR5: El sistema debe permitir cerrar la sesión desde la página segura y, al hacerlo, invalidar el acceso a `/secure` hasta un nuevo login.

## Precondiciones
- Existe al menos un usuario válido registrado en el sistema (usuario: `tomsmith`, contraseña: `SuperSecretPassword!`).
- El usuario no tiene una sesión activa previa (navegador sin cookies de sesión).
- La aplicación está desplegada y accesible en la URL del SUT.

## Dependencias
- Ninguna dependencia externa: el módulo de login es independiente y no requiere otros servicios previos.

## Estimaciones (VCR)
No aplica en esta etapa — la estimación de Valor/Costo/Riesgo se define en la
ceremonia de Planning Poker del equipo (QDF), no en la HU original del analista.

## Escenarios de Prueba (Criterios de Aceptación)

### E1: Login exitoso con credenciales válidas
DADO que el usuario está en la página de login (`/login`)
CUANDO ingresa el usuario `tomsmith` y la contraseña `SuperSecretPassword!` y presiona "Login"
ENTONCES el sistema lo redirige a `/secure`
Y muestra el mensaje "You logged into a secure area!"

### E2: Login fallido con usuario inexistente
DADO que el usuario está en la página de login
CUANDO ingresa un usuario que no existe (ej. `usuario_invalido`) y cualquier contraseña, y presiona "Login"
ENTONCES el sistema muestra el mensaje de error "Your username is invalid!"
Y el usuario permanece en `/login`

### E3: Login fallido con contraseña incorrecta
DADO que el usuario está en la página de login
CUANDO ingresa el usuario válido `tomsmith` con una contraseña incorrecta y presiona "Login"
ENTONCES el sistema muestra el mensaje de error "Your password is invalid!"
Y el usuario permanece en `/login`

### E4: Logout exitoso desde la página segura
DADO que el usuario tiene una sesión activa en `/secure`
CUANDO presiona el botón "Logout"
ENTONCES el sistema lo redirige a `/login`
Y muestra el mensaje "You logged out of the secure area!"
Y un intento posterior de acceder directamente a `/secure` lo redirige de nuevo a `/login`

## Dentro del Alcance
- Validación de usuario y contraseña en el formulario de login.
- Redirección a área segura tras login exitoso.
- Mensajes de error para usuario inválido y contraseña inválida.
- Cierre de sesión (logout) e invalidación de acceso a `/secure`.

## Fuera del Alcance
- Recuperación de contraseña ("¿Olvidaste tu contraseña?") — no existe en este SUT, se cubriría en una HU aparte si se implementa.
- Registro de nuevos usuarios (sign up) — no existe en este SUT.
- Autenticación multifactor (MFA) — no aplica a esta versión del sistema.

## Referencias
- SUT: https://the-internet.herokuapp.com/login
- Documentación pública del proyecto "The Internet" (Heroku), sección Login.

## Notas
Esta HU describe el comportamiento observable y verificado manualmente contra el SUT público. El control anti-enumeración (BR2) y el manejo de mensajes de error diferenciados por campo (E2/E3) están documentados aquí de forma explícita para que el análisis de NEXUS los cubra directamente, sin depender de que el modelo los infiera como gap.
