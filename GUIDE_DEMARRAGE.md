# 🛡️ Guardian - Guide de Démarrage

## 🚀 Lancement Rapide

### Méthode Simple (Recommandée)
```bash
python3 run.py
```

### Accès à l'interface
- **Interface principale** : http://localhost:5001
- **Page de démonstration** : http://localhost:5001/demo

## 📂 Structure Organisée

Le projet est maintenant organisé pour un **code clair et facilement pris en main** :

### 🎯 Points d'Entrée
- `run.py` - Point d'entrée principal simplifié
- `scripts/` - Scripts utilitaires et de démarrage

### ⚙️ Configuration
- `config/` - Tous les fichiers de configuration
  - `api_keys.yaml` - Clés API (à configurer)
  - `api_keys_template.yaml` - Modèle de configuration
  - `requirements_interface.txt` - Dépendances Python

### 🤖 Code Source
- `guardian/` - Modules IA et logique métier
- `web/` - Interface web Flask
- `tests/` - Tests automatisés

### 📊 Ressources
- `models/` - Modèles IA (Vosk français)
- `logs/` - Journaux d'application
- `docs/` - Documentation
- `demos/` - Exemples et démonstrations

## 🔧 Configuration

1. **Copiez le modèle de configuration :**
   ```bash
   cp config/api_keys_template.yaml config/api_keys.yaml
   ```

2. **Éditez vos clés API dans `config/api_keys.yaml`**

3. **Installez les dépendances :**
   ```bash
   pip install -r config/requirements_interface.txt
   ```

## 🎤 Fonctionnalités

- ✅ **Reconnaissance vocale** (Vosk français offline)
- ✅ **Intelligence artificielle** (Gemini 2.5 Flash)
- ✅ **Géolocalisation** (OpenStreetMap)
- ✅ **Interface web interactive**
- ✅ **Alertes d'urgence** (Email/SMS)
- ✅ **Détection de chute**
- ✅ **Navigation intelligente**

## 🛠️ Développement

### Structure des Modules
```python
# Guardian IA
from guardian.gemini_agent import VertexAIAgent
from guardian.speech_agent import SpeechAgent
from guardian.emergency_response import EmergencyResponse

# Interface Web
from web.web_interface_simple import app
```

### Tests
```bash
python -m pytest tests/
```

### Logs
```bash
tail -f logs/guardian.log
```

## 📱 Interface Utilisateur

1. **Démarrage** : Cliquez sur "Permettre les notifications"
2. **Géolocalisation** : Autorisez l'accès à votre position
3. **Voice** : Cliquez sur le micro pour parler
4. **Carte** : Navigation interactive OpenStreetMap
5. **Urgence** : Bouton d'alerte rapide

---

**Note** : Le projet est maintenant structuré pour faciliter la maintenance et l'extension. Chaque dossier a un rôle spécifique et le point d'entrée `run.py` simplifie le démarrage.