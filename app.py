# =============================================================================
# APP PRINCIPAL - SISTEMA EXPERTO CARDÍACO MX
# Framework: Flask | Puerto: 5000
# =============================================================================

import logging
from flask import Flask, request, jsonify, render_template

from rules import evaluar_sintomas, obtener_catalogo_sintomas
from database import guardar_evaluacion, obtener_estadisticas

# ── Configuración ────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config["JSON_ENSURE_ASCII"] = False


# ── Rutas de interfaz ────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Página principal de la aplicación."""
    try:
        sintomas = obtener_catalogo_sintomas()
        return render_template("index.html", sintomas=sintomas)
    except Exception as e:
        logger.error(f"Error cargando la interfaz: {e}")
        return "Error cargando la aplicación", 500


# ── API REST ─────────────────────────────────────────────────────────────────

@app.route("/api/sintomas", methods=["GET"])
def get_sintomas():
    """GET /api/sintomas → Catálogo completo de síntomas."""
    try:
        return jsonify({
            "success": True,
            "sintomas": obtener_catalogo_sintomas(),
        })
    except Exception as e:
        logger.error(f"Error obteniendo síntomas: {e}")
        return jsonify({"success": False, "error": "Error interno"}), 500


@app.route("/api/evaluar", methods=["POST"])
def evaluar():
    """
    POST /api/evaluar
    Recibe síntomas + datos del paciente y devuelve evaluación.
    """

    try:
        datos = request.get_json(force=True, silent=True) or {}

        sintomas = datos.get("sintomas", [])
        if not isinstance(sintomas, list):
            return jsonify({
                "success": False,
                "error": "El campo 'sintomas' debe ser una lista."
            }), 400

        # ── Ejecutar motor de inferencia ─────────────────────────
        resultado = evaluar_sintomas(sintomas)

        # ── Datos del paciente ──────────────────────────────────
        paciente = datos.get("paciente", {})

        # ── Guardar en base de datos ────────────────────────────
        try:
            eval_id = guardar_evaluacion(paciente, sintomas, resultado)
            if eval_id:
                resultado["evaluacion_id"] = eval_id
                logger.info(f"✔ Evaluación guardada ID: {eval_id}")
            else:
                logger.warning("⚠ No se pudo guardar la evaluación en la BD")
        except Exception as db_error:
            logger.error(f"❌ Error guardando en DB: {db_error}")

        # ── Log general ─────────────────────────────────────────
        logger.info(
            f"Evaluación completada | "
            f"Síntomas: {len(sintomas)} | "
            f"Riesgo: {resultado.get('nivel_riesgo')} | "
            f"Condición: {resultado.get('condicion')}"
        )

        return jsonify({
            "success": True,
            "resultado": resultado
        })

    except Exception as e:
        logger.error(f"❌ Error en evaluación: {e}")
        return jsonify({
            "success": False,
            "error": "Error interno del servidor"
        }), 500


@app.route("/api/estadisticas", methods=["GET"])
def estadisticas():
    """GET /api/estadisticas → Estadísticas del sistema."""
    try:
        stats = obtener_estadisticas()
        return jsonify({
            "success": True,
            "estadisticas": stats
        })
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        return jsonify({
            "success": False,
            "error": "Error interno"
        }), 500


# ── Manejo de errores global ─────────────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "success": False,
        "error": "Recurso no encontrado."
    }), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({
        "success": False,
        "error": "Error interno del servidor."
    }), 500


# ── Punto de entrada ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    logger.info("🚀 Iniciando CardioScan MX en http://localhost:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)