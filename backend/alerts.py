import requests
import os

def enviar_alerta_whatsapp_twilio():
    account_sid = os.getenv("TWILIO_SID")  # ACxxx
    auth_token = os.getenv("TWILIO_AUTH")  # Token de Twilio
    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"

    data = {
        'To': 'whatsapp:+5214421092362',
        'From': 'whatsapp:+14155238886',
        'ContentSid': 'HXb5b62575e6e4ff6129ad7c8efe1f983e',  # reemplázalo con el tuyo real si es diferente
        'ContentVariables': '{"1":"28/07","2":"6:00pm"}'  # Simula tu alerta, luego personalizaremos esto
    }

    response = requests.post(url, data=data, auth=(account_sid, auth_token))
    print("Status:", response.status_code)
    print("Response:", response.text)
    return response.status_code
