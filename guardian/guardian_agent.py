import threading
import time
import os
import logging
import queue
from guardian.GPS_agent import StaticAgent
from guardian.voice_agent import VoiceAgent
from guardian.emergency_response import EmergencyResponse
from guardian.intelligent_advisor import IntelligentAdvisor, SmartResponseSystem
from guardian.emergency_locations import EmergencyLocationService
from guardian.fall_detector import FallDetector

class GuardianOrchestrator:
    """Orchestrateur principal pour GuardianNav selon le workflow défini"""
    
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
        
        # Système d'IA et de conseils
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
        
        print(f"\n🚨 ALERTE ({trigger_type}) : Tout va bien ? 🚨")
        print("Répondez 'oui' ou 'non' (vocal ou texte)")
        
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
        print("✅ OK, merci de votre réponse. Surveillance continue.\n")
        
        # Envoyer notification de confirmation si configuré
        self.emergency_response.send_confirmation_alert("Situation normale - Utilisateur a confirmé")
    
    def _handle_negative_response(self):
        """Gère une réponse négative ('non') avec IA"""
        self.logger.warning("Réponse négative reçue - Demande d'aide")
        print("⚠️  Que se passe-t-il ? Décrivez votre situation :")
        print("🤖 Le système IA va analyser votre réponse pour vous conseiller...")
        
        # Demander des détails sur la situation
        try:
            reason = self.response_queue.get(timeout=120)  # 2 minutes pour expliquer
            self.logger.warning(f"Motif reçu: {reason}")
            
            # Analyser la situation avec l'IA
            smart_response = self.smart_response_system.process_emergency_response(reason, "emergency_description")
            
            print("\n" + "="*60)
            print(smart_response["message"])
            print("="*60)
            
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
        print("🚨 AUCUNE RÉPONSE DÉTECTÉE - DÉCLENCHEMENT D'URGENCE AUTOMATIQUE 🚨")
        
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
            
            print("\n🚨 ALERTE DE DANGER IMMÉDIAT envoyée à tous vos contacts!")
            print("📍 Informations sur les refuges et transports incluses")
            
        else:
            # Fallback si pas de service de localisation
            self.emergency_response.send_immediate_danger_alert(self.current_position, reason)
        
        print("\n⚡ **ACTIONS RECOMMANDÉES IMMÉDIATEMENT:**")
        print("   1. 📞 Appelez le 17 (Police) si en danger immédiat")
        print("   2. 🏃 Dirigez-vous vers le refuge le plus proche")
        print("   3. 🚇 Utilisez les transports publics pour vous éloigner")
        print("   4. 📱 Restez en contact avec vos proches")

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
            
        else:
            # Fallback standard
            enhanced_reason = f"{reason}\n\nAnalyse IA:\n- Type: {ai_analysis['emergency_type']}\n- Urgence: {ai_analysis['urgency_level']}\n- Actions: {', '.join(ai_analysis['immediate_actions'])}"
            self.emergency_response.send_location_to_contacts(self.current_position, enhanced_reason)
        
        print("\n✅ Contacts notifiés avec informations d'aide à proximité")
    
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
        
        # Demander confirmation de l'état
        print(f"\n❓ Êtes-vous blessé(e) ? (Répondez 'oui' ou 'non' dans les 30 secondes)")
        print("   Si aucune réponse, j'alerterai automatiquement les secours...")
        
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
                        print("\n✅ Bien reçu - Vous semblez aller bien")
                        print("🤖 Guardian: Parfait ! Je continue la surveillance au cas où.")
                        print("   Prenez votre temps pour vous remettre et soyez prudent(e).")
                        
                        # Reset du détecteur mais continuer surveillance
                        return
                        
                    elif response.lower() == 'oui':
                        print("\n🚨 URGENCE CONFIRMÉE - BLESSURE APRÈS CHUTE")
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
        
        # Utiliser l'IA pour analyser la situation de chute
        if self.intelligent_advisor:
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
            ai_analysis = {'emergency_type': 'Accident/Chute', 'urgency_level': 'Élevée'}
        
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
            
        else:
            # Envoyer l'alerte visuelle de chute
            self.emergency_response.send_fall_emergency_alert(position, fall_info)
            
            # Alerte traditionnelle de fallback
            enhanced_reason = f"{reason}\n\nAnalyse IA:\n- Type: {ai_analysis['emergency_type']}\n- Urgence: {ai_analysis['urgency_level']}"
            self.emergency_response.send_critical_alert(position, enhanced_reason)
        
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
    """Point d'entrée principal pour GuardianNav"""
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
        
        logger.info("GuardianNav démarré avec succès!")
        print("🛡️  GuardianNav est actif et surveille votre sécurité")
        print("📱 Tapez 'oui' ou 'non' pour répondre aux alertes")
        print("🔄 Le système surveille votre position et écoute les mots-clés d'urgence")
        print("⏹️  Appuyez sur Ctrl+C pour arrêter")
        print("-" * 60)
        
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