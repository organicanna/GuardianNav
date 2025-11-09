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
except ImportError as e:
    VOSK_AVAILABLE = False

# Chargement de l'agent Guardian comme dans demo_live_agent.py
guardian_agent = None
gmail_agent = None
# Configuration des chemins depuis le sous-dossier web
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

try:
    
    config_path = os.path.join(parent_dir, 'config', 'api_keys.yaml')
    with open(config_path, 'r', encoding='utf-8') as f:
        guardian_config = yaml.safe_load(f)
    
    from guardian.gemini_agent import GeminiAgent
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
    
    print(f"🔧 Configuration Guardian: {guardian_config}")
    guardian_agent = GeminiAgent(guardian_config)
    print(f"✅ Guardian agent créé: {guardian_agent}")
    gmail_agent = GmailEmergencyAgent(guardian_config)
    google_service = GoogleAPIsService(guardian_config)
    
    # Ajouter l'agent Gmail à l'agent principal
    guardian_agent.gmail_agent = gmail_agent
    
    print(f"🔍 Guardian agent disponible: {guardian_agent is not None}")
    
except Exception as e:
    logging.error(f"Erreur chargement Guardian: {e}")
    print(f"❌ Exception lors du chargement: {e}")
    import traceback
    traceback.print_exc()
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
                
            self.model = vosk.Model(self.model_path)
            self.rec = vosk.KaldiRecognizer(self.model, 16000)
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
                                logger.info(f"RECONNU: '{text}'")
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
            logger.info(f"Reconnaissance terminée: '{recognized_text}'")
            return recognized_text if recognized_text else None
            
        except Exception as e:
            logger.error(f"Erreur écoute: {e}")
            self.is_listening = False
            return None
    
    def stop_listening(self):
        """Arrête l'écoute"""
        self.is_listening = False

