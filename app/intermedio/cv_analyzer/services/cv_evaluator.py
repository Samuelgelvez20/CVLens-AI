from langchain_openai import ChatOpenAI

from models.cv_model import AnalisisCV
from prompts.cv_prompts import crear_sistema_prompts


def crear_evaluador_cv():
    """Configura el modelo ChatOpenAI con salida estructurada AnalisisCV."""
    modelo_base = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.2,
    )
    modelo_estructurado = modelo_base.with_structured_output(AnalisisCV)
    chat_prompt = crear_sistema_prompts()
    return chat_prompt | modelo_estructurado
