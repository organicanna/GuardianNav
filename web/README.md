# Interface Web - Guardian

Interface web moderne et épurée pour Guardian avec Flask et JavaScript.

## Structure

```
web/
├── web_interface_simple.py    # Serveur Flask principal avec Vosk
├── templates/                 # Pages HTML
│   └── demo.html            # Interface principale optimisée
└── static/                   # Assets statiques (si nécessaire)
    ├── css/                  # Styles CSS
    └── js/                   # Scripts JavaScript
```

## Utilisation

### Lancement de l'interface web
```bash
cd web/
python3 web_interface_simple.py
```
Puis ouvrir http://localhost:5001 dans votre navigateur.

## Fonctionnalités

- **Reconnaissance Vocale**: Vosk français local et fiable
- **Synthèse Vocale Contrôlable**: TTS avec boutons ON/OFF
- **Conversation Temps Réel**: Interface directe avec Guardian AI
- **Alertes Email**: Envoi automatique selon niveau d'urgence
- **Cartes Interactives**: OpenStreetMap avec Leaflet
- **Interface Épurée**: Design moderne et professionnel
- **Notifications Intelligentes**: Messages de bienvenue contrôlés

## Pages Disponibles

- `/demo` - Interface principale complète (recommandée)
- `/map` - Carte interactive standalone
- `/emergency` - Interface d'urgence

## Configuration

Le serveur utilise automatiquement :
- **Port**: 5001 (ou port libre suivant)
- **Host**: 0.0.0.0 (accessible sur réseau local)
- **Config**: `../api_keys.yaml` (depuis racine du projet)
- **Modèle Vosk**: `../vosk-model-small-fr-0.22/`

## API Endpoints

### Guardian AI
- `POST /api/guardian/analyze` - Analyse situation avec IA
- `GET /api/vosk/status` - Status reconnaissance vocale
- `POST /api/vosk/listen` - Démarrer écoute Vosk

### Système
- `GET /health` - Vérification santé du serveur
- `GET /debug` - Informations de debug

## Dépannage

**Erreur de chemins**: Les chemins sont configurés automatiquement depuis le dossier web vers la racine du projet.

**Vosk non trouvé**: Le modèle doit être dans `../vosk-model-small-fr-0.22/` relatif au dossier web.

**Configuration manquante**: Le fichier `../api_keys.yaml` doit exister à la racine du projet.

---

**Note**: Cette interface web a été optimisée pour une expérience utilisateur fluide avec un code professionnel et épuré.