# backend/alerts.py
import os
import requests
from urllib.parse import quote

def enviar_alerta_whatsapp_twilio(mensaje_personalizado=None):
    """
    Envía una alerta de WhatsApp usando la API de Twilio.
    :param mensaje_personalizado: Mensaje opcional personalizado
    :return: True si se envió, False si falló
    """
    try:
        # 🔐 Obtener credenciales (asegúrate de que estén en Netlify)
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        from_whatsapp = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")
        to_whatsapp = os.getenv("ALERTS_TO_WHATSAPP")  # Ej: "whatsapp:+5214421092362"

        # 🛑 Validar variables críticas
        if not account_sid or not auth_token or not to_whatsapp:
            print("❌ Faltan variables de entorno para Twilio")
            print(f"  TWILIO_ACCOUNT_SID: {'✅' if account_sid else '❌'}")
            print(f"  TWILIO_AUTH_TOKEN: {'✅' if auth_token else '❌'}")
            print(f"  ALERTS_TO_WHATSAPP: {'✅' if to_whatsapp else '❌'}")
            return False

        # 📝 Mensaje por defecto
        mensaje = mensaje_personalizado or (
            "🚨 *Quickflow - Alerta de tareas*\n"
            "Tienes tareas pendientes.\n"
            "Revisa tu panel: https://peppy-starlight-fd4c37.netlify.app ✅"
        )

        # 🌐 URL corregida (sin espacios)
        url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"

        # ✅ Datos bien formados
        data = {
            'To': to_whatsapp,
            'From': from_whatsapp,
            'Body': mensaje
        }

        # 📡 Enviar solicitud
        response = requests.post(
            url,
            data=data,
            auth=(account_sid, auth_token),
            timeout=10
        )

        # 📊 Resultados
        print(f"✅ WhatsApp API Status: {response.status_code}")
        if response.status_code == 201:
            print("💬 Mensaje enviado correctamente")
            return True
        else:
            print(f"❌ Error en API de Twilio: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Error de red al enviar WhatsApp: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado en enviar_alerta_whatsapp_twilio: {str(e)}")
        return False
