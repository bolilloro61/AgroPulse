# 🌱 AgroPulse - Plataforma de Monitoreo & Recomendaciones Agronómicas

**Autor**: TZAPHQUIEL RODRIGUEZ JARALILLO  
**Proyecto**: AgroPulse  
**Versión**: 1.0.0  

---

## 📋 Descripción del Proyecto
**AgroPulse** es una plataforma integral para el monitoreo agronómico, supervisión de fincas y parcelas, alertas climáticas tempranas y generación de recomendaciones explicables basadas en sensores (humedad del suelo, temperatura ambiental y tendencias meteorológicas).

---

## 👥 Usuarios de Prueba para Inicio de Sesión

Todos los usuarios registrados en la plataforma cuentan con el perfil de **Gerente** con acceso total y todos los permisos habilitados (gestión de parcelas, monitoreo en tiempo real y motor de recomendaciones).

| Usuario / Perfil | Correo Electrónico | Contraseña | Rol Funcional | Permisos |
| :--- | :--- | :--- | :--- | :--- |
| **Gerente Principal** | `gerente@agropulse.com` | `password123` | **Gerente** | Total (`all`) |
| **Administrador** | `admin@agropulse.com` | `password123` | **Gerente** | Total (`all`) |
| **Productor Agrícola** | `productor@agropulse.com` | `password123` | **Gerente** | Total (`all`) |
| **Técnico Supervisor** | `tecnico@agropulse.com` | `password123` | **Gerente** | Total (`all`) |

> 💡 **Nota rápida**: En los modales y pantallas de inicio de sesión puedes hacer clic directamente sobre cualquiera de los botones de **Usuarios de prueba** para autocompletar las credenciales al instante.

---

## 🚀 Módulo de Autenticación & Control de Acceso
- **Proveedor de Autenticación**: Firebase Authentication (Email y Contraseña).
- **Base de Datos de Usuarios y Roles**: Google Cloud Firestore (`users/{uid}`).
- **Asignación Automática de Rol**: Al registrarse una nueva cuenta, se asigna automáticamente el rol **Gerente** con todos los permisos del sistema.
- **Persistencia y Estado de Sesión**: Integrado reactivamente con Nuxt 4 vía composable `useAuth()` y Firebase Client SDK.
- **Navegación Dinámica**:
  - Al iniciar sesión con éxito, la interfaz regresa automáticamente a la vista principal.
  - El encabezado (*header*) despliega el badge de rol del usuario y el botón de acceso directo a la sección de **Parcelas**.

---

## 🛠️ Tecnologías Empleadas
- **Frontend**: Nuxt 4, Vue 3 (Composition API / `<script setup>`), Tailwind CSS.
- **Backend / BaaS**: Firebase Authentication, Google Cloud Firestore, Firebase Admin SDK.
- **Agronomía & Simulación**: Motor de reglas explicables por tipo de cultivo (Tomate Saladette, Maíz Grano, Aguacate Hass, etc.).

---

## 💻 Puesta en Marcha en Desarrollo

1. **Instalar Dependencias**:
   ```bash
   cd apps/web
   npm install
   ```

2. **Iniciar Servidor de Desarrollo**:
   ```bash
   npm run dev
   ```
   La aplicación estará disponible en `http://localhost:3000`.

---
Desarrollado por **TZAPHQUIEL RODRIGUEZ JARALILLO**.
