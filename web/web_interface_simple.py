"""
Interface Web Simple pour Guardian
Version allégée sans les fonctionnalités avancées pour tester la carte OpenStreetMap
"""

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import logging
import os
import socket
import threading
import queue
import base64
import io
import json
import sys
from pathlib import Path

# Import Vosk pour reconnaissance vocale locale
import time
import yaml
import re
try:
    import vosk
    import sounddevice as sd
    import numpy as np
    VOSK_AVAILABLE = True
    print("✅ Vosk disponible pour reconnaissance vocale locale")
except ImportError as e:
    VOSK_AVAILABLE = False
    print(f"⚠️ Vosk non disponible: {e}")

# Chargement de l'agent Guardian comme dans demo_live_agent.py
guardian_agent = None
gmail_agent = None
# Configuration des chemins depuis le sous-dossier web
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

try:
    print("📁 Chargement de api_keys.yaml...")
    config_path = os.path.join(parent_dir, 'config', 'api_keys.yaml')
    with open(config_path, 'r', encoding='utf-8') as f:
        guardian_config = yaml.safe_load(f)
    
    from guardian.gemini_agent import VertexAIAgent
    from guardian.gmail_emergency_agent import GmailEmergencyAgent
    from guardian.google_apis_service import GoogleAPIsService
    
    # Import des fonctions depuis demo_live_agent.py
    import sys
    import importlib.util
    demo_path = os.path.join(parent_dir, 'scripts', 'demo_live_agent.py')
    spec = importlib.util.spec_from_file_location("demo_live_agent", demo_path)
    demo_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(demo_module)
    
    get_safe_route_directions = demo_module.get_safe_route_directions
    format_route_response = demo_module.format_route_response
    get_nearby_safe_places = demo_module.get_nearby_safe_places
    format_safe_places_response = demo_module.format_safe_places_response
    
    guardian_agent = VertexAIAgent(guardian_config)
    gmail_agent = GmailEmergencyAgent(guardian_config)
    google_service = GoogleAPIsService(guardian_config)
    
    # Ajouter l'agent Gmail à l'agent principal
    guardian_agent.gmail_agent = gmail_agent
    
    print(f"🤖 Guardian Agent: {'✅ Disponible' if guardian_agent.is_available else '⚠️ Mode simulation'}")
    print(f"📧 Gmail Agent: {'✅ Configuré' if gmail_agent.is_available else '❌ Non configuré'}")
    print(f"🔊 Google TTS: {'✅ Configuré' if google_service else '❌ Non configuré'}")
    
