# AgroPulse - Monitoreo y Recomendaciones Agronómicas

Plataforma web full-stack para el monitoreo de parcelas agrícolas y el análisis de parámetros ambientales (humedad del suelo, temperatura, etc.), orientada a la detección oportuna de anomalías y la generación de recomendaciones transparentes de riego e inspección mediante un motor basado en reglas y tendencias.

---

## 1. Problema

En la gestión agrícola moderna, la falta de monitoreo continuo y sistematizado sobre las condiciones ambientales de los cultivos suele derivar en un uso ineficiente del agua, estrés hídrico en las plantas o pérdidas por variaciones bruscas de temperatura. Los productores y técnicos supervisores carecen frecuentemente de una herramienta centralizada que les permita visualizar tendencias históricas, parametrizar los rangos óptimos para sus cultivos y recibir alertas operativas con recomendaciones claras que fundamenten la toma de decisiones sin depender de cajas negras o automatizaciones a ciegas.

---

## 2. Objetivo

Desarrollar una aplicación web full-stack con arquitectura desacoplada y persistencia en Firebase Cloud Firestore que permita a productores y técnicos supervisores registrar, consultar y analizar parámetros ambientales por finca y parcela, ofreciendo un motor de sugerencias basado en reglas y tendencias que emita recomendaciones explicables sobre el manejo de riego e inspección de cultivos.

---

## 3. Alcance del MVP (Producto Mínimo Viable)

El MVP abarca las capacidades acordadas para cumplir con las tres entregas del proyecto:

* **Gestión de Entidades y Parámetros:** Administrar fincas, parcelas, tipos de cultivo y sus rangos ambientales esperados (humedad y temperatura).
* **Captura e Importación de Mediciones:** Registro manual de lecturas ambientales e importación masiva vía archivos `.csv` con validación estricta en servidor.
* **Autenticación y Control de Acceso (RBAC):** Inicio de sesión y asignación de permisos diferenciados para dos roles (Productor y Técnico Supervisor) utilizando Firebase Authentication.
* **Monitoreo y Ciclo de Alertas:** Visualización de series históricas mediante gráficas, detección automática de lecturas fuera de rango o variaciones bruscas, y gestión del ciclo de vida de alertas (marcar como atendida agregando observaciones).
* **Motor de Recomendaciones (Componente Innovador):** Algoritmo explicable en Python que evalúa reglas de cultivo y tendencias recientes para sugerir acciones de riego o inspección, justificando explícitamente cuál fue la medición o condición que disparó el mensaje.
* **Pruebas y Despliegue:** Mínimo de 10 pruebas automatizadas aprobadas y despliegue del frontend y API en plataformas de hosting en la nube.

---

## 4. Parámetros Agronómicos y Reglas del Motor de Recomendaciones

Para garantizar la precisión de las alertas y la justificación explicable de las recomendaciones, el sistema parametriza umbrales biológicos y edafoclimáticos por especie cultivada.

### 4.1. Sensibilidad Crítica: ¿Puede el Tomate Saladette sobrevivir a 0 °C?

**No.** El tomate Saladette (*Solanum lycopersicum*) es una solanácea de clima templado-cálido sumamente vulnerable a las bajas temperaturas:

* **Por debajo de 12 °C (Estrés por frío / *Chilling injury*):** Se detiene la fotosíntesis, el transporte de savia y la absorción de fósforo; ocurre aborto de flores y se frena el cuajado de frutos.
* **Por debajo de 2 °C y en torno a 0 °C (Congelamiento letal / *Freezing injury*):** Se cristaliza el agua en los espacios intercelulares, provocando la lisis celular, colapso vascular, necrosis foliar y la **muerte irreversible de la planta**.
* **Acción requerida a 0 °C:** El motor clasifica esta condición como **Emergencia por Helada**, ordenando la activación urgente de sistemas activos de defensa térmica (riego por aspersión térmica antihelada, calefactores de combustión o ventiladores de inversión térmica) y cubiertas protectoras.

---

### 4.2. Matriz de Rangos Agronómicos por Cultivo

