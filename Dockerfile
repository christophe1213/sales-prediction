FROM python:3.11-slim

WORKDIR /app

# Installation des dépendances
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN apt-get update && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

# Copie du code de l'API et des fichiers du modèle
# (modele_prediction_ventes.pkl et encodeurs.pkl doivent être présents
# dans ce dossier avant le build - voir README.md)
COPY . .

RUN chmod +x start.sh
# Hugging Face Spaces (Docker SDK) écoute par défaut sur le port 7860
EXPOSE 7860

CMD ["./start.sh"]