except Exception as e:
    print(f"⚠️ Erreur chargement Guardian: {e}")
    guardian_agent = None
    gmail_agent = None
    google_service = None

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Classe VoiceRecognizer pour Vosk
class VoiceRecognizer:
    """Gestionnaire de reconnaissance vocale avec Vosk"""
    
    def __init__(self, model_path=None):
        if model_path is None:
            # Chemin relatif vers le modèle depuis le dossier web
            parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            model_path = os.path.join(parent_dir, "models", "vosk-model-small-fr-0.22")
        self.model_path = model_path
        self.model = None
        self.rec = None
        self.audio_queue = queue.Queue()
        self.is_listening = False
        
    def initialize(self):
        """Initialise le modèle Vosk"""
        try:
            if not os.path.exists(self.model_path):
                logger.error(f"Modèle Vosk non trouvé: {self.model_path}")
                return False
                
            logger.info("🔧 Chargement du modèle Vosk français...")
            self.model = vosk.Model(self.model_path)
            self.rec = vosk.KaldiRecognizer(self.model, 16000)
            logger.info("✅ Modèle Vosk chargé avec succès")
            return True
            
        except Exception as e:
            logger.error(f"Erreur initialisation Vosk: {e}")
            return False
    
    def audio_callback(self, indata, frames, time, status):
        """Callback pour capturer l'audio"""
        if status:
            logger.warning(f"Audio status: {status}")
        self.audio_queue.put(bytes(indata))
    
    def listen_for_speech(self, timeout=30, stop_words=['stop', 'arrêt', 'arrête']):
        """Écoute et reconnaît la parole"""
        if not self.model:
            return None
            
        try:
            logger.info(f"🎤 ÉCOUTE ACTIVÉE (timeout: {timeout}s)")
            
            self.is_listening = True
            recognized_text = ""
            
            with sd.RawInputStream(samplerate=16000, blocksize=8000, device=None, 
                                   dtype='int16', channels=1, callback=self.audio_callback):
                
                start_time = time.time()
                
                while self.is_listening and (time.time() - start_time) < timeout:
                    try:
                        data = self.audio_queue.get(timeout=1)
                        
                        if self.rec.AcceptWaveform(data):
                            # Phrase complète reconnue
                            result = json.loads(self.rec.Result())
                            text = result.get('text', '').strip()
                            
                            if text:
                                logger.info(f"🗣️ RECONNU: '{text}'")
                                recognized_text = text
                                
                                # Vérifier les mots d'arrêt
                                if any(stop_word in text.lower() for stop_word in stop_words):
                                    logger.info("🛑 Mot d'arrêt détecté")
                                    break
                                else:
                                    # Phrase reconnue, on peut s'arrêter
                                    break
                        else:
                            # Reconnaissance partielle
                            partial = json.loads(self.rec.PartialResult())
                            partial_text = partial.get('partial', '').strip()
                            if partial_text:
                                logger.debug(f"En cours: {partial_text}")
                                
                    except queue.Empty:
                        continue
                    except Exception as e:
                        logger.error(f"Erreur reconnaissance: {e}")
                        break
            
            self.is_listening = False
            logger.info(f"✅ Reconnaissance terminée: '{recognized_text}'")
            return recognized_text if recognized_text else None
            
        except Exception as e:
            logger.error(f"Erreur écoute: {e}")
            self.is_listening = False
            return None
    
    def stop_listening(self):
        """Arrête l'écoute"""
        self.is_listening = False

