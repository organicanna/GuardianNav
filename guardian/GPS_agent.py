import time
import logging
from typing import Tuple, Generator
import random
from guardian.utils import haversine

class StaticAgent: #Début de l'agent statique
    def __init__(self, distance_threshold=10, time_threshold=300): #définition du seuil à partir de quand qq est "statique"
        self.distance_threshold = distance_threshold #seuil de distance
        self.time_threshold = time_threshold #seuil de temps
        self.last_position = None #aucune position au départ
        self.last_time = None #aucun temps au départ
        self.static_time = 0 #compteur de temps cumulé sans bouger
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        self.logger.info(f"Agent statique initialisé - Seuils: {distance_threshold}m, {time_threshold}s")

    def update_position(self, coord: Tuple[float, float]) -> bool: #méthode appelée à chaque nouvelle coordonnée
        """
        Met à jour la position et vérifie si une alerte doit être déclenchée
        
        Args:
            coord: Tuple (latitude, longitude)
            
        Returns:
            bool: True si alerte à déclencher, False sinon
        """
        try:
            now = time.time() #récupération de l'heure actuelle en secondes
            alert = False
            
            if self.last_position is None: 
                self.last_position = coord #définition du premier point
                self.last_time = now #définition du premier temps
                self.logger.info(f"Position initiale définie: {coord}")
                return False
                
            dist = haversine(self.last_position, coord) #calcule la distance en mètres entre position actuelle et dernière position
            elapsed = now - self.last_time
            
            if dist < self.distance_threshold: #si la distance est inférieure au seuil de distance
                self.static_time += elapsed #ajout au compteur de temps cumulé la durée écoulée en secondes depuis la dernière mise à jour
                self.logger.debug(f"Immobile: {dist:.1f}m, temps cumulé: {self.static_time:.1f}s")
                
                if self.static_time > self.time_threshold: #si compteur est supérieur au seuil de temps
                    alert = True
                    self.logger.warning(f"Alerte immobilité: {self.static_time:.1f}s > {self.time_threshold}s")
                    self.static_time = 0 #compteur statique retourne à 0
            else:
                self.logger.debug(f"Mouvement détecté: {dist:.1f}m")
                self.static_time = 0 #si distance est supérieure ou égale au seuil de distance, compteur statique à 0
                
            self.last_position = coord #mise à jour position
            self.last_time = now #mise à jour temps
            return alert
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la mise à jour de position: {e}")
            return False 

    def simulate_gps(self) -> Generator[Tuple[float, float], None, None]: #simulation de coordonnées GPS aléatoire autour d'un point fixe car pas de vrai GPS pour l'instant
        """
        Simule des coordonnées GPS pour les tests
        
        Yields:
            Tuple[float, float]: Coordonnées (latitude, longitude)
        """
        lat, lon = 48.8566, 2.3522 #point de départ est Paris
        self.logger.info(f"Simulation GPS démarrée depuis Paris: {lat}, {lon}")
        
        try:
            while True: #boucle infinie
                jitter = random.choice([0, 0.00001, 0.00002, 0.00005]) #petits déplacements aléatoires
                new_coord = (lat + jitter, lon + jitter)
                self.logger.debug(f"Nouvelle position simulée: {new_coord}")
                yield new_coord #simulation de coordonnées de points
                time.sleep(10)  # 10 secondes entre chaque mise à jour des positions > pour aller plus vite dans les tests
        except Exception as e:
            self.logger.error(f"Erreur dans la simulation GPS: {e}")
            raise