def fallback_situation_analysis(situation_text, user_info={}):
    """Analyse de situation de fallback quand Gemini n'est pas disponible"""
    logger.info("🔄 Activation du système de fallback Guardian")
    
    first_name = user_info.get('firstName', 'mon ami')
    situation = situation_text.lower().strip()
    
    # Classification basique par mots-clés
    emergency_keywords = ['urgence', 'danger', 'secours', 'aide', 'accident', 'blessé', 'sang', 'évanouissement']
    medical_keywords = ['mal', 'douleur', 'coeur', 'respiration', 'vertiges', 'malaise', 'chute', 'tombé']
    security_keywords = ['menace', 'agression', 'vol', 'suspect', 'peur', 'suivre', 'harcèlement']
    location_keywords = ['perdu', 'égaré', 'retrouver', 'direction', 'chemin', 'où']
    stress_keywords = ['stress', 'anxieux', 'panique', 'angoisse', 'inquiet']
    
    # Détermination du niveau d'urgence et des conseils
    if any(word in situation for word in emergency_keywords):
        urgency_level = 9
        emergency_type = "URGENCE MAJEURE"
        advice = [
            f"🚨 {first_name}, situation d'urgence détectée!",
            "📞 Appelez immédiatement le 112 (urgences)",
            "📍 Restez à votre position actuelle",
            "🛡️ Guardian surveille votre situation"
        ]
        recommendations = [
            "Appelez le 112 ou 15 immédiatement",
            "Restez en sécurité et calme",
            "Gardez votre téléphone allumé"
        ]
        email_urgency = True
    elif any(word in situation for word in medical_keywords):
        urgency_level = 8
        emergency_type = "URGENCE MÉDICALE"
        advice = [
            f"🏥 {first_name}, problème médical détecté",
            "🩺 Évaluez l'intensité de vos symptômes",
            "📞 SAMU 15 si douleurs intenses",
            "🧘‍♀️ Restez calme et respirez profondément"
        ]
        recommendations = [
            "Appelez le 15 (SAMU) si nécessaire",
            "Asseyez-vous dans un endroit sûr",
            "Ne prenez pas de médicaments sans avis médical"
        ]
        email_urgency = True
    elif any(word in situation for word in security_keywords):
        urgency_level = 7
        emergency_type = "PROBLÈME DE SÉCURITÉ"
        advice = [
            f"🛡️ {first_name}, restez vigilant",
            "🚶‍♀️ Dirigez-vous vers un lieu public",
            "👥 Rapprochez-vous d'autres personnes",
            "📞 17 (Police) si menace directe"
        ]
        recommendations = [
            "Restez dans des zones éclairées et fréquentées",
            "Appelez le 17 si danger imminent",
            "Évitez les confrontations"
        ]
        email_urgency = False
    elif any(word in situation for word in location_keywords):
        urgency_level = 5
        emergency_type = "PROBLÈME D'ORIENTATION"
        advice = [
            f"🧭 {first_name}, ne paniquez pas",
            "📱 Utilisez votre GPS pour vous localiser",
            "🏪 Cherchez des commerces ou lieux publics",
            "📞 Contactez vos proches si besoin"
        ]
        recommendations = [
            "Notez les noms de rues autour de vous",
            "Demandez de l'aide dans un commerce",
            "Utilisez les transports en commun si possible"
        ]
        email_urgency = False
    elif any(word in situation for word in stress_keywords):
        urgency_level = 4
        emergency_type = "SOUTIEN PSYCHOLOGIQUE"
        advice = [
            f"🤗 {first_name}, je comprends votre inquiétude",
            "🧘‍♀️ Prenez 5 respirations profondes",
            "💪 Cette sensation va passer",
            "🌟 Vous n'êtes pas seul(e)"
        ]
        recommendations = [
            "Respirez lentement: 4 temps inspiration, 6 temps expiration",
            "Trouvez un endroit calme pour vous asseoir",
            "Contactez un proche ou un professionnel si besoin"
        ]
        email_urgency = False
    else:
        # Situation générale
        urgency_level = 3
        emergency_type = "SURVEILLANCE NORMALE"
        advice = [
            f"👋 Bonjour {first_name}",
            "🛡️ Guardian vous écoute",
            "💬 Décrivez votre situation plus précisément",
            "🆘 Je suis là pour vous aider"
        ]
        recommendations = [
            "Soyez plus spécifique sur votre situation",
            "Guardian est là pour vous accompagner",
            "N'hésitez pas à demander de l'aide"
        ]
        email_urgency = False
    
    return {
        'success': True,
        'urgency_level': urgency_level,
        'emergency_type': emergency_type,
        'advice': advice,
        'recommendations': recommendations,
        'immediate_actions': advice[:2],  # Les 2 premières actions
        'emergency_services': "112 (Urgences générales)" if urgency_level >= 7 else None,
        'specific_advice': " ".join(advice),
        'email_urgency': email_urgency,
        'fallback_mode': True,
        'response': f"Mode Guardian Fallback activé. {emergency_type} détecté (niveau {urgency_level}/10). " + advice[0]
    }

