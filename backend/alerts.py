import requests
import os

def enviar_alerta_whatsapp_twilio():
    account_sid = os.getenv("TWILIO_SID")  # Tu Twilio SID real
    auth_token = os.getenv("TWILIO_AUTH")  # Tu Twilio token real

    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"

    mensaje = (
        "🚨 *Quickflow Alerta*:\n"
        "Tienes tareas pendientes en tu panel.\n"
        "Revisa y organiza tu día desde: https://quickflow.app ✅"
    )

    data = {
        'To': 'whatsapp:+5214421092362',  # Tu número validado
        'From': 'whatsapp:+14155238886',  # Número del sandbox Twilio
        'Body': mensaje
    }

    response = requests.post(url, data=data, auth=(account_sid, auth_token))

    print("Status:", response.status_code)
    print("Response:", response.text)

    return response.status_code
