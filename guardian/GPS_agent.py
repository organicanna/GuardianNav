import time
from typing import Tuple
from math import radians, cos, sin, asin, sqrt
import random

def haversine(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:  #Calcule la distance en mètres entre deux points GPS
    lon1, lat1 = coord1 #coordonnée 1 = longitude et latitude du premier point
    lon2, lat2 = coord2 #idem pour le deuxième point
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2]) #convertir en radians pour faire de la trigonométrie et calculer les distances
    dlon = lon2 - lon1 #calcul de la diff de longitude entre deux points
    dlat = lat2 - lat1 #idem pour la latitude
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2 #formule de Haversine 
    c = 2 * asin(sqrt(a)) #convertit a en radian donc résultat en distance angulaire
    r = 6371000 #rayon moyen de la terre
    return c * r #calcul de la distance linéaire entre 2 points

class StaticAgent: #Début de l'agent statique
    def __init__(self, distance_threshold=10, time_threshold=300): #définition du seuil à partir de quand qq est "statique"
        self.distance_threshold = distance_threshold #seuil de distance
        self.time_threshold = time_threshold #seuil de temps
        self.last_position = None #aucune position au départ
        self.last_time = None #aucun temps au départ
        self.static_time = 0 #compteur de temps cumulé sans bouger

    def update_position(self, coord: Tuple[float, float]): #méthode appelée à chaque nouvelle coordonnée
        now = time.time() #récupération de l'heure actuelle en secondes
        alert = False
        if self.last_position is None: 
            self.last_position = coord #définition du premier point
            self.last_time = now #définition du premier temps
            return False
        dist = haversine(coord, self.last_position) #calcule la distance en mètres entre position actuelle et dernière position
        if dist < self.distance_threshold: #si la distance est inférieure au seuil de distance
            self.static_time += (now - self.last_time) #ajout au compteur de temps cumulé la durée écoulée en secondes depuis la dernière mise à jour
            if self.static_time > self.time_threshold: #si compteur est supérieur au seuil de temps
                alert = True
                self.static_time = 0 #compteur statique retourne à 0
        else:
            self.static_time = 0 #si distance est supérieure ou égale au seuil de distance, compteur statique à 0
        self.last_position = coord #mise à jour position
        self.last_time = now #mise à jour temps
        return alert 

    def simulate_gps(self): #simulation de coordonnées GPS aléatoire autour d'un point fixe car pas de vrai GPS pour l'instant
        lat, lon = 48.8566, 2.3522 #point de départ est Paris
        while True: #boucle infinie
            jitter = random.choice([0, 0.00001, 0.00002, 0.00005]) #petits déplacements aléatoires
            yield (lat + jitter, lon + jitter) #simulation de coordonnées de points
            time.sleep(10)  # 10 secondes entre chaque mise à jour des positions > pour aller plus vite dans les tests