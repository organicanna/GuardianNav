# Guardian - Architecture du Système

## Vue d'ensemble

Guardian est un assistant de sécurité personnelle utilisant l'IA pour analyser les situations d'urgence et fournir une assistance en temps réel. Version actuelle : **v3.1** (Code 100% professionnel).

## 🏗️ Structure du Projet

```
GuardianNav/
├── guardian/                    # Modules IA et agents
│   ├── gemini_agent.py         # Agent Gemini AI (analyse d'urgence)
│   ├── gmail_emergency_agent.py # Envoi d'emails d'urgence
│   ├── intelligent_advisor.py  # Système de conseils intelligents
│   ├── speech_agent.py         # Reconnaissance vocale
│   ├── voice_agent.py          # Interface vocale
│   ├── voice_conversation_agent.py # Conversation vocale
│   ├── guardian_agent.py       # Agent principal Guardian
│   ├── GPS_agent.py           # Services géolocalisation
│   ├── sms_agent.py           # Notifications SMS
│   ├── emergency_email_generator.py # Génération emails
│   ├── emergency_locations.py  # Localisation d'urgence
│   ├── emergency_response.py   # Réponse aux urgences
│   ├── fall_detector.py        # Détection de chute
│   ├── google_apis_service.py  # Services Google APIs
│   ├── what3words_service.py   # Localisation What3Words
│   └── config.py              # Configuration système
├── web/                        # Interface web et serveur
│   ├── templates/             # Templates HTML
│   │   ├── demo.html          # Interface principale
│   │   ├── conversation.html   # Interface conversation
│   │   ├── debug.html         # Page de debug
│   │   ├── emergency.html     # Interface urgence
│   │   ├── guardian_agent.html # Agent Guardian
│   │   ├── guardian_setup.html # Configuration
│   │   ├── home.html          # Page d'accueil
│   │   ├── map.html           # Interface cartes
│   │   └── voice_test.html    # Tests vocaux
│   ├── web_interface_simple.py # Serveur Flask principal
│   ├── start_web_server.py    # Démarrage serveur
│   └── guardian_web_test.py   # Tests interface web
├── docs/                       # Documentation technique
│   ├── ARCHITECTURE.md        # Architecture système (ce fichier)
│   ├── CODE_EXPLANATION.md    # Explications techniques détaillées
│   ├── DEPLOYMENT.md          # Guide d'installation
│   ├── CLEANUP_REPORT.md      # Rapport de nettoyage
│   ├── INDEX.md               # Index de la documentation
│   ├── INTERNATIONAL_EXPANSION.md # Plan d'expansion mondiale
│   └── UPDATE_SUMMARY.md      # Résumé des mises à jour
├── tests/                      # Tests unitaires et d'intégration
├── scripts/                    # Scripts utilitaires  
├── models/                     # Modèles de reconnaissance vocale
│   └── vosk-model-small-fr-0.22/ # Modèle Vosk français local
├── config/                     # Configuration et clés API (non versionné)
├── run.py                     # Point d'entrée principal
├── requirements.txt           # Dépendances Python
├── .gitignore                # Fichiers ignorés Git
└── LICENSE                   # Licence MIT
```

## 🔧 Technologies Utilisées

### Intelligence Artificielle
- **Google Gemini 2.5 Flash** - Analyse contextuelle d'urgence
- **Vosk (français)** - Reconnaissance vocale locale offline
- **Google TTS** - Synthèse vocale (via Web Speech API)

### Backend
- **Python 3.9+** - Langage principal
- **Flask** - Serveur web et APIs REST
- **SocketIO** - Communication temps réel
- **Gmail API** - Envoi d'emails d'urgence enrichis
- **Google Maps API** - Géolocalisation et itinéraires
- **What3Words API** - Localisation précise

### Frontend  
- **HTML5/CSS3** - Interface utilisateur responsive
- **JavaScript ES6** - Logique côté client
- **Leaflet.js** - Cartographie interactive
- **Web Speech API** - Synthèse vocale navigateur
- **WebRTC** - Capture audio temps réel

### Infrastructure
- **YAML** - Configuration système
- **JSON** - Échange de données APIs
- **Logging rotatif** - Traçabilité professionnelle
- **Git** - Versioning et déploiement

## 🚀 Fonctionnalités Principales

### 1. Reconnaissance Vocale Intelligente
- **Vosk local français** : Traitement offline, rapide et privé
- **Détection contextuelle** : Analyse automatique des situations d'urgence
- **Commandes naturelles** : Interface vocale intuitive
- **Temps réel** : Réponse < 7 secondes bout en bout

### 2. Analyse IA Guardian
- **Gemini 2.5 Flash** : Évaluation intelligente des urgences
- **Scoring automatique** : Niveau d'urgence de 1 à 10
- **Décisions autonomes** : Alertes automatiques si urgence ≥ 7/10
- **Conseils personnalisés** : Recommandations contextuelles

### 3. Système d'Alertes Complet
- **Emails d'urgence enrichis** : Avec géolocalisation et cartes
- **SMS automatiques** : Via Twilio pour contacts prioritaires
- **WhatsApp intégré** : Liens directs de communication
- **Escalade intelligente** : Selon la gravité détectée

