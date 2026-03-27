# 1. Usamos la versión 3.11 ligera (slim)
FROM python:3.11-slim

# 2. Configuraciones para que los logs se vean en tiempo real
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. Directorio de trabajo
WORKDIR /app

# 4. Instalamos herramientas necesarias para conectar con MySQL
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 5. Copiamos tu archivo de dependencias (se llama 'requirements')
COPY requirements .
RUN pip install --no-cache-dir -r requirements

# 6. Copiamos el resto de tu código
COPY . .

# 7. Exponemos el puerto de Flask
EXPOSE 5000

# 8. EJECUCIÓN: Primero crea/puebla la DB y luego arranca la web
CMD ["sh", "-c", "python init_db.py && python app.py"]