import threading
import time
import os
import logging
import queue
from guardian.GPS_agent import StaticAgent
from guardian.voice_agent import VoiceAgent
from guardian.speech_agent import SpeechAgent
from guardian.gemini_agent import GeminiAgent
from guardian.sms_agent import SMSAgent
from guardian.gmail_emergency_agent import GmailEmergencyAgent
from guardian.emergency_response import EmergencyResponse
from guardian.intelligent_advisor import IntelligentAdvisor, SmartResponseSystem
from guardian.emergency_locations import EmergencyLocationService
from guardian.fall_detector import FallDetector

class GuardianOrchestrator:
    """Orchestrateur principal pour Guardian selon le workflow défini"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        # Charger les clés API pour emails visuels
        try:
            import yaml
            with open('api_keys.yaml', 'r', encoding='utf-8') as f:
                api_keys_config = yaml.safe_load(f)
        except Exception:
            api_keys_config = {}
            
        self.emergency_response = EmergencyResponse(config.get('emergency_response', {}), api_keys_config)
        
        # Agent de synthèse vocale
        self.speech_agent = SpeechAgent(api_keys_config)
        
        # Agent SMS pour notifications d'urgence
        self.sms_agent = SMSAgent(api_keys_config)
        
        # Agent Gemini pour l'analyse avancée
        self.gemini_agent = GeminiAgent(api_keys_config)
        
        # Agent Gmail pour emails d'urgence
        self.gmail_agent = GmailEmergencyAgent(api_keys_config)
        
        # Système d'IA et de conseils (fallback si Gemini indisponible)
        self.intelligent_advisor = IntelligentAdvisor()
        self.smart_response_system = SmartResponseSystem(self.intelligent_advisor)
        
        # Système de localisation d'urgence
        try:
            api_config = {}  # Chargé depuis api_keys.yaml si disponible
            self.emergency_locations = EmergencyLocationService(api_config)
        except Exception as e:
            self.logger.warning(f"Service de localisation d'urgence non disponible: {e}")
            self.emergency_locations = None
        
        # Détecteur de chute
        self.fall_detector = FallDetector(
            speed_threshold_high=15.0,  # km/h - vitesse élevée à vélo
            speed_threshold_low=2.0,    # km/h - quasi-immobile
            acceleration_threshold=-8.0, # m/s² - décélération brutale
            stationary_time=30.0        # secondes sans mouvement = urgence
        )
        
        # États du système
        self.current_position = None
        self.agents_lock = threading.Lock()
        self.shutdown_event = threading.Event()
        self.response_queue = queue.Queue()
        
        # Timeout pour les réponses utilisateur
        self.response_timeout = config.get('emergency_response', {}).get('timeout_seconds', 600)
        
    def handle_alert(self, trigger_type: str, position: tuple = None):
        """Gère une alerte selon le workflow du diagramme"""
        self.logger.warning(f"ALERTE déclenchée: {trigger_type}")
        
        if position:
            self.current_position = position
        
        alert_message = f"ALERTE {trigger_type}. Tout va bien ? Répondez oui ou non."
        print(f"\n🚨 ALERTE ({trigger_type}) : Tout va bien ? 🚨")
        print("Répondez 'oui' ou 'non' (vocal ou texte)")
        
        # Synthèse vocale de l'alerte
        self.speech_agent.speak_alert("emergency", alert_message)
        
        # Démarrer l'écoute de réponse avec timeout
        response = self._wait_for_response()
        
        if response == "oui":
            self._handle_positive_response()
        elif response == "non":
            self._handle_negative_response()
        else:
            self._handle_no_response()
    
    def _wait_for_response(self) -> str:
        """Attend une réponse utilisateur avec timeout"""
        self.logger.info(f"Attente de réponse (timeout: {self.response_timeout}s)")
        
        try:
            # Attendre une réponse pendant le timeout
            response = self.response_queue.get(timeout=self.response_timeout)
            self.logger.info(f"Réponse reçue: {response}")
            return response.lower()
        except queue.Empty:
            self.logger.warning("Aucune réponse reçue dans le délai imparti")
            return None
    
    def _handle_positive_response(self):
        """Gère une réponse positive ('oui')"""
        self.logger.info("Réponse positive reçue - Situation normale")
        confirmation_message = "OK, merci de votre réponse. Surveillance continue."
        print("✅ OK, merci de votre réponse. Surveillance continue.\n")
        
        # Synthèse vocale de confirmation
        self.speech_agent.speak_alert("confirmation", confirmation_message)
        
        # Envoyer notification de confirmation si configuré
        self.emergency_response.send_confirmation_alert("Situation normale - Utilisateur a confirmé")
    
    def _handle_negative_response(self):
        """Gère une réponse négative ('non') avec IA"""
        self.logger.warning("Réponse négative reçue - Demande d'aide")
        question_message = "Que se passe-t-il ? Décrivez votre situation. Le système IA va analyser votre réponse."
        print("⚠️  Que se passe-t-il ? Décrivez votre situation :")
        print("🤖 Le système IA va analyser votre réponse pour vous conseiller...")
        
        # Synthèse vocale de la question
        self.speech_agent.speak_alert("emergency", question_message)
        
        # Demander des détails sur la situation
        try:
            reason = self.response_queue.get(timeout=120)  # 2 minutes pour expliquer
            self.logger.warning(f"Motif reçu: {reason}")
            
            # Analyser la situation avec Gemini ou IA de fallback
            if self.gemini_agent.is_available:
                ai_analysis = self.gemini_agent.analyze_emergency_situation(
                    reason, 
                    {
                        'position': self.current_position,
                        'trigger_type': 'user_negative_response',
                        'time_of_day': 'current'
                    }
                )
                
                # Message personnalisé de Gemini
                personalized_message = self.gemini_agent.get_personalized_emergency_message(ai_analysis)
                print("\n" + "="*60)
                print(f"🤖 ANALYSE GEMINI 2.5 FLASH:")
                print(personalized_message)
                print("="*60)
                
                # Synthèse vocale des conseils IA
                self.speech_agent.speak_alert("info", ai_analysis.get('specific_advice', ''))
                
                # Déclencher l'assistance avec l'analyse Gemini
                self._trigger_emergency_assistance_with_gemini(reason, ai_analysis)
                
            else:
                # Fallback vers l'ancien système IA
                smart_response = self.smart_response_system.process_emergency_response(reason, "emergency_description")
                
                print("\n" + "="*60)
                print(smart_response["message"])
                print("="*60)
                
                # Synthèse vocale des conseils IA
                self.speech_agent.speak_alert("info", smart_response["message"])
                
                # Déclencher l'assistance avec les conseils IA
                self._trigger_emergency_assistance_with_ai(reason, smart_response["analysis"])
            
        except queue.Empty:
            reason = "Aucun détail fourni"
            self.logger.warning("Aucun détail fourni par l'utilisateur")
            # Déclencher l'assistance sans analyse IA
            self._trigger_emergency_assistance(reason)
    
    def _handle_no_response(self):
        """Gère l'absence de réponse (timeout)"""
        self.logger.critical("AUCUNE RÉPONSE - Déclenchement d'urgence automatique")
        emergency_message = "AUCUNE RÉPONSE DÉTECTÉE. Je déclenche automatiquement l'urgence."
        print("🚨 AUCUNE RÉPONSE DÉTECTÉE - DÉCLENCHEMENT D'URGENCE AUTOMATIQUE 🚨")
        
        # Synthèse vocale d'urgence critique
        self.speech_agent.speak_alert("emergency", emergency_message)
        
        self._trigger_emergency_assistance("Aucune réponse de l'utilisateur")
    
    def _trigger_emergency_assistance(self, reason: str):
        """Déclenche l'assistance d'urgence complète"""
        self.logger.critical(f"Déclenchement assistance d'urgence: {reason}")
        
        print("🆘 ASSISTANCE D'URGENCE DÉCLENCHÉE:")
        print("   📍 Envoi de localisation aux contacts")
        print("   📞 Notification des contacts d'urgence")
        print("   ⏱️  Escalade automatique programmée")
        
        # Envoyer la localisation aux contacts
        if self.current_position:
            self.emergency_response.send_location_to_contacts(self.current_position, reason)
        
        # Envoyer aussi le SMS d'urgence
        emergency_context = {
            'emergency_type': 'URGENCE GÉNÉRALE',
            'what3words': ''
        }
        self._send_emergency_notifications(emergency_context, reason)
        
        # Programmer l'escalade d'urgence
        self._schedule_emergency_escalation(reason)
        
        print("✅ Contacts d'urgence notifiés. Aide en route.")
    
    def _trigger_emergency_assistance_with_ai(self, reason: str, ai_analysis: dict):
        """Déclenche l'assistance d'urgence avec analyse IA"""
        self.logger.critical(f"Déclenchement assistance d'urgence avec IA: {reason}")
        
        # Actions immédiates basées sur l'analyse IA
        print(f"\n🤖 **ASSISTANCE IA ACTIVÉE** - Type: {ai_analysis['emergency_type']}")
        print(f"🚨 Urgence: {ai_analysis['urgency_level']}")
        
        print("\n📋 **ACTIONS IMMÉDIATES:**")
        for action in ai_analysis['immediate_actions']:
            print(f"   ✓ {action}")
        
        # Cas spéciaux selon le type d'urgence
        if ai_analysis['emergency_type'] == 'security' and ai_analysis['urgency_level'] == 'high':
            self._handle_immediate_danger_situation(reason, ai_analysis)
        else:
            self._handle_standard_emergency(reason, ai_analysis)
        
        # Programmer l'escalade avec priorité selon l'urgence
        urgency_multiplier = {"high": 0.3, "medium": 1.0, "low": 2.0}
        escalation_delay = 300 * urgency_multiplier.get(ai_analysis['urgency_level'], 1.0)  # 1.5-10 min
        self._schedule_emergency_escalation(reason, int(escalation_delay))
    
    def _trigger_emergency_assistance_with_gemini(self, reason: str, gemini_analysis: dict):
        """Déclenche l'assistance d'urgence avec analyse Gemini avancée"""
        self.logger.critical(f"Déclenchement assistance d'urgence avec Gemini: {reason}")
        
        urgency_level = gemini_analysis.get('urgency_level', 5)
        emergency_type = gemini_analysis.get('emergency_type', 'Urgence')
        
        # Actions immédiates basées sur l'analyse Gemini
        print(f"\n🧠 **GEMINI 2.5 FLASH ACTIVÉ** - Type: {emergency_type}")
        print(f"🚨 Niveau d'urgence: {urgency_level}/10 ({gemini_analysis.get('urgency_category', 'modérée')})")
        
        # Afficher les risques identifiés
        risks = gemini_analysis.get('risks_identified', [])
        if risks:
            print(f"\n⚠️ **RISQUES IDENTIFIÉS:**")
            for risk in risks:
                print(f"   • {risk}")
        
        # Actions immédiates
        actions = gemini_analysis.get('immediate_actions', [])
        if actions:
            print(f"\n📋 **ACTIONS IMMÉDIATES:**")
            for i, action in enumerate(actions, 1):
                print(f"   {i}. {action}")
        
        # Services d'urgence recommandés
        emergency_services = gemini_analysis.get('emergency_services', 'Aucun')
        if emergency_services != 'Aucun':
            print(f"\n📞 **SERVICE RECOMMANDÉ:** {emergency_services}")
        
        # Cas spéciaux selon le niveau d'urgence Gemini
        if urgency_level >= 8:
            self._handle_gemini_critical_emergency(reason, gemini_analysis)
        elif urgency_level >= 6:
            self._handle_gemini_high_emergency(reason, gemini_analysis)
        else:
            self._handle_gemini_standard_emergency(reason, gemini_analysis)
        
        # Programmer l'escalade basée sur l'urgence Gemini
        escalation_delays = {
            10: 60,   # 1 minute pour urgence maximale
            9: 120,   # 2 minutes pour critique
            8: 180,   # 3 minutes pour grave
            7: 300,   # 5 minutes pour élevée
            6: 450,   # 7.5 minutes pour modérée-haute
            5: 600,   # 10 minutes standard
        }
        delay = escalation_delays.get(urgency_level, 600)
        self._schedule_emergency_escalation(reason, delay)
    
    def _handle_gemini_critical_emergency(self, reason: str, analysis: dict):
        """Gère les urgences critiques selon Gemini (niveau 8-10)"""
        self.logger.critical("URGENCE CRITIQUE GEMINI")
        
        print(f"\n🚨 **URGENCE CRITIQUE DÉTECTÉE PAR IA** 🚨")
        print(f"🤖 Confidence Gemini: Situation nécessitant intervention immédiate")
        
        # Instructions vocales d'urgence critique
        critical_instructions = analysis.get('immediate_actions', [])[:3]
        if critical_instructions:
            self.speech_agent.speak_emergency_instructions(critical_instructions)
        
        # Localiser l'aide d'urgence
        if self.current_position and self.emergency_locations:
            print(f"\n🚑 Recherche d'aide d'urgence immédiate...")
            
            emergency_help = self.emergency_locations.find_emergency_refuges(self.current_position, radius_m=1000)
            transports = self.emergency_locations.find_emergency_transport(self.current_position, radius_m=500)
            
            help_message = self.emergency_locations.format_emergency_locations_message(
                emergency_help, transports, current_location=self.current_position
            )
            
            # Alerte immédiate avec analyse Gemini
            enhanced_reason = f"{reason}\n\n🧠 ANALYSE GEMINI 2.5 FLASH:\n"
            enhanced_reason += f"- Type: {analysis['emergency_type']}\n"
            enhanced_reason += f"- Urgence: {analysis['urgency_level']}/10\n"
            enhanced_reason += f"- Conseils IA: {analysis.get('specific_advice', '')}\n\n{help_message}"
            
            self.emergency_response.send_immediate_danger_alert(self.current_position, enhanced_reason)
            
            # Envoyer emails d'urgence aux proches pour urgence critique
            self.send_emergency_email_alert(
                user_name="Utilisateur Guardian",
                location=f"Position GPS: {self.current_position}",
                situation=enhanced_reason,
                urgency_level=analysis['urgency_level']
            )
            
            # Envoyer aussi le SMS d'urgence
            emergency_context = {
                'emergency_type': 'URGENCE CRITIQUE',
                'what3words': analysis.get('what3words', '')
            }
            self._send_emergency_notifications(emergency_context, reason)
        else:
            # Alerte critique sans localisation
            enhanced_reason = f"{reason}\n\n🧠 ANALYSE GEMINI CRITIQUE:\n{analysis.get('specific_advice', '')}"
            self.emergency_response.send_immediate_danger_alert(self.current_position, enhanced_reason)
            
            # Envoyer aussi le SMS d'urgence
            emergency_context = {
                'emergency_type': 'URGENCE CRITIQUE',
                'what3words': analysis.get('what3words', '')
            }
            self._send_emergency_notifications(emergency_context, reason)
    
    def _handle_gemini_high_emergency(self, reason: str, analysis: dict):
        """Gère les urgences élevées selon Gemini (niveau 6-7)"""
        print(f"\n🆘 **URGENCE ÉLEVÉE - ASSISTANCE IA RENFORCÉE**")
        
        if self.current_position and self.emergency_locations:
            print(f"\n🔍 Recherche d'assistance adaptée...")
            
            refuges = self.emergency_locations.find_emergency_refuges(self.current_position)
            transports = self.emergency_locations.find_emergency_transport(self.current_position)
            
            refuges_message = self.emergency_locations.format_emergency_locations_message(
                refuges, transports, current_location=self.current_position
            )
            
            # Notification avec analyse Gemini complète
            enhanced_reason = f"{reason}\n\n🧠 ANALYSE GEMINI:\n"
            enhanced_reason += f"- Type: {analysis['emergency_type']}\n"
            enhanced_reason += f"- Niveau: {analysis['urgency_level']}/10 ({analysis['urgency_category']})\n"
            enhanced_reason += f"- Conseils: {analysis.get('specific_advice', '')}\n"
            if analysis.get('emergency_services') != 'Aucun':
                enhanced_reason += f"- Service recommandé: {analysis['emergency_services']}\n"
            enhanced_reason += f"\n{refuges_message}"
            
            self.emergency_response.send_location_with_refuges_info(self.current_position, refuges_message, enhanced_reason)
            
            # Envoyer emails d'urgence aux proches pour urgence élevée
            self.send_emergency_email_alert(
                user_name="Utilisateur Guardian",
                location=f"Position GPS: {self.current_position}",
                situation=enhanced_reason,
                urgency_level=analysis['urgency_level']
            )
            
            # Envoyer aussi le SMS d'urgence
            emergency_context = {
                'emergency_type': 'URGENCE ÉLEVÉE',
                'what3words': analysis.get('what3words', '')
            }
            self._send_emergency_notifications(emergency_context, reason)
        else:
            # Fallback sans localisation
            enhanced_reason = f"{reason}\n\n🧠 ANALYSE GEMINI:\n{analysis.get('specific_advice', '')}"
            self.emergency_response.send_location_to_contacts(self.current_position, enhanced_reason)
            
            # Envoyer aussi le SMS d'urgence
            emergency_context = {
                'emergency_type': 'URGENCE ÉLEVÉE',
                'what3words': analysis.get('what3words', '')
            }
            self._send_emergency_notifications(emergency_context, reason)
    
    def _handle_gemini_standard_emergency(self, reason: str, analysis: dict):
        """Gère les urgences standard avec analyse Gemini (niveau 1-5)"""
        print(f"\n📋 **ASSISTANCE AVEC ANALYSE IA PERSONNALISÉE**")
        
        # Message rassurant de Gemini
        reassurance = analysis.get('reassurance_message', '')
        if reassurance:
            print(f"💬 {reassurance}")
            self.speech_agent.speak_alert("confirmation", reassurance)
        
        # Notification standard avec conseils IA
        enhanced_reason = f"{reason}\n\n🤖 CONSEILS GEMINI:\n{analysis.get('specific_advice', '')}"
        
        if analysis.get('follow_up_needed', True):
            enhanced_reason += f"\n\nSuivi recommandé par l'IA."
        
        self.emergency_response.send_location_to_contacts(self.current_position, enhanced_reason)
        
        # Envoyer aussi le SMS d'urgence
        emergency_context = {
            'emergency_type': 'URGENCE STANDARD',
            'what3words': analysis.get('what3words', '')
        }
        self._send_emergency_notifications(emergency_context, reason)
        
        print(f"\n✅ Contacts notifiés avec analyse personnalisée Gemini (Email + SMS)")

    def _handle_immediate_danger_situation(self, reason: str, ai_analysis: dict):
        """Gère une situation de danger immédiat (agression, menace, etc.)"""
        self.logger.critical("SITUATION DE DANGER IMMÉDIAT DÉTECTÉE")
        
        print("\n🚨 **DANGER IMMÉDIAT DÉTECTÉ - PROTOCOLE D'URGENCE ACTIVÉ** 🚨")
        
        if self.current_position and self.emergency_locations:
            print("\n🔍 Recherche de refuges et moyens d'évasion...")
            
            # Trouver refuges et transports d'urgence
            refuges = self.emergency_locations.find_emergency_refuges(self.current_position, radius_m=300)
            transports = self.emergency_locations.find_emergency_transport(self.current_position, radius_m=500)
            
            # Formatter les informations avec itinéraires d'évacuation
            refuges_message = self.emergency_locations.format_emergency_locations_message(
                refuges, transports, current_location=self.current_position
            )
            
            print(refuges_message)
            
            # Envoyer alerte critique aux contacts avec refuges
            enhanced_reason = f"DANGER IMMÉDIAT: {reason}\n\n{refuges_message}"
            self.emergency_response.send_immediate_danger_alert(self.current_position, enhanced_reason)
            
            # Envoyer aussi le SMS d'urgence
            emergency_context = {
                'emergency_type': 'DANGER IMMÉDIAT',
                'what3words': ai_analysis.get('what3words', '')
            }
            self._send_emergency_notifications(emergency_context, f"DANGER IMMÉDIAT: {reason}")
            
            print("\n🚨 ALERTE DE DANGER IMMÉDIAT envoyée à tous vos contacts! (Email + SMS)")
            print("📍 Informations sur les refuges et transports incluses")
            
        else:
            # Fallback si pas de service de localisation
            self.emergency_response.send_immediate_danger_alert(self.current_position, reason)
            
            # Envoyer aussi le SMS d'urgence
            emergency_context = {
                'emergency_type': 'DANGER IMMÉDIAT',
                'what3words': ai_analysis.get('what3words', '')
            }
            self._send_emergency_notifications(emergency_context, f"DANGER IMMÉDIAT: {reason}")
        
        print("\n⚡ **ACTIONS RECOMMANDÉES IMMÉDIATEMENT:**")
        print("   1. 📞 Appelez le 17 (Police) si en danger immédiat")
        print("   2. 🏃 Dirigez-vous vers le refuge le plus proche")
        print("   3. 🚇 Utilisez les transports publics pour vous éloigner")
        print("   4. 📱 Restez en contact avec vos proches")
        
        # Instructions vocales d'urgence
        emergency_instructions = [
            "Appelez le 17 si en danger immédiat",
            "Dirigez-vous vers le refuge le plus proche", 
            "Utilisez les transports publics pour vous éloigner",
            "Restez en contact avec vos proches"
        ]
        self.speech_agent.speak_emergency_instructions(emergency_instructions)

    def _handle_standard_emergency(self, reason: str, ai_analysis: dict):
        """Gère une urgence standard avec refuges et transports"""
        print("\n🆘 **ASSISTANCE D'URGENCE AVEC REFUGES**")
        
        if self.current_position and self.emergency_locations:
            print("\n🔍 Recherche d'aide à proximité...")
            
            # Trouver refuges et transports
            refuges = self.emergency_locations.find_emergency_refuges(self.current_position)
            transports = self.emergency_locations.find_emergency_transport(self.current_position)
            
            # Formatter et afficher avec itinéraires
            refuges_message = self.emergency_locations.format_emergency_locations_message(
                refuges, transports, current_location=self.current_position
            )
            print(refuges_message)
            
            # Notification avec informations de refuges
            enhanced_reason = f"{reason}\n\nAnalyse IA:\n- Type: {ai_analysis['emergency_type']}\n- Urgence: {ai_analysis['urgency_level']}\n\n{refuges_message}"
            self.emergency_response.send_location_with_refuges_info(self.current_position, refuges_message, enhanced_reason)
            
            # Envoyer aussi le SMS d'urgence
            emergency_context = {
                'emergency_type': 'URGENCE STANDARD',
                'what3words': ai_analysis.get('what3words', '')
            }
            self._send_emergency_notifications(emergency_context, reason)
            
        else:
            # Fallback standard
            enhanced_reason = f"{reason}\n\nAnalyse IA:\n- Type: {ai_analysis['emergency_type']}\n- Urgence: {ai_analysis['urgency_level']}\n- Actions: {', '.join(ai_analysis['immediate_actions'])}"
            self.emergency_response.send_location_to_contacts(self.current_position, enhanced_reason)
            
            # Envoyer aussi le SMS d'urgence
            emergency_context = {
                'emergency_type': 'URGENCE STANDARD',
                'what3words': ai_analysis.get('what3words', '')
            }
            self._send_emergency_notifications(emergency_context, reason)
        
        print("\n✅ Contacts notifiés avec informations d'aide à proximité (Email + SMS)")
    
    def handle_fall_detection(self, fall_info: dict):
        """
        Gère la détection d'une chute
        
        Args:
            fall_info: Informations sur la chute détectée
        """
        fall_type = fall_info.get('fall_type', 'chute_generale')
        severity = fall_info.get('severity', 'modérée')
        position = fall_info.get('position', self.current_position)
        
        print(f"\n🚨 CHUTE DÉTECTÉE ! 🚨")
        print(f"Type: {self._translate_fall_type(fall_type)}")
        print(f"Sévérité: {severity}")
        print(f"Vitesse avant chute: {fall_info.get('previous_speed', 0):.1f} km/h")
        print(f"Décélération: {fall_info.get('acceleration', 0):.1f} m/s²")
        
        # Message personnalisé selon le type de chute
        message = self._get_fall_response_message(fall_type, severity)
        print(f"\n🤖 Guardian: {message}")
        
        # Synthèse vocale pour la chute
        self.speech_agent.speak_fall_alert(fall_info)
        
        # Demander confirmation de l'état
        confirmation_question = "Êtes-vous blessé ? Répondez oui ou non dans les 30 secondes. Sans réponse, j'alerterai les secours."
        print(f"\n❓ Êtes-vous blessé(e) ? (Répondez 'oui' ou 'non' dans les 30 secondes)")
        print("   Si aucune réponse, j'alerterai automatiquement les secours...")
        
        # Synthèse vocale de la question
        self.speech_agent.speak_alert("emergency", confirmation_question)
        
        # Démarrer countdown d'urgence
        self._start_fall_emergency_countdown(fall_info)
    
    def handle_post_fall_emergency(self, post_fall_info: dict):
        """
        Gère l'urgence prolongée après une chute
        """
        time_since_fall = post_fall_info.get('time_since_fall', 0)
        
        print(f"\n🆘 URGENCE MAXIMALE - IMMOBILITÉ PROLONGÉE APRÈS CHUTE 🆘")
        print(f"Temps écoulé depuis la chute: {time_since_fall:.0f} secondes")
        print(f"Mouvement détecté: {post_fall_info.get('movement_since_fall', 0):.1f}m")
        
        # Alerte immédiate sans demander confirmation
        self._trigger_fall_emergency_response(post_fall_info, immediate=True)
    
    def _translate_fall_type(self, fall_type: str) -> str:
        """Traduit les types de chute en français"""
        translations = {
            'chute_velo': '🚴 Chute à vélo',
            'chute_haute_vitesse': '🏃 Chute à haute vitesse', 
            'impact_brutal': '💥 Impact brutal',
            'chute_generale': '⚠️ Chute générale'
        }
        return translations.get(fall_type, fall_type)
    
    def _get_fall_response_message(self, fall_type: str, severity: str) -> str:
        """
        Génère un message personnalisé selon le type et la sévérité de chute
        """
        if fall_type == 'chute_velo':
            if severity in ['critique', 'grave']:
                return "J'ai détecté une chute à vélo potentiellement grave. Restez immobile si possible et ne bougez pas la tête si vous ressentez des douleurs au cou. Les secours arrivent."
            else:
                return "Chute à vélo détectée. Vérifiez si vous pouvez bouger vos membres sans douleur. Attention aux blessures qui ne sont pas immédiatement visibles."
                
        elif fall_type == 'chute_haute_vitesse':
            return "Chute à haute vitesse détectée ! Ne bougez pas si vous ressentez des douleurs. J'alerte immédiatement les secours et vos contacts d'urgence."
            
        elif fall_type == 'impact_brutal':
            return "Impact brutal détecté. Restez calme et évaluez vos blessures. Si vous avez mal à la tête, au cou ou au dos, ne bougez pas."
            
        else:
            return "Chute détectée. Prenez votre temps pour vous relever et vérifiez que vous n'êtes pas blessé(e). Je surveille votre état."
    
    def _start_fall_emergency_countdown(self, fall_info: dict):
        """
        Démarre un countdown d'urgence après chute avec possibilité d'annulation
        """
        def emergency_countdown():
            # Attendre réponse utilisateur pendant 30 secondes
            start_time = time.time()
            timeout = 30.0
            
            while time.time() - start_time < timeout:
                if self.shutdown_event.is_set():
                    return
                    
                try:
                    response = self.response_queue.get(timeout=1.0)
                    
                    if response.lower() == 'non':
                        recovery_message = "Bien reçu. Vous semblez aller bien. Parfait ! Je continue la surveillance au cas où. Prenez votre temps pour vous remettre."
                        print("\n✅ Bien reçu - Vous semblez aller bien")
                        print("🤖 Guardian: Parfait ! Je continue la surveillance au cas où.")
                        print("   Prenez votre temps pour vous remettre et soyez prudent(e).")
                        
                        # Synthèse vocale de confirmation
                        self.speech_agent.speak_alert("confirmation", recovery_message)
                        
                        # Reset du détecteur mais continuer surveillance
                        return
                        
                    elif response.lower() == 'oui':
                        injury_message = "URGENCE CONFIRMÉE. Blessure après chute. Je déclenche immédiatement les secours."
                        print("\n🚨 URGENCE CONFIRMÉE - BLESSURE APRÈS CHUTE")
                        
                        # Synthèse vocale d'urgence
                        self.speech_agent.speak_alert("emergency", injury_message)
                        
                        self._trigger_fall_emergency_response(fall_info, user_confirmed=True)
                        return
                        
                except queue.Empty:
                    continue
            
            # Timeout - déclencher urgence automatique
            print("\n⏰ TIMEOUT - AUCUNE RÉPONSE APRÈS CHUTE")
            print("🚨 Je déclenche automatiquement l'alerte d'urgence")
            self._trigger_fall_emergency_response(fall_info, timeout=True)
        
        # Démarrer le countdown dans un thread séparé
        countdown_thread = threading.Thread(target=emergency_countdown, daemon=True)
        countdown_thread.start()
    
    def _trigger_fall_emergency_response(self, fall_info: dict, user_confirmed: bool = False, 
                                       timeout: bool = False, immediate: bool = False):
        """
        Déclenche la réponse d'urgence pour chute avec contexte spécialisé
        """
        fall_type = fall_info.get('fall_type', 'chute_generale')
        severity = fall_info.get('severity', 'modérée')
        position = fall_info.get('position', self.current_position)
        
        # Construire le message d'urgence spécialisé
        if immediate:
            reason = f"🆘 URGENCE MAXIMALE - IMMOBILITÉ PROLONGÉE APRÈS CHUTE\n\n"
        elif user_confirmed:
            reason = f"🚨 URGENCE CONFIRMÉE - BLESSURE APRÈS CHUTE\n\n"
        elif timeout:
            reason = f"⏰ URGENCE AUTOMATIQUE - AUCUNE RÉPONSE APRÈS CHUTE\n\n"
        else:
            reason = f"🚨 CHUTE DÉTECTÉE NÉCESSITANT ASSISTANCE\n\n"
        
        reason += f"Type de chute: {self._translate_fall_type(fall_type)}\n"
        reason += f"Sévérité évaluée: {severity}\n"
        reason += f"Vitesse avant chute: {fall_info.get('previous_speed', 0):.1f} km/h\n"
        reason += f"Décélération mesurée: {fall_info.get('acceleration', 0):.1f} m/s²\n"
        
        if immediate:
            reason += f"⚠️ Personne immobile depuis {fall_info.get('time_since_fall', 0):.0f} secondes après la chute"
        
        # Utiliser Gemini pour analyser la situation de chute
        if self.gemini_agent.is_available:
            # Analyse avancée de chute avec Gemini
            user_response_text = None
            if user_confirmed:
                user_response_text = "Je suis blessé après ma chute"
            elif timeout:
                user_response_text = None  # Aucune réponse
            
            gemini_analysis = self.gemini_agent.analyze_fall_emergency(fall_info, user_response_text)
            
            print(f"\n🧠 **ANALYSE GEMINI DE LA CHUTE:**")
            print(f"   🎯 Type: {vertex_analysis['emergency_type']}")
            print(f"   📊 Urgence: {vertex_analysis['urgency_level']}/10")
            
            # Conseils spécifiques aux chutes
            fall_advice = vertex_analysis.get('fall_specific_advice', [])
            if fall_advice:
                print(f"   🏥 Conseils spécialisés:")
                for advice in fall_advice[:3]:
                    print(f"      • {advice}")
            
            ai_analysis = vertex_analysis
            
        elif self.intelligent_advisor:
            # Fallback vers l'ancien système IA
            ai_context = f"Chute détectée: {fall_type}, sévérité {severity}, "
            if user_confirmed:
                ai_context += "utilisateur confirme être blessé"
            elif timeout:
                ai_context += "aucune réponse de l'utilisateur après 30 secondes"
            elif immediate:
                ai_context += "immobilité prolongée après chute"
            else:
                ai_context += "chute nécessitant vérification"
                
            ai_analysis = self.intelligent_advisor.analyze_emergency_situation(
                ai_context, position, "chute_accident"
            )
        else:
            ai_analysis = {'emergency_type': 'Accident/Chute', 'urgency_level': 8}
        
        # Recherche d'aide médicale d'urgence à proximité
        if self.emergency_locations and position:
            print("\n🚑 Recherche d'aide médicale d'urgence à proximité...")
            
            medical_help = self.emergency_locations.find_emergency_refuges(position, radius_m=2000)
            transports = self.emergency_locations.find_emergency_transport(position, radius_m=1000)
            
            medical_message = self.emergency_locations.format_emergency_locations_message(
                medical_help, transports, current_location=position
            )
            
            print(medical_message)
            
            # Envoyer l'alerte visuelle de chute avec informations complètes
            self.emergency_response.send_fall_emergency_alert(position, fall_info)
            
            # Envoyer aussi l'alerte traditionnelle avec refuges
            enhanced_reason = f"{reason}\n\nAnalyse IA:\n- Type: {ai_analysis['emergency_type']}\n- Urgence: {ai_analysis['urgency_level']}\n\n{medical_message}"
            self.emergency_response.send_critical_alert_with_refuges(position, medical_message, enhanced_reason)
            
            # Envoyer aussi le SMS d'urgence
            emergency_context = {
                'emergency_type': 'CHUTE DÉTECTÉE',
                'what3words': ai_analysis.get('what3words', '')
            }
            self._send_emergency_notifications(emergency_context, reason)
            
        else:
            # Envoyer l'alerte visuelle de chute
            self.emergency_response.send_fall_emergency_alert(position, fall_info)
            
            # Alerte traditionnelle de fallback
            enhanced_reason = f"{reason}\n\nAnalyse IA:\n- Type: {ai_analysis['emergency_type']}\n- Urgence: {ai_analysis['urgency_level']}"
            self.emergency_response.send_critical_alert(position, enhanced_reason)
            
            # Envoyer aussi le SMS d'urgence
            emergency_context = {
                'emergency_type': 'CHUTE DÉTECTÉE',
                'what3words': ai_analysis.get('what3words', '')
            }
            self._send_emergency_notifications(emergency_context, reason)
        
        print(f"\n✅ Alerte d'urgence envoyée pour chute")
        print(f"🚑 Les secours et vos contacts ont été notifiés")
        
        if not immediate:
            print(f"📱 Gardez votre téléphone près de vous")
            print(f"🏥 Des informations sur l'aide médicale à proximité ont été partagées")
    
    def _schedule_emergency_escalation(self, reason: str, delay_seconds: int = 600):
        """Programme une escalade d'urgence après délai personnalisé"""
        def escalate():
            time.sleep(delay_seconds)
            if not self.shutdown_event.is_set():
                self.emergency_response.escalate_emergency(self.current_position, delay_seconds)
                print(f"\n🚨 ESCALADE AUTOMATIQUE après {delay_seconds}s d'inactivité")
                print("📞 Services d'urgence contactés automatiquement")
        
        escalation_thread = threading.Thread(target=escalate)
        escalation_thread.daemon = True
        escalation_thread.start()
    
    def process_user_input(self, text_input: str):
        """Traite l'entrée utilisateur (texte ou vocal)"""
        if text_input.lower() in ["oui", "non"]:
            self.response_queue.put(text_input)
        else:
            # Pour les explications détaillées
            self.response_queue.put(text_input)

    def _send_emergency_notifications(self, emergency_context: dict, reason: str):
        """Envoie les notifications d'urgence (email + SMS)"""
        
        # Préparer les contacts d'urgence
        contacts = self.config.get('emergency_contacts', [])
        
        if not contacts:
            self.logger.warning("Aucun contact d'urgence configuré")
            return
        
        # L'email d'urgence sera envoyé par les méthodes appelantes
        # Cette fonction se concentre uniquement sur les SMS
        
        # Envoyer le SMS d'urgence (nouveau)
        try:
            sms_context = {
                'user_name': 'Votre proche',  # Peut être configuré
                'emergency_type': emergency_context.get('emergency_type', 'Urgence'),
                'location': {
                    'address': self._get_location_address(),
                    'what3words': emergency_context.get('what3words', '')
                }
            }
            
            sms_sent = self.sms_agent.send_emergency_sms(contacts, sms_context)
            
            if sms_sent:
                self.logger.info("SMS d'urgence envoyé avec succès")
                print("📱 SMS d'urgence envoyé aux contacts")
            else:
                self.logger.warning("Échec envoi SMS d'urgence")
                print("📱 SMS d'urgence en mode simulation")
                
        except Exception as e:
            self.logger.error(f"Erreur envoi SMS: {e}")
    
    def _get_location_address(self) -> str:
        """Retourne l'adresse actuelle formatée"""
        if not self.current_position:
            return "Position inconnue"
        
        lat, lon = self.current_position
        return f"{lat:.6f}, {lon:.6f}"

