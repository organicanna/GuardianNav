import threading
import time
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
            if voice:
                # Si valid_responses est défini (ex: ["oui", "non"]), filtrer dessus
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

if __name__ == "__main__":
    static_agent = StaticAgent(distance_threshold=10, time_threshold=30)
    voice_agent = VoiceAgent(
        keywords=["aide", "stop", "urgence", "secours", "oui", "non"],
        model_path="/Users/anna/Desktop/GuardianNav/vosk-model-small-fr-0.22"
    )

    agents_lock = threading.Lock()

    def orchestrator(trigger_type, agents_lock, voice_agent):
        ask_user(trigger_type, agents_lock, voice_agent)

    t_static = threading.Thread(target=static_monitor, args=(static_agent, orchestrator, agents_lock, voice_agent))
    t_voice = threading.Thread(target=voice_monitor, args=(voice_agent, orchestrator, agents_lock, voice_agent))

    t_static.start()
    t_voice.start()
    t_static.join()
    t_voice.join()