import threading
import time
import os
from guardian.GPS_agent import StaticAgent
from guardian.voice_agent import VoiceAgent

def get_response_voice_or_text(voice_agent, prompt="Votre réponse : ", valid_responses=None):
    print(prompt)
    response = None

    def listen_voice():
        nonlocal response
        print("Vous pouvez répondre à l'oral…")
        while response is None:
            voice = voice_agent.listen_for_keywords()
            if voice and isinstance(voice, str):
                if valid_responses:
                    if voice.lower() in valid_responses:
                        response = voice.lower()
                        break
                else:
                    response = voice
                    break

    thread_voice = threading.Thread(target=listen_voice)
    thread_voice.start()

    while response is None:
        text = input()
        if valid_responses:
            if text.lower() in valid_responses:
                response = text.lower()
        else:
            response = text
    thread_voice.join(timeout=0.1)
    return response

def ask_user(trigger_type, agents_lock, voice_agent):
    print(f"\nALERTE ({trigger_type}) : Tout va bien ? (oui/non)")
    response = get_response_voice_or_text(voice_agent, prompt="Votre réponse (oui/non) :", valid_responses=["oui", "non"])
    if response == "oui":
        print("OK, pas de question supplémentaire.\n")
    elif response == "non":
        reason = get_response_voice_or_text(voice_agent, prompt="Pourquoi ? : ")
        print(f"Motif reçu : {reason}\n")
    else:
        print("Réponse non reconnue. Aucune action prise.\n")
    agents_lock.release()

def static_monitor(agent, alert_callback, agents_lock, voice_agent):
    for position in agent.simulate_gps():
        if agents_lock.acquire(blocking=False):
            if agent.update_position(position):
                alert_callback("immobilité", agents_lock, voice_agent)
            else:
                agents_lock.release()
        time.sleep(1)

def voice_monitor(agent, alert_callback, agents_lock, voice_agent):
    while True:
        if agents_lock.acquire(blocking=False):
            if agent.listen_for_keywords():
                alert_callback("mot-clé vocal", agents_lock, voice_agent)
            else:
                agents_lock.release()
        time.sleep(1)

def main():
    """Point d'entrée principal pour GuardianNav"""
    import logging
    from guardian.config import Config
    
    logger = logging.getLogger(__name__)
    
    try:
        # Charger la configuration
        config = Config()
        
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
        
        agents_lock = threading.Lock()

        def orchestrator(trigger_type, agents_lock, voice_agent):
            ask_user(trigger_type, agents_lock, voice_agent)

        # Démarrer le monitoring GPS
        logger.info("Démarrage du monitoring GPS...")
        t_static = threading.Thread(target=static_monitor, 
                                   args=(static_agent, orchestrator, agents_lock, voice_agent))
        t_static.daemon = True
        t_static.start()
        
        # Démarrer le monitoring vocal si disponible
        if voice_agent:
            logger.info("Démarrage du monitoring vocal...")
            t_voice = threading.Thread(target=voice_monitor, 
                                     args=(voice_agent, orchestrator, agents_lock, voice_agent))
            t_voice.daemon = True
            t_voice.start()
        
        logger.info("GuardianNav démarré avec succès!")
        print("GuardianNav est actif. Appuyez sur Ctrl+C pour arrêter.")
        
        # Attendre indéfiniment (les threads sont en daemon)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Arrêt demandé par l'utilisateur")
            
    except Exception as e:
        logger.error(f"Erreur lors du démarrage: {e}")
        raise

if __name__ == "__main__":
    main()