def static_monitor(orchestrator, agent):
    """Surveille les positions GPS"""
    logger = logging.getLogger("static_monitor")
    
    for position in agent.simulate_gps():
        if orchestrator.shutdown_event.is_set():
            break
            
        orchestrator.current_position = position
        
        if orchestrator.agents_lock.acquire(blocking=False):
            try:
                # Vérifier immobilité prolongée
                if agent.update_position(position):
                    orchestrator.handle_alert("immobilité prolongée", position)
                
                # Vérifier détection de chute
                fall_info = orchestrator.fall_detector.update_position(position)
                if fall_info:
                    orchestrator.handle_fall_detection(fall_info)
                    
                # Vérifier statut post-chute
                post_fall_info = orchestrator.fall_detector.check_post_fall_status(position)
                if post_fall_info:
                    orchestrator.handle_post_fall_emergency(post_fall_info)
                    
            finally:
                orchestrator.agents_lock.release()
        
        time.sleep(1)

def voice_monitor(orchestrator, voice_agent):
    """Surveille les commandes vocales"""
    logger = logging.getLogger("voice_monitor")
    
    while not orchestrator.shutdown_event.is_set():
        if orchestrator.agents_lock.acquire(blocking=False):
            try:
                result = voice_agent.listen_for_keywords()
                if result:
                    # Vérifier si c'est une réponse à une alerte ou une demande d'aide
                    # Pour simplifier, on traite tous les mots-clés comme des alertes
                    orchestrator.handle_alert("mot-clé d'urgence détecté")
            finally:
                orchestrator.agents_lock.release()
        
        time.sleep(1)

    def send_emergency_email_alert(self, user_name: str, location: str, situation: str, urgency_level: int = 8):
        """Envoie des emails d'urgence aux contacts configurés quand Gemini détecte un danger élevé"""
        
        # Seuil pour envoyer des emails (niveau 7 et plus sur 10)
        if urgency_level < 7:
            self.logger.info(f"Niveau d'urgence {urgency_level}/10 - Pas d'envoi d'email")
            return
        
        if not self.gmail_agent or not self.gmail_agent.is_available:
            self.logger.warning("Agent Gmail non disponible - emails d'urgence désactivés")
            return
        
        try:
            self.logger.critical(f"ENVOI D'EMAILS D'URGENCE - Niveau {urgency_level}/10")
            print(f"\n📧 **ENVOI D'ALERTES EMAIL AUX PROCHES** (Urgence: {urgency_level}/10)")
            
            result = self.gmail_agent.send_to_emergency_contacts(
                user_name=user_name,
                location=location, 
                situation=situation
            )
            
            if result['success']:
                self.logger.info(f"Emails d'urgence envoyés: {result['successful_sends']}/{result['total_contacts']}")
                print(f"✅ {result['successful_sends']}/{result['total_contacts']} emails d'urgence envoyés")
                print("📨 Vos proches ont été alertés de votre situation")
                
                # Notification vocale
                try:
                    self.speech_agent.speak_alert(
                        "info", 
                        f"Vos proches ont été alertés par email de votre situation d'urgence"
                    )
                except:
                    pass
                    
            else:
                self.logger.error(f"Erreur envoi emails: {result.get('error', 'Inconnu')}")
                print(f"❌ Erreur envoi emails: {result.get('error', 'Inconnu')}")
                
        except Exception as e:
            self.logger.error(f"Exception lors de l'envoi d'emails: {e}")
            print(f"❌ Exception emails d'urgence: {e}")

