import threading
import time
from guardian.GPS_agent import StaticAgent
from guardian.voice_agent import VoiceAgent

def trigger_alert():
    print("ALERTE : Vous semblez immobile ou un mot clé vocal a été détecté. Tout va bien ?")

def static_monitor(agent, alert_callback):
    for position in agent.simulate_gps(): #mettre Google Maps API au lieu du simulate.gps
        if agent.update_position(position):
            alert_callback()
        time.sleep(1)

def voice_monitor(agent, alert_callback):
    while True:
        if agent.listen_for_keywords():
            alert_callback()
        time.sleep(1)

if __name__ == "__main__":
    static_agent = StaticAgent(distance_threshold=10, time_threshold=180)
    voice_agent = VoiceAgent(keywords=["aide", "stop", "urgence", "secours"])

    t1 = threading.Thread(target=static_monitor, args=(static_agent, trigger_alert))
    t2 = threading.Thread(target=voice_monitor, args=(voice_agent, trigger_alert))
    t1.start()
    t2.start()
    t1.join()
    t2.join()