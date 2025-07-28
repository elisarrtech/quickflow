from flask import Blueprint, jsonify
from backend.alerts import enviar_alerta_whatsapp_twilio  # Ajusta si cambia tu estructura

alertas_bp = Blueprint('alertas_bp', __name__)

@alertas_bp.route('/api/verificar-uso', methods=['GET'])
def verificar_uso():
    status = enviar_alerta_whatsapp_twilio()
    return jsonify({"mensaje": "Alerta enviada por WhatsApp", "status": status}), 200
