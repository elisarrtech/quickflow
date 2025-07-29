from flask import Blueprint, jsonify, render_template
from weasyprint import HTML
from datetime import datetime
from backend.utils.mail_utils import enviar_pdf
from backend.auth_utils import token_required
from backend.db import tasks_collection

report_bp = Blueprint("report", __name__)

@report_bp.route("/api/enviar-reporte", methods=["POST"])
@token_required
def enviar_reporte(usuario_email):
    tareas = list(tasks_collection.find({"usuario": usuario_email}))

    completadas = sum(1 for t in tareas if t.get("estado") == "completada")
    pendientes = sum(1 for t in tareas if t.get("estado") == "pendiente")
    atrasadas = sum(1 for t in tareas if t.get("fecha") and t.get("estado") != "completada" and datetime.strptime(t["fecha"], "%Y-%m-%d") < datetime.now())

    total = completadas + pendientes
    cumplimiento = int((completadas / total) * 100) if total > 0 else 0

    categorias = {}
    for t in tareas:
        cat = t.get("categoria", "Sin categoría")
        categorias[cat] = categorias.get(cat, 0) + 1

    html = render_template("reporte.html", 
      usuario=usuario_email, 
      fecha=datetime.now().strftime("%d/%m/%Y"), 
      completadas=completadas,
      pendientes=pendientes,
      atrasadas=atrasadas,
      cumplimiento=cumplimiento,
      categorias=categorias)

    pdf_data = HTML(string=html).write_pdf()
    enviar_pdf(usuario_email, pdf_data)

    return jsonify({"msg": "Reporte enviado correctamente."})

