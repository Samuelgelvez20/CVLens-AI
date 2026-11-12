# Analizador de currículums con IA (`cv_analyzer`)

Módulo principal de **CVLens-AI** construido con Streamlit, LangChain, Google Gemini y Pydantic.

## Arquitectura del módulo

- `app.py`: punto de entrada que ejecuta `ui.streamlit_ui.main()`.
- `models/cv_model.py`: modelo Pydantic `AnalisisCV` para la salida estructurada.
- `prompts/cv_prompts.py`: plantilla `ChatPromptTemplate` con los pesos de evaluación (40% experiencia, 35% habilidades, 15% formación, 10% coherencia).
- `services/pdf_processor.py`: lectura de PDF en memoria con `PyPDF2`.
- `services/cv_evaluator.py`: evaluación con `ChatGoogleGenerativeAI`, control de longitud, reintento rápido ante bloqueos transitorios y mensajes de error amigables.
- `services/database.py`: persistencia de vacantes y análisis en PostgreSQL (o SQLite como respaldo local).
- `ui/streamlit_ui.py`: carga múltiple en paralelo, barra lateral de historial, diálogos de **Ver vacante** y **Ver CVs**, y exportación CSV/JSON.

## Ejecución

Desde este directorio (`app/intermedio/cv_analyzer`):

```bash
python -m streamlit run app.py --server.address=0.0.0.0 --server.port=8501
```
