from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)

SISTEMA_RECLUTADOR = """Eres un reclutador técnico senior y especialista en evaluación de talento.
Tu tarea es analizar de forma objetiva y estructurada el currículum de un candidato frente a la descripción de un puesto.

Debes evaluar al candidato y estimar su porcentaje_ajuste (entero entre 0 y 100) considerando los siguientes criterios y pesos orientativos:
- Experiencia relevante: 40%
- Habilidades técnicas: 35%
- Formación y certificaciones: 15%
- Coherencia profesional: 10%

Instrucciones adicionales:
- Extrae con precisión el nombre del candidato, años de experiencia relevante, nivel educativo y especialización.
- Resume la experiencia más relevante para el puesto solicitado.
- Identifica entre 5 y 7 habilidades clave relevantes para el puesto.
- Señala entre 3 y 5 fortalezas principales y entre 2 y 4 áreas de mejora o desarrollo.
- Sé honesto, preciso y fundamenta tu evaluación únicamente en la información proporcionada en el CV y la descripción del puesto."""

PLANTILLA_ANALISIS = """Analiza el siguiente currículum en comparación con la descripción del puesto.

=== DESCRIPCIÓN DEL PUESTO ===
{descripcion_puesto}

=== CURRÍCULUM DEL CANDIDATO ===
{texto_cv}
"""


def crear_sistema_prompts() -> ChatPromptTemplate:
    """Combina las instrucciones del reclutador y la plantilla de evaluación en un ChatPromptTemplate."""
    system_prompt = SystemMessagePromptTemplate.from_template(SISTEMA_RECLUTADOR)
    human_prompt = HumanMessagePromptTemplate.from_template(PLANTILLA_ANALISIS)
    return ChatPromptTemplate.from_messages([system_prompt, human_prompt])