def analyze_situation_with_guardian_ai(situation_text, user_info={}):
    """Analyze situation with Guardian AI"""
    if not guardian_agent:
        logger.error("Guardian agent non disponible")
        return fallback_situation_analysis(situation_text, user_info)
    
    try:
        user_firstname = user_info.get('firstName', 'mon ami')
        user_fullname = user_info.get('fullName', user_firstname)
        user_phone = user_info.get('phone', 'Non renseigné')
        
        full_prompt = f"""Tu es GUARDIAN, assistant IA de sécurité bienveillant.

SITUATION: "{situation_text}"
UTILISATEUR: {user_firstname}
LIEU: Paris 9e

RÉPONSE ULTRA-CONCISE (1-2 PHRASES MAXIMUM):

**NIVEAU D'URGENCE:** [chiffre]/10

**MESSAGE:**
[1 phrase courte et directe avec le conseil immédiat]

**ACTION:**
[Si urgence >= 7: DEMANDE_ENVOI_EMAIL_URGENCE]
[Si besoin lieu sûr: DEMANDE_LIEUX_SECURISES]

CONSIGNE STRICTE: Maximum 1-2 phrases courtes. Sois direct, pas de détails inutiles."""

        logger.info("🧠 Analyse IA Guardian en cours...")
        
        # Appel API Guardian
        response = guardian_agent._make_api_request(full_prompt)
        
        if not response or 'candidates' not in response:
            raise Exception("Pas de réponse valide de l'API Guardian")
        
        ai_text = response['candidates'][0]['content']['parts'][0]['text']
        logger.info(f"✅ Réponse Guardian reçue: {ai_text[:100]}...")
        
        # Extraire le niveau d'urgence
        urgency_match = re.search(r'\*\*NIVEAU D\'URGENCE:\*\*\s*(\d+)/10', ai_text)
        urgency_level = int(urgency_match.group(1)) if urgency_match else 5
        
        # Initialiser la réponse
        processed_response = ai_text
        safe_places_list = []  # AJOUT: Stocker les lieux sécurisés
        
        # 1. Traitement des lieux sécurisés
        if "DEMANDE_LIEUX_SECURISES" in ai_text:
            logger.info("🏪 Recherche lieux sécurisés...")
            location = "48.8758,2.3251"  # Coordonnées Google France (8 Rue de Londres)
            
            places_info = get_nearby_safe_places(
                guardian_config, 
                location,
                ['hospital', 'police', 'pharmacy', 'gas_station']
            )
            
            user_coords = location.split(',')
            user_lat, user_lng = float(user_coords[0]), float(user_coords[1])
            
            # AJOUT: Stocker les lieux pour la carte
            if isinstance(places_info, list):
                safe_places_list = places_info
            
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
        
        # 3. ENVOI EMAIL AUTOMATIQUE si urgence >= 8 OU si demandé par l'IA
        email_sent = False
        should_send_email = urgency_level >= 8 or "DEMANDE_ENVOI_EMAIL_URGENCE" in ai_text
        
        if should_send_email:
            logger.info(f"📧 Envoi email d'urgence (niveau {urgency_level}/10)...")
            if gmail_agent and gmail_agent.is_available:
                email_sent = send_emergency_email_guardian(
                    user_phone=user_phone,
                    real_location="8 rue de Londres, 75009 Paris (bureaux Google France)",
                    real_situation=situation_text,
                    user_fullname=user_fullname,
                    user_info=user_info
                )
                
                if email_sent:
                    email_msg = "✅ Email d'urgence envoyé avec succès aux contacts d'urgence."
                else:
                    email_msg = "❌ Erreur lors de l'envoi de l'email d'urgence."
                
                # Remplacer le marqueur si présent
                if "DEMANDE_ENVOI_EMAIL_URGENCE" in processed_response:
                    processed_response = processed_response.replace("DEMANDE_ENVOI_EMAIL_URGENCE", email_msg)
                else:
                    # Ajouter le message à la fin si pas de marqueur
                    processed_response += f"<br><br>{email_msg}"
            else:
                error_msg = "⚠️ Service d'email d'urgence non configuré."
                if "DEMANDE_ENVOI_EMAIL_URGENCE" in processed_response:
                    processed_response = processed_response.replace("DEMANDE_ENVOI_EMAIL_URGENCE", error_msg)
                else:
                    processed_response += f"<br><br>{error_msg}"
        elif "DEMANDE_ENVOI_EMAIL_URGENCE" in processed_response:
            # Supprimer le marqueur si l'email n'est pas envoyé
            processed_response = processed_response.replace("DEMANDE_ENVOI_EMAIL_URGENCE", "")
        
        # 4. NETTOYAGE FINAL du markdown (APRÈS tous les traitements)
        # Supprimer TOUS les ** et * (markdown)
        processed_response = processed_response.replace('**', '')
        processed_response = processed_response.replace('*', '')
        
        # Remplacer les marqueurs par des emojis simples
        processed_response = processed_response.replace('NIVEAU DURGENCE:', '🚨 Urgence:')
        processed_response = processed_response.replace('MESSAGE:', '<br>💬 Message:')
        processed_response = processed_response.replace('ACTION:', '<br>🤖 Action:')
        
        # Convertir les sauts de ligne en <br> pour HTML
        processed_response = processed_response.replace('\n', '<br>')
        
        # Supprimer les lignes vides et les crochets
        clean_lines = [line for line in processed_response.split('<br>') if line.strip() and not line.strip().startswith('[') and line.strip() != ']']
        processed_response = '<br>'.join(clean_lines)
        
        # Extraire les sections pour le retour structuré
        analysis_section = processed_response
        recommendations_list = [processed_response]
        
        logger.info(f"📊 Analyse terminée - Urgence: {urgency_level}/10, Email envoyé: {email_sent}")
        
        return {
            'success': True,
            'response': processed_response,
            'urgency_level': urgency_level,
            'email_sent': email_sent,
            'safe_places': safe_places_list,  # AJOUT: Retourner les lieux sécurisés
            'advice': [analysis_section] if analysis_section else [processed_response],
            'recommendations': recommendations_list,
            'formatted_response': True
        }
        
    except Exception as e:
        logger.error(f"Erreur analyse Guardian: {e}")
        logger.info("🔄 Basculement vers le système de fallback")
        return fallback_situation_analysis(situation_text, user_info)