### 4. Géolocalisation et Navigation
- **GPS précis** : Localisation temps réel
- **What3Words** : Adresses précises au mètre près
- **Itinéraires sécurisés** : Évitement zones dangereuses
- **Points d'intérêt d'urgence** : Hôpitaux, commissariats, refuges

### 5. Interface Web Professionnelle
- **Design épuré** : Interface moderne sans emojis
- **TTS contrôlable** : Synthèse vocale ON/OFF
- **Multi-templates** : Pages spécialisées (urgence, conversation, debug)
- **Responsive** : Adaptation mobile et desktop

## 🎨 Design System

### Palette de Couleurs
- **Bleu principal** #4285F4 - Actions et navigation
- **Rouge urgence** #EA4335 - Alertes critiques
- **Vert validation** #34A853 - Confirmations et succès
- **Orange attention** #FBBC05 - Avertissements
- **Gris interface** #5f6368 - Textes secondaires

### Typographie
- **Police principale** : Roboto, -apple-system, BlinkMacSystemFont
- **Tailles** : 14px (texte), 16px (labels), 20px (titres)
- **Poids** : 400 (normal), 500 (medium), 600 (semi-bold)

### Composants UI
- **Boutons** : Coins arrondis 8px, ombre subtile
- **Messages** : Indicateurs textuels (OK, INFO, ERROR, WARN)
- **Cartes** : Ombre douce, bordure #e8eaed
- **Animations** : Transitions 0.3s ease-in-out

## 🔒 Sécurité et Confidentialité

### Protection des Données
- **Clés API sécurisées** : Stockage dans config/ non versionné
- **Traitement local** : Vosk offline, pas de données vocales envoyées
- **HTTPS obligatoire** : Communications chiffrées
- **Pas de stockage utilisateur** : Données temporaires uniquement

### Confidentialité  
- **Reconnaissance locale** : Vosk traite l'audio sur l'appareil
- **APIs sécurisées** : Communication chiffrée avec Google services
- **Logs anonymisés** : Aucune donnée personnelle dans les logs
- **RGPD compliant** : Minimisation et transparence des données

### Authentification
- **Clés API individuelles** : Une configuration par installation
- **Tokens temporaires** : Sessions courtes pour les APIs
- **Validation serveur** : Vérification des requêtes côté Flask

## 📱 Déploiement

### Développement Local
```bash
# Installation des dépendances
pip install -r requirements.txt

# Configuration des clés API
cp config/api_keys_template.yaml config/api_keys.yaml
# Éditer config/api_keys.yaml avec vos clés

# Démarrage du serveur
python3 run.py
# Interface : http://localhost:5001
```

### Production
- **WSGI** : Gunicorn ou uWSGI recommandé
- **Variables d'environnement** : Clés API sécurisées
- **Reverse proxy** : Nginx pour HTTPS et load balancing
- **Monitoring** : Logs centralisés et alertes système

### Docker (Optionnel)
```bash
# Build image
docker build -t guardian .

# Run container
docker run -p 5001:5001 -v ./config:/app/config guardian
```

## 🧪 Tests et Qualité

### Tests Disponibles
```bash
# Tests unitaires complets
python -m pytest tests/ -v

# Tests spécifiques
python tests/test_gemini_simple.py          # IA Gemini
python tests/test_voice_agent.py            # Reconnaissance vocale  
python tests/test_speech_agent.py           # Synthèse vocale
python tests/test_guardian_fall_response.py # Détection chute
```

### Outils de Développement
```bash
# Nettoyage automatique du code
python scripts/clean_orphans.py

# Vérification des dépendances  
python scripts/test_dependencies.py

# Tests d'intégration web
python web/guardian_web_test.py
```

## 📊 Monitoring et Logs

### Système de Logs
- **Logs rotatifs** : Automatique par taille et date
- **Niveaux** : DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Format professionnel** : Sans emojis, messages techniques
- **Localisation** : Logs système centralisés

### Métriques Clés
- **Temps de réponse IA** : < 7s objectif
- **Précision Vosk** : Taux de reconnaissance vocale
- **Disponibilité APIs** : Google services uptime
- **Alertes envoyées** : Volume et succès des notifications



## � Ambition Future

### Intégration Plateformes de Mobilité
Guardian vise à s'intégrer aux principales plateformes de transport pour offrir une protection continue durant les déplacements :
- **Uber/Lyft** - Activation automatique Guardian en course
- **RATP/Transports publics** - Protection dans les transports en commun
- **Applications de navigation** - Intégration aux GPS pour alertes proactives
- **Plateformes de covoiturage** - Sécurité renforcée pour trajets partagés

## �📋 Architecture Technique Détaillée

Pour plus d'informations techniques approfondies :
- **[CODE_EXPLANATION.md](CODE_EXPLANATION.md)** - Détails de l'implémentation
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Guide d'installation complet

---

**Version actuelle** : Guardian v3.1 (Novembre 2025)  
**Maintenu par** : Équipe Guardian  
**Licence** : MIT  
**Repository** : https://github.com/organicanna/GuardianNav