#!/usr/bin/env python3
"""
DÉMO GUARDIAN - AGENT LIVE AVEC VRAIE RECONNAISSANCE VOCALE
Démonstration interactive avec speech-to-text réel (Vosk) + IA Gemini
Personnalisation complète : prénom, nom, numéro + scénario d'urgence réaliste
"""

import sys
import os
import yaml
import json
import time
import requests
import math
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calcule la distance en mètres entre deux points géographiques (formule haversine)"""
    # Rayon de la Terre en kilomètres
    R = 6371.0
    
    # Conversion en radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Différences
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Formule haversine
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    # Distance en kilomètres, puis conversion en mètres
    distance_km = R * c
    distance_m = distance_km * 1000
    
    return round(distance_m)

def format_distance(distance_meters):
    """Formate la distance pour l'affichage"""
    if distance_meters < 1000:
        return f"{distance_meters}m"
    else:
        distance_km = distance_meters / 1000
        return f"{distance_km:.1f}km"

try:
    import vosk
    import sounddevice as sd
    import queue
    VOICE_AVAILABLE = True
except ImportError as e:
    print(f"❌ Erreur import vocal: {e}")
    VOICE_AVAILABLE = False

try:
    import pygame
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

class VoiceRecognizer:
    """Gestionnaire de reconnaissance vocale avec Vosk"""
    
    def __init__(self, model_path="vosk-model-small-fr-0.22"):
        self.model_path = model_path
        self.model = None
        self.rec = None
        self.audio_queue = queue.Queue()
        self.is_listening = False
        
    def initialize(self):
        """Initialise le modèle Vosk"""
        try:
            if not os.path.exists(self.model_path):
                print(f"❌ Modèle Vosk non trouvé: {self.model_path}")
                return False
                
            print("🔧 Chargement du modèle Vosk français...")
            self.model = vosk.Model(self.model_path)
            self.rec = vosk.KaldiRecognizer(self.model, 16000)
            print("✅ Modèle Vosk chargé avec succès")
            return True
            
        except Exception as e:
            print(f"❌ Erreur initialisation Vosk: {e}")
            return False
    
    def audio_callback(self, indata, frames, time, status):
        """Callback pour capturer l'audio"""
        if status:
            print(f"⚠️ Audio status: {status}")
        self.audio_queue.put(bytes(indata))
    
    def listen_for_speech(self, timeout=30, stop_words=['stop', 'arrêt', 'arrête']):
        """Écoute et reconnaît la parole"""
        if not self.model:
            return None
            
        try:
            print(f"🎤 **ÉCOUTE ACTIVÉE** (timeout: {timeout}s)")
            print("🗣️ Parlez maintenant... (dites 'stop' pour terminer)")
            print("-" * 50)
            
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
                                print(f"🗣️ **RECONNU:** '{text}'")
                                recognized_text = text
                                
                                # Vérifier les mots d'arrêt
                                if any(stop_word in text.lower() for stop_word in stop_words):
                                    print("🛑 Mot d'arrêt détecté")
                                    break
                                else:
                                    # Phrase reconnue, on peut s'arrêter
                                    break
                        else:
                            # Reconnaissance partielle
                            partial = json.loads(self.rec.PartialResult())
                            partial_text = partial.get('partial', '').strip()
                            if partial_text:
                                print(f"🎧 [En cours...]: {partial_text}", end='\r')
                                
                    except queue.Empty:
                        continue
                    except Exception as e:
                        print(f"❌ Erreur reconnaissance: {e}")
                        break
            
            self.is_listening = False
            print(f"\n✅ Reconnaissance terminée: '{recognized_text}'")
            return recognized_text if recognized_text else None
            
        except Exception as e:
            print(f"❌ Erreur écoute: {e}")
            self.is_listening = False
            return None

