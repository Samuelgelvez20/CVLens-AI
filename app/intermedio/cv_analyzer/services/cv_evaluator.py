import os

from langchain_google_genai import ChatGoogleGenerativeAI

from models.cv_model import AnalisisCV
from prompts.cv_prompts import crear_sistema_prompts

MAX_CV_CHARS = 25000
MODELOS_EVALUACION = (
    "gemini-3.1-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-3-flash-preview",
)


class EvaluacionError(Exception):
    """Error controlado con mensaje comprensible para el usuario final."""


def limitar_texto_cv(texto_cv: str, max_chars: int = MAX_CV_CHARS) -> tuple[str, bool]:
    """Recorta el texto del CV si supera el límite seguro de caracteres."""
    if len(texto_cv) <= max_chars:
        return texto_cv, False
    return texto_cv[:max_chars], True


def traducir_error_amigable(exc: Exception) -> str:
    """Convierte errores técnicos de red o API en mensajes claros sin jerga técnica."""
    mensaje = str(exc).lower()

    if "clave de acceso" in mensaje or "no se encontró la clave" in mensaje:
        return (
            "Falta configurar la clave de acceso al servicio de inteligencia artificial. "
            "Verifica tu archivo de configuración antes de continuar."
        )

    if any(
        token in mensaje
        for token in ("401", "403", "api_key_invalid", "invalid api key", "incorrect api key", "permission_denied")
    ):
        return (
            "La clave de acceso al servicio de inteligencia artificial no es válida o no tiene permisos. "
            "Revisa que esté bien escrita y activa."
        )

    if any(token in mensaje for token in ("429", "resource_exhausted", "quota", "rate limit")):
        return (
            "Se alcanzó el límite temporal de consultas disponibles. "
            "Espera unos segundos y vuelve a intentarlo."
        )

    if any(token in mensaje for token in ("503", "unavailable", "high demand", "overloaded")):
        return (
            "El servicio de análisis está muy ocupado en este momento. "
            "Por favor, inténtalo nuevamente en unos instantes."
        )

    if any(token in mensaje for token in ("504", "deadline_exceeded", "timeout", "timed out")):
        return (
            "El análisis tardó más de lo esperado en responder. "
            "Por favor, inténtalo de nuevo en unos segundos."
        )

    if any(
        token in mensaje
        for token in ("connection", "connecterror", "nameresolution", "network", "dns", "unreachable")
    ):
        return (
            "No fue posible conectarse con el servicio de análisis. "
            "Verifica tu conexión a Internet e inténtalo nuevamente."
        )

    return (
        "No se pudo completar el análisis del currículum en este momento. "
        "Verifica el archivo PDF y vuelve a intentarlo."
    )


def crear_evaluador_cv(modelo: str = "gemini-3.1-flash-lite"):
    """Configura el modelo ChatGoogleGenerativeAI con salida estructurada AnalisisCV."""
    api_key = (
        os.getenv("GOOGLE_API_KEY")
        or os.getenv("GEMINI_API_KEY")
        or os.getenv("OPENAI_API_KEY")
    )
    if not api_key:
        raise ValueError("No se encontró la clave de acceso.")

    modelo_base = ChatGoogleGenerativeAI(
        model=modelo,
        temperature=0.2,
        google_api_key=api_key,
        timeout=12,
        max_retries=0,
    )
    modelo_estructurado = modelo_base.with_structured_output(AnalisisCV)
    chat_prompt = crear_sistema_prompts()
    return chat_prompt | modelo_estructurado


def evaluar_candidato(texto_cv: str, descripcion_puesto: str) -> AnalisisCV:
    """Invoca la cadena de evaluación con reintentos rápidos ante bloqueos transitorios."""
    texto_seguro, _ = limitar_texto_cv(texto_cv)
    ultimo_error: Exception | None = None

    for modelo in MODELOS_EVALUACION:
        try:
            cadena_evaluacion = crear_evaluador_cv(modelo=modelo)
            resultado = cadena_evaluacion.invoke(
                {
                    "texto_cv": texto_seguro,
                    "descripcion_puesto": descripcion_puesto,
                }
            )
            if resultado is None:
                raise ValueError("Respuesta vacía del servicio.")
            return resultado
        except Exception as exc:
            ultimo_error = exc
            mensaje = str(exc).lower()
            es_transitorio = any(
                token in mensaje
                for token in ("503", "504", "unavailable", "deadline_exceeded", "timeout", "timed out", "high demand")
            )
            if not es_transitorio:
                break

    raise EvaluacionError(traducir_error_amigable(ultimo_error or Exception("Error desconocido")))
