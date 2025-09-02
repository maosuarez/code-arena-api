FROM python:3.11-slim

# 🔐 Declarar los argumentos que vienen del workflow
ARG COSMOS_URL
ARG SECRET_KEY
ARG COSMOS_DB

# 🧬 Exportarlos como variables de entorno si los necesitas en tiempo de ejecución
ENV COSMOS_URL=${COSMOS_URL}
ENV SECRET_KEY=${SECRET_KEY}
ENV COSMOS_DB=${COSMOS_DB}

# Evita problemas con buffering
ENV PYTHONUNBUFFERED=1

# Crea directorio de trabajo
WORKDIR /app

# Instala dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el código fuente
COPY ./app ./app

# Expone el puerto
EXPOSE 8000

# Comando de arranque
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
