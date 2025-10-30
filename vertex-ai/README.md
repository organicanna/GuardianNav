# GUARDIAN VERTEX AI - README

## 🚀 Déploiement Cloud de Guardian sur Vertex AI

Version cloud-native de Guardian optimisée pour Google Cloud Platform avec Vertex AI.

## 📋 Architecture

```
Guardian Vertex AI
├── Cloud Run (API REST)
├── Vertex AI (Modèles IA) 
├── Firestore (Base de données)
├── Cloud Storage (Fichiers)
├── Cloud Monitoring (Surveillance)
└── Cloud Logging (Logs)
```

## 🛠️ Prérequis

### Logiciels requis
```bash
# Google Cloud CLI
brew install google-cloud-sdk

# Docker Desktop
# Télécharger depuis docker.com

# Python 3.9+
python3 --version
```

### Configuration GCP
```bash
# Authentification
gcloud auth login
gcloud auth application-default login

# Configuration du projet
gcloud config set project guardian-ai-urgence
gcloud config set run/region europe-west1
```

## 🚀 Déploiement Rapide

### 1. Déploiement automatique
```bash
# Déploiement complet en une commande
./deploy.sh
```

### 2. Déploiement manuel

#### Étape 1: Activation des APIs
```bash
gcloud services enable \
    aiplatform.googleapis.com \
    cloudfunctions.googleapis.com \
    cloudrun.googleapis.com \
    cloudbuild.googleapis.com
```

#### Étape 2: Construction et déploiement
```bash
# Construction Docker
docker build -t gcr.io/guardian-ai-urgence/guardian-vertex-ai:latest .

# Push vers Container Registry  
docker push gcr.io/guardian-ai-urgence/guardian-vertex-ai:latest

# Déploiement Cloud Run
gcloud run deploy guardian-vertex-ai \
    --image gcr.io/guardian-ai-urgence/guardian-vertex-ai:latest \
    --platform managed \
    --region europe-west1 \
    --allow-unauthenticated
```

## 📡 API REST

### Endpoints disponibles

#### Health Check
```bash
GET /health
```
Response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T14:30:00Z",
  "service": "Guardian Vertex AI",
  "version": "1.0.0"
}
```

#### Analyse d'urgence
```bash
POST /emergency
Content-Type: application/json

{
  "situation": "Je suis perdu dans la forêt",
  "user_info": {
    "name": "Jean Dupont",
    "phone": "+33123456789",
    "location": "Forêt de Fontainebleau, 77300"
  }
}
```

Response:
```json
{
  "urgency_level": 6,
  "emergency_type": "navigation",
  "immediate_actions": [
    "Restez où vous êtes",
    "Activez votre GPS", 
    "Signalez votre position"
  ],
  "alert_contacts": false,
  "message": "Je vous guide pour sortir de la forêt.",
  "metadata": {
    "processing_time_ms": 245,
    "timestamp": "2024-01-15T14:30:00Z",
    "region": "europe-west1",
    "model": "gemini-vertex-ai"
  }
}
```

## 🧪 Tests

### Test local
```bash
# Démarrage local
python main.py

# Test health check
curl http://localhost:8080/health

# Test urgence
curl -X POST http://localhost:8080/emergency \
  -H 'Content-Type: application/json' \
  -d '{"situation":"Test urgence", "user_info":{"name":"Test","location":"Paris"}}'
```

### Test production
```bash
# Récupération URL du service
SERVICE_URL=$(gcloud run services describe guardian-vertex-ai \
  --region=europe-west1 --format="value(status.url)")

# Test health
curl $SERVICE_URL/health

# Test urgence  
curl -X POST $SERVICE_URL/emergency \
  -H 'Content-Type: application/json' \
  -d '{"situation":"Je suis en danger", "user_info":{"name":"Test User","location":"Lyon"}}'
```

## 📊 Monitoring

### Logs en temps réel
```bash
# Logs Cloud Run
gcloud logging read 'resource.type=cloud_run_revision AND resource.labels.service_name=guardian-vertex-ai' --limit=50

# Logs structurés
gcloud logging read 'jsonPayload.service="Guardian Vertex AI"' --format=json
```

### Métriques
- **Latence**: Temps de réponse moyen < 500ms
- **Disponibilité**: Uptime > 99.9%
- **Erreurs**: Taux d'erreur < 0.1%
- **Throughput**: Requêtes par minute

### Alertes configurées
- Latence > 1s pendant 5min
- Taux d'erreur > 1% pendant 2min  
- CPU > 80% pendant 10min
- Mémoire > 90% pendant 5min

## ⚙️ Configuration

### Variables d'environnement
```bash
GOOGLE_CLOUD_PROJECT=guardian-ai-urgence
GOOGLE_CLOUD_REGION=europe-west1
PORT=8080
```

### Configuration Vertex AI
Voir `vertex_config.yaml` pour:
- Configuration des modèles
- Paramètres d'endpoint
- Scaling automatique
- Monitoring avancé

## 🔐 Sécurité

### Authentification
- Service Account avec permissions minimales
- Tokens JWT pour API externe  
- CORS configuré pour domaines autorisés

### Rate Limiting
- 60 requêtes/minute par IP
- 1000 requêtes/heure par utilisateur
- Blocage automatique des attaques

### Chiffrement
- TLS 1.3 pour toutes les communications
- Données chiffrées au repos dans Firestore
- Logs anonymisés automatiquement

## 🔧 Maintenance

### Mise à jour
```bash
# Nouvelle version
docker build -t gcr.io/guardian-ai-urgence/guardian-vertex-ai:v1.1.0 .
docker push gcr.io/guardian-ai-urgence/guardian-vertex-ai:v1.1.0

# Déploiement zero-downtime
gcloud run deploy guardian-vertex-ai \
  --image gcr.io/guardian-ai-urgence/guardian-vertex-ai:v1.1.0
```

### Rollback
```bash
# Retour version précédente
gcloud run services replace-traffic guardian-vertex-ai \
  --to-revisions=guardian-vertex-ai-00001-abc=100
```

## 🆘 Dépannage

### Problèmes courants

#### Service ne démarre pas
```bash
# Vérifier les logs
gcloud logging read 'resource.type=cloud_run_revision' --limit=10

# Vérifier la configuration
gcloud run services describe guardian-vertex-ai --region=europe-west1
```

#### Erreur Vertex AI
```bash
# Vérifier les quotas
gcloud compute project-info describe --project=guardian-ai-urgence

# Vérifier les permissions
gcloud iam service-accounts get-iam-policy guardian@guardian-ai-urgence.iam.gserviceaccount.com
```

#### Timeout sur les requêtes
- Augmenter le timeout Cloud Run (max 3600s)
- Vérifier la taille des modèles Vertex AI
- Optimiser les prompts IA

## 📞 Support

En cas de problème critique:
1. Vérifier le status: `curl $SERVICE_URL/health`
2. Consulter les logs: `gcloud logging read`  
3. Vérifier les métriques dans Cloud Console
4. Contacter l'équipe DevOps

## 📄 Licence

Guardian Vertex AI - Version Cloud
Propriétaire: ONEPOINT