| Cultivo | Temp. Letal / Helada | Temp. Mín. Vegetativa | Temp. Óptima (Día / Noche) | Temp. Máx. Crítica (Estrés) | Humedad Suelo Óptima | Humedad Mín. (Estrés Hídrico) | Humedad Máx. (Saturación) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Tomate Saladette** | $\le 2^\circ\text{C}$ (Letal a $0^\circ\text{C}$) | $12^\circ\text{C}$ | $18^\circ\text{C} - 27^\circ\text{C}$ | $\ge 32^\circ\text{C}$ | $60\% - 80\%$ | $< 45\%$ | $> 80\%$ (Riesgo *Phytophthora*) |
| **Maíz Grano** | $\le 0^\circ\text{C}$ | $10^\circ\text{C}$ | $20^\circ\text{C} - 30^\circ\text{C}$ | $\ge 35^\circ\text{C}$ | $50\% - 70\%$ | $< 35\%$ | $> 75\%$ (Asfixia radicular) |
| **Aguacate Hass** | $\le 0^\circ\text{C}$ (Daño en brotes a $1^\circ\text{C}$) | $10^\circ\text{C}$ | $15^\circ\text{C} - 26^\circ\text{C}$ | $\ge 32^\circ\text{C}$ | $55\% - 75\%$ | $< 40\%$ | $> 80\%$ (Extrema susceptibilidad a hongos) |
| **Vid / Uva** | $\le -1^\circ\text{C}$ (En brotación) | $10^\circ\text{C}$ | $16^\circ\text{C} - 28^\circ\text{C}$ | $\ge 35^\circ\text{C}$ | $40\% - 65\%$ | $< 25\%$ | $> 70\%$ (Sensible a mildiú y oídio) |

---

### 4.3. Jerarquía de Evaluación y Explicabilidad del Motor

El motor algorítmico evalúa las condiciones bajo la siguiente prioridad agronómica para generar recomendaciones transparentes:

1. **Emergencia por Helada ($T \le T_{\text{letal}}$):** Disparo de máxima prioridad. Alerta destructiva; exige protección activa inmediata contra el congelamiento tisular.
2. **Estrés Térmico por Frío ($T < T_{\text{mín\_opt}}$):** Advertencia de letargo vegetativo. Recomienda suspender riegos nocturnos fríos.
3. **Golpe de Calor ($T \ge T_{\text{máx\_crit}}$ o alza térmica rápida):** Riesgo de quemaduras y aborto reproductivo. Recomienda micropulverización o riego de alivio térmico vespertino.
4. **Estrés Hídrico Crítico ($H < H_{\text{mín\_opt}} - 15\%$ o caída brusca):** Sequía en la zona de raíces activas. Exige activación inmediata de riego por goteo con duración calculada.
5. **Déficit Hídrico Moderado ($H < H_{\text{mín\_opt}}$):** Programación preventiva de turno de riego antes de entrar en punto de marchitez temporal.
6. **Sobresaturación ($H > H_{\text{máx\_opt}}$):** Peligro de asfixia radicular y enfermedades fúngicas. Exige suspensión de riego y verificación de drenajes.
7. **Condición Óptima:** Notificación de estabilidad sin necesidad de intervenciones manuales ni consumo innecesario de agua.

---

## 5. Tecnologías Elegidas

* **Frontend:** Nuxt (Vue.js) + Tailwind CSS (Componentes reactivos, formularios con validación y gráficas de series temporales).
* **Backend:** Python (FastAPI / Flask) (API HTTP/REST para procesamiento de reglas, validaciones de backend e integración con servicios).
* **Persistencia:** Firebase Cloud Firestore (Colecciones principales: `users`, `farms`, `plots`, `crops`, `measurements`, `alerts`, `recommendations`).
* **Autenticación:** Firebase Authentication.
* **Control de Versiones:** Git y GitHub (Flujo de ramas `feature/*` -> `develop` -> `main`, Pull Requests y etiquetas por revisión).

---

## 6. Integrantes y Matriz de Responsabilidades

El proyecto es desarrollado colaborativamente por dos integrantes. Ambos participan de forma transversal en el desarrollo Full-Stack, repartiendo la responsabilidad de los módulos en cada revisión:

| Integrante | Enfosis en el Proyecto | Modulos Asignados (Ciclo Completo) |
| :--- | :--- | :--- |
| **Rogelio** | Frontend, Auth & Core Dev | Módulo de Autenticación (Firebase Auth), Gestión de Fincas y Parcelas, Cargador Frontend CSV, Visualizaciones Gráficas, Dashboard Consolidado de Finca y Despliegue Frontend. |
| **Tzaphquiel** | Backend, Data & Algoritmos | Historias de Usuario, Dashboard de Bienvenida, Formulario e Historial de Mediciones, Backend API Importador CSV, Motor de Alertas & Recomendaciones Explicables (Python) y Pruebas Automatizadas. |

---

## 7. Calendario de Entregas y Entregables (Roadmap)

### 📌 R1: Arquitectura y Primera Operación (19 de Noviembre de 2026)
* **Documentación:** `README.md` base, al menos 5 historias de usuario, diagrama de componentes y modelo de Firestore.
* **Diseño UI:** Wireframes / prototipos navegables de 4 pantallas clave.
* **Funcionalidad Ejecutable:** Registro/Login con Firebase Auth, primer rol activo, CRUD inicial de fincas/parcelas y formulario con consulta persistente en Firestore.
* **GitHub:** Tag `revision-1-2026-11-19` y reporte de evidencias en `docs/revisiones/R1.md`.

