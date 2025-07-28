# Usa Python base image
FROM python:3.11

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos del proyecto
COPY . /app

# Instala dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Expón el puerto que usará Flask (Fly por defecto redirige a este)
EXPOSE 8080

# Define la variable de entorno para Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV PORT=8080

# Comando de inicio
CMD ["flask", "run", "--host=0.0.0.0", "--port=8080"]