def send_emergency_email_guardian(user_phone, real_location, real_situation, user_fullname, user_info={}):
    """Envoie un email d'urgence aux contacts - priorité aux contacts saisis par l'utilisateur"""
    if not gmail_agent or not gmail_agent.is_available:
        return False
    
    try:
        # Coordonnées exactes Google France
        demo_location = (48.8756, 2.3264)
        
        # PRIORITÉ 1: Contact d'urgence saisi par l'utilisateur
        emergency_contacts = []
        if user_info and user_info.get('emergencyContact'):
            emergency_contact = user_info['emergencyContact']
            if emergency_contact.get('email'):
                emergency_contacts = [{
                    "email": emergency_contact['email'],
                    "name": emergency_contact.get('name', 'Contact d\'urgence'),
                    "phone": emergency_contact.get('phone', 'Non renseigné')
                }]
                print(f"📧 Utilisation du contact d'urgence utilisateur: {emergency_contact['email']}")
        
        # PRIORITÉ 2: Contacts par défaut de la configuration si aucun contact utilisateur
        if not emergency_contacts:
            emergency_contacts = guardian_config.get('emergency_contacts', [
                {"email": "demo@example.com", "name": "Contact Demo"}
            ])
            print(f"📧 Utilisation des contacts de configuration par défaut")
        
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

def generate_location_recommendations(urgency_level, coordinates):
    """
    Generate location recommendations based on urgency level
    
    Args:
        urgency_level (int): Urgency level 1-10
        coordinates (tuple): (latitude, longitude)
    
    Returns:
        str: Formatted location recommendations
    """
    lat, lon = coordinates
    
    # Paris 9e arrondissement - près de Gare Saint-Lazare
    if urgency_level >= 7:
        # Urgence critique - proposer des secours
        return """🆘 **LIEUX D'URGENCE À PROXIMITÉ :**
• Hôpital Saint-Louis (15 min) - 1 Avenue Claude Vellefaux
• Pharmacie de Garde Opéra (5 min) - 6 Boulevard des Capucines  
• Commissariat 9e arrondissement (10 min) - 14 Rue Louis le Grand
• Caserne Pompiers Châteaudun (8 min) - 8 Rue de Châteaudun
• SAMU 75: 15 | Police: 17 | Pompiers: 18"""
        
    elif urgency_level >= 5:
        # Urgence modérée - proposer des lieux de repos
        return """☕ **LIEUX DE REPOS RECOMMANDÉS :**
• Café de la Paix (3 min à pied) - 5 Place de l'Opéra
• Square Louis XVI (7 min) - Place Louis XVI  
• Galeries Lafayette (espaces détente, 5 min) - 40 Boulevard Haussmann
• Hall de l'Hôtel Scribe (climatisé, 2 min) - 1 Rue Scribe
• Printemps Haussmann (6 min) - 64 Boulevard Haussmann"""
        
    elif urgency_level >= 3:
        # Situation normale - proposer des points d'intérêt
        return """📍 **POINTS D'INTÉRÊT À PROXIMITÉ :**
• Opéra Garnier (5 min de visite) - Place de l'Opéra
• Printemps Haussmann (shopping, 3 min) - 64 Boulevard Haussmann  
• Place Vendôme (luxe et patrimoine, 8 min) - Place Vendôme
• Jardins des Tuileries (détente, 12 min) - Place de la Concorde
• Musée Grévin (divertissement, 6 min) - 10 Boulevard Montmartre"""
    else:
        # Faible urgence - informations générales
        return """ℹ️ **SERVICES À PROXIMITÉ :**
• Transports: Métro Opéra (lignes 3, 7, 8), Gare Saint-Lazare
• Commerces: Galeries Lafayette, Printemps, Place Vendôme
• Culture: Opéra Garnier, Musée Grévin, Grands Boulevards
• Restauration: Café de la Paix, Brasseries du quartier"""