### 📌 R2: Flujo Principal e Innovación Inicial (26 de Noviembre de 2026)
* **Funcionalidad Core:** Permisos efectivos para 2 roles (Productor y Técnico Supervisor), importador de datos CSV validado en API backend.
* **Visualización y Alertas:** Gráficas de series históricas, motor de alertas persistentes al detectar umbrales sobrepasados y flujo de atención de alertas con observaciones.
* **Componente Innovador:** Primera versión del motor de recomendaciones agronómicas explicables en Python.
* **Calidad y GitHub:** Documentación de API, primeras 5 pruebas automatizadas aprobadas, tag `revision-2-2026-11-26` y reporte en `docs/revisiones/R2.md`.

### 📌 R3: MVP Publicado y Demostración Final (03 de Diciembre de 2026)
* **Funcionalidad Final:** Motor de sugerencias completo, dashboard general consolidado por finca y ciclo End-to-End funcional.
* **Pruebas y Seguridad:** Suite completa de 10+ pruebas automatizadas aprobadas y reglas de seguridad de Firestore configuradas (`firebase/firestore.rules`).
* **Despliegue Público:** Frontend y API desplegados en la nube con URLs de acceso público y datos de prueba ficticios.
* **GitHub:** Tag `revision-3-2026-12-03`, manual de uso en `docs/manual.md` y reporte final en `docs/revisiones/R3.md`.

---

## 8. Estructura del Repositorio

```text
agropulse/
├── apps/
│   ├── web/               # Cliente Frontend en Nuxt (Vue.js)
│   └── api/               # Servidor Backend API en Python (FastAPI/Flask)
├── firebase/              # Reglas de seguridad e índices de Firestore (firestore.rules)
├── docs/
│   ├── arquitectura.md    # Diagrama de componentes y modelo de base de datos
│   ├── manual.md          # Guía de usuario e importación de datos
│   └── revisiones/        # Evidencias por entrega (R1.md, R2.md, R3.md)
├── tests/                 # Suite de pruebas automatizadas en Python
├── evidencias/            # Capturas de pantalla y demostraciones en video
├── .env.example           # Plantilla de variables de entorno (sin secretos)
└── README.md              # Documentación principal del proyecto
```

---

## 9. Instrucciones de Configuración y Ejecución Local

### Prerrequisitos
* Node.js v18+ (para el frontend en Nuxt)
* Python 3.10+ (para la API en Python)
* Cuenta en Firebase con un proyecto activo de Cloud Firestore

### 1. Clonar el repositorio
```bash
git clone https://github.com/usuario/agropulse.git
cd agropulse
```

### 2. Configuración de Variables de Entorno
Copiar el archivo `.env.example` tanto en la carpeta web como en la api:
```bash
cp .env.example apps/web/.env
cp .env.example apps/api/.env
```
*Completar las llaves públicas de Firebase en `apps/web/.env` y la configuración de servicio backend en `apps/api/.env`.*

### 3. Ejecutar el Backend (Python)
```bash
cd apps/api
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### 4. Ejecutar el Frontend (Nuxt)
```bash
cd apps/web
npm install
npm run dev
```

### Cargar el catálogo inicial de cultivos
El script carga en Firestore la colección `crops` con los cinco cultivos y sus umbrales ambientales. Coloca una clave de cuenta de servicio con permisos de escritura en `firebase/serviceAccountKey.json` (archivo ignorado por Git), o configura `GOOGLE_APPLICATION_CREDENTIALS` con la ruta de la clave. Desde la raíz del repositorio, en PowerShell:

```powershell
python -m pip install -r apps/api/requirements.txt
$env:GOOGLE_APPLICATION_CREDENTIALS = (Resolve-Path .\firebase\serviceAccountKey.json).Path
python .\scripts\seed_crops.py
```

No agregues la clave al repositorio ni la compartas; al terminar, elimina la variable de la sesión con `Remove-Item Env:GOOGLE_APPLICATION_CREDENTIALS`.

---

## 10. Cuentas de Prueba Ficticias (Entorno de Demostración)

| Rol | Correo Electrónico | Contraseña | Descripción |
| :--- | :--- | :--- | :--- |
| **Gerente** | `productor@agropulse.test` | `Productor123!` | Acceso a registro manual de mediciones, vista de parcelas y recepción de alertas. |
| **Gerente** | `admin@agropulse.test` | `admin` | Acceso a parametrización de rangos, atención de alertas y recomendaciones del motor. |

---
