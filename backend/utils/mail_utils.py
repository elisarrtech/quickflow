from flask_mail import Mail, Message

mail = Mail()

def init_mail(app):
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USERNAME'] = 'tucorreo@gmail.com'
    app.config['MAIL_PASSWORD'] = 'tu_contraseña_app'
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    mail.init_app(app)

def enviar_pdf(destinatario, pdf_data, asunto="Reporte Quickflow"):
    msg = Message(asunto, sender='tucorreo@gmail.com', recipients=[destinatario])
    msg.body = "Adjunto encontrarás tu reporte PDF generado automáticamente desde Quickflow."
    msg.attach("reporte.pdf", "application/pdf", pdf_data)
    mail.send(msg)

