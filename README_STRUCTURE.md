# 🛡️ Guardian - Structure du Projet

## 📂 Organisation des Dossiers

```
GuardianNav/
├── run.py                     # 🚀 Point d'entrée principal
├── README.md                  # Documentation principale
├── README_STRUCTURE.md        # Ce fichier - Structure du projet
├── LICENSE                    # Licence du projet
│
├── config/                    # ⚙️ Configuration
│   └── requirements_interface.txt   # Dépendances Python
│
├── scripts/                   # 📜 Scripts utilitaires
│   ├── demo_live_agent.py          # Démo agent en direct
│   ├── guardian_web.py             # Script web Guardian
│   ├── setup_local.sh              # Configuration locale
│   ├── start_guardian.sh           # Démarrage Guardian
│   ├── start_guardian_demo.sh      # Démarrage démo
│   └── start_guardian_web.sh       # Démarrage web
│
├── guardian/                  # 🤖 Modules IA Guardian
│   ├── __init__.py
│   ├── config.py                   # Configuration générale
│   ├── gemini_agent.py             # Agent Gemini AI
│   ├── guardian_agent.py           # Agent principal
│   ├── speech_agent.py             # Reconnaissance vocale
│   ├── voice_agent.py              # Synthèse vocale
│   ├── emergency_response.py       # Réponse d'urgence
│   ├── fall_detector.py            # Détection de chute
│   ├── GPS_agent.py                # Géolocalisation
│   └── ...                         # Autres modules
│
├── web/                       # 🌐 Interface Web
│   ├── web_interface_simple.py     # Serveur Flask
│   ├── templates/                  # Templates HTML
│   │   └── demo.html              # Page de démonstration
│   └── static/                     # Ressources statiques
│       ├── css/                    # Feuilles de style
│       └── js/                     # JavaScript
│
├── tests/                     # 🧪 Tests
│   ├── __init__.py
│   ├── test_speech_agent.py        # Tests reconnaissance vocale
│   ├── test_fall_detector.py       # Tests détection chute
│   └── ...                         # Autres tests
│
├── models/                    # 🎯 Modèles IA
│   └── vosk-model-small-fr-0.22/   # Modèle vocal français
│
├── logs/                      # 📝 Journaux
│   └── guardian.log                # Logs de l'application
│
├── docs/                      # 📚 Documentation
│
├── demos/                     # 🎨 Démonstrations
│
└── vertex-ai/                 # ☁️ Intégration Google Cloud
    └── ...                         # Modules Vertex AI
```

## 🚀 Utilisation

### Démarrage Simple
```bash
python run.py
```

### Démarrage avec Scripts
```bash
# Depuis le dossier scripts/
./scripts/start_guardian_web.sh
```

## 🔧 Configuration

1. **Configuration principale** : `config/requirements_interface.txt`
2. **Clés API** : À configurer dans `config/api_keys.yaml` (à créer)
3. **Modèles** : Vosk français dans `models/`

## 📦 Installation

```bash
# Installer les dépendances
pip install -r config/requirements_interface.txt

# Lancer l'application
python run.py
```

## 🎯 Points d'Entrée

- **Interface Web** : `http://localhost:5001`
- **Démo Interactive** : `http://localhost:5001/demo`
- **API Guardian** : Modules dans `guardian/`

## 📋 Fonctionnalités

- 🎤 **Reconnaissance vocale** (Vosk français)
- 🤖 **Intelligence artificielle** (Gemini 2.5 Flash)
- 📍 **Géolocalisation** (OpenStreetMap)
- 🚨 **Alertes d'urgence** (Email, SMS)
- 🏃 **Détection de chute**
- 🗺️ **Navigation intelligente**

---

*Structure organisée pour un code clair et facilement pris en main*