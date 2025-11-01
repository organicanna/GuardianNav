# Explication du Code - Guardian

> Guide technique détaillé de l'architecture et du fonctionnement du code Guardian

## Architecture Générale

### Principe de Fonctionnement

Guardian suit un pattern **Pipeline Event-Driven** :

```
Input Vocal → Reconnaissance → Analyse IA → Décision → Actions → Retour Utilisateur
```

### Structure des Modules

```
guardian/
├── voice_agent.py                  # Reconnaissance vocale (Vosk)
├── gemini_agent.py                 # Intelligence artificielle (Gemini)  
├── speech_agent.py                 # Synthèse vocale (Google TTS)
├── // guardian_agent.py            # Orchestrateur principal
├── / gmail_emergency_agent.py     # Gestion emails d'urgence
├── / sms_agent.py                 # Notifications SMS/WhatsApp
├── // GPS_agent.py                 # Géolocalisation et navigation
├── / emergency_response.py        # Réponses d'urgence coordonnées
├── // config.py                    # Configuration système
└── / __init__.py                  # Initialisation du package
```

---

## / Module de Reconnaissance Vocale

### `voice_agent.py`

**Rôle** : Convertir la parole en texte avec Vosk (offline)

```python
class VoiceRecognizer:
    def __init__(self, model_path="models/vosk-model-small-fr-0.22"):
        """
        Initialise Vosk avec le modèle français
        - model_path: Chemin vers le modèle Vosk français
        - sample_rate: 16000 Hz (optimisé français)
        - channels: 1 (mono)
        """
        
    def listen_once(self, timeout=10):
        """
        Écoute une phrase complète
        - timeout: Durée max d'écoute (10s par défaut)
        - return: Texte reconnu ou None si échec
        """
        
    def start_continuous_listening(self, callback):
        """
        Mode écoute continue (pour surveillance)
        - callback: Fonction appelée à chaque reconnaissance
        """
```

**Algorithme de Reconnaissance** :
1. **Initialisation** : Chargement modèle Vosk français
2. **Capture Audio** : Microphone → Buffer 16kHz mono
3. **Traitement** : Vosk analyse les chunks audio
4. **Détection Silence** : Fin de phrase → Résultat final
5. **Nettoyage** : Suppression bruit, normalisation

**Avantages Vosk** :
- / **Offline complet** (aucune donnée envoyée)
- / **Optimisé français** (accents, expressions)
- / **Temps réel** (< 500ms)
- / **Léger** (100MB vs 2GB Google)

---

## / Module Intelligence Artificielle  

### `gemini_agent.py`

**Rôle** : Analyse contextuelle avec Google Gemini 2.5 Flash

```python
class VertexAIAgent:
    def __init__(self):
        """
        Configuration Gemini optimisée Guardian
        - model: gemini-2.5-flash (le plus rapide)
        - temperature: 0.1 (réponses cohérentes)
        - max_tokens: 1000 (réponses concises)
        """
        
    def analyze_emergency_situation(self, user_input, context):
        """
        Analyse intelligente de la situation
        - user_input: Texte reconnu par Vosk
        - context: Localisation, historique, profil utilisateur
        - return: Niveau urgence (1-10) + actions recommandées
        """
```

**Prompt Engineering Guardian** :
```python
GUARDIAN_SYSTEM_PROMPT = """
Tu es GUARDIAN, assistant IA de sécurité personnelle.

MISSION: Analyser les situations d'urgence et guider l'utilisateur.

ÉVALUATION URGENCE (1-10):
- 1-3: Information/Conseil simple
- 4-6: Situation préoccupante, surveillance  
- 7-8: Urgence modérée, alerte proches
- 9-10: Danger immédiat, services d'urgence

RÉPONSE FORMAT:
**NIVEAU D'URGENCE:** X/10
**ANALYSE EXPRESS:** [Description situation]
**ACTIONS IMMÉDIATES:** [Ce que doit faire l'utilisateur] 
**OÙ ALLER:** [Lieu sécurisé le plus proche]
**APPELER:** [Numéro d'urgence approprié]
**DÉCISIONS AUTONOMES:** [Actions automatiques Guardian]

STYLE: Direct, rassurant, actionnable. Pas de bavardage.
"""
```

**Logique de Décision IA** :
1. **Classification** : Type d'urgence (médicale, sécurité, info)
2. **Contextualisation** : Heure, lieu, profil utilisateur
3. **Évaluation Risque** : Algorithme de scoring 1-10
4. **Actions Automatiques** : Si score ≥ 7 → Alerte automatique
5. **Recommandations** : Actions personnalisées selon situation

---

## // Orchestrateur Principal

### `guardian_agent.py`

**Rôle** : Chef d'orchestre coordonnant tous les modules

