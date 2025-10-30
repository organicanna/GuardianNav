# 🌐 Web Interface - Guardian

Interface web moderne pour Guardian avec Flask et JavaScript.

## 📁 Structure

```
web/
├── 🚀 start_web_server.py      # Lanceur du serveur web
├── 🌐 web_interface_simple.py  # Serveur Flask principal
├── 📄 templates/              # Pages HTML
│   ├── home.html             # Page d'accueil avec formulaire
│   ├── demo.html             # Interface principale (carte + conversation)
│   ├── conversation.html     # Page conversation seule
│   ├── debug.html            # Page de debug
│   ├── voice_test.html       # Test de reconnaissance vocale
│   ├── map.html              # Carte interactive
│   ├── emergency.html        # Interface d'urgence
│   ├── guardian_agent.html   # Configuration Guardian
│   └── guardian_setup.html   # Setup initial
└── 📦 static/                # Assets statiques
    ├── css/                  # Styles CSS
    └── js/                   # Scripts JavaScript
```

## 🚀 Utilisation

### Lancement direct
```bash
cd web/
python3 start_web_server.py
```

### Lancement depuis la racine
```bash
python3 guardian_web.py
```

## 🔧 Fonctionnalités

- **🎤 Reconnaissance Vocale**: Vosk local + Web Speech API fallback
- **💬 Conversation Temps Réel**: WebSocket avec Guardian AI
- **📧 Alertes Email**: Envoi automatique selon niveau d'urgence
- **🗺️ Cartes Interactives**: OpenStreetMap avec Leaflet
- **📱 Responsive Design**: Compatible mobile et desktop
- **🎨 Interface Moderne**: Google Material Design

## 🌍 Pages Disponibles

- `/` - Page d'accueil avec formulaire utilisateur
- `/demo` - Interface principale (recommandée)
- `/conversation` - Conversation seule
- `/map` - Carte interactive
- `/emergency` - Interface d'urgence
- `/debug` - Outils de debug
- `/voice-test` - Test reconnaissance vocale

## 🔧 Configuration

Le serveur utilise automatiquement :
- **Port**: 5001 (ou port libre suivant)
- **Host**: 0.0.0.0 (accessible sur réseau local)
- **Config**: `../api_keys.yaml` (depuis racine du projet)
- **Modèle Vosk**: `../vosk-model-small-fr-0.22/`

## 📡 API Endpoints

### Guardian AI
- `POST /api/guardian/analyze` - Analyse situation avec IA
- `GET /api/vosk/status` - Status reconnaissance vocale
- `POST /api/vosk/listen` - Démarrer écoute Vosk

### Système
- `GET /health` - Vérification santé du serveur
- `GET /debug` - Informations de debug

## 🔧 Dépannage

**Erreur de chemins**: Les chemins sont configurés automatiquement depuis le dossier web vers la racine du projet.

**Vosk non trouvé**: Le modèle doit être dans `../vosk-model-small-fr-0.22/` relatif au dossier web.

**Configuration manquante**: Le fichier `../api_keys.yaml` doit exister à la racine du projet.

---

💡 **Conseil**: Pour une utilisation normale, utilisez `python3 guardian_web.py` depuis la racine du projet.