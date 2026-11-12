import os

from langchain_google_genai import ChatGoogleGenerativeAI

from models.cv_model import AnalisisCV
from prompts.cv_prompts import crear_sistema_prompts


def crear_evaluador_cv():
    """Configura el modelo ChatGoogleGenerativeAI con salida estructurada AnalisisCV."""
    api_key = (
        os.getenv("GOOGLE_API_KEY")
        or os.getenv("GEMINI_API_KEY")
        or os.getenv("OPENAI_API_KEY")
    )
    if not api_key:
        raise ValueError(
            "No se encontró la clave de API. Configura GOOGLE_API_KEY en tu entorno o archivo .env."
        )

    modelo_base = ChatGoogleGenerativeAI(
        model="gemini-3.8-flash",
        temperature=0.2,
        google_api_key=api_key,
    )
    modelo_estructurado = modelo_base.with_structured_output(AnalisisCV)
    chat_prompt = crear_sistema_prompts()
    return chat_prompt | modelo_estructurado


def evaluar_candidato(texto_cv: str, descripcion_puesto: str) -> AnalisisCV:
    """Invoca la cadena de evaluación y devuelve el análisis estructurado del candidato."""
    try:
        cadena_evaluacion = crear_evaluador_cv()
        resultado = cadena_evaluacion.invoke(
            {
                "texto_cv": texto_cv,
                "descripcion_puesto": descripcion_puesto,
            }
        )
        return resultado
    except Exception as exc:
        return AnalisisCV(
            nombre_candidato="Error en el análisis",
            experiencia_años=0,
            habilidades_clave=["No disponible"],
            education="No disponible",
            experiencia_relevante=f"No se pudo completar el análisis: {str(exc)}",
            fortalezas=["Requiere revisión manual"],
            areas_mejora=["Verificar configuración de API y formato del CV"],
            porcentaje_ajuste=0,
        )
