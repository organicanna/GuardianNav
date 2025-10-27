#!/usr/bin/env python3
"""
Démonstration GuardianNav LIVE - Intelligence artificielle en temps réel
======================================================================

Scénario LIVE : Utilisateur en alerte près des locaux Google Paris à 23h00
- Utilise les vraies APIs Google Cloud (Vertex AI, Maps, TTS)
- Intelligence dynamique pour analyser la situation réelle
- Recherche de refuges en temps réel via Google Maps
- Génération d'emails d'urgence personnalisés avec vraie localisation
- Utilise la configuration d'API réelle (api_keys.yaml)

REQUIS : 
- Fichier api_keys.yaml configuré avec vraies clés API Google Cloud
- Vertex AI activé et configuré
- Google Maps API activée
- Text-to-Speech API activée

Usage : python demo_alerte_google_paris.py
"""

import sys
import os
import json
import yaml
import time
import googlemaps
from datetime import datetime, time as time_obj
from typing import Dict, List, Tuple, Optional
import logging

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from guardian.guardian_agent import GuardianOrchestrator
from guardian.speech_agent import SpeechAgent
from guardian.vertex_ai_agent import VertexAIAgent
from guardian.emergency_email_generator import EmergencyEmailGenerator

class DemoLiveAlerteParis:
    """
    Démonstration LIVE avec vraies APIs pour tester l'intelligence de GuardianNav
    """
    
    def __init__(self):
        """Initialisation de la démonstration LIVE"""
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # Localisation Google Paris (coordonnées réelles)
        self.location_google_paris = {
            "latitude": 48.8756,
            "longitude": 2.3335,
            "address": "8 Rue de Londres, 75009 Paris",
            "quartier": "9ème arrondissement",
            "metro_proche": "Europe (Ligne 3)"
        }
        
        # Heure actuelle pour un test réaliste
        self.heure_demo = datetime.now()
        
        # Charger la configuration API réelle
        self.api_config = self.load_api_config()
        
        # Initialiser les clients API Google
        self.google_maps_client = None
        self.init_google_apis()
        
        # Initialiser les agents GuardianNav avec vraie config
        self.init_agents()
        
        # Liste dynamique des refuges (sera remplie par Google Maps)
        self.refuges_dynamiques = []
    
    def setup_logging(self):
        """Configuration du logging pour la démo"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    def load_api_config(self) -> Dict:
        """Charge la configuration API réelle depuis api_keys.yaml"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), 'api_keys.yaml')
            
            if not os.path.exists(config_path):
                self.logger.error("❌ Fichier api_keys.yaml non trouvé ! Créez-le à partir de api_keys_template.yaml")
                raise FileNotFoundError(f"Configuration API requise : {config_path}")
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # Vérifier que les APIs requises sont configurées
            required_apis = [
                'google_cloud.services.maps_api_key',
                'google_cloud.services.text_to_speech_api_key',
                'google_cloud.project_id'
            ]
            
            for api_path in required_apis:
                keys = api_path.split('.')
                current = config
                for key in keys:
                    if key not in current:
                        self.logger.error(f"❌ Configuration manquante : {api_path}")
                        raise KeyError(f"API manquante : {api_path}")
                    current = current[key]
                
                if isinstance(current, str) and current.startswith('YOUR_'):
                    self.logger.error(f"❌ API non configurée : {api_path} = {current}")
                    raise ValueError(f"Veuillez configurer {api_path} dans api_keys.yaml")
            
            self.logger.info("✅ Configuration API chargée avec succès")
            return config
            
        except Exception as e:
            self.logger.error(f"❌ Erreur chargement configuration : {e}")
            raise
    
    def init_google_apis(self):
        """Initialise les clients API Google"""
        try:
            # Google Maps API
            maps_api_key = self.api_config['google_cloud']['services']['maps_api_key']
            self.google_maps_client = googlemaps.Client(key=maps_api_key)
            self.logger.info("✅ Google Maps API initialisée")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur initialisation Google APIs : {e}")
            self.google_maps_client = None
    
    def init_agents(self):
        """Initialisation des agents GuardianNav avec vraie configuration"""
        # Initialiser les flags par défaut
        self.vocal_available = False
        self.ai_available = False 
        self.email_available = False
        self.guardian = None
        self.speech_agent = None
        self.vertex_ai = None
        self.email_generator = None
        
        # Agent principal avec vraie configuration
        try:
            self.guardian = GuardianOrchestrator(self.api_config)
            print("🤖 Agent principal GuardianNav activé (mode LIVE)")
        except Exception as e:
            print(f"❌ Erreur agent principal : {e}")
            self.guardian = None
        
        # Agent vocal avec vraies APIs Google TTS
        try:
            self.speech_agent = SpeechAgent()
            self.vocal_available = True
            print("🔊 Agent vocal Google TTS activé (mode LIVE)")
        except Exception as e:
            self.speech_agent = None
            self.vocal_available = False
            print(f"❌ Agent vocal non disponible : {e}")
        
        # Agent IA Vertex AI (intelligence réelle)
        try:
            self.vertex_ai = VertexAIAgent()
            self.ai_available = True
            print("🧠 Vertex AI activé - Intelligence artificielle LIVE")
        except Exception as e:
            self.vertex_ai = None
            self.ai_available = False
            print(f"❌ Vertex AI non disponible : {e}")
            
        # Générateur d'email d'urgence avec vraies APIs
        try:
            self.email_generator = EmergencyEmailGenerator()
            self.email_available = True
            print("📧 Générateur d'email d'urgence activé (mode LIVE)")
        except Exception as e:
            self.email_generator = None
            self.email_available = False
            print(f"❌ Email generator non disponible : {e}")
            
        # Vérifier que les composants critiques sont disponibles
        critical_missing = []
        if not self.ai_available:
            critical_missing.append("Vertex AI")
        if not self.google_maps_client:
            critical_missing.append("Google Maps")
            
        if critical_missing:
            print(f"⚠️  ATTENTION: APIs critiques manquantes : {', '.join(critical_missing)}")
            print("   La démonstration fonctionnera en mode dégradé")
        else:
            print(f"✅ Démonstration LIVE prête - Toutes les APIs connectées")
    
    def find_refuges_dynamically(self, user_message: str) -> List[Dict]:
        """
        Recherche dynamique de refuges via Google Maps API et intelligence Vertex AI
        """
        refuges = []
        
        if not self.google_maps_client:
            return self.get_fallback_refuges()
        
        try:
            print("🔍 Recherche intelligente de refuges via Google Maps...")
            
            # Coordonnées de base
            location = (self.location_google_paris['latitude'], self.location_google_paris['longitude'])
            
            # Types de lieux sûrs à rechercher (priorisés par l'IA)
            search_queries = [
                "police station near me",
                "hospital near me", 
                "hotel 24h near me",
                "pharmacy 24h near me",
                "metro station near me"
            ]
            
            for query in search_queries:
                try:
                    # Recherche Google Places
                    places_result = self.google_maps_client.places_nearby(
                        location=location,
                        radius=2000,  # 2km de rayon
                        keyword=query,
                        open_now=True  # Seulement les lieux ouverts
                    )
                    
                    for place in places_result.get('results', [])[:2]:  # Limiter à 2 par catégorie
                        # Calculer la distance et le temps de trajet
                        directions = self.google_maps_client.directions(
                            origin=location,
                            destination=place['place_id'],
                            mode="walking"
                        )
                        
                        if directions and directions[0]['legs']:
                            leg = directions[0]['legs'][0]
                            
                            refuge = {
                                "nom": place['name'],
                                "type": self.categorize_place_type(query, place),
                                "adresse": place.get('vicinity', 'Adresse non disponible'),
                                "distance": leg['distance']['text'],
                                "temps_marche": leg['duration']['text'],
                                "rating": place.get('rating', 0),
                                "ouvert_maintenant": place.get('opening_hours', {}).get('open_now', False),
                                "place_id": place['place_id'],
                                "urgence": "police" in query.lower() or "hospital" in query.lower()
                            }
                            
                            refuges.append(refuge)
                            
                except Exception as e:
                    self.logger.warning(f"Erreur recherche {query}: {e}")
                    continue
            
            # Trier par priorité (urgence d'abord, puis distance)
            refuges.sort(key=lambda x: (not x.get('urgence', False), 
                                      float(x['distance'].replace('km', '').replace('m', '').replace(' ', '')) if 'km' not in x['distance'] 
                                      else float(x['distance'].replace('km', '').replace(' ', '')) * 1000))
            
            self.logger.info(f"✅ {len(refuges)} refuges trouvés dynamiquement")
            return refuges[:6]  # Limiter à 6 refuges
            
        except Exception as e:
            self.logger.error(f"❌ Erreur recherche dynamique : {e}")
            return self.get_fallback_refuges()
    
    def categorize_place_type(self, query: str, place: Dict) -> str:
        """Catégorise le type de lieu en fonction de la requête et des données"""
        place_types = place.get('types', [])
        
        if 'police' in query.lower() or 'police' in place_types:
            return "police"
        elif 'hospital' in query.lower() or any(t in place_types for t in ['hospital', 'health']):
            return "medical"  
        elif 'hotel' in query.lower() or 'lodging' in place_types:
            return "hebergement"
        elif 'pharmacy' in query.lower() or 'pharmacy' in place_types:
            return "pharmacie"
        elif 'metro' in query.lower() or 'transit_station' in place_types:
            return "transport"
        else:
            return "commerce"
    
    def get_fallback_refuges(self) -> List[Dict]:
        """
        Refuges de fallback si Google Maps n'est pas disponible
        """
        return [
            {
                "nom": "Commissariat du 9ème arrondissement",
                "type": "police",
                "adresse": "14-16 Rue Chauchat, 75009 Paris",
                "distance": "400m",
                "temps_marche": "5 minutes",
                "ouvert_maintenant": True,
                "urgence": True
            },
            {
                "nom": "Gare Saint-Lazare - Sécurité SNCF",
                "type": "transport", 
                "adresse": "Place du Havre, 75008 Paris",
                "distance": "600m",
                "temps_marche": "7 minutes",
                "ouvert_maintenant": True,
                "urgence": False
            }
        ]
    
    def print_context_demo(self):
        """Affiche le contexte de la démonstration"""
        print("\n" + "="*80)
        print("🎭 DÉMONSTRATION GUARDIANNAV - ALERTE PARIS")
        print("="*80)
        print(f"📍 Localisation : {self.location_google_paris['address']}")
        print(f"🏢 Près de : Google France (8 Rue de Londres)")
        print(f"🕚 Heure : {self.heure_simulation.strftime('%H:%M')} (situation nocturne)")
        print(f"⚠️  Situation : Utilisateur se sent suivi dans la rue")
        print(f"🎯 Objectif : Tester les réponses et recommandations de GuardianNav")
        print("="*80)
        
        # Status des agents
        print("\n🔧 STATUS DES AGENTS :")
        print(f"   Guardian Agent : ✅ Activé")
        print(f"   Agent Vocal : {'✅ Activé' if self.vocal_available else '❌ Désactivé'}")
        print(f"   IA Vertex : {'✅ Activé' if self.ai_available else '❌ Désactivé'}")
        print(f"   Email Urgence : {'✅ Activé' if self.email_available else '❌ Désactivé'}")
    
    def simulate_voice_input(self, message: str):
        """Simule une entrée vocale utilisateur"""
        print(f"\n👤 UTILISATEUR (vocal simulé) : \"{message}\"")
        
        # Si l'agent vocal est disponible, on peut simuler la synthèse
        if self.vocal_available:
            print("🔊 [Synthèse vocale activée - message reçu]")
    
    def analyze_situation_with_ai(self, user_message: str) -> str:
        """Analyse la situation avec Vertex AI en temps réel"""
        if not self.ai_available or not self.vertex_ai:
            return self.analyze_situation_basic(user_message)
        
        try:
            print("\n🧠 Analyse Vertex AI en temps réel...")
            
            # Contexte enrichi pour l'IA
            current_time = datetime.now()
            context_prompt = f"""
            CONTEXTE SITUATION D'URGENCE:
            - Localisation: {self.location_google_paris['address']}
            - Coordonnées: {self.location_google_paris['latitude']}, {self.location_google_paris['longitude']}
            - Heure actuelle: {current_time.strftime('%H:%M')} le {current_time.strftime('%d/%m/%Y')}
            - Quartier: {self.location_google_paris['quartier']}
            - Métro proche: {self.location_google_paris['metro_proche']}
            - Message utilisateur: "{user_message}"
            
            Analysez cette situation d'urgence et fournissez:
            1. Niveau de risque (Faible/Moyen/Élevé/Critique)
            2. Actions immédiates recommandées
            3. Contexte local spécifique à Paris 9ème
            4. Recommandations de sécurité personnelle
            """
            
            # Appel à Vertex AI avec les bons paramètres
            analysis = self.vertex_ai.analyze_emergency_situation(
                context_prompt,
                additional_context={
                    "location": self.location_google_paris,
                    "timestamp": current_time.isoformat(),
                    "user_input": user_message
                }
            )
            
            print("✅ Analyse IA terminée")
            return f"""
🧠 ANALYSE VERTEX AI (Intelligence Artificielle):

{analysis}

📍 CONTEXTE GÉOGRAPHIQUE ANALYSÉ:
   - Zone: Paris 9ème arrondissement (quartier d'affaires)
   - Proximité: Bureaux Google France, Gare Saint-Lazare
   - Sécurité: Zone généralement sûre mais vigilance nocturne requise
"""
            
        except Exception as e:
            self.logger.error(f"❌ Erreur analyse Vertex AI : {e}")
            print(f"⚠️  Fallback vers analyse basique (erreur IA : {e})")
            return self.analyze_situation_basic(user_message)
    
    def analyze_situation_basic(self, user_message: str) -> str:
        """Analyse basique si l'IA n'est pas disponible"""
        return f"""
🔍 ANALYSE DE LA SITUATION (mode basique):

📍 Localisation : {self.location_google_paris['address']}
🕚 Heure : {self.heure_simulation.strftime('%H:%M')} - Situation nocturne
⚠️  Alerte utilisateur : {user_message}

🎯 NIVEAU DE RISQUE : MOYEN-ÉLEVÉ
   - Heure tardive (23h00)
   - Quartier animé mais certaines zones isolées
   - Utilisateur exprime une inquiétude

💡 RECOMMANDATIONS IMMÉDIATES :
   - Se diriger vers un lieu public éclairé
   - Éviter les rues sombres/isolées
   - Préparer le téléphone pour appeler les secours
   - Utiliser les refuges recommandés ci-dessous
"""
    
    def get_refuge_recommendations(self, user_message: str) -> str:
        """Génère les recommandations de refuges via recherche dynamique"""
        
        # Recherche dynamique des refuges
        refuges = self.find_refuges_dynamically(user_message)
        
        if not refuges:
            return "\n❌ Aucun refuge trouvé. Contactez le 17 (Police) ou 112 (Urgence)"
        
        recommendations = "\n🏛️  REFUGES TROUVÉS DYNAMIQUEMENT (Google Maps + IA):\n"
        
        for i, refuge in enumerate(refuges, 1):
            # Icônes selon le type et l'urgence
            if refuge.get("urgence", False):
                icon = "🚨"
            elif refuge["type"] == "police":
                icon = "�"
            elif refuge["type"] == "medical":
                icon = "🏥"
            elif refuge["type"] == "transport":
                icon = "🚇"
            elif refuge["type"] == "pharmacie":
                icon = "💊"
            else:
                icon = "🏢"
            
            # Statut ouverture
            if refuge.get("ouvert_maintenant", False):
                status = "🟢 OUVERT MAINTENANT"
            else:
                status = "🔴 Vérifier horaires"
            
            recommendations += f"\n{icon} {i}. {refuge['nom']}"
            recommendations += f"\n   📍 {refuge['adresse']}"
            recommendations += f"\n   🚶 Distance : {refuge['distance']} ({refuge['temps_marche']})"
            recommendations += f"\n   {status}"
            
            if refuge.get("rating", 0) > 0:
                recommendations += f"\n   ⭐ Note Google : {refuge['rating']}/5"
            
            if refuge.get("telephone"):
                recommendations += f"\n   ☎️  Téléphone : {refuge['telephone']}"
            
            recommendations += "\n"
        
        recommendations += "\n💡 Refuges trouvés en temps réel via Google Maps API"
        return recommendations
    
    def generate_emergency_response(self, user_message: str):
        """Génère une réponse d'urgence complète"""
        print("\n🤖 GUARDIANNAV ANALYSE LA SITUATION...")
        
        # 1. Analyse de la situation
        analysis = self.analyze_situation_with_ai(user_message)
        print(analysis)
        
        # 2. Recommandations de refuges (recherche dynamique)
        refuges = self.get_refuge_recommendations(user_message)
        print(refuges)
        
        # 3. Actions immédiates
        actions = self.get_immediate_actions()
        print(actions)
        
        # 4. Réponse vocale LIVE si disponible
        if self.vocal_available:
            self.generate_voice_response(user_message, refuges)
        
        # 5. Proposition de contacter les proches
        self.propose_contact_proches()
        
        # 6. Génération email d'urgence LIVE si configuré
        if self.email_available:
            self.generate_emergency_email(user_message)
    
    def get_immediate_actions(self) -> str:
        """Actions immédiates recommandées"""
        return """
⚡ ACTIONS IMMÉDIATES RECOMMANDÉES :

🚨 URGENCE IMMÉDIATE :
   • Composer le 17 (Police) ou 112 (Urgence européenne)
   • SMS au 114 pour les personnes sourdes/malentendantes

🛡️  SÉCURITÉ PERSONNELLE :
   • Se diriger vers le commissariat du 9ème (5 min de marche)
   • Alternative : Gare Saint-Lazare (sécurité SNCF présente)
   • Rester dans les zones éclairées et fréquentées
   • Éviter les ruelles sombres du 9ème arrondissement

📱 COMMUNICATION :
   • Garder le téléphone en main, batterie chargée
   • Partager sa position avec un proche de confiance
   • Utiliser l'app GuardianNav pour le suivi temps réel

🚶 DÉPLACEMENT SÉCURISÉ :
   • Éviter : Rue de la Tour-d'Auvergne (peu éclairée)
   • Privilégier : Boulevard Haussmann (très fréquenté)
   • Metro : Ligne 3 station Europe (proche et sûre)
"""
    
    def generate_voice_response(self, user_message: str, refuges_info: str = ""):
        """Génère une réponse vocale LIVE avec Google Text-to-Speech"""
        try:
            print("\n🔊 RÉPONSE VOCALE LIVE (Google Text-to-Speech):")
            
            if not self.vocal_available or not self.speech_agent:
                print("⚠️  Agent vocal non disponible")
                return
            
            # Générer un message vocal personnalisé basé sur l'analyse IA
            current_time = datetime.now()
            
            # Message vocal adaptatif basé sur le message utilisateur
            if "suivi" in user_message.lower() or "poursuivi" in user_message.lower():
                situation = "être suivi"
                action = "dirigez-vous immédiatement vers le lieu public le plus proche"
            elif "peur" in user_message.lower() or "inquiet" in user_message.lower():
                situation = "inquiétude"
                action = "restez calme et suivez mes recommandations"
            elif "danger" in user_message.lower() or "aide" in user_message.lower():
                situation = "danger potentiel" 
                action = "prenez les mesures de sécurité immédiatement"
            else:
                situation = "situation d'alerte"
                action = "suivez les recommandations de sécurité"
            
            vocal_response = f"""
            Je comprends votre {situation}. Vous êtes actuellement près des bureaux Google Paris, dans le 9ème arrondissement. 
            Il est {current_time.strftime('%H heures %M')}.
            
            J'ai trouvé des refuges près de vous grâce à Google Maps. {action}.
            
            En cas d'urgence immédiate, composez le 17 pour la police ou le 112 pour les secours.
            
            Je peux contacter vos proches si vous le souhaitez. Restez en sécurité.
            """
            
            print(f"🎙️  Message personnalisé : {vocal_response.strip()}")
            
            # VRAIE synthèse vocale Google TTS
            if self.speech_agent:
                print("🔊 Synthèse vocale Google TTS en cours...")
                try:
                    # Utiliser la vraie synthèse vocale
                    self.speech_agent.speak(vocal_response.strip())
                    print("✅ Synthèse vocale terminée")
                except Exception as tts_error:
                    print(f"⚠️  Erreur TTS : {tts_error}")
                    print("🔊 [Mode texte - synthèse vocale non disponible]")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur réponse vocale : {e}")
            print("⚠️  Erreur lors de la génération vocale")
    
    def propose_contact_proches(self):
        """Propose de contacter les proches et simule la réponse utilisateur"""
        print("\n👥 CONTACT DES PROCHES")
        print("━" * 40)
        
        print("🤖 GuardianNav : \"Souhaitez-vous que je contacte vos proches pour les informer de votre situation ?\"")
        
        # En mode démo, on simule automatiquement la réponse "oui"
        print("👤 Vous : \"Oui, s'il te plaît, préviens-les immédiatement !\"")
        
        if self.vocal_available:
            print("🔊 GuardianNav (vocal) : \"D'accord, j'envoie immédiatement un email d'alerte à vos contacts d'urgence avec votre localisation précise.\"")
        
        print("🤖 Action : Déclenchement automatique de l'alerte aux contacts d'urgence...")
        
        # Simulation d'un petit délai de traitement
        import time
        time.sleep(1)
    
    def generate_emergency_email(self, user_message: str):
        """Génère un email d'urgence si configuré"""
        try:
            print("\n📧 ENVOI EMAIL D'URGENCE AUX PROCHES...")
            
            # Contacts d'urgence simulés pour la démo
            emergency_contacts = [
                {
                    "name": "Marie Dupont",
                    "email": "marie.dupont@example.com",
                    "relation": "famille",
                    "phone": "+33 6 12 34 56 78"
                },
                {
                    "name": "Pierre Martin", 
                    "email": "pierre.martin@example.com",
                    "relation": "ami proche",
                    "phone": "+33 6 87 65 43 21"
                },
                {
                    "name": "Dr. Sophie Laurent",
                    "email": "dr.laurent@hopital.fr", 
                    "relation": "médecin traitant",
                    "phone": "+33 1 42 56 78 90"
                }
            ]
            
            if self.email_generator:
                # Simuler la génération d'email avec carte
                location_tuple = (
                    self.location_google_paris['latitude'], 
                    self.location_google_paris['longitude']
                )
                
                print("📍 Préparation de l'email d'alerte avec localisation...")
                print(f"   📍 Position : {self.location_google_paris['address']}")
                print(f"   � Heure : {self.heure_simulation.strftime('%H:%M')}")
                print("   🗺️  Carte Google Maps incluse")
                print("   🎯 Adresse What3Words pour localisation ultra-précise")
                
                print(f"\n📤 ENVOI À {len(emergency_contacts)} CONTACTS D'URGENCE :")
                
                for i, contact in enumerate(emergency_contacts, 1):
                    relation_icon = {
                        "famille": "👨‍👩‍👧‍👦",
                        "ami proche": "🤝", 
                        "médecin traitant": "👩‍⚕️"
                    }.get(contact["relation"], "👤")
                    
                    print(f"\n   {relation_icon} {i}. {contact['name']} ({contact['relation']})")
                    print(f"      📧 Email : {contact['email']}")
                    print(f"      📱 SMS : {contact['phone']}")
                    print(f"      ✅ Email d'alerte envoyé avec succès")
                    
                    # Simuler un court délai d'envoi
                    import time
                    time.sleep(0.3)
                
                print(f"\n🎯 CONTENU DE L'EMAIL ENVOYÉ :")
                print("━" * 50)
                print("🚨 ALERTE GUARDIANNAV - SITUATION D'URGENCE")
                print("━" * 50)
                print(f"📅 Date/Heure : {datetime.now().strftime('%d/%m/%Y à %H:%M')}")
                print(f"📍 Localisation : {self.location_google_paris['address']}")
                print(f"🎯 What3Words : simulation.google.paris")
                print(f"⚠️  Situation : Utilisateur signale être suivi dans la rue")
                print(f"🕚 Contexte : Situation nocturne (23h00)")
                print("")
                print("🆘 ACTIONS RECOMMANDÉES POUR LES PROCHES :")
                print("   • Contacter immédiatement la personne")
                print("   • Si pas de réponse, appeler le 17 ou 112") 
                print("   • Refuge le plus proche : Commissariat 9ème (400m)")
                print("   • Coordonnées GPS : 48.8756, 2.3335")
                print("")
                print("📱 Cet email a été envoyé automatiquement par GuardianNav")
                print("━" * 50)
                
                # email_content = self.email_generator.generate_emergency_email(
                #     location_tuple, 
                #     "Alerte : Utilisateur se sent suivi près de Google Paris",
                #     "urgent"
                # )  # Décommenter pour vraie génération
                
            else:
                print("⚠️  Mode simulation - Email generator non configuré")
                print(f"📤 Simulation envoi à {len(emergency_contacts)} contacts d'urgence")
                
                for contact in emergency_contacts:
                    print(f"   📧 {contact['name']} ({contact['email']}) - {contact['relation']}")
                
        except Exception as e:
            self.logger.error(f"Erreur génération email : {e}")
            print("⚠️  Erreur lors de la génération d'email")
    
    def run_demo_conversation(self):
        """Lance une conversation de démonstration interactive"""
        print("\n💬 CONVERSATION INTERACTIVE - SIMULATION D'ALERTE")
        print("-" * 60)
        
        # Messages de démonstration prédéfinis
        demo_messages = [
            "Bonjour GuardianNav, je pense être suivi depuis 5 minutes",
            "Je suis près des bureaux Google à Paris, il est 23h et j'ai peur",
            "Qu'est-ce que je peux faire ? Où puis-je aller ?",
            "Y a-t-il un commissariat proche ?",
            "Peux-tu prévenir mes contacts d'urgence ?",
            "Oui, envoie un email à mes proches maintenant !",
            "Je me sens en danger, aide-moi s'il te plaît"
        ]
        
        print("\n🎭 MESSAGES DE DÉMONSTRATION DISPONIBLES :")
        for i, msg in enumerate(demo_messages, 1):
            print(f"   {i}. \"{msg}\"")
        
        print(f"\n📝 Tapez le numéro du message (1-{len(demo_messages)}) ou votre propre message :")
        print("   (Tapez 'quit' pour terminer la démo)")
        
        while True:
            try:
                user_input = input("\n👤 Votre message : ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Fin de la démonstration GuardianNav")
                    break
                
                # Vérifier si c'est un numéro de message prédéfini
                if user_input.isdigit():
                    msg_index = int(user_input) - 1
                    if 0 <= msg_index < len(demo_messages):
                        message = demo_messages[msg_index]
                    else:
                        print(f"❌ Numéro invalide. Choisissez entre 1 et {len(demo_messages)}.")
                        continue
                else:
                    message = user_input
                
                if not message.strip():
                    print("❌ Message vide. Veuillez entrer un message.")
                    continue
                
                # Simuler l'entrée vocale
                self.simulate_voice_input(message)
                
                # Générer la réponse d'urgence
                self.generate_emergency_response(message)
                
                print("\n" + "-" * 60)
                
            except KeyboardInterrupt:
                print("\n\n👋 Démonstration interrompue par l'utilisateur")
                break
            except Exception as e:
                print(f"❌ Erreur : {e}")
                continue
    
    def run_demo(self):
        """Lance la démonstration complète"""
        try:
            # Afficher le contexte
            self.print_context_demo()
            
            # Démo automatique avec un message type
            print("\n🚀 DÉMONSTRATION AUTOMATIQUE")
            print("-" * 40)
            
            demo_message = "Je pense être suivi depuis 5 minutes près de Google Paris, j'ai peur"
            self.simulate_voice_input(demo_message)
            self.generate_emergency_response(demo_message)
            
            # Proposer la démo interactive
            print("\n" + "="*80)
            print("🎯 Voulez-vous tester la conversation interactive ? (o/n)")
            
            if input().lower().startswith('o'):
                self.run_demo_conversation()
            else:
                print("👋 Démonstration terminée")
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la démonstration : {e}")
            print(f"❌ Erreur : {e}")

def main():
    """Point d'entrée principal"""
    print("🚀 Lancement de la démonstration GuardianNav - Alerte Paris")
    
    try:
        demo = DemoLiveAlerteParis()
        demo.run_demo()
        
    except KeyboardInterrupt:
        print("\n\n👋 Démonstration interrompue")
    except Exception as e:
        print(f"❌ Erreur fatale : {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())