```python
class GuardianAgent:
    def __init__(self):
        # Initialisation tous les agents
        self.voice_agent = VoiceRecognizer()
        self.ai_agent = VertexAIAgent() 
        self.speech_agent = SpeechSynthesizer()
        self.gmail_agent = GmailEmergencyAgent()
        self.gps_agent = GPSAgent()
        
    def handle_voice_input(self, audio_data):
        """
        Pipeline principal de traitement
        """
        # 1. Reconnaissance vocale
        text = self.voice_agent.transcribe(audio_data)
        
        # 2. Enrichissement contexte
        context = self.build_context()
        
        # 3. Analyse IA
        analysis = self.ai_agent.analyze_emergency_situation(text, context)
        
        # 4. Décisions automatiques
        if analysis.urgency_level >= 7:
            self.trigger_emergency_response(analysis)
            
        # 5. Réponse utilisateur
        self.speech_agent.speak(analysis.response)
        
        return analysis
```

**Pipeline de Traitement** :
```
📥 Audio Input
    ↓
/ Vosk STT (< 500ms)
    ↓  
/ Gemini Analysis (< 2s)
    ↓
⚖/ Decision Engine
    ↓
/ Emergency Actions (si besoin)
    ↓
/ Voice Response (< 1s)
    ↓
/ Logging & Metrics
```

---

## / Système d'Alertes d'Urgence

### `gmail_emergency_agent.py`

**Rôle** : Envoi intelligent d'emails d'urgence

```python
class GmailEmergencyAgent:
    def send_emergency_alert(self, situation, location, contacts):
        """
        Génère et envoie emails d'urgence personnalisés
        - situation: Analyse IA de la situation
        - location: GPS + adresse lisible  
        - contacts: Liste contacts d'urgence
        """
```

**Template Email Dynamique** :
```html
<!-- Génération automatique -->
<h2>/ ALERTE GUARDIAN - {situation.urgency_level}/10</h2>

<div class="situation">
    <h3>Situation Rapportée</h3>
    <p>"{user_voice_input}"</p>
    <p><strong>Analyse IA:</strong> {situation.analysis}</p>
</div>

<div class="location">  
    <h3>/ Localisation Exacte</h3>
    <p>{address} - {gps_coordinates}</p>
    <a href="{google_maps_link}">/ Voir sur Google Maps</a>
</div>

<div class="actions">
    <a href="tel:{user_phone}" class="btn-call">📞 Appeler {user_name}</a>
    <a href="{whatsapp_link}" class="btn-whatsapp">/ WhatsApp Direct</a>
</div>
```

**Logique d'Envoi Intelligente** :
- **Urgence 1-6** : Pas d'envoi automatique
- **Urgence 7-8** : Envoi aux contacts famille
- **Urgence 9-10** : Envoi à tous + services d'urgence

---

## // Géolocalisation et Navigation

### `GPS_agent.py`

**Rôle** : Localisation précise et calcul d'itinéraires sécurisés

```python
class GPSAgent:
    def get_current_location(self):
        """
        Obtient la position actuelle
        - return: {lat, lng, address, accuracy}
        """
        
    def find_safe_route(self, destination, current_location):
        """
        Calcul itinéraire sécurisé avec Google Directions
        - Évitement zones dangereuses
        - Privilégier rues éclairées et fréquentées
        - Points de refuge sur le trajet
        """
        
    def find_nearby_safe_places(self, location, emergency_type):
        """
        Trouve lieux sécurisés à proximité
        - emergency_type: "medical", "security", "general"
        - return: Hôpitaux, commissariats, lieux publics
        """
```

**Algorithme de Sécurisation Routes** :
1. **Appel Google Directions** : Route optimale standard
2. **Analyse Sécurité** : Croisement base données incidents
3. **Pondération** : Éclairage + fréquentation + services
4. **Alternative** : Proposition routes plus sûres (+10% temps)
5. **Points Refuge** : Identification tous les 200m

---

## 🌐 Interface Web

### `web/web_interface_simple.py`

**Rôle** : Serveur Flask exposant les APIs REST

```python
@app.route('/api/vosk/listen', methods=['POST'])
def vosk_listen():
    """
    API reconnaissance vocale
    - Méthode: POST
    - Input: Audio stream ou commande déclenchement  
    - Output: JSON {text, confidence, timestamp}
    """

@app.route('/api/guardian/analyze', methods=['POST']) 
def analyze_situation():
    """
    API analyse IA Guardian
    - Input: {text, location, user_profile}
    - Output: {urgency_level, analysis, actions, email_sent}
    """

@app.route('/demo')
def demo_page():
    """
    Interface démo complète
    - Reconnaissance vocale temps réel
    - Visualisation carte interactive
    - Simulation scenarios d'urgence
    """
```

**Architecture Frontend** :
```javascript
// Gestion reconnaissance vocale
class VoiceRecognition {
    startListening() {
        // Appel API /api/vosk/listen
        // Affichage temps réel du texte reconnu
    }
    
    sendToGuardian(text) {
        // Envoi à /api/guardian/analyze
        // Traitement réponse IA
        // Mise à jour interface utilisateur
    }
}

// Carte interactive Leaflet
class GuardianMap {
    showUserLocation() { /* GPS + marqueur */ }
    displaySafeRoute() { /* Itinéraire sécurisé */ }  
    highlightSafePlaces() { /* Points refuge */ }
}
```

