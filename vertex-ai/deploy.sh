#!/bin/bash

# GUARDIAN VERTEX AI - Script de déploiement
# Déploie Guardian sur Google Cloud Platform avec Vertex AI

set -e  # Exit on any error

# Configuration
PROJECT_ID="guardian-ai-urgence"
REGION="europe-west1"
SERVICE_NAME="guardian-vertex-ai"

echo "🚀 DÉPLOIEMENT GUARDIAN VERTEX AI"
echo "=================================="

# Vérification des prérequis
echo "🔍 Vérification des prérequis..."

if ! command -v gcloud &> /dev/null; then
    echo "❌ Google Cloud CLI non installé"
    echo "Installez avec: brew install google-cloud-sdk"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo "❌ Docker non installé"
    echo "Installez Docker Desktop"
    exit 1
fi

echo "✅ Prérequis validés"

# Configuration du projet
echo "🔧 Configuration du projet GCP..."
gcloud config set project $PROJECT_ID
gcloud config set run/region $REGION

# Authentification
echo "🔑 Vérification de l'authentification..."
gcloud auth application-default login --quiet || true

# Activation des APIs nécessaires
echo "⚡ Activation des APIs Google Cloud..."
gcloud services enable \
    aiplatform.googleapis.com \
    cloudfunctions.googleapis.com \
    cloudrun.googleapis.com \
    cloudbuild.googleapis.com \
    storage-api.googleapis.com \
    monitoring.googleapis.com \
    logging.googleapis.com \
    firestore.googleapis.com \
    --project=$PROJECT_ID

# Création du bucket de stockage
echo "🗄️  Création du bucket de stockage..."
BUCKET_NAME="${PROJECT_ID}-guardian-storage"
gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://$BUCKET_NAME/ || echo "Bucket déjà existant"

# Construction de l'image Docker
echo "🐳 Construction de l'image Docker..."
docker build -t gcr.io/$PROJECT_ID/$SERVICE_NAME:latest .

# Push de l'image vers Container Registry
echo "📤 Push vers Container Registry..."
docker push gcr.io/$PROJECT_ID/$SERVICE_NAME:latest

# Déploiement sur Cloud Run
echo "☁️  Déploiement sur Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image gcr.io/$PROJECT_ID/$SERVICE_NAME:latest \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --set-env-vars GOOGLE_CLOUD_PROJECT=$PROJECT_ID,GOOGLE_CLOUD_REGION=$REGION \
    --memory 512Mi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 10 \
    --timeout 300 \
    --project $PROJECT_ID

# Configuration Vertex AI
echo "🤖 Configuration Vertex AI..."
python3 << EOF
import os
from google.cloud import aiplatform

# Initialisation
aiplatform.init(project='$PROJECT_ID', location='$REGION')

# Création de l'endpoint (si non existant)
try:
    endpoint = aiplatform.Endpoint.list(
        filter='display_name="guardian-gemini-endpoint"'
    )
    if endpoint:
        print("✅ Endpoint Vertex AI déjà configuré")
    else:
        print("🔧 Création de l'endpoint Vertex AI...")
        endpoint = aiplatform.Endpoint.create(
            display_name="guardian-gemini-endpoint",
            project='$PROJECT_ID',
            location='$REGION'
        )
        print(f"✅ Endpoint créé: {endpoint.resource_name}")
except Exception as e:
    print(f"⚠️  Configuration Vertex AI: {e}")
EOF

# Configuration Firestore
echo "🔥 Configuration Firestore..."
gcloud firestore databases create \
    --location=$REGION \
    --project=$PROJECT_ID \
    --type=firestore-native || echo "Base Firestore déjà existante"

# Test de déploiement
echo "🧪 Test du déploiement..."
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")

curl -s "$SERVICE_URL/health" | python3 -m json.tool || echo "⚠️  Service pas encore prêt"

echo ""
echo "🎉 DÉPLOIEMENT TERMINÉ!"
echo "======================"
echo "Service URL: $SERVICE_URL"
echo "Health Check: $SERVICE_URL/health"
echo "Emergency API: $SERVICE_URL/emergency"
echo ""
echo "📖 Test avec:"
echo "curl -X POST $SERVICE_URL/emergency \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"situation\":\"Je suis perdu\", \"user_info\":{\"name\":\"Test\", \"location\":\"Paris\"}}'"
echo ""
echo "🔍 Monitoring:"
echo "- Logs: gcloud logging read 'resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME'"
echo "- Metrics: Console Cloud > Cloud Run > $SERVICE_NAME"
echo ""