# Création de l'application Flask
app = Flask(__name__, static_folder='static', static_url_path='/static')
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
        pass
    else:
        logger.error("Échec d'initialisation du VoiceRecognizer")
        voice_recognizer = None
else:
    logger.warning("Vosk non disponible, reconnaissance vocale désactivée")

@app.route('/')
def home():
    """Page d'accueil épurée - Informations utilisateur"""
    return render_template('user_info.html')

@app.route('/contact_urgence')
def contact_urgence():
    """Page contact d'urgence"""
    return render_template('contact_urgence.html')

@app.route('/demo_navigation')
def demo_navigation():
    """Démonstration de navigation Gare Saint-Lazare → Place Concorde"""
    return render_template('demo_navigation.html')

@app.route('/demo')
def demo():
    """Page de démonstration avec trajet et conversation Guardian"""
    return render_template('demo_working.html')

@app.route('/admin')
def admin():
    """Ancienne page d'accueil avec toutes les fonctionnalités"""
    return render_template('home.html')

@app.route('/demo_fixed')
def demo_fixed():
    """Page de démonstration avec reconnaissance vocale réparée"""
    return render_template('demo_working.html')

@app.route('/conversation')
def conversation():
    """Page de conversation avec Gemini"""
    return render_template('conversation.html')

@app.route('/voice-test')
def voice_test():
    """Page de test du microphone et reconnaissance vocale Vosk"""
    return render_template('voice_test.html')

@app.route('/map')
def map_page():
    """Page avec la carte interactive"""
    return render_template('map.html')

@app.route('/emergency')
def emergency_page():
    """Page d'interface d'urgence"""
    return render_template('emergency.html')

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
        
        logger.info(f"Démarrage de l'agent Guardian pour {user_info['firstName']}")
        
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
    """Prepare text for client-side TTS"""
    try:
        data = request.json
        text = data.get('text', '')
        voice_name = data.get('voice', 'fr-FR-Neural2-A')
        
        if not text or len(text.strip()) == 0:
            return jsonify({'success': False, 'error': 'Texte requis'}), 400
        
        logger.info(f"TTS préparé pour: '{text[:50]}...'")
        
        # Clean text for better synthesis
        clean_text = text.strip()
        clean_text = clean_text.replace('**', '')
        clean_text = clean_text.replace('*', '')
        
        # Validation successful - TTS will be done client-side
        logger.info("TTS préparé avec succès")
        return jsonify({
            'success': True,
            'message': 'Texte prêt pour synthèse vocale',
            'text': clean_text,
            'voice': voice_name,
            'use_browser_tts': True
        })
    
    except Exception as e:
        logger.error(f"Erreur préparation TTS: {e}")
        return jsonify({
            'success': False,
            'error': f'Erreur: {str(e)}',
            'fallback': True
        }), 500

