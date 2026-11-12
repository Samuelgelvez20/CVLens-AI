import json
import os
import sqlite3
from pathlib import Path

from models.cv_model import AnalisisCV

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:  # pragma: no cover - fallback cuando psycopg2 no está instalado
    psycopg2 = None
    RealDictCursor = None

SQLITE_PATH = Path(__file__).resolve().parent.parent / "cv_analyzer.db"


def obtener_conexion() -> tuple[object, str]:
    """Obtiene una conexión a PostgreSQL si está disponible, o SQLite como respaldo."""
    pg_db = os.getenv("POSTGRES_DB")
    pg_user = os.getenv("POSTGRES_USER")
    pg_password = os.getenv("POSTGRES_PASSWORD")
    pg_host = os.getenv("POSTGRES_HOST", "postgres")
    pg_port = int(os.getenv("POSTGRES_INTERNAL_PORT", "5432"))

    if psycopg2 and pg_db and pg_user and pg_password:
        try:
            conn = psycopg2.connect(
                dbname=pg_db,
                user=pg_user,
                password=pg_password,
                host=pg_host,
                port=pg_port,
                connect_timeout=3,
            )
            return conn, "postgres"
        except Exception:
            pass

    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    return conn, "sqlite"


def inicializar_bd() -> None:
    """Crea las tablas de vacantes y análisis de CV si no existen."""
    conn, motor = obtener_conexion()
    try:
        cursor = conn.cursor()
        if motor == "postgres":
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS vacantes (
                    id SERIAL PRIMARY KEY,
                    titulo TEXT NOT NULL,
                    descripcion TEXT NOT NULL,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS analisis_cv (
                    id SERIAL PRIMARY KEY,
                    vacante_id INTEGER NOT NULL REFERENCES vacantes(id) ON DELETE CASCADE,
                    nombre_archivo_pdf TEXT NOT NULL,
                    nombre_candidato TEXT NOT NULL,
                    experiencia_anos INTEGER NOT NULL,
                    habilidades_clave TEXT NOT NULL,
                    education TEXT NOT NULL,
                    experiencia_relevante TEXT NOT NULL,
                    fortalezas TEXT NOT NULL,
                    areas_mejora TEXT NOT NULL,
                    porcentaje_ajuste INTEGER NOT NULL,
                    fecha_analisis TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            )
        else:
            cursor.execute("PRAGMA foreign_keys = ON;")
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS vacantes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    titulo TEXT NOT NULL,
                    descripcion TEXT NOT NULL,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS analisis_cv (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    vacante_id INTEGER NOT NULL,
                    nombre_archivo_pdf TEXT NOT NULL,
                    nombre_candidato TEXT NOT NULL,
                    experiencia_anos INTEGER NOT NULL,
                    habilidades_clave TEXT NOT NULL,
                    education TEXT NOT NULL,
                    experiencia_relevante TEXT NOT NULL,
                    fortalezas TEXT NOT NULL,
                    areas_mejora TEXT NOT NULL,
                    porcentaje_ajuste INTEGER NOT NULL,
                    fecha_analisis TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (vacante_id) REFERENCES vacantes(id) ON DELETE CASCADE
                );
                """
            )
        conn.commit()
    finally:
        conn.close()


def extraer_titulo_vacante(descripcion: str) -> str:
    """Obtiene un título corto representativo a partir del enunciado de la vacante."""
    for linea in descripcion.splitlines():
        limpia = linea.strip()
        if not limpia:
            continue
        if limpia.lower().startswith("puesto:"):
            limpia = limpia.split(":", 1)[1].strip()
        return limpia[:80] if len(limpia) <= 80 else limpia[:77] + "..."
    return "Vacante sin título"


def guardar_analisis_en_bd(
    titulo_vacante: str,
    descripcion_vacante: str,
    nombre_archivo_pdf: str,
    analisis: AnalisisCV,
) -> tuple[int, int]:
    """Guarda o reutiliza la vacante y registra el análisis del CV asociado."""
    inicializar_bd()
    titulo_final = (titulo_vacante or "").strip() or extraer_titulo_vacante(descripcion_vacante)
    descripcion_limpia = descripcion_vacante.strip()

    conn, motor = obtener_conexion()
    placeholder = "%s" if motor == "postgres" else "?"
    try:
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT id FROM vacantes WHERE descripcion = {placeholder} LIMIT 1",
            (descripcion_limpia,),
        )
        fila_vacante = cursor.fetchone()

        if fila_vacante:
            vacante_id = fila_vacante[0] if not isinstance(fila_vacante, dict) else fila_vacante["id"]
        else:
            if motor == "postgres":
                cursor.execute(
                    "INSERT INTO vacantes (titulo, descripcion) VALUES (%s, %s) RETURNING id",
                    (titulo_final, descripcion_limpia),
                )
                vacante_id = cursor.fetchone()[0]
            else:
                cursor.execute(
                    "INSERT INTO vacantes (titulo, descripcion) VALUES (?, ?)",
                    (titulo_final, descripcion_limpia),
                )
                vacante_id = cursor.lastrowid

        datos_analisis = (
            vacante_id,
            nombre_archivo_pdf or "cv.pdf",
            analisis.nombre_candidato,
            analisis.experiencia_años,
            json.dumps(analisis.habilidades_clave, ensure_ascii=False),
            analisis.education,
            analisis.experiencia_relevante,
            json.dumps(analisis.fortalezas, ensure_ascii=False),
            json.dumps(analisis.areas_mejora, ensure_ascii=False),
            analisis.porcentaje_ajuste,
        )

        if motor == "postgres":
            cursor.execute(
                """
                INSERT INTO analisis_cv (
                    vacante_id, nombre_archivo_pdf, nombre_candidato, experiencia_anos,
                    habilidades_clave, education, experiencia_relevante,
                    fortalezas, areas_mejora, porcentaje_ajuste
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                datos_analisis,
            )
            analisis_id = cursor.fetchone()[0]
        else:
            cursor.execute(
                """
                INSERT INTO analisis_cv (
                    vacante_id, nombre_archivo_pdf, nombre_candidato, experiencia_anos,
                    habilidades_clave, education, experiencia_relevante,
                    fortalezas, areas_mejora, porcentaje_ajuste
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                datos_analisis,
            )
            analisis_id = cursor.lastrowid

        conn.commit()
        return int(vacante_id), int(analisis_id)
    finally:
        conn.close()

