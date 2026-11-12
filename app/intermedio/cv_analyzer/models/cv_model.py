from pydantic import BaseModel, Field


class AnalisisCV(BaseModel):
    """Esquema estructurado para el resultado del análisis de un currículum."""

    nombre_candidato: str = Field(
        ...,
        description="Nombre completo del candidato extraído del CV",
    )
    experiencia_años: int = Field(
        ...,
        description="Años de experiencia relevante para el puesto",
    )
    habilidades_clave: list[str] = Field(
        ...,
        description="Lista de 5 a 7 habilidades clave relevantes para el puesto",
    )
    education: str = Field(
        ...,
        description="Nivel educativo más alto y especialización principal",
    )
    experiencia_relevante: str = Field(
        ...,
        description="Resumen conciso de la experiencia más relevante para el puesto",
    )
    fortalezas: list[str] = Field(
        ...,
        description="Lista de 3 a 5 principales fortalezas del candidato",
    )
    areas_mejora: list[str] = Field(
        ...,
        description="Lista de 2 a 4 áreas donde el candidato podría mejorar o desarrollarse",
    )
    porcentaje_ajuste: int = Field(
        ...,
        ge=0,
        le=100,
        description="Porcentaje de ajuste al puesto entre 0 y 100",
    )
