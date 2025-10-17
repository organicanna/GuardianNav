from guardian.GPS_agent import StaticAgent

def trigger_alert():
    print("ALERTE : Vous semblez immobile ou un mot clé vocal a été détecté. Tout va bien ?")

# Crée un agent statique avec des seuils (distance en mètres, temps en secondes)
agent = StaticAgent(distance_threshold=10, time_threshold=30)  # 30s pour tests rapides

for position in agent.simulate_gps():
    if agent.update_position(position):
        trigger_alert()
    else:
        print(f"Position : {position} - Aucun problème détecté.")