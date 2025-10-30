# Utiliser une image Python officielle comme base
FROM python:3.9-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de requirements
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY . .

# Exposer le port
EXPOSE 8080

# Variables d'environnement
ENV PORT=8080
ENV PYTHONPATH=/app

# Commande de démarrage
CMD ["python", "main.py"]