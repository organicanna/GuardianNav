import threading
import time
import os
import logging
import queue
from guardian.GPS_agent import StaticAgent
from guardian.voice_agent import VoiceAgent
from guardian.emergency_response import EmergencyResponse
from guardian.intelligent_advisor import IntelligentAdvisor, SmartResponseSystem

class GuardianOrchestrator:
    """Orchestrateur principal pour GuardianNav selon le workflow défini"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.emergency_response = EmergencyResponse(config.get('emergency_response', {}))
        
        # Système d'IA et de conseils
        self.intelligent_advisor = IntelligentAdvisor()
        self.smart_response_system = SmartResponseSystem(self.intelligent_advisor)
        
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
        
        # Notification des contacts avec analyse IA
        if self.current_position:
            enhanced_reason = f"{reason}\n\nAnalyse IA:\n- Type: {ai_analysis['emergency_type']}\n- Urgence: {ai_analysis['urgency_level']}\n- Actions: {', '.join(ai_analysis['immediate_actions'])}"
            self.emergency_response.send_location_to_contacts(self.current_position, enhanced_reason)
        
        print("\n✅ Assistance IA et contacts notifiés. Aide spécialisée en route.")
        
        # Programmer l'escalade avec priorité selon l'urgence
        urgency_multiplier = {"high": 0.5, "medium": 1.0, "low": 2.0}
        escalation_delay = 300 * urgency_multiplier.get(ai_analysis['urgency_level'], 1.0)  # 2.5-10 min
        self._schedule_emergency_escalation(reason, int(escalation_delay))
    
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
                if agent.update_position(position):
                    orchestrator.handle_alert("immobilité prolongée", position)
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