@app.route('/api/guardian/analyze', methods=['POST'])
def guardian_analyze():
    """Guardian analysis API with location recommendations"""
    try:
        data = request.json
        situation = data.get('situation', '')
        location_info = data.get('location', '')
        user_info = data.get('user_info', {})
        conversation_history = data.get('conversation_history', [])
        request_locations = data.get('request_locations', False)
        
        # Extract coordinates if provided
        current_coords = None
        if isinstance(location_info, dict) and 'coordinates' in location_info:
            coords = location_info['coordinates']
            current_coords = (coords.get('lat', 48.8758), coords.get('lon', 2.3251))
        else:
            # Default to Paris center for demo
            current_coords = (48.8758, 2.3251)
        
        logger.info(f"Guardian analysis for: '{situation}' at {current_coords}")
        
        # Use Guardian AI analysis
        analysis_result = analyze_situation_with_guardian_ai(situation, user_info)
        
        if analysis_result['success']:
            response_data = {
                'urgency_level': analysis_result['urgency_level'],
                'advice': analysis_result['advice'],
                'recommendations': analysis_result.get('recommendations', []),
                'response': analysis_result.get('response', ''),
                'email_sent': analysis_result.get('email_sent', False),
                'safe_places': analysis_result.get('safe_places', []),  # AJOUT: Lieux sécurisés
                'status': 'success',
                'guardian_active': True,
                'message': 'Analyse Guardian complète réalisée',
                'location': location_info,
                'timestamp': data.get('timestamp', 'N/A')
            }
            
            # Add location-specific recommendations based on urgency level
            if request_locations and current_coords:
                urgency = analysis_result['urgency_level']
                location_recommendations = generate_location_recommendations(urgency, current_coords)
                response_data['location_recommendations'] = location_recommendations
                
                # Enhance response with location context
                if location_recommendations:
                    response_data['response'] += f"\n\n{location_recommendations}"
            
            return jsonify(response_data)
        else:
            # Fallback vers l'analyse intelligente en cas d'erreur Guardian
            logger.warning("Activation du système de fallback Guardian")
            fallback_result = fallback_situation_analysis(situation, user_info)
            
            response_data = {
                'urgency_level': fallback_result['urgency_level'],
                'emergency_type': fallback_result['emergency_type'],
                'advice': fallback_result['advice'],
                'recommendations': fallback_result['recommendations'],
                'immediate_actions': fallback_result['immediate_actions'],
                'emergency_services': fallback_result['emergency_services'],
                'specific_advice': fallback_result['specific_advice'],
                'response': fallback_result['response'],
                'email_sent': False,
                'status': 'fallback',
                'guardian_active': False,
                'fallback_mode': True,
                'message': 'Mode Guardian Fallback - Analyse basique activée',
                'location': location_info,
                'timestamp': data.get('timestamp', 'N/A')
            }
            
            # Add location recommendations for fallback too
            if request_locations and current_coords:
                urgency = fallback_result['urgency_level']
                location_recommendations = generate_location_recommendations(urgency, current_coords)
                response_data['location_recommendations'] = location_recommendations
                
                if location_recommendations:
                    response_data['response'] += f"\n\n{location_recommendations}"
            
            return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse Guardian: {e}")
        return jsonify({'error': 'Erreur lors de l\'analyse Guardian'}), 500

@app.route('/api/vosk/start', methods=['POST'])
def start_vosk_recognition():
    """Start Vosk recognition - REAL microphone capture"""
    try:
        data = request.json
        duration = data.get('duration', 8)
        language = data.get('language', 'fr')
        
        logger.info(f"🎤 Démarrage reconnaissance RÉELLE Vosk (durée: {duration}s)")
        
        # UTILISER VRAIMENT VOSK - PAS DE SIMULATION
        if not voice_recognizer:
            logger.error("❌ VoiceRecognizer non initialisé")
            return jsonify({
                'success': False,
                'error': 'Système de reconnaissance vocale non disponible',
                'method': 'vosk_unavailable'
            }), 503
        
        try:
            # Capturer l'audio RÉEL du microphone avec Vosk
            logger.info("🎙️ Écoute du microphone en cours...")
            transcript = voice_recognizer.listen_for_speech(timeout=duration)
            
            if transcript and transcript.strip():
                logger.info(f"✅ Vosk a reconnu: '{transcript}'")
                return jsonify({
                    'success': True,
                    'transcript': transcript.strip(),
                    'method': 'vosk_real_microphone',
                    'duration': duration
                })
            else:
                logger.warning("⚠️ Aucune parole détectée par Vosk")
                return jsonify({
                    'success': False,
                    'error': 'Aucune parole détectée. Parlez plus fort ou rapprochez-vous du micro.',
                    'method': 'vosk_no_speech'
                })
                
        except Exception as e:
            logger.error(f"❌ Erreur lors de la capture Vosk: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'error': f'Erreur microphone: {str(e)}',
                'method': 'vosk_error'
            }), 500
        
    except Exception as e:
        logger.error(f"Erreur reconnaissance Vosk: {e}")
        return jsonify({
            'success': False,
            'error': f'Erreur système: {e}',
            'method': 'system_error'
        }), 500

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

