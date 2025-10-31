# 🛡️ Guardian - Architecture du Système

## 📋 Vue d'ensemble

Guardian est un système d'assistance de sécurité personnelle utilisant l'IA pour analyser les situations d'urgence et fournir des conseils en temps réel.

## 🏗️ Structure du Projet

```
GuardianNav/
├── 📁 config/           # Configuration et clés API
│   ├── api_keys.yaml    # Clés d'API (Google, Gmail, etc.)
│   └── settings.yaml    # Paramètres système
├── 📁 guardian/         # Modules IA et agents
│   ├── gemini_agent.py       # Agent Gemini AI (analyse)
│   ├── gmail_emergency_agent.py # Envoi d'emails d'urgence
│   ├── speech_agent.py       # Reconnaissance vocale
│   └── voice_conversation_agent.py # Conversation vocale
├── 📁 web/              # Interface web
│   ├── templates/       
│   │   ├── demo.html    # Page démonstration interactive
│   │   ├── home.html    # Page d'accueil
│   │   └── map.html     # Carte de navigation
│   └── web_interface_simple.py # Serveur Flask
├── 📁 models/           # Modèles ML et données
│   └── vosk-model-small-fr-0.22/ # Modèle Vosk français
├── 📁 scripts/          # Scripts utilitaires
├── 📁 tests/            # Tests unitaires
├── 📁 demos/            # Fichiers de démonstration
├── 📁 docs/             # Documentation technique
├── 📁 logs/             # Fichiers de logs
└── run.py               # Point d'entrée principal
```

## 🔧 Technologies Utilisées

### Backend
- **Python 3.9+** - Langage principal
- **Flask** - Serveur web et API REST
- **Google Gemini 2.5 Flash** - Intelligence artificielle
- **Vosk** - Reconnaissance vocale locale (français)
- **Gmail API** - Envoi d'emails d'urgence
- **Google Maps API** - Calcul d'itinéraires sécurisés

### Frontend
- **HTML5/CSS3** - Interface utilisateur
- **JavaScript ES6** - Logique côté client
- **Leaflet.js** - Cartographie interactive
- **Web Speech API** - Synthèse vocale

### Données et Stockage
- **YAML** - Configuration
- **SessionStorage** - Persistance côté client
- **Logs rotatifs** - Traçabilité système

## 🚀 Fonctionnalités Principales

### 1. 🎤 Reconnaissance Vocale
- Détection automatique de situations d'urgence
- Support du français avec modèle Vosk local
- Traitement en temps réel

### 2. 🤖 Analyse IA Guardian
- Évaluation du niveau d'urgence (1-10)
- Recommandations contextuelles
- Prise de décisions autonomes

### 3. 📧 Alertes d'Urgence
- Envoi automatique d'emails aux contacts
- Géolocalisation incluse
- Templates personnalisables

### 4. 🗺️ Navigation Sécurisée
- Calcul d'itinéraires optimaux
- Évitement des zones dangereuses
- Visualisation temps réel

## 🎨 Design System

### Couleurs Officielles Google
- **Bleu** #4285F4 - Actions principales
- **Rouge** #EA4335 - Urgences
- **Vert** #34A853 - Confirmations
- **Jaune** #FBBC05 - Avertissements

### Typographie
- **Police principale** : Roboto
- **Fallback** : System fonts (-apple-system, BlinkMacSystemFont)

## 🔒 Sécurité

### Protection des Données
- Clés API chiffrées et sécurisées
- Aucune donnée utilisateur stockée
- Communication HTTPS obligatoire

### Confidentialité
- Reconnaissance vocale locale (offline)
- Traitement IA via API sécurisées
- Logs anonymisés

## 📱 Déploiement

### Développement Local
```bash
python3 run.py
# Serveur : http://localhost:5010
```

### Production
- Configuration WSGI recommandée
- Variables d'environnement pour les clés API
- Reverse proxy (Nginx) conseillé

## 🧪 Tests

```bash
# Tests unitaires
python -m pytest tests/

# Tests d'intégration
python scripts/test_integration.py
```

## 📊 Monitoring

- Logs centralisés dans `/logs/`
- Métriques de performance temps réel
- Alertes système automatiques

## 🔮 Évolutions Futures

### Phase 2
- [ ] Support multilingue
- [ ] Application mobile native
- [ ] Intégration WhatsApp/SMS

### Phase 3
- [ ] IA embarquée (edge computing)
- [ ] Analyse vidéo temps réel
- [ ] Réseau Guardian communautaire

---

**Version** : 2025.10.31  
**Maintenu par** : Équipe Guardian  
**Licence** : MIT