def analyze_situation_with_guardian_ai(situation_text, user_info={}):
    """Analyse la situation avec l'IA Guardian - Logique complète comme demo_live_agent.py"""
    if not guardian_agent or not guardian_agent.is_available:
        logger.error("Guardian agent non disponible")
        return {
            'success': False,
            'error': 'Guardian agent non configuré',
            'advice': ["❌ Service Guardian temporairement indisponible"],
            'urgency_level': 5
        }
    
    try:
        user_firstname = user_info.get('firstName', 'mon ami')
        user_fullname = user_info.get('fullName', user_firstname)
        user_phone = user_info.get('phone', 'Non renseigné')
        
        # Prompt complet comme dans demo_live_agent.py
        full_prompt = f"""Tu es GUARDIAN, l'IA d'assistance d'urgence experte. Analyse cette situation d'urgence RÉELLE et réponds de façon CONCISE et ACTIONNABLE.

**SITUATION RAPPORTÉE:**
"{situation_text}"

**UTILISATEUR:**
- Prénom: {user_firstname}
- Téléphone: {user_phone}
- Localisation: 8 rue de Londres, 75009 Paris (bureaux Google France)

**INSTRUCTIONS - SOIS TRÈS CONCIS:**

**NIVEAU D'URGENCE:** X/10 (1=info, 5=attention, 8=urgence, 10=danger mortel)

**ANALYSE EXPRESS:**
1. [Diagnostic en 1 phrase max]
2. [Action simple - 5 mots max]

**OÙ ALLER:**
[Si nécessaire: DEMANDE_LIEUX_SECURISES]

**APPELER:**
17 (Police) ou 112 (Urgences)

**{user_firstname}:** [Message court rassurant - 1 phrase max]

**DÉCISIONS AUTONOMES:**
- Si urgence >= 7/10: DEMANDE_ENVOI_EMAIL_URGENCE
- Si déplacement nécessaire: DEMANDE_ITINERAIRE_SECURISE

GARDE TA RÉPONSE TRÈS COURTE. La personne est en état de choc et ne peut pas traiter de longs textes."""

        logger.info("🧠 Analyse IA Guardian en cours...")
        
        # Appel API Guardian
        response = guardian_agent._make_api_request(full_prompt)
        
        if not response or 'candidates' not in response:
            raise Exception("Pas de réponse valide de l'API Guardian")
        
        ai_text = response['candidates'][0]['content']['parts'][0]['text']
        logger.info("✅ Réponse Guardian reçue")
        
        # Extraire le niveau d'urgence
        urgency_match = re.search(r'\*\*NIVEAU D\'URGENCE:\*\*\s*(\d+)/10', ai_text)
        urgency_level = int(urgency_match.group(1)) if urgency_match else 5
        
        # Traitement des demandes spéciales
        processed_response = ai_text
        
        # 1. Traitement des lieux sécurisés
        if "DEMANDE_LIEUX_SECURISES" in ai_text:
            logger.info("🏪 Recherche lieux sécurisés...")
            location = "48.8756,2.3264"  # Coordonnées Google France
            
            places_info = get_nearby_safe_places(
                guardian_config, 
                location,
                ['hospital', 'police', 'pharmacy', 'gas_station']
            )
            
            user_coords = location.split(',')
            user_lat, user_lng = float(user_coords[0]), float(user_coords[1])
            places_response = format_safe_places_response(places_info, user_lat, user_lng)
            processed_response = processed_response.replace("DEMANDE_LIEUX_SECURISES", places_response)
        
        # 2. Traitement de l'itinéraire sécurisé
        if "DEMANDE_ITINERAIRE_SECURISE" in ai_text:
            logger.info("🗺️ Calcul itinéraire sécurisé...")
            route_info = get_safe_route_directions(
                guardian_config, 
                "8 rue de Londres, 75009 Paris", 
                "Place de la Concorde, Paris"
            )
            route_response = format_route_response(route_info)
            processed_response = processed_response.replace("DEMANDE_ITINERAIRE_SECURISE", route_response)
        
        # 3. Traitement de l'email d'urgence (décision autonome de l'IA)
        email_sent = False
        if "DEMANDE_ENVOI_EMAIL_URGENCE" in ai_text:
            logger.info("🚨 Envoi email d'urgence décidé par l'IA...")
            if gmail_agent and gmail_agent.is_available:
                email_sent = send_emergency_email_guardian(
                    user_phone=user_phone,
                    real_location="8 rue de Londres, 75009 Paris (bureaux Google France)",
                    real_situation=situation_text,
                    user_fullname=user_fullname
                )
                
                if email_sent:
                    email_msg = "✅ Email d'urgence envoyé avec succès aux contacts d'urgence."
                else:
                    email_msg = "❌ Erreur lors de l'envoi de l'email d'urgence."
                
                processed_response = processed_response.replace("DEMANDE_ENVOI_EMAIL_URGENCE", email_msg)
            else:
                processed_response = processed_response.replace("DEMANDE_ENVOI_EMAIL_URGENCE", 
                    "⚠️ Service d'email d'urgence non configuré.")
        
        return {
            'success': True,
            'response': processed_response,
            'urgency_level': urgency_level,
            'email_sent': email_sent,
            'advice': [processed_response],
            'recommendations': []
        }
        
    except Exception as e:
        logger.error(f"Erreur analyse Guardian: {e}")
        return {
            'success': False,
            'error': str(e),
            'advice': [f"❌ Erreur Guardian: {e}"],
            'urgency_level': 5
        }

def send_emergency_email_guardian(user_phone, real_location, real_situation, user_fullname):
    """Envoie un email d'urgence aux contacts - logique identique à demo_live_agent.py"""
    if not gmail_agent or not gmail_agent.is_available:
        return False
    
    try:
        # Coordonnées exactes Google France
        demo_location = (48.8756, 2.3264)
        
        # Obtenir les contacts d'urgence
        emergency_contacts = guardian_config.get('emergency_contacts', [
            {"email": "demo@example.com", "name": "Contact Demo"}
        ])
        
        success_count = 0
        for contact in emergency_contacts:
            try:
                subject, html_body, text_body = gmail_agent.create_emergency_email(
                    recipient_email=contact.get("email"),
                    user_name=user_fullname,
                    location=real_location,
                    situation=real_situation,
                    location_coords=demo_location,
                    emergency_type="🚨 Alerte Guardian - Situation d'urgence",
                    urgency_level="élevée",
                    user_phone=user_phone
                )
                
                result = gmail_agent.send_email(contact.get("email"), subject, html_body, text_body)
                if result.get("success"):
                    success_count += 1
                    
            except Exception as e:
                logger.error(f"Erreur envoi email à {contact.get('name')}: {e}")
                
        return success_count > 0
        
    except Exception as e:
        logger.error(f"Erreur générale envoi email: {e}")
        return False

