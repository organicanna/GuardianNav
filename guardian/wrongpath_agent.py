import googlemaps #type: ignore
from math import radians, cos, sin, asin, sqrt
import time

def haversine(coord1, coord2): #même chose que pour le GPS_agent
    lon1, lat1 = coord1
    lon2, lat2 = coord2
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371000
    return c * r

class WrongPathAgent:
    def __init__(self, api_key, origin, destination, deviation_threshold=50):
        self.gmaps = googlemaps.Client(key=api_key)
        self.origin = origin
        self.destination = destination
        self.deviation_threshold = deviation_threshold
        self.route = self.get_route_points()

    def get_route_points(self):
        result = self.gmaps.directions(self.origin, self.destination, mode="walking")
        steps = result[0]['legs'][0]['steps']
        route_points = []
        for step in steps:
            lat = step['start_location']['lat']
            lon = step['start_location']['lng']
            route_points.append((lat, lon))
        # Ajoute le point d'arrivée
        end = steps[-1]['end_location']
        route_points.append((end['lat'], end['lng']))
        return route_points

    def check_position(self, current_position):
        """Vérifie si la position actuelle est trop éloignée du trajet."""
        min_dist = min(haversine(current_position, point) for point in self.route)
        print(f"Distance à l'itinéraire : {min_dist:.1f} m")
        if min_dist > self.deviation_threshold:
            self.ask_if_ok(min_dist)
            return True
        return False

    def ask_if_ok(self, deviation):
        print(f"ALERTE : Vous êtes à {deviation:.1f} m du trajet prévu. Tout va bien ?")

# Exemple d'utilisation, à adapter avec la vraie source de position :
if __name__ == "__main__":
    API_KEY = "TA_CLE_API"  # Mets ta clé Google Maps ici !
    origin = "48.8566,2.3522"       # Paris
    destination = "48.8584,2.2945"  # Tour Eiffel

    agent = WrongPathAgent(API_KEY, origin, destination, deviation_threshold=50)

    # Exemple : simule des positions (remplace par le flux GPS réel)
    positions = [
        (48.8566, 2.3522),      # Sur le trajet
        (48.8570, 2.3530),      # Sur le trajet
        (48.8600, 2.3500),      # Un peu dévié
        (48.8650, 2.3400),      # Loin du trajet (déclenche alerte)
    ]
    for pos in positions:
        agent.check_position(pos)
        time.sleep(2)