@app.route('/api/vosk/process_audio', methods=['POST'])
def process_audio():
    """API pour traiter un fichier audio avec Vosk"""
    try:
        if 'audio' not in request.files:
            return jsonify({
                'success': False,
                'error': 'Aucun fichier audio fourni'
            }), 400
            
        audio_file = request.files['audio']
        language = request.form.get('language', 'fr-FR')
        
        if audio_file.filename == '':
            return jsonify({
                'success': False,
                'error': 'Nom de fichier audio invalide'
            }), 400
        
        # Utiliser Vosk si disponible
        if voice_recognizer and hasattr(voice_recognizer, 'recognize_from_file'):
            try:
                # Sauvegarder temporairement le fichier
                import tempfile
                import os
                
                with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                    audio_file.save(temp_file.name)
                    
                    # Traiter avec Vosk
                    transcript = voice_recognizer.recognize_from_file(temp_file.name)
                    
                    # Nettoyer le fichier temporaire
                    os.unlink(temp_file.name)
                    
                    if transcript and transcript.strip():
                        logger.info(f"✅ Transcript audio Vosk: {transcript}")
                        return jsonify({
                            'success': True,
                            'transcript': transcript.strip(),
                            'method': 'vosk_file_processing',
                            'language': language
                        })
                    else:
                        return jsonify({
                            'success': False,
                            'error': 'Aucune parole détectée dans l\'audio'
                        })
                        
            except Exception as e:
                logger.error(f"Erreur traitement audio Vosk: {e}")
                # Continue vers simulation
        
        # Simulation intelligente basée sur la taille du fichier
        logger.warning("Vosk non disponible pour fichiers audio - simulation basée sur métadonnées")
        
        file_size = len(audio_file.read())
        audio_file.seek(0)  # Reset file pointer
        
        # Simuler basé sur la taille (plus réaliste)
        if file_size < 1000:  # Très petit fichier
            transcript = "Guardian, aidez-moi"
        elif file_size < 5000:  # Petit fichier
            transcript = "Guardian, je ne me sens pas bien"
        elif file_size < 10000:  # Fichier moyen
            transcript = "Guardian, pouvez-vous me dire où je suis"
        else:  # Gros fichier
            transcript = "Guardian, j'ai besoin d'aide pour rentrer chez moi"
            
        logger.info(f"📱 Simulation audio réaliste: {transcript} (taille: {file_size} bytes)")
        
        return jsonify({
            'success': True,
            'transcript': transcript,
            'method': 'audio_simulation',
            'language': language,
            'note': f'Simulation basée sur audio {file_size} bytes'
        })
        
    except Exception as e:
        logger.error(f"Erreur traitement audio: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
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
            logger.error("Impossible de trouver un port disponible")
            exit(1)
        
        logger.info("Démarrage de Guardian Web Interface Simple")
        logger.info(f"Projet: {project_dir}")
        logger.info(f"URL: http://localhost:{port}")
        logger.info(f"Carte: http://localhost:{port}/map")
        logger.info(f"Urgence: http://localhost:{port}/emergency")
        logger.info("")
        logger.info(f"Ouvrez votre navigateur sur: http://localhost:{port}")
        logger.info("")
        
        # Démarrage du serveur
        socketio.run(app, host='0.0.0.0', port=port, debug=False)
        
    except KeyboardInterrupt:
        logger.info("🛑 Arrêt de Guardian Web Interface")
    except Exception as e:
        logger.error(f"❌ Erreur lors du démarrage: {e}")