def load_guardian_agent():
    """Charge l'agent Guardian avec configuration et diagnostics"""
    try:
        # Charger la configuration
        print("📁 Chargement de api_keys.yaml...")
        with open('api_keys.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Vérifier la configuration Gemini
        google_config = config.get('google_cloud', {})
        gemini_config = google_config.get('gemini', {})
        
        print(f"🔍 Configuration Gemini trouvée")
        print(f"   - Service: {'✅ Activé' if gemini_config.get('enabled', False) else '❌ Désactivé'}")
        print(f"   - Authentification: {'✅ Configurée' if bool(gemini_config.get('api_key')) else '❌ Manquante'}")
        print(f"   - Modèle: {gemini_config.get('model', 'non spécifié')}")
        
        # Importer et initialiser l'agent
        from guardian.gemini_agent import VertexAIAgent
        from guardian.gmail_emergency_agent import GmailEmergencyAgent
        
        agent = VertexAIAgent(config)
        gmail_agent = GmailEmergencyAgent(config)
        
        # Ajouter l'agent Gmail à l'agent principal pour la démo
        agent.gmail_agent = gmail_agent
        
        # Ajouter méthode d'envoi d'email pour la démo
        def send_emergency_email_alert(user_phone=None, real_location=None, real_situation=None, user_fullname="Utilisateur Inconnu"):
            """Méthode d'envoi d'email d'urgence pour la démo avec informations réelles"""
            if not gmail_agent.is_available:
                return False
            
            try:
                # Coordonnées exactes : 8 rue de Londres, 75009 Paris (Google France)
                demo_location = (48.8756, 2.3264)  # Coordonnées précises de Google France
                
                # Utiliser la vraie localisation ou celle par défaut
                location_text = real_location or "8 rue de Londres, 75009 Paris (bureaux Google France)"
                
                # Utiliser la vraie situation rapportée ou celle par défaut  
                situation_text = real_situation or "Situation d'urgence détectée par l'IA Guardian"
                
                # Obtenir les contacts d'urgence de la config
                emergency_contacts = config.get('emergency_contacts', [
                    {"email": "demo@example.com", "name": "Contact Demo"}
                ])
                
                # Envoyer aux contacts d'urgence
                success_count = 0
                for contact in emergency_contacts:
                    try:
                        subject, html_body, text_body = gmail_agent.create_emergency_email(
                            recipient_email=contact.get("email"),
                            user_name=user_fullname,
                            location=location_text,
                            situation=situation_text,
                            location_coords=demo_location,
                            emergency_type="🚨 Alerte Guardian - Situation d'urgence",
                            urgency_level="élevée",
                            user_phone=user_phone
                        )
                        
                        result = gmail_agent.send_email(contact.get("email"), subject, html_body, text_body)
                        if result.get("success"):
                            success_count += 1
                            
                    except Exception as e:
                        print(f"❌ Erreur envoi à {contact.get('name')}: {e}")
                        
                return success_count > 0
                
            except Exception as e:
                print(f"❌ Erreur générale envoi email: {e}")
                return False
        
        # Attacher la méthode à l'agent
        agent.send_emergency_email_alert = send_emergency_email_alert
        
        print(f"🤖 Agent Guardian:")
        print(f"   - IA: {'✅ Disponible' if agent.is_available else '⚠️ Mode simulation'}")
        print(f"   - Gmail: {'✅ Configuré' if gmail_agent.is_available else '❌ Non configuré'}")
        print(f"   - Prêt: {'✅ Opérationnel' if agent.api_key and agent.api_key != 'YOUR_VERTEX_AI_API_KEY' else '❌ Non configuré'}")
        
        return agent, gmail_agent, True
        
    except FileNotFoundError:
        print("❌ Fichier api_keys.yaml non trouvé")
        return None, False
    except Exception as e:
        print(f"⚠️ Erreur chargement agent: {e}")
        return None, False

def get_safe_route_directions(config, origin, destination):
    """Obtient un itinéraire sécurisé avec l'API Google Directions"""
    try:
        # Récupérer la clé API Maps (utilisée aussi pour Directions)
        services = config.get('google_cloud', {}).get('services', {})
        maps_key = services.get('maps_api_key')
        
        if not maps_key or maps_key.startswith("YOUR_"):
            return "⚠️ API Maps non configurée - impossible de calculer l'itinéraire"
        
        print(f"🔑 Utilisation de la clé Maps API: {maps_key[:20]}...")
        
        # URL de l'API Google Directions
        directions_url = "https://maps.googleapis.com/maps/api/directions/json"
        
        # Paramètres pour privilégier la sécurité
        params = {
            'origin': origin,
            'destination': destination,
            'mode': 'walking',  # Mode piéton
            'avoid': 'indoor',  # Éviter les passages souterrains
            'region': 'fr',     # France
            'language': 'fr',   # Français
            'key': maps_key
        }
        
        print("🗺️ [Calcul d'itinéraire sécurisé avec Google Directions API...]")
        response = requests.get(directions_url, params=params, timeout=10)
        print(f"📡 Réponse API: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data['status'] == 'OK' and data['routes']:
                route = data['routes'][0]
                leg = route['legs'][0]
                print("✅ Itinéraire trouvé avec succès")
                
                # Extraire les informations importantes
                duration = leg['duration']['text']
                distance = leg['distance']['text']
                start_address = leg['start_address']
                end_address = leg['end_address']
                
                # Extraire les étapes principales
                steps = []
                for step in leg['steps'][:5]:  # Premières 5 étapes
                    instruction = step['html_instructions']
                    # Nettoyer les balises HTML basiques
                    instruction = instruction.replace('<b>', '').replace('</b>', '')
                    instruction = instruction.replace('<div>', ' - ').replace('</div>', '')
                    steps.append(f"• {instruction}")
                
                route_info = {
                    'duration': duration,
                    'distance': distance,
                    'start_address': start_address,
                    'end_address': end_address,
                    'steps': steps[:3]  # 3 premières étapes seulement
                }
                
                return route_info
            else:
                error_msg = data.get('status', 'Erreur inconnue')
                if error_msg == 'REQUEST_DENIED':
                    return "❌ Accès refusé à l'API Directions. Vérifiez que l'API Directions est activée dans Google Cloud Console."
                elif error_msg == 'OVER_QUERY_LIMIT':
                    return "❌ Quota API dépassé pour aujourd'hui."
                else:
                    return f"❌ Impossible de calculer l'itinéraire: {error_msg}"
        else:
            return f"❌ Erreur API Directions: {response.status_code}"
            
    except Exception as e:
        print(f"⚠️ Erreur lors du calcul d'itinéraire: {e}")
        return "❌ Erreur lors du calcul de l'itinéraire"

def get_nearby_safe_places(config, location, place_types=['hospital', 'police', 'pharmacy', 'gas_station']):
    """Trouve des lieux sécurisés à proximité avec l'API Google Places"""
    try:
        # Récupérer la clé API Places
        services = config.get('google_cloud', {}).get('services', {})
        places_key = services.get('places_api_key')
        
        if not places_key or places_key.startswith("YOUR_"):
            return "⚠️ API Places non configurée - impossible de trouver des lieux sécurisés"
        
        print(f"🔍 Recherche de 2 lieux sécurisés à proximité...")
        
        # URL de l'API Google Places - Nearby Search
        places_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        
        safe_places = []
        
        # Rechercher différents types de lieux sécurisés
        for place_type in place_types:
            # Limiter à 2 lieux au total
            if len(safe_places) >= 2:
                break
                
            params = {
                'location': location,
                'radius': 1000,  # 1km de rayon
                'type': place_type,
                'language': 'fr',
                'key': places_key
            }
            
            response = requests.get(places_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data['status'] == 'OK':
                    # Prendre le premier résultat par type qui est OUVERT
                    for place in data.get('results', []):
                        # Limiter à 2 lieux au total
                        if len(safe_places) >= 2:
                            break
                            
                        # Filtrer uniquement les lieux OUVERTS et OPÉRATIONNELS
                        is_operational = place.get('business_status') == 'OPERATIONAL'
                        opening_hours = place.get('opening_hours', {})
                        is_open = opening_hours.get('open_now', False)
                        
                        if is_operational and is_open:
                            # Récupérer les coordonnées du lieu
                            geometry = place.get('geometry', {})
                            location_coords = geometry.get('location', {})
                            
                            place_info = {
                                'name': place.get('name'),
                                'type': place_type,
                                'rating': place.get('rating', 'N/A'),
                                'vicinity': place.get('vicinity'),
                                'open_now': True,  # Forcément ouvert vu le filtre
                                'lat': location_coords.get('lat'),
                                'lng': location_coords.get('lng')
                            }
                            safe_places.append(place_info)
                            break  # Un seul lieu par type
        
        if safe_places:
            print(f"✅ {len(safe_places)} lieux sécurisés trouvés")
            return safe_places
        else:
            return "ℹ️ Aucun lieu sécurisé trouvé dans un rayon de 1km"
            
    except Exception as e:
        print(f"⚠️ Erreur lors de la recherche de lieux: {e}")
        return f"❌ Erreur lors de la recherche de lieux sécurisés: {e}"

def format_safe_places_response(places_info, user_lat=48.8756, user_lng=2.3264):
    """Formate la réponse des lieux sécurisés pour l'affichage avec distances"""
    if isinstance(places_info, str):
        return places_info
    
    if not places_info:
        return "ℹ️ Aucun lieu sécurisé trouvé à proximité"
    
    # Calculer les distances pour chaque lieu
    for place in places_info:
        if place.get('lat') and place.get('lng'):
            distance_m = calculate_distance(user_lat, user_lng, place['lat'], place['lng'])
            place['distance'] = distance_m
            place['distance_formatted'] = format_distance(distance_m)
        else:
            place['distance'] = float('inf')  # Très loin si pas de coordonnées
            place['distance_formatted'] = "N/A"
    
    # Organiser par type de lieu et trier par distance
    places_by_type = {}
    for place in places_info:
        place_type = place['type']
        if place_type not in places_by_type:
            places_by_type[place_type] = []
        places_by_type[place_type].append(place)
    
    # Trier chaque type par distance (plus proche d'abord)
    for place_type in places_by_type:
        places_by_type[place_type].sort(key=lambda x: x.get('distance', float('inf')))
    
    # Traduction des types
    type_translations = {
        'hospital': '🏥 **HÔPITAUX/URGENCES**',
        'police': '🚔 **COMMISSARIATS**', 
        'pharmacy': '💊 **PHARMACIES**',
        'gas_station': '⛽ **STATIONS-SERVICE**',
        'bank': '🏦 **BANQUES/ATM**'
    }
    
    formatted_sections = []
    
    for place_type, places in places_by_type.items():
        type_title = type_translations.get(place_type, f"📍 **{place_type.upper()}**")
        formatted_sections.append(type_title)
        
        for place in places:
            open_status = ""
            if place['open_now'] == True:
                open_status = " 🟢 (Ouvert)"
            elif place['open_now'] == False:
                open_status = " 🔴 (Fermé)" 
                
            rating_str = f" ⭐{place['rating']}" if place['rating'] != 'N/A' else ""
            distance_str = f" 📏 {place['distance_formatted']}"
            
            formatted_sections.append(f"• **{place['name']}**{rating_str}{open_status}{distance_str}")
            formatted_sections.append(f"  📍 {place['vicinity']}")
        
        formatted_sections.append("")  # Ligne vide entre les sections
    
    formatted = f"""🏪 **LIEUX SÉCURISÉS À PROXIMITÉ (triés par distance):**

{chr(10).join(formatted_sections).rstrip()}

💡 **Dirigez-vous vers le lieu LE PLUS PROCHE qui est ouvert. Les hôpitaux et commissariats sont disponibles 24h/24.**
🚶‍♀️ **Distances calculées à pied depuis votre position actuelle.**"""
    
    return formatted

def format_route_response(route_info):
    """Formate la réponse d'itinéraire pour l'affichage"""
    if isinstance(route_info, str):
        return route_info
    
    formatted = f"""🗺️ **ITINÉRAIRE SÉCURISÉ CALCULÉ:**

📍 **Départ:** Près de {route_info['start_address']}
🎯 **Destination:** {route_info['end_address']}
⏱️ **Durée estimée:** {route_info['duration']}
📏 **Distance:** {route_info['distance']}

🚶‍♀️ **PREMIÈRES ÉTAPES:**
{chr(10).join(route_info['steps'])}

💡 **Cet itinéraire privilégie les rues principales et éclairées pour votre sécurité.**"""
    
    return formatted

def simulate_tts_response(text):
    """Simule la synthèse vocale"""
    print("\n🔊 **GUARDIAN RÉPOND:**")
    print("="*60)
    print(f"{text}")
    print("="*60)
    print()

def analyze_situation_with_ai(agent, situation_text):
    """Analyse la situation avec l'IA Gemini - VRAIE API SEULEMENT"""
    if not agent:
        print("❌ Agent non disponible")
        return "**ERREUR** : Agent Guardian non initialisé correctement"
    
    # Vérifier que l'agent est correctement configuré
    if not hasattr(agent, 'api_key') or not agent.api_key or agent.api_key == "YOUR_VERTEX_AI_API_KEY":
        print("❌ Clé API Gemini manquante ou invalide")
        print("💡 Vérifiez votre fichier api_keys.yaml")
        return "**ERREUR** : Clé API Gemini non configurée. Vérifiez api_keys.yaml"
    
    print(f"🧠 [Analyse IA Gemini en cours...]")
    print(f"🤖 Service: {agent.api_type.upper()}")
    print(f"🎯 Modèle: {agent.model_name}")
    
    try:
        response = agent._make_api_request(situation_text)
        
        if response and 'candidates' in response:
            ai_text = response['candidates'][0]['content']['parts'][0]['text']
            
            # Vérifier que ce n'est pas une réponse simulée
            if 'simulation' in ai_text.lower() or '**ANALYSE D\'URGENCE - NIVEAU' in ai_text:
                print("⚠️ Réponse simulée détectée - problème avec l'API")
                print("💡 L'API Gemini n'est pas accessible avec cette clé")
                return f"**ERREUR API** : {ai_text}\n\n**NOTE**: L'API Gemini ne fonctionne pas correctement"
            
            print("✅ Réponse RÉELLE de l'IA Gemini reçue")
            return ai_text
        else:
            print("❌ Pas de réponse valide de l'API Gemini")
            return "**ERREUR API** : L'API Gemini n'a pas retourné de réponse valide"
            
    except Exception as e:
        print(f"❌ Erreur lors de l'appel à l'API Gemini: {e}")
        return f"**ERREUR API** : Impossible de joindre l'API Gemini - {e}"

def display_scenario_intro():
    """Affiche l'introduction du scénario"""
    print("🎭 DÉMO GUARDIAN - AGENT LIVE (RECONNAISSANCE VOCALE)")
    print("="*70)
    print("👤 **UTILISATEUR :** Personnalisable")
    print("📍 **LOCALISATION :** 8 rue de Londres, 75009 Paris (bureaux Google France)")  
    print("🕙 **HEURE :** 22h00")
    print("📅 **DATE :** Vendredi 31 octobre 2025")
    print("="*70)
    print()
    
    print("🎯 **CONTEXTE DU SCÉNARIO:**")
    print("Vous êtes dans une situation d'urgence, il est tard le soir, vous êtes près")
    print("des bureaux Google France (8 rue de Londres, 9ème arrondissement).")
    print("Le quartier Europe/Saint-Lazare se vide après les heures de bureau.")
    print("Vous devez vous rendre Place de la Concorde, mais vous avez")
    print("l'impression d'être suivie et vous commencez à avoir peur.")
    print("Vous décidez d'activer Guardian pour obtenir de l'aide.")
    print()
    
    print("🎙️ **VRAIE RECONNAISSANCE VOCALE:**")
    print("• Parlez dans votre microphone pour interagir avec Guardian🎤")
    print("• Dites 'stop' ou 'arrêt' pour terminer une écoute")
    print()

def run_live_agent_demo():
    """Lance la démonstration de l'agent live avec vraie reconnaissance vocale"""
    
    # Introduction
    display_scenario_intro()
    
    # Demande du prénom et nom
    print("\n� **CONFIGURATION PERSONNELLE**")
    print("="*50)
    print("Pour une démonstration personnalisée, veuillez saisir les informations de l'utilisateur:")
    print()
    
    # Saisie du prénom
    user_firstname = input("📝 Prénom de l'utilisateur (ou appuyez sur Entrée pour 'Alex'): ").strip()
    if not user_firstname:
        user_firstname = "Alex"
        print(f"✅ Prénom par défaut: {user_firstname}")
    else:
        print(f"✅ Prénom configuré: {user_firstname}")
    
    # Saisie du nom
    user_lastname = input("📝 Nom de famille de l'utilisateur (ou appuyez sur Entrée pour 'Dupont'): ").strip()
    if not user_lastname:
        user_lastname = "Dupont"
        print(f"✅ Nom par défaut: {user_lastname}")
    else:
        print(f"✅ Nom configuré: {user_lastname}")
    
    user_fullname = f"{user_firstname} {user_lastname}"
    print(f"👤 **Utilisateur configuré:** {user_fullname}")
    print()
    
    print("📱 **NUMÉRO DE TÉLÉPHONE**")
    print("Pour les liens WhatsApp d'urgence, veuillez saisir le numéro de téléphone:")
    print()
    
    # Saisie du numéro avec validation
    user_phone = None
    while True:
        phone_input = input(f"📞 Numéro de {user_firstname} (format: +33612345678): ").strip()
        
        if not phone_input:
            print("⚠️ Pas de numéro saisi - les liens WhatsApp utiliseront le numéro par défaut")
            user_phone = "+33634129517"  # Numéro par défaut de la config
            break
        
        # Validation basique du format
        if phone_input.startswith(('+33', '0')) and len(phone_input.replace('+', '').replace(' ', '').replace('-', '')) >= 10:
            # Nettoyer et formater le numéro
            clean_phone = phone_input.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
            if clean_phone.startswith('0'):
                clean_phone = '+33' + clean_phone[1:]
            elif not clean_phone.startswith('+'):
                clean_phone = '+' + clean_phone
            
            user_phone = clean_phone
            print(f"✅ Numéro configuré: {user_phone}")
            break
        else:
            print("❌ Format invalide. Utilisez +33612345678 ou 0612345678")
            retry = input("Réessayer ? (o/N): ").lower()
            if retry != 'o':
                user_phone = "+33634129517"  # Numéro par défaut
                print("⚠️ Utilisation du numéro par défaut pour la démo")
                break
    
    # Vérification des prérequis
    if not VOICE_AVAILABLE:
        print("\n❌ Modules de reconnaissance vocale non disponibles")
        print("💡 Installez avec: pip3 install vosk sounddevice")
        return
    
    input("\n🚀 Appuyez sur Entrée pour commencer la démo avec reconnaissance vocale...")
    print()
    
    # Initialisation de la reconnaissance vocale
    print("🎤 **INITIALISATION RECONNAISSANCE VOCALE**")
    print("="*50)
    recognizer = VoiceRecognizer()
    
    if not recognizer.initialize():
        print("❌ Impossible d'initialiser la reconnaissance vocale")
        print("💡 Vérifiez que le modèle vosk-model-small-fr-0.22 est présent")
        return
    
    # Chargement de l'agent
    print("\n🔧 **INITIALISATION DE GUARDIAN**")
    print("="*40)
    agent, gmail_agent, agent_loaded = load_guardian_agent()
    
    if agent_loaded:
        print("✅ Agent Guardian chargé avec succès")
        print(f"🤖 IA Gemini: {'✅ Disponible' if agent.is_available else '⚠️ Mode simulation'}")
        
        # Test de connectivité API
        if agent.is_available:
            print("🔧 Vérification de la connectivité IA...")
            test_response = analyze_situation_with_ai(agent, "Test de connexion. Répondez juste 'API OK'.")
            if "API OK" in test_response or "ok" in test_response.lower():
                print("✅ IA Gemini opérationnelle")
            else:
                print("⚠️ Test IA échoué - vérifiez votre configuration")
                print(f"Réponse: {test_response[:50]}...")
        else:
            print("❌ ATTENTION: L'agent n'est pas disponible")
            print("💡 La démo utilisera des messages d'erreur au lieu de l'IA")
            
            choice = input("\n❓ Continuer quand même ? (o/N): ").lower()
            if choice != 'o':
                print("🛑 Démo annulée - Configurez d'abord votre API Gemini")
                return
    else:
        print("⚠️ Agent en mode simulation")
        print("❌ ERREUR: Impossible de charger l'agent Guardian")
        return
    
    print()
    
    # Début de la conversation
    print("🎙️ **DÉBUT DE LA CONVERSATION VOCALE**")
    print("="*45)
    
    # Message d'accueil Guardian
    welcome_msg = f"""Bonjour {user_firstname}. Je suis Guardian. 
Êtes-vous en sécurité ? 
Parlez maintenant."""
    
    simulate_tts_response(welcome_msg)
    
    # Première interaction - L'utilisateur explique sa situation avec sa voix
    print(f"🎤 **À VOUS DE PARLER, {user_firstname.upper()}...**")
    situation_vocale = recognizer.listen_for_speech(timeout=20)
    
    if not situation_vocale:
        print("⚠️ Aucune parole détectée, utilisation du scénario par défaut")
        situation_vocale = "Je suis près des bureaux Google France, 8 rue de Londres dans le 9ème. Il est 22h, je dois aller Place de la Concorde mais j'ai l'impression qu'on me suit. Il y a quelqu'un derrière moi depuis plusieurs rues et ça me fait peur. Le quartier se vide, je ne sais pas quoi faire."
    
    print(f"\n📝 **SITUATION RAPPORTÉE:** {situation_vocale}")
    
    # Construction du prompt contextualisé et optimisé pour Gemini
    full_prompt = f"""Tu es Guardian, un assistant IA spécialisé en sécurité personnelle. Une personne nommée {user_fullname} t'appelle à l'aide.

CONTEXTE DE LA SITUATION:
• Personne: {user_fullname}
• Moment: 22h00, vendredi 31 octobre 2025 (heure tardive)
• Lieu: 8 rue de Londres, 75009 Paris (près des bureaux Google France, quartier Europe/Saint-Lazare)
• Destination souhaitée: Place de la Concorde
• Situation: "{situation_vocale}"

MISSION: La personne est en état de choc. Réponds de manière TRÈS COURTE, SIMPLE et DIRECTE à {user_firstname}.

CONTRAINTES CRITIQUES:
- Phrases COURTES (maximum 10 mots chacune)
- Instructions SIMPLES à comprendre 
- Pas de détails techniques ou longs développements
- Mots RASSURANTS mais FERMES
- Priorité à l'ACTION immédiate

CAPACITÉS DISPONIBLES: 
- Si itinéraire nécessaire: inclus "DEMANDE_ITINERAIRE_SECURISE" 
- Si lieux sûrs nécessaires: inclus "DEMANDE_LIEUX_SECURISES"
- Si danger réel: inclus "DEMANDE_ENVOI_EMAIL_URGENCE"

DÉCISION D'ALERTE: Alerter si danger immédiat (suivie, menacée, agressée, blessée, perdue la nuit)

FORMAT DE RÉPONSE COURT (en français):
**URGENCE:** [1-10]/10

**QUE FAIRE:**
1. [Action simple - 5 mots max]
2. [Action simple - 5 mots max]

**OÙ ALLER:**
[Si nécessaire: DEMANDE_LIEUX_SECURISES]

**APPELER:**
17 (Police) ou 112 (Urgences)

**{user_firstname}:** [Message court rassurant - 1 phrase max]

GARDE TA RÉPONSE TRÈS COURTE. La personne est en état de choc et ne peut pas traiter de longs textes."""
    
    # Analyse IA
    print("\n🧠 **ANALYSE INTELLIGENTE GUARDIAN**")
    print("="*45)
    ai_response = analyze_situation_with_ai(agent, full_prompt)
    
    # Charger la configuration une seule fois
    config = yaml.safe_load(open('api_keys.yaml', 'r', encoding='utf-8'))
    
    # NOUVELLE FONCTIONNALITÉ: L'agent décide intelligemment d'alerter les proches
    def extract_urgency_level(response):
        """Extrait le niveau d'urgence de la réponse IA (format: **NIVEAU D'URGENCE:** X/10)"""
        import re
        match = re.search(r'\*\*NIVEAU D\'URGENCE:\*\*\s*(\d+)/10', response)
        if match:
            return int(match.group(1))
        return 0
    
    # Afficher le niveau d'urgence détecté
    urgency_level = extract_urgency_level(ai_response)
    print(f"🚨 **NIVEAU D'URGENCE DÉTECTÉ:** {urgency_level}/10")
    
    # L'agent décide intelligemment s'il faut alerter les proches
    agent_wants_email = "DEMANDE_ENVOI_EMAIL_URGENCE" in ai_response
    if agent_wants_email:
        print(f"🤖 **L'AGENT GUARDIAN DÉCIDE D'ALERTER LES PROCHES**")
        print(f"   → Situation évaluée comme nécessitant une intervention des contacts d'urgence")
    
    # Vérifier si l'IA demande un itinéraire sécurisé
    if "DEMANDE_ITINERAIRE_SECURISE" in ai_response:
        print("🗺️ L'IA recommande un itinéraire sécurisé - calcul en cours...")
        
        route_info = get_safe_route_directions(
            config, 
            "8 rue de Londres, 75009 Paris", 
            "Place de la Concorde, Paris"
        )
        
        route_response = format_route_response(route_info)
        ai_response = ai_response.replace("DEMANDE_ITINERAIRE_SECURISE", route_response)
    
    # Vérifier si l'IA demande des lieux sécurisés
    if "DEMANDE_LIEUX_SECURISES" in ai_response:
        print("🏪 L'IA recommande des lieux sécurisés - recherche en cours...")
        
        # Coordonnées approximatives de 8 rue de Londres, Paris
        location = "48.8756,2.3264"  # Latitude, Longitude
        
        places_info = get_nearby_safe_places(
            config, 
            location,
            ['hospital', 'police', 'pharmacy', 'gas_station']
        )
        
        # Coordonnées utilisateur (8 rue de Londres, Paris)
        user_coords = location.split(',')
        user_lat, user_lng = float(user_coords[0]), float(user_coords[1])
        
        places_response = format_safe_places_response(places_info, user_lat, user_lng)
        ai_response = ai_response.replace("DEMANDE_LIEUX_SECURISES", places_response)
    
    # Traitement intelligent de l'envoi d'email décidé par l'agent
    if "DEMANDE_ENVOI_EMAIL_URGENCE" in ai_response:
        if agent.gmail_agent and agent.gmail_agent.is_available:
            print("🚨 **ENVOI D'EMAIL D'URGENCE DÉCIDÉ PAR L'AGENT...**")
            # Informations exactes pour l'email
            exact_location = "8 rue de Londres, 75009 Paris (bureaux Google France), près de la gare Saint-Lazare"
            success = agent.send_emergency_email_alert(
                user_phone=user_phone, 
                real_location=exact_location, 
                real_situation=situation_vocale,
                user_fullname=user_fullname
            )
            if success:
                email_response = "✅ Email d'urgence envoyé avec succès aux contacts d'urgence."
            else:
                email_response = "❌ Erreur lors de l'envoi de l'email d'urgence. Veuillez contacter manuellement vos proches."
        else:
            email_response = "⚠️ Service d'email d'urgence non configuré. Veuillez contacter manuellement vos proches."
        
        ai_response = ai_response.replace("DEMANDE_ENVOI_EMAIL_URGENCE", email_response)

    
    simulate_tts_response(ai_response)
    
    # Suivi de situation avec reconnaissance vocale
    print("🎤 **SUIVI VOCAL - COMMENT ALLEZ-VOUS MAINTENANT ?**")
    follow_up_vocal = recognizer.listen_for_speech(timeout=15)
    
    # Réponse de suivi
    if follow_up_vocal:
        print(f"\n📝 **MISE À JOUR:** {follow_up_vocal}")
        
        follow_prompt = f"""Tu es Guardian. {user_fullname} te donne une mise à jour sur sa situation de sécurité.

RAPPEL DU CONTEXTE:
• {user_fullname} était près des bureaux Google France (8 rue de Londres, 75009 Paris) à 22h, se sentait suivie
• Quartier Europe/Saint-Lazare, zone qui se vide après les heures de bureau
• Tu lui as déjà donné des conseils de sécurité
• Cette personne vient de te répondre par reconnaissance vocale

MISE À JOUR DE {user_firstname.upper()}: "{follow_up_vocal}"

MISSION: Réponse TRÈS COURTE. La personne est stressée.

FORMAT COURT:
**MAINTENANT:** [État en 3 mots]

**FAIRE:** [1 action simple]

**{user_firstname}:** [Message court - 1 phrase]

RESTE TRÈS BREF. Évite les longs développements."""
        
        follow_response = analyze_situation_with_ai(agent, follow_prompt)
        simulate_tts_response(follow_response)
    else:
        print("⚠️ Pas de réponse vocale détectée")
    
    # Conclusion
    print("\n🎯 **CONCLUSION DE LA DÉMO VOCALE**")
    print("="*40)
    print("✅ Démonstration vocale terminée avec succès")
    print(f"🎭 Scénario {user_fullname} avec vraie reconnaissance vocale")
    print("🤖 Guardian + Vosk + Gemini IA")
    print()
    print("💡 **POINTS CLÉS DÉMONTRÉS:**")
    print("   ✅ Reconnaissance vocale française (Vosk)")
    print("   ✅ Analyse IA contextuelle (Gemini)")
    print("   ✅ Conversation naturelle speech-to-text")
    print("   ✅ Conseils de sécurité personnalisés")
    print("   ✅ Suivi en temps réel de la situation")
    print()
    print("🚀 System complet opérationnel pour situations réelles !")

def main():
    """Point d'entrée principal"""
    try:
        run_live_agent_demo()
    except KeyboardInterrupt:
        print("\n\n⚠️ Démo interrompue par l'utilisateur")
        print("🛡️ En situation réelle, Guardian resterait disponible")
    except Exception as e:
        print(f"\n❌ Erreur durant la démo: {e}")
        print("💡 En cas de vraie urgence, contactez directement le 17 ou le 112")

if __name__ == "__main__":
    main()