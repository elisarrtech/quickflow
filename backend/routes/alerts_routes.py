from flask import Blueprint
from backend.alerts import enviar_alerta_whatsapp_twilio

alerts_bp = Blueprint("alerts", __name__)

@alerts_bp.route("/alerta-prueba")
def alerta_prueba():
    return {"mensaje": "Alerta funcionando ✅"}

@alerts_bp.route("/verificar-uso")
def verificar_uso():
    status = enviar_alerta_whatsapp_twilio()
    return {"mensaje": "Verificación enviada", "status": status}
