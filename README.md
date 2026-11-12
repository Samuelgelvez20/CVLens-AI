# CVLens-AI — Analizador de Currículums con IA

<p align="center">
  <img src="https://img.shields.io/badge/Status-Completado-success?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Version-v1.0.0-blue?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" />
  <img src="https://img.shields.io/badge/Google_Gemini-8E75C2?style=for-the-badge&logo=google&logoColor=white" />
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" />
  <img src="https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white" />
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" />
</p>


Aplicación web construida con **Streamlit**, **LangChain** y **Google Gemini** que compara uno o varios currículums en PDF frente a la descripción de una vacante, genera un análisis estructurado con porcentaje de ajuste y almacena el historial de vacantes y candidatos en **PostgreSQL** (con respaldo automático en **SQLite** para ejecución local).

---

## Funcionalidades principales

- **Carga múltiple de CVs en paralelo:** admite uno o varios archivos PDF con texto seleccionable y los evalúa concurrentemente mostrando el tiempo total de procesamiento.
- **Evaluación estructurada con IA:** utiliza `ChatGoogleGenerativeAI` (`gemini-3.1-flash-lite` con reintento rápido y respaldo en `gemini-3-flash-preview`) y salida estructurada validada con **Pydantic** (`AnalisisCV`).
- **Criterios de evaluación:**
  - Experiencia relevante: 40%
  - Habilidades técnicas: 35%
  - Formación y certificaciones: 15%
  - Coherencia profesional: 10%
- **Umbrales de clasificación:**
  - **Evaluación principal:** `80–100` Excelente | `60–79` Bueno | `40–59` Regular | `0–39` Bajo.
  - **Recomendación final:** `70–100` Candidato recomendado | `50–69` Candidato con potencial | `0–49` Candidato no recomendado.
- **Historial persistente por vacante:** barra lateral con mini-tarjetas de cada vacante guardada, botón **Ver vacante** (enunciado completo y carga al formulario) y botón **Ver CVs** (ranking ordenado por porcentaje, detalle completo por candidato y exportación en **CSV** y **JSON**).
- **Control de longitud y errores amigables:** recorte seguro para documentos extensos (25,000 caracteres) y mensajes de error claros sin exponer detalles técnicos.

---

## Estructura del proyecto

```text
CVLens-AI/
├── .env.example                     # Plantilla de variables de entorno
├── .gitignore
├── Dockerfile                       # Imagen base Python 3.12
├── docker-compose.yml               # Servicios: app, postgres y pgadmin
├── requirements.txt                 # Dependencias del proyecto
├── README.md
└── app/
    └── intermedio/
        └── cv_analyzer/
            ├── README.md
            ├── app.py               # Punto de entrada de Streamlit
            ├── models/
            │   └── cv_model.py      # Esquema Pydantic AnalisisCV
            ├── prompts/
            │   └── cv_prompts.py    # Instrucciones y plantilla de evaluación
            ├── services/
            │   ├── pdf_processor.py # Extracción de texto del PDF con PyPDF2
            │   ├── cv_evaluator.py  # Configuración de Gemini, reintentos y errores
            │   └── database.py      # Persistencia en PostgreSQL / SQLite
            └── ui/
                └── streamlit_ui.py  # Interfaz, estado de sesión, historial y exportación
```

---

## Configuración y ejecución

### 1. Variables de entorno

Copia `.env.example` a `.env` y completa tu clave de Gemini (`GOOGLE_API_KEY`) y credenciales locales:

```bash
cp .env.example .env
```

### 2. Con Docker Compose (recomendado)

```bash
docker compose up -d --build
docker compose exec -w /app/app/intermedio/cv_analyzer app \
  python -m streamlit run app.py --server.address=0.0.0.0 --server.port=8501
```

Abre **<http://localhost:8501>** en tu navegador.

### 3. Ejecución local (sin Docker)

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

export GOOGLE_API_KEY="tu_clave_de_gemini"
cd app/intermedio/cv_analyzer
python -m streamlit run app.py --server.port=8501
```

*(En ejecución local sin PostgreSQL, la aplicación guarda automáticamente el historial en un archivo local `cv_analyzer.db` con SQLite.)*

---

## 👥 Metodología y Flujo Git Flow

- **Estrategia de Ramificación:** Separación de trabajo en ramas de características (, , , , ), integradas en  y estabilizadas en  bajo la versión .
- **Conventional Commits:** Trazabilidad estandarizada (, , , ).

---

## 📄 Licencia

Este proyecto está bajo la Licencia **MIT** — consulta el archivo [LICENSE](LICENSE) para más detalles.
