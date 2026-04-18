
import os
import json
import logging
from datetime import datetime

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False

logger = logging.getLogger(__name__)

# Configuración de conexión desde variables de entorno
DB_CONFIG = {
    "host":     os.getenv("DB_HOST", "localhost"),
    "port":     os.getenv("DB_PORT", "5432"),
    "database": os.getenv("DB_NAME", "sistema_cardiaco"),
    "user":     os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "TeamNavySeal6"),
}


def get_connection():
    """Establece y retorna una conexión a PostgreSQL."""
    if not DB_AVAILABLE:
        raise RuntimeError("psycopg2 no está instalado.")
    return psycopg2.connect(**DB_CONFIG)


def guardar_evaluacion(datos_paciente: dict, sintomas: list, resultado: dict) -> int | None:
    """
    Guarda una evaluación completa en la base de datos.

    Args:
        datos_paciente: Nombre, edad, sexo del paciente
        sintomas: Lista de IDs de síntomas reportados
        resultado: Resultado del motor de inferencia

    Returns:
        ID de la evaluación creada, o None si falla
    """
    if not DB_AVAILABLE:
        logger.warning("DB no disponible. Evaluación no guardada.")
        return None

    sql = """
        INSERT INTO evaluaciones (
            nombre_paciente, edad, sexo,
            sintomas_reportados, condicion_detectada,
            nivel_riesgo, puntaje, recomendaciones,
            fecha_evaluacion
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id;
    """
    try:
        with get_connection() as conn:
            print("Conectando a BD:", DB_CONFIG)
            with conn.cursor() as cur:
                cur.execute(sql, (
                    datos_paciente.get("nombre", "Anónimo"),
                    datos_paciente.get("edad"),
                    datos_paciente.get("sexo"),
                    json.dumps(sintomas, ensure_ascii=False),
                    resultado.get("condicion"),
                    resultado.get("nivel_riesgo"),
                    resultado.get("puntaje_total"),
                    json.dumps(resultado.get("recomendaciones", []), ensure_ascii=False),
                    datetime.utcnow(),
                ))
                return cur.fetchone()[0]
    except Exception as e:
        logger.error(f"Error al guardar evaluación: {e}")
        return None


def obtener_estadisticas() -> dict:
    """Retorna estadísticas agregadas de evaluaciones previas."""
    if not DB_AVAILABLE:
        return {}
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT
                        COUNT(*) AS total,
                        SUM(CASE WHEN nivel_riesgo = 'alto'  THEN 1 ELSE 0 END) AS alto,
                        SUM(CASE WHEN nivel_riesgo = 'medio' THEN 1 ELSE 0 END) AS medio,
                        SUM(CASE WHEN nivel_riesgo = 'bajo'  THEN 1 ELSE 0 END) AS bajo
                    FROM evaluaciones;
                """)
                return dict(cur.fetchone() or {})
    except Exception as e:
        logger.error(f"Error al obtener estadísticas: {e}")
        return {}
