import time
from typing import Tuple
from math import radians, cos, sin, asin, sqrt
import random

def haversine(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
    """Calcule la distance en mètres entre deux points GPS."""
    lon1, lat1 = coord1
    lon2, lat2 = coord2
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371000
    return c * r

class StaticAgent:
    def __init__(self, distance_threshold=10, time_threshold=300):
        self.distance_threshold = distance_threshold
        self.time_threshold = time_threshold
        self.last_position = None
        self.last_time = None
        self.static_time = 0

    def update_position(self, coord: Tuple[float, float]):
        now = time.time()
        if self.last_position is None:
            self.last_position = coord
            self.last_time = now
            return
        dist = haversine(coord, self.last_position)
        if dist < self.distance_threshold:
            self.static_time += (now - self.last_time)
            if self.static_time > self.time_threshold:
                self.send_alert()
                self.static_time = 0
        else:
            self.static_time = 0
        self.last_position = coord
        self.last_time = now

    def send_alert(self):
        print("Vous semblez immobile depuis plusieurs minutes. Tout va bien ?")

    def simulate_gps(self):
        """Méthode de simulation qui génère des positions GPS aléatoires autour d'un point fixe."""
        lat, lon = 48.8566, 2.3522
        while True:
            # Simuler des petits déplacements
            jitter = random.choice([0, 0.00001, 0.00002, 0.00005])
            yield (lat + jitter, lon + jitter)
            time.sleep(60)  # 1 minute entre chaque relevé

if __name__ == "__main__":
    agent = StaticAgent()
    gps_source = agent.simulate_gps()  # À remplacer par la vraie source Google Maps API si besoin
    for position in gps_source:
        agent.update_position(position)