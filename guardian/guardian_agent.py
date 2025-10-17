import threading
import time
from guardian.GPS_agent import StaticAgent
from guardian.voice_agent import VoiceAgent
# from guardian.path_agent import PathAgent  # ajoute si tu as PathAgent

def ask_user(trigger_type):
    print(f"\nALERTE ({trigger_type}) : Tout va bien ? (oui/non)")
    response = input().strip().lower()
    if response == "oui":
        print("OK, pas de question supplémentaire.\n")
    elif response == "non":
        reason = input("Pourquoi ? : ")
        print(f"Motif reçu : {reason}\n")
    else:
        print("Réponse non reconnue. Aucune action prise.\n")

def static_monitor(agent, alert_callback):
    for position in agent.simulate_gps():
        if agent.update_position(position):
            alert_callback("immobilité")
        time.sleep(1)

def voice_monitor(agent, alert_callback):
    while True:
        if agent.listen_for_keywords():
            alert_callback("mot-clé vocal")
        time.sleep(1)

def path_monitor(agent, alert_callback):
    for position in agent.simulate_gps():
        if agent.update_position(position):
            alert_callback("déviation de trajet")
        time.sleep(1)

if __name__ == "__main__":
    static_agent = StaticAgent(distance_threshold=10, time_threshold=30)  # seuils pour test rapide
    voice_agent = VoiceAgent(keywords=["aide", "stop", "urgence", "secours"], model_path="/Users/anna/Desktop/GuardianNav/vosk-model-small-fr-0.22")
    # path_agent = PathAgent(...)

    def orchestrator(trigger_type):
        ask_user(trigger_type)

    t_static = threading.Thread(target=static_monitor, args=(static_agent, orchestrator))
    t_voice = threading.Thread(target=voice_monitor, args=(voice_agent, orchestrator))
    # t_path = threading.Thread(target=path_monitor, args=(path_agent, orchestrator))

    t_static.start()
    t_voice.start()
    # t_path.start()
    t_static.join()
    t_voice.join()
    # t_path.join()