import io
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, File, Form, HTTPException, Response, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Garantizar que el directorio cv_analyzer esté en sys.path
DIRECTORIO_ACTUAL = Path(__file__).resolve().parent
if str(DIRECTORIO_ACTUAL) not in sys.path:
    sys.path.insert(0, str(DIRECTORIO_ACTUAL))

from models.cv_model import AnalisisCV
from services.cv_evaluator import (
    EvaluacionError,
    evaluar_candidato,
    limitar_texto_cv,
    MAX_CV_CHARS,
)
from services.database import (
    extraer_titulo_vacante,
    guardar_analisis_en_bd,
    inicializar_bd,
    listar_analisis_por_vacante,
    listar_vacantes,
    obtener_conexion,
    obtener_vacante_por_id,
)
from services.pdf_processor import extraer_texto_pdf

app = FastAPI(
    title="CVLens-AI API",
    description="Motor Inteligente de Evaluación, Ranking y Análisis Estructurado de Currículums con LLMs",
    version="2.0.0",
)

# CORS para comunicación con el frontend en React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class GuardarAnalisisItem(BaseModel):
    nombre_archivo: str
    analisis: AnalisisCV


class GuardarLoteRequest(BaseModel):
    titulo: str
    descripcion: str
    items: List[GuardarAnalisisItem]


@app.on_event("startup")
def startup_event():
    inicializar_bd()


@app.get("/api/health")
def health_check():
    """Verifica estado del servicio y motor de base de datos."""
    conn, motor = obtener_conexion()
    conn.close()
    return {
        "status": "online",
        "service": "CVLens-AI Core Engine",
        "database_engine": motor,
        "max_cv_chars": MAX_CV_CHARS,
    }


@app.get("/api/vacantes")
def obtener_vacantes():
    """Lista todas las vacantes registradas junto con el total de candidatos analizados."""
    try:
        return listar_vacantes()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar vacantes: {str(exc)}",
        )


@app.get("/api/vacantes/{vacante_id}")
def obtener_vacante(vacante_id: int):
    """Obtiene los detalles de una vacante específica."""
    vacante = obtener_vacante_por_id(vacante_id)
    if not vacante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vacante con ID {vacante_id} no encontrada",
        )
    return vacante


@app.get("/api/vacantes/{vacante_id}/analisis")
def obtener_analisis_vacante(vacante_id: int):
    """Retorna el ranking de candidatos evaluados para una vacante, ordenados por porcentaje de ajuste."""
    vacante = obtener_vacante_por_id(vacante_id)
    if not vacante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vacante con ID {vacante_id} no encontrada",
        )
    analisis = listar_analisis_por_vacante(vacante_id)
    return {
        "vacante": vacante,
        "total_candidatos": len(analisis),
        "ranking": analisis,
    }


def procesar_un_archivo_cv(nombre_archivo: str, contenido_bytes: bytes, descripcion_puesto: str) -> dict:
    """Extrae el texto del PDF y ejecuta el agente evaluador con salida estructurada."""
    try:
        texto_cv = extraer_texto_pdf(io.BytesIO(contenido_bytes))
        if texto_cv.startswith("Error:"):
            return {
                "nombre_archivo": nombre_archivo,
                "ok": False,
                "error": texto_cv,
                "analisis": None,
                "truncado": False,
            }

        _, truncado = limitar_texto_cv(texto_cv)
        resultado: AnalisisCV = evaluar_candidato(
            texto_cv=texto_cv,
            descripcion_puesto=descripcion_puesto,
        )

        return {
            "nombre_archivo": nombre_archivo,
            "ok": True,
            "error": None,
            "analisis": resultado.model_dump(),
            "truncado": truncado,
        }
    except EvaluacionError as err:
        return {
            "nombre_archivo": nombre_archivo,
            "ok": False,
            "error": str(err),
            "analisis": None,
            "truncado": False,
        }
    except Exception as exc:
        return {
            "nombre_archivo": nombre_archivo,
            "ok": False,
            "error": f"Fallo no controlado: {str(exc)}",
            "analisis": None,
            "truncado": False,
        }


