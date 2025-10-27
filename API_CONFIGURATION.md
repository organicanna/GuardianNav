# Configuration APIs GuardianNav - Version Optimisée

Ce guide décrit la configuration des APIs **réellement utilisées** par GuardianNav après nettoyage complet.

## 🎯 APIs UTILISÉES (Liste Minimale)

### Google Cloud Platform APIs

#### 1. **Vertex AI Gemini** (Intelligence Artificielle Avancée)
- **Utilisation**: `guardian/vertex_ai_agent.py`
- **Fonction**: Analyse intelligente des situations d'urgence
- **Configuration**: Dans `google_cloud.vertex_ai`
- **Région recommandée**: `europe-west1`

#### 2. **Google Cloud Text-to-Speech** (Synthèse Vocale)
- **Utilisation**: `guardian/speech_agent.py`
- **Fonction**: Réponses vocales d'urgence
- **Configuration**: Dans `google_cloud.services.text_to_speech_api_key`
- **Coût**: ~4$ par million de caractères

#### 3. **Google Maps Platform** (Cartes et Géolocalisation)
- **Utilisation**: `demo_live_alerte_paris.py`, `guardian/emergency_email_generator.py`
- **Fonction**: Recherche de lieux d'urgence, génération de cartes
- **Configuration**: Dans `google_cloud.services.maps_api_key`

### APIs de Localisation

#### 4. **What3Words API** (Adresses Précises)
- **Utilisation**: `guardian/emergency_email_generator.py`
- **Fonction**: Localisation précise pour les équipes de secours
- **Configuration**: Dans `location_apis.what3words_api_key`

## 📋 Configuration Complète

### Fichier `api_keys.yaml`

```yaml
# Configuration Google Cloud APIs - SEULEMENT LES APIs UTILISÉES
google_cloud:
  project_id: "your-google-cloud-project-id"
  
  # Vertex AI Configuration (utilisé par vertex_ai_agent.py)
  vertex_ai:
    enabled: true
    region: "europe-west1"
    service_account_path: "path/to/service-account.json"  # Optionnel
  
  # Clés pour les services Google Cloud Platform UTILISÉS
  services:
    # Google Maps Platform APIs
    maps_api_key: "YOUR_MAPS_API_KEY_HERE"
    
    # Google Cloud Text-to-Speech API
    text_to_speech_api_key: "YOUR_TTS_API_KEY_HERE"

# APIs de localisation UTILISÉES
location_apis:
  # What3Words
  what3words_api_key: "YOUR_WHAT3WORDS_API_KEY_HERE"

# Contacts d'urgence
emergency_contacts:
  - name: "Contact Famille"
    phone: "+33123456789"
    email: "famille@example.com"

# Configuration email
email:
  enabled: false
  smtp_server: "smtp.gmail.com"
  smtp_port: 587
  from_email: "your-email@gmail.com"
  password: "your-app-password"
```

## 🚀 Instructions d'Installation

### 1. Activation Google Cloud APIs

```bash
# Activer les APIs nécessaires
gcloud services enable aiplatform.googleapis.com
gcloud services enable texttospeech.googleapis.com
gcloud services enable maps-backend.googleapis.com
gcloud services enable places-backend.googleapis.com
```

### 2. Obtenir les Clés API

#### **Google Cloud Console**: [console.cloud.google.com](https://console.cloud.google.com)

1. **Vertex AI**: Pas de clé requise (utilise l'auth par défaut)
2. **Text-to-Speech**: API & Services > Credentials > Create API Key
3. **Maps Platform**: API & Services > Credentials > Create API Key

#### **What3Words**: [developer.what3words.com](https://developer.what3words.com)
- Inscription gratuite + plan freemium

### 3. Configuration Sécurisée

```bash
# 1. Copier le template
cp api_keys_template.yaml api_keys.yaml

# 2. Éditer avec vos vraies clés
nano api_keys.yaml

# 3. Vérifier la configuration
python tests/test_api_config.py
```

## 📊 Coûts Estimés

| API | Usage typique | Coût mensuel |
|-----|---------------|--------------|
| **Vertex AI Gemini** | 1000 analyses | ~15-20€ |
| **Text-to-Speech** | 10k mots/jour | ~8-12€ |
| **Maps Platform** | 5k requêtes | ~10-15€ |
| **What3Words** | < 1000 req | Gratuit |
| **TOTAL** | Usage normal | **~35-50€/mois** |

## 🔒 Sécurité

- ✅ `api_keys.yaml` dans `.gitignore`
- ✅ Aucune clé dans le code source
- ✅ Authentication Google via service accounts
- ✅ Scope minimal des permissions

## 🧪 Tests et Validation

```bash
# Test de configuration
python tests/test_api_config.py

# Test système hybride
python tests/test_hybrid_approach.py

# Démo complète
python demo_live_alerte_paris.py
```

## ⚡ Mode Simulation

Le système fonctionne **sans APIs configurées** :
- Vertex AI → Simple IA de fallback
- Text-to-Speech → Simulation vocale
- Maps → Données statiques
- What3Words → Adresses simulées

## 📞 Support

- **Google Cloud Support**: [cloud.google.com/support](https://cloud.google.com/support)
- **What3Words Support**: [developer.what3words.com/support](https://developer.what3words.com/support)
- **Vertex AI Documentation**: [cloud.google.com/vertex-ai](https://cloud.google.com/vertex-ai)

---

🎯 **Configuration optimisée pour un coût maîtrisé et une sécurité maximale**