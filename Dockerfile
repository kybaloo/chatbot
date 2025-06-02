
FROM python:3.12.1

WORKDIR /code

# Copier les fichiers nécessaires au projet
COPY ./requirements.txt /code/requirements.txt
COPY ./src /code/src
COPY ./.env /code/.env

# Installation des dépendances
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --upgrade -r /code/requirements.txt && \
    pip install uvicorn

# Installation des outils AWS CLI pour DynamoDB
RUN apt-get update && \
    apt-get install -y curl unzip && \
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install && \
    rm -rf awscliv2.zip ./aws && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Port pour FastAPI
EXPOSE 80

# Port supplémentaire pour le bot Telegram (si nécessaire)
EXPOSE 8000

# Healthcheck pour vérifier que le service est en cours d'exécution
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:80/ || exit 1

# Configuration pour reprendre automatiquement après un crash
ENV PYTHONUNBUFFERED=1

# Commande de démarrage
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "80"]