---

## / Synthèse Vocale

### `speech_agent.py`

**Rôle** : Conversion texte → parole avec Google TTS

```python
class SpeechSynthesizer:
    def speak(self, text, urgency_level=1):
        """
        Synthèse vocale adaptative selon urgence
        - urgency_level 1-3: Voix normale
        - urgency_level 4-7: Voix accélérée
        - urgency_level 8-10: Voix urgente + volume élevé
        """
```

**Paramètres Adaptatifs** :
```python
# Configuration selon urgence
VOICE_PARAMS = {
    1-3: {"rate": 1.0, "pitch": 0, "volume": 0.8},      # Normal
    4-7: {"rate": 1.2, "pitch": +2, "volume": 0.9},     # Alerte
    8-10: {"rate": 1.4, "pitch": +4, "volume": 1.0}     # Urgence
}
```

---

## / Gestion Configuration

### `config.py`

**Rôle** : Centralisation configuration et secrets

```python
class GuardianConfig:
    def __init__(self, config_path="config/api_keys.yaml"):
        self.load_config(config_path)
        self.validate_required_keys()
        
    def get_gemini_config(self):
        """Configuration optimisée Gemini Guardian"""
        return {
            "model": "gemini-2.5-flash",
            "temperature": 0.1,           # Cohérence 
            "max_output_tokens": 1000,    # Concision
            "top_p": 0.8,                # Créativité limitée
            "top_k": 40                   # Diversité contrôlée
        }
```

**Structure Configuration** :
```yaml
# Hiérarchie des paramètres
system:
  debug_mode: false
  log_level: "INFO"
  max_audio_duration: 30
  
voice_recognition:
  engine: "vosk"
  language: "fr-FR"
  confidence_threshold: 0.7
  
ai_analysis:
  provider: "google_genai"
  model: "gemini-2.5-flash"
  emergency_threshold: 7
  
notifications:
  email_enabled: true
  sms_enabled: true
  auto_send_threshold: 7
```

---

## / Tests et Validation

### Structure Tests
```
tests/
├── / test_voice_agent.py         # Tests reconnaissance vocale
├── / test_gemini_agent.py        # Tests analyse IA
├── / test_email_emergency.py     # Tests envoi emails 
├── // test_gps_agent.py           # Tests géolocalisation
├── / test_integration.py         # Tests bout en bout
└── / test_performance.py         # Tests performance
```

**Tests Critiques** :
```python
def test_emergency_pipeline():
    """Test complet pipeline d'urgence"""
    # 1. Simulation input vocal urgence niveau 9
    # 2. Vérification analyse IA correcte  
    # 3. Validation envoi email automatique
    # 4. Contrôle temps réponse < 7s
    
def test_voice_recognition_accuracy():
    """Test précision reconnaissance française"""
    # Échantillons audio phrases d'urgence
    # Vérification taux reconnaissance > 85%
```

---

## / Performance et Optimisation

### Métriques Cibles
- **Reconnaissance vocale** : < 500ms
- **Analyse IA Gemini** : < 2s  
- **Envoi email d'urgence** : < 3s
- **Pipeline complet** : < 7s

### Optimisations Implémentées
```python
# Cache intelligent réponses IA
@lru_cache(maxsize=100)
def get_cached_analysis(text_hash):
    """Cache analyses similaires"""

# Pool connexions HTTP réutilisables  
session = requests.Session()
session.mount('https://', HTTPAdapter(pool_maxsize=20))

# Traitement audio asynchrone
async def process_audio_stream():
    """Reconnaissance en parallèle de l'écoute"""
```

---

## 🔒 Sécurité et Confidentialité

### Protection Données
- / **Reconnaissance offline** (Vosk local)
- / **Aucun stockage** des conversations
- / **Chiffrement HTTPS** pour APIs
- / **Clés API isolées** dans fichiers séparés

### Validation Input
```python
def sanitize_voice_input(text):
    """
    Nettoyage sécurisé input utilisateur
    - Suppression caractères dangereux
    - Limitation longueur (500 chars)
    - Validation encoding UTF-8
    """
```

---

## 📈 Monitoring et Logs

### Système de Logs
```python
# Configuration logging structuré
logging.config = {
    "formatters": {
        "guardian": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    },
    "handlers": {
        "file": {
            "class": "RotatingFileHandler",
            "filename": "logs/guardian.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5
        }
    }
}
```

### Métriques Collectées
- **Temps de réponse** par module
- **Taux de reconnaissance** vocale  
- **Succès/échecs** APIs
- **Fréquence urgences** par niveau
- **Performance** système (CPU/RAM)

---

**Version Code** : 2025.10.31  
**Mainteneur** : Guardian Team  
**Docs Techniques** : `docs/`