@app.post("/api/evaluar")
async def evaluar_candidatos(
    files: List[UploadFile] = File(...),
    descripcion_puesto: str = Form(...),
    titulo_vacante: Optional[str] = Form(None),
):
    """
    Recibe uno o varios archivos PDF y la descripción del puesto.
    Ejecuta el pipeline de extracción y evaluación estructurada en paralelo.
    """
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe proporcionar al menos un archivo de CV en formato PDF.",
        )

    if not descripcion_puesto.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La descripción del puesto no puede estar vacía.",
        )

    # Cargar en memoria para procesamiento concurrente seguro
    archivos_en_memoria = []
    for f in files:
        bytes_data = await f.read()
        archivos_en_memoria.append((f.filename or "candidato.pdf", bytes_data))

    inicio = time.perf_counter()
    with ThreadPoolExecutor(max_workers=min(4, len(archivos_en_memoria))) as pool:
        futuros = [
            pool.submit(procesar_un_archivo_cv, nombre, data, descripcion_puesto.strip())
            for nombre, data in archivos_en_memoria
        ]
        resultados = [futuro.result() for futuro in futuros]
    duracion = time.perf_counter() - inicio

    titulo_final = (
        (titulo_vacante or "").strip()
        or extraer_titulo_vacante(descripcion_puesto.strip())
    )

    exitosos = [r for r in resultados if r["ok"]]
    fallidos = [r for r in resultados if not r["ok"]]

    # Ordenar candidatos exitosos por ajuste descendente
    exitosos.sort(key=lambda x: x["analisis"]["porcentaje_ajuste"], reverse=True)

    return {
        "titulo": titulo_final,
        "descripcion": descripcion_puesto.strip(),
        "duracion_segundos": round(duracion, 2),
        "total": len(resultados),
        "total_exitosos": len(exitosos),
        "total_fallidos": len(fallidos),
        "resultados": exitosos + fallidos,
    }


@app.post("/api/vacantes/guardar")
def guardar_lote_analisis(request: GuardarLoteRequest):
    """Persiste en PostgreSQL / SQLite la vacante y los análisis de candidatos generados."""
    try:
        vacante_id = None
        guardados = 0
        for item in request.items:
            v_id, _ = guardar_analisis_en_bd(
                titulo_vacante=request.titulo,
                descripcion_vacante=request.descripcion,
                nombre_archivo_pdf=item.nombre_archivo,
                analisis=item.analisis,
            )
            vacante_id = v_id
            guardados += 1

        return {
            "ok": True,
            "vacante_id": vacante_id,
            "guardados": guardados,
            "mensaje": f"Se guardaron exitosamente {guardados} análisis en el historial.",
        }
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al guardar análisis: {str(exc)}",
        )


@app.get("/api/vacantes/{vacante_id}/export-csv")
def exportar_ranking_csv(vacante_id: int):
    """Genera y descarga un CSV estructurado con el ranking de candidatos evaluados."""
    vacante = obtener_vacante_por_id(vacante_id)
    if not vacante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vacante no encontrada",
        )

    analisis_lista = listar_analisis_por_vacante(vacante_id)
    import csv

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "Posicion",
            "Candidato",
            "Archivo PDF",
            "Porcentaje Ajuste",
            "Anos Experiencia",
            "Educacion",
            "Habilidades Clave",
            "Fortalezas",
            "Areas de Mejora",
            "Experiencia Relevante",
        ]
    )

    for idx, item in enumerate(analisis_lista, start=1):
        writer.writerow(
            [
                idx,
                item["nombre_candidato"],
                item["nombre_archivo_pdf"],
                f"{item['porcentaje_ajuste']}%",
                item["experiencia_anos"],
                item["education"],
                "; ".join(item["habilidades_clave"]),
                "; ".join(item["fortalezas"]),
                "; ".join(item["areas_mejora"]),
                item["experiencia_relevante"],
            ]
        )

    csv_content = buffer.getvalue()
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=ranking_vacante_{vacante_id}.csv"
        },
    )


# Montar la aplicación frontend React compilada (en frontend/dist)
RUTA_FRONTEND_DIST = Path(__file__).resolve().parent.parent.parent.parent / "frontend" / "dist"

if RUTA_FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=RUTA_FRONTEND_DIST / "assets"), name="assets")

    @app.get("/{full_path:path}")
    def servir_spa(full_path: str):
        archivo = RUTA_FRONTEND_DIST / full_path
        if archivo.is_file():
            return FileResponse(archivo)
        return FileResponse(RUTA_FRONTEND_DIST / "index.html")