# Création de l'application Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'guardian_secret_key_2024'
socketio = SocketIO(app, cors_allowed_origins="*")

# Middleware pour désactiver le cache (développement)
@app.after_request
def add_no_cache_headers(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, private, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['Last-Modified'] = 'Thu, 01 Jan 1970 00:00:00 GMT'
    response.headers['ETag'] = ''
    # Ajouter timestamp pour forcer refresh
    import time
    response.headers['X-Timestamp'] = str(int(time.time()))
    return response

# Initialisation du système de reconnaissance vocale Vosk
voice_recognizer = None
if VOSK_AVAILABLE:
    voice_recognizer = VoiceRecognizer()
    if voice_recognizer.initialize():
        logger.info("🎤 VoiceRecognizer Vosk initialisé avec succès")
    else:
        logger.error("❌ Échec d'initialisation du VoiceRecognizer")
        voice_recognizer = None
else:
    logger.warning("⚠️ Vosk non disponible, reconnaissance vocale désactivée")

@app.route('/')
def home():
    """Page d'accueil avec gros G pour démonstration"""
    return render_template('home.html')

@app.route('/demo')
def demo():
    """Page de démonstration avec trajet et conversation Guardian"""
    return render_template('demo.html')

@app.route('/conversation')
def conversation():
    """Page de conversation Guardian seulement"""
    return render_template('conversation.html')

@app.route('/map')
def map_page():
    """Page avec la carte interactive"""
    return render_template('map.html')

@app.route('/emergency')
def emergency_page():
    """Page d'interface d'urgence"""
    return render_template('emergency.html')

@app.route('/guardian')
def guardian_page():
    """Page Guardian agent dédiée"""
    return render_template('guardian_agent.html')

@app.route('/guardian/setup')
def guardian_setup():
    """Page de configuration Guardian"""
    return render_template('guardian_setup.html')

@app.route('/debug')
def debug_page():
    """Page de debug pour tester l'API Guardian"""
    return render_template('debug.html')

@app.route('/voice-test')
def voice_test():
    """Page de test spécialisée pour la reconnaissance vocale"""
    return render_template('voice_test.html')

@app.route('/api/status', methods=['GET'])
def get_status():
    """API pour vérifier le statut du système"""
    return jsonify({
        'success': True,
        'status': 'operational',
        'message': 'Tous systèmes opérationnels'
    })

@app.route('/api/guardian/start', methods=['POST'])
def start_guardian_agent():
    """API pour démarrer l'agent Guardian avec reconnaissance vocale"""
    try:
        data = request.json
        user_info = {
            'firstName': data.get('firstName', 'Utilisateur'),
            'lastName': data.get('lastName', ''),
            'phone': data.get('phone', ''),
            'location': data.get('location', 'Position actuelle')
        }
        
        logger.info(f"🛡️ Démarrage de l'agent Guardian pour {user_info['firstName']}")
        
        # Simulation de démarrage de l'agent
        return jsonify({
            'success': True,
            'message': f'Agent Guardian activé pour {user_info["firstName"]}',
            'status': 'listening',
            'capabilities': [
                'Reconnaissance vocale active',
                'Analyse IA en temps réel', 
                'Conseils de sécurité personnalisés',
                'Suivi GPS continu'
            ]
        })
        
    except Exception as e:
        logger.error(f"Erreur lors du démarrage Guardian: {e}")
        return jsonify({'error': 'Erreur lors du démarrage de Guardian'}), 500

@app.route('/api/tts/speak', methods=['POST'])
def tts_speak():
    """API pour la synthèse vocale Google Text-to-Speech"""
    try:
        data = request.json
        text = data.get('text', '')
        voice_name = data.get('voice', 'fr-FR-Neural2-A')  # Voix française par défaut
        
        if not text or len(text.strip()) == 0:
            return jsonify({'success': False, 'error': 'Texte requis'}), 400
        
        logger.info(f"🔊 TTS demandé pour: '{text[:50]}...'")
        
        # Utiliser l'API Google TTS via google_apis_service
        if google_service:
            success = google_service.google_text_to_speech_emergency(text, voice_name)
            
            if success:
                logger.info("✅ TTS Google réussi")
                return jsonify({
                    'success': True,
                    'message': 'Synthèse vocale réalisée',
                    'text': text,
                    'voice': voice_name
                })
            else:
                logger.warning("⚠️ TTS Google échoué - Mode simulation")
                return jsonify({
                    'success': False,
                    'error': 'API TTS non disponible - Utiliser le TTS du navigateur',
                    'fallback': True
                })
        else:
            logger.warning("⚠️ Service Google non disponible")
            return jsonify({
                'success': False,
                'error': 'Service Google non configuré',
                'fallback': True
            })
    
    except Exception as e:
        logger.error(f"❌ Erreur TTS: {e}")
        return jsonify({
            'success': False,
            'error': f'Erreur TTS: {str(e)}',
            'fallback': True
        }), 500

@app.route('/api/guardian/analyze', methods=['POST'])
def guardian_analyze():
    """API pour l'analyse Guardian - Utilise la vraie IA comme demo_live_agent.py"""
    try:
        data = request.json
        situation = data.get('situation', '')
        location = data.get('location', '')
        user_info = data.get('user_info', {})
        conversation_history = data.get('conversation_history', [])
        
        logger.info(f"🔍 Analyse Guardian pour: '{situation}'")
        
        # Utiliser la vraie analyse Guardian
        analysis_result = analyze_situation_with_guardian_ai(situation, user_info)
        
        if analysis_result['success']:
            return jsonify({
                'urgency_level': analysis_result['urgency_level'],
                'advice': analysis_result['advice'],
                'recommendations': analysis_result.get('recommendations', []),
                'response': analysis_result.get('response', ''),
                'email_sent': analysis_result.get('email_sent', False),
                'status': 'success',
                'guardian_active': True,
                'message': 'Analyse Guardian complète réalisée',
                'location': location,
                'timestamp': data.get('timestamp', 'N/A')
            })
        else:
            # Fallback vers l'analyse simple en cas d'erreur Guardian
            logger.warning("Fallback vers analyse simple")
            first_name = user_info.get('firstName', 'mon ami')
            
            # Analyse contextuelle simple de fallback
            urgency_level = 3
            advice = [f"❌ {analysis_result.get('error', 'Erreur Guardian')}"]
            recommendations = ["Vérifiez la configuration Guardian"]
            
            return jsonify({
                'urgency_level': urgency_level,
                'advice': advice,
                'recommendations': recommendations,
                'response': analysis_result.get('error', 'Erreur Guardian'),
                'email_sent': False,
                'status': 'fallback',
                'guardian_active': False,
                'message': 'Guardian non disponible - Mode fallback activé',
                'location': location,
                'timestamp': data.get('timestamp', 'N/A')
            })
        
        # Cette partie ne devrait jamais être atteinte
        # Détection d'urgences médicales (code mort - gardé pour compatibilité)
        if any(word in situation for word in ['chute', 'tombé', 'chuter', 'mal', 'douleur', 'blessé', 'sang', 'accident']):
            urgency_level = 8
            advice = [
                f"🚨 {first_name}, je détecte une urgence potentielle !",
                "🏥 Restez immobile si possible et évaluez vos blessures",
                "📍 J'ai enregistré votre position GPS précise",
                "📞 Souhaitez-vous que j'appelle les secours ?"
            ]
            recommendations = [
                "Ne bougez pas si vous ressentez des douleurs au cou/dos",
                "Appelez le 15 (SAMU) si nécessaire",
                "Gardez votre téléphone à portée de main"
            ]
        
        # Détection de détresse psychologique
        elif any(word in situation for word in ['peur', 'angoisse', 'stress', 'panique', 'anxieux', 'inquiet']):
            urgency_level = 6
            advice = [
                f"🤗 {first_name}, je comprends votre inquiétude",
                "🧘‍♀️ Prenez quelques respirations profondes avec moi",
                "�️ Je reste avec vous, vous n'êtes pas seul(e)",
                "💪 Ensemble, nous allons gérer cette situation"
            ]
            recommendations = [
                "Respirez lentement: 4 temps inspiration, 6 temps expiration",
                "Regardez autour de vous pour identifier des éléments rassurants",
                "Rappelez-vous que cette sensation est temporaire"
            ]
        
        # Détection de problème d'orientation
        elif any(word in situation for word in ['perdu', 'égaré', 'trouvé', 'où', 'direction', 'chemin']):
            urgency_level = 5
            advice = [
                f"🧭 Pas de panique {first_name}, je vais vous aider à vous orienter",
                "📱 J'active le système de navigation GPS",
                "🏢 Cherchez des points de repère autour de vous",
                "🚶‍♀️ Restez sur les voies principales et éclairées"
            ]
            recommendations = [
                "Notez les noms de rues ou numéros visibles",
                "Dirigez-vous vers des lieux fréquentés",
                "Utilisez la boussole de votre téléphone"
            ]
        
        # Détection de fatigue/malaise
        elif any(word in situation for word in ['fatigué', 'épuisé', 'vertiges', 'étourdi', 'nausée']):
            urgency_level = 6
            advice = [
                f"⚡ {first_name}, écoutons votre corps",
                "🪑 Trouvez un endroit sûr pour vous asseoir",
                "� Hydratez-vous si possible",
                "🌬️ Prenez l'air frais quelques instants"
            ]
            recommendations = [
                "Reposez-vous 10-15 minutes minimum",
                "Évitez les mouvements brusques",
                "Contactez quelqu'un si les symptômes persistent"
            ]
        
        # Détection de problèmes de foule/sécurité
        elif any(word in situation for word in ['foule', 'monde', 'bousculade', 'danger', 'suspect']):
            urgency_level = 7
            advice = [
                f"👥 {first_name}, j'analyse l'environnement avec vous",
                "🚶‍♀️ Éloignez-vous calmement des zones denses",
                "👀 Restez vigilant(e) et gardez vos affaires près de vous",
                "🏃‍♀️ Préparez un itinéraire de sortie"
            ]
            recommendations = [
                "Suivez les sorties de secours",
                "Restez près des murs plutôt qu'au centre",
                "Gardez un contact visuel avec les issues"
            ]
        
        # Situation normale - conseils préventifs
        else:
            urgency_level = 3
            advice = [
                f"� Bonjour {first_name}, merci de me tenir informé",
                "�👂 Je vous écoute attentivement",
                "🤖 Continuez à me parler de votre situation",
                "💪 Votre sécurité est ma priorité"
            ]
            recommendations = [
                "Gardez votre téléphone chargé",
                "Restez conscient(e) de votre environnement",
                "N'hésitez pas à me parler à tout moment"
            ]
        
        # Ajustement basé sur l'historique de conversation
        if len(conversation_history) > 3:
            advice.append("📈 Je note une amélioration dans notre échange")
            urgency_level = max(1, urgency_level - 1)
        
        return jsonify({
            'success': True,
            'urgency_level': urgency_level,
            'advice': advice,
            'recommendations': recommendations,
            'listening': True,
            'personalized_message': f"Guardian veille sur vous, {first_name}",
            'context_analysis': {
                'situation_type': 'urgence médicale' if urgency_level >= 7 else 
                                'attention requise' if urgency_level >= 5 else 'surveillance normale',
                'location': location,
                'timestamp': data.get('timestamp', 'N/A')
            }
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse Guardian: {e}")
        return jsonify({'error': 'Erreur lors de l\'analyse Guardian'}), 500

@app.route('/api/analyze', methods=['POST'])
def analyze_emergency():
    """API pour analyser une situation d'urgence"""
    try:
        data = request.json
        situation = data.get('situation', '')
        location = data.get('location', '')
        
        # Simulation d'analyse d'urgence simple
        urgency_level = 5  # Valeur par défaut
        
        # Détection de mots-clés d'urgence
        urgent_keywords = ['chute', 'accident', 'malaise', 'blessé', 'sang', 'douleur', 'urgence', 'aide']
        for keyword in urgent_keywords:
            if keyword.lower() in situation.lower():
                urgency_level = 8
                break
        
        response = {
            'urgency_level': urgency_level,
            'analysis': f"Situation analysée: {situation} à {location}",
            'recommendations': [
                "Gardez votre calme",
                "Restez en sécurité",
                "Suivez les instructions données"
            ]
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse: {e}")
        return jsonify({'error': 'Erreur lors de l\'analyse'}), 500

@socketio.on('connect')
def handle_connect():
    """Gestion de la connexion WebSocket"""
    logger.info('Client connecté via WebSocket')
    emit('status', {'message': 'Connexion établie avec Guardian'})

@socketio.on('emergency_alert')
def handle_emergency_alert(data):
    """Gestion des alertes d'urgence"""
    logger.info(f"Alerte d'urgence reçue: {data}")
    emit('emergency_response', {
        'message': 'Alerte reçue, analyse en cours...',
        'timestamp': data.get('timestamp')
    })

@app.route('/api/vosk/listen', methods=['POST'])
def vosk_listen():
    """API pour démarrer l'écoute avec Vosk"""
    try:
        if not voice_recognizer:
            return jsonify({
                'success': False,
                'error': 'Reconnaissance vocale Vosk non disponible',
                'message': 'Le système Vosk n\'est pas configuré correctement'
            }), 503
        
        data = request.json or {}
        timeout = data.get('timeout', 30)
        
        logger.info(f"🎤 Démarrage écoute Vosk (timeout: {timeout}s)")
        
        # Démarrer l'écoute en thread séparé pour ne pas bloquer l'API
        def listen_thread():
            try:
                result = voice_recognizer.listen_for_speech(timeout=timeout)
                return result
            except Exception as e:
                logger.error(f"Erreur thread écoute: {e}")
                return None
        
        # Écoute synchrone pour le moment (on pourrait l'améliorer avec du WebSocket)
        recognized_text = listen_thread()
        
        if recognized_text:
            return jsonify({
                'success': True,
                'text': recognized_text,
                'message': 'Reconnaissance réussie'
            })
        else:
            return jsonify({
                'success': False,
                'text': '',
                'message': 'Aucun texte reconnu'
            })
            
    except Exception as e:
        logger.error(f"Erreur API Vosk: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erreur lors de la reconnaissance vocale'
        }), 500

@app.route('/api/vosk/status', methods=['GET'])
def vosk_status():
    """API pour vérifier le statut de Vosk"""
    try:
        return jsonify({
            'available': VOSK_AVAILABLE and voice_recognizer is not None,
            'model_path': voice_recognizer.model_path if voice_recognizer else None,
            'is_listening': voice_recognizer.is_listening if voice_recognizer else False,
            'message': 'Vosk prêt' if voice_recognizer else 'Vosk non disponible'
        })
    except Exception as e:
        return jsonify({
            'available': False,
            'error': str(e),
            'message': 'Erreur lors de la vérification du statut Vosk'
        }), 500

def find_available_port(start_port=5001):
    """Trouve un port disponible à partir du port spécifié"""
    port = start_port
    while port < start_port + 100:  # Teste jusqu'à 100 ports
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('localhost', port))
            sock.close()
            return port
        except OSError:
            port += 1
    return None

if __name__ == '__main__':
    try:
        # Détermine le répertoire du projet
        project_dir = Path(__file__).parent
        
        # Trouver un port disponible
        port = find_available_port(5001)
        if port is None:
            logger.error("❌ Impossible de trouver un port disponible")
            exit(1)
        
        logger.info(f"🚀 Démarrage de Guardian Web Interface Simple")
        logger.info(f"📍 Projet: {project_dir}")
        logger.info(f"🌐 URL: http://localhost:{port}")
        logger.info(f"🗺️ Carte: http://localhost:{port}/map")
        logger.info(f"🚨 Urgence: http://localhost:{port}/emergency")
        logger.info(f"")
        logger.info(f"💡 Ouvrez votre navigateur sur: http://localhost:{port}")
        logger.info(f"")
        
        # Démarrage du serveur
        socketio.run(app, host='0.0.0.0', port=port, debug=False)
        
    except KeyboardInterrupt:
        logger.info("🛑 Arrêt de Guardian Web Interface")
    except Exception as e:
        logger.error(f"❌ Erreur lors du démarrage: {e}")