def console_input_monitor(orchestrator):
    """Surveille les entrées console en arrière-plan"""
    logger = logging.getLogger("console_input")
    
    while not orchestrator.shutdown_event.is_set():
        try:
            user_input = input().strip()
            if user_input:
                orchestrator.process_user_input(user_input)
        except (EOFError, KeyboardInterrupt):
            break
        except Exception as e:
            logger.debug(f"Erreur entrée console: {e}")
            time.sleep(1)

def main():
    """Point d'entrée principal pour Guardian"""
    import logging
    from guardian.config import Config
    
    logger = logging.getLogger(__name__)
    
    try:
        # Charger la configuration
        config = Config()
        
        # Créer l'orchestrateur principal
        orchestrator = GuardianOrchestrator(config.config_data)
        
        # Créer les agents avec la configuration
        static_config = config.get_static_agent_config()
        voice_config = config.get_voice_agent_config()
        
        logger.info("Initialisation des agents...")
        static_agent = StaticAgent(**static_config)
        
        # Vérifier que le modèle Vosk existe
        model_path = voice_config.get("model_path")
        if not model_path or not os.path.exists(model_path):
            logger.warning(f"Modèle Vosk non trouvé à {model_path}")
            logger.info("Fonctionnement en mode GPS uniquement")
            voice_agent = None
        else:
            voice_agent = VoiceAgent(**voice_config)
        
        # Démarrer le monitoring GPS
        logger.info("Démarrage du monitoring GPS...")
        t_static = threading.Thread(target=static_monitor, args=(orchestrator, static_agent))
        t_static.daemon = True
        t_static.start()
        
        # Démarrer le monitoring vocal si disponible
        if voice_agent:
            logger.info("Démarrage du monitoring vocal...")
            t_voice = threading.Thread(target=voice_monitor, args=(orchestrator, voice_agent))
            t_voice.daemon = True
            t_voice.start()
        
        # Démarrer le monitoring des entrées console
        logger.info("Démarrage du monitoring des entrées...")
        t_input = threading.Thread(target=console_input_monitor, args=(orchestrator,))
        t_input.daemon = True
        t_input.start()
        
        logger.info("Guardian démarré avec succès!")
        
        startup_message = "Guardian est actif et surveille votre sécurité"
        print("🛡️  Guardian est actif et surveille votre sécurité")
        print("📱 Tapez 'oui' ou 'non' pour répondre aux alertes")
        print("🔄 Le système surveille votre position et écoute les mots-clés d'urgence")
        print("⏹️  Appuyez sur Ctrl+C pour arrêter")
        print("-" * 60)
        
        # Test de synthèse vocale au démarrage
        try:
            orchestrator.speech_agent.speak_alert("info", startup_message)
            print("🔊 Synthèse vocale activée")
        except Exception as e:
            logger.warning(f"Synthèse vocale non disponible: {e}")
            print("🔇 Synthèse vocale en mode simulation")
        
        # Test de Vertex AI au démarrage
        try:
            vertex_test = orchestrator.vertex_ai_agent.test_vertex_ai_connection()
            if vertex_test['success']:
                print("🧠 Vertex AI Gemini activé")
                print(f"   📊 {vertex_test['details']}")
            else:
                print("🤖 Vertex AI en mode simulation")
                print(f"   ⚠️ {vertex_test['message']}")
        except Exception as e:
            logger.warning(f"Vertex AI non disponible: {e}")
            print("🤖 Vertex AI en mode simulation")
        
        # Attendre indéfiniment (les threads sont en daemon)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Arrêt demandé par l'utilisateur")
            orchestrator.shutdown_event.set()
            
    except Exception as e:
        logger.error(f"Erreur lors du démarrage: {e}")
        raise

if __name__ == "__main__":
    main()