FROM python:3.11-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos necesarios (incluyendo templates)
COPY requirements.txt .
COPY app.py .
COPY templates/ ./templates/

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto donde corre la app web
EXPOSE 5000

# Comando para ejecutar la aplicación
CMD ["python", "app.py"]