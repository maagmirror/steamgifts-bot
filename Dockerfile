# Dockerfile

# Usa una imagen base de Python
FROM python:3.8-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos de requerimientos y el código fuente
COPY requirements.txt ./
COPY src/ ./src

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copia el archivo de entorno (asegúrate de crear un archivo .env local con PHPSESSID en él)
COPY .env .env

# Configura la variable de entorno para que la aplicación lea las variables del .env
ENV PYTHONUNBUFFERED=1

# Ejecuta el bot
CMD ["python", "src/cli.py"]