# backend/routes/alerts_routes.py
from flask import Blueprint, jsonify, current_app
from backend.alerts import enviar_alerta_whatsapp_twilio
import logging

alerts_bp = Blueprint("alerts", __name__)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@alerts_bp.route("/alerta-prueba", methods=["GET"])
def alerta_prueba():
    """
    Ruta de prueba para verificar que el sistema de alertas está funcionando.
    """
    logger.info("✅ Ruta de prueba de alertas accedida")
    return jsonify({"mensaje": "Alerta funcionando ✅"}), 200


@alerts_bp.route("/verificar-uso", methods=["GET"])
def verificar_uso():
    """
    Verifica el uso de recursos (ej. tareas próximas) y envía alerta si es necesario.
    Simulación: busca tareas con fecha de hoy o mañana.
    """
    try:
        # Simulamos obtener tareas del usuario autenticado
        # En producción, esto vendría con token_required
        mongo = current_app.mongo
        email_usuario = "usuario@ejemplo.com"  # Reemplaza con token_required

        hoy = mongo.db.tasks.find({
            "usuario": email_usuario,
            "fecha": {"$gte": "2025-04-05", "$lte": "2025-04-06"}  # Usa datetime en producción
        })

        tareas_proximas = list(hoy)
        logger.info(f"🔍 {len(tareas_proximas)} tareas próximas encontradas")

        if tareas_proximas:
            # Enviar alerta
            mensaje = f"Tienes {len(tareas_proximas)} tarea(s) pendiente(s) hoy o mañana."
            status = enviar_alerta_whatsapp_twilio(mensaje)
            return jsonify({
                "mensaje": "Alerta enviada",
                "tareas_proximas": len(tareas_proximas),
                "status": status
            }), 200
        else:
            return jsonify({
                "mensaje": "No hay tareas próximas",
                "tareas_proximas": 0,
                "status": "no_enviado"
            }), 200

    except Exception as e:
        logger.error(f"❌ Error en verificar_uso: {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500
