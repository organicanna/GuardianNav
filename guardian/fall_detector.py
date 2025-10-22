"""
Détecteur de chute pour GuardianNav
Analyse les mouvements suspects et détecte les chutes potentielles
"""

import time
import logging
from typing import Tuple, List, Optional, Dict
from math import radians, cos, sin, asin, sqrt
import random

class FallDetector:
    """
    Détecteur de chute basé sur l'analyse GPS et de mouvement
    """
    
    def __init__(self, 
                 speed_threshold_high: float = 15.0,  # km/h - vitesse élevée avant chute
                 speed_threshold_low: float = 2.0,    # km/h - vitesse très faible après chute
                 acceleration_threshold: float = -8.0, # m/s² - décélération brutale
                 stationary_time: float = 30.0):       # secondes immobile après chute
        
        self.speed_threshold_high = speed_threshold_high
        self.speed_threshold_low = speed_threshold_low 
        self.acceleration_threshold = acceleration_threshold
        self.stationary_time = stationary_time
        
        # Historique des positions pour analyser le mouvement
        self.position_history: List[Dict] = []
        self.max_history = 10  # Garder les 10 dernières positions
        
        # État de détection
        self.fall_detected = False
        self.fall_detection_time = None
        self.last_speed = 0.0
        
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.info(f"Détecteur de chute initialisé - Seuils: {speed_threshold_high}km/h → {speed_threshold_low}km/h")
    
    def _calculate_speed(self, pos1: Tuple[float, float], pos2: Tuple[float, float], 
                        time1: float, time2: float) -> float:
        """
        Calcule la vitesse entre deux positions en km/h
        """
        if time2 <= time1:
            return 0.0
            
        # Distance en mètres
        distance = self._haversine_distance(pos1, pos2)
        
        # Temps en secondes
        time_diff = time2 - time1
        
        # Vitesse en m/s puis conversion en km/h
        speed_ms = distance / time_diff
        speed_kmh = speed_ms * 3.6
        
        return speed_kmh
    
    def _calculate_acceleration(self, speed1: float, speed2: float, time_diff: float) -> float:
        """
        Calcule l'accélération entre deux vitesses en m/s²
        """
        if time_diff <= 0:
            return 0.0
            
        # Conversion km/h → m/s
        speed1_ms = speed1 / 3.6
        speed2_ms = speed2 / 3.6
        
        # Accélération en m/s²
        acceleration = (speed2_ms - speed1_ms) / time_diff
        return acceleration
    
    def _haversine_distance(self, coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
        """Calcule la distance en mètres entre deux points GPS"""
        lat1, lon1 = coord1
        lat2, lon2 = coord2
        
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371000  # Rayon de la Terre en mètres
        
        return c * r
    
    def update_position(self, position: Tuple[float, float]) -> Optional[Dict]:
        """
        Met à jour la position et analyse le mouvement pour détecter une chute
        
        Args:
            position: (latitude, longitude)
            
        Returns:
            Dict avec informations de chute si détectée, None sinon
        """
        current_time = time.time()
        
        # Ajouter la nouvelle position à l'historique
        position_data = {
            'position': position,
            'timestamp': current_time,
            'speed': 0.0
        }
        
        # Calculer la vitesse si on a une position précédente
        if len(self.position_history) > 0:
            prev_data = self.position_history[-1]
            speed = self._calculate_speed(
                prev_data['position'], 
                position,
                prev_data['timestamp'],
                current_time
            )
            position_data['speed'] = speed
            
            # Analyser pour détecter une chute
            fall_info = self._analyze_fall_pattern(speed, current_time)
            if fall_info:
                return fall_info
        
        # Maintenir l'historique à jour
        self.position_history.append(position_data)
        if len(self.position_history) > self.max_history:
            self.position_history.pop(0)
            
        return None
    
    def _analyze_fall_pattern(self, current_speed: float, current_time: float) -> Optional[Dict]:
        """
        Analyse le pattern de mouvement pour détecter une chute
        """
        if len(self.position_history) < 2:
            return None
            
        prev_data = self.position_history[-1]
        prev_speed = prev_data['speed']
        time_diff = current_time - prev_data['timestamp']
        
        # Calculer l'accélération
        acceleration = self._calculate_acceleration(prev_speed, current_speed, time_diff)
        
        # Pattern de chute détecté ?
        fall_detected = self._detect_fall_pattern(prev_speed, current_speed, acceleration, current_time)
        
        if fall_detected:
            fall_type = self._classify_fall_type(prev_speed, current_speed, acceleration)
            
            fall_info = {
                'type': 'fall_detected',
                'fall_type': fall_type,
                'previous_speed': prev_speed,
                'current_speed': current_speed,
                'acceleration': acceleration,
                'detection_time': current_time,
                'severity': self._assess_fall_severity(prev_speed, acceleration),
                'position': self.position_history[-1]['position']
            }
            
            self.fall_detected = True
            self.fall_detection_time = current_time
            
            self.logger.warning(f"🚨 CHUTE DÉTECTÉE ! Type: {fall_type}, Sévérité: {fall_info['severity']}")
            
            return fall_info
            
        return None
    
    def _detect_fall_pattern(self, prev_speed: float, current_speed: float, 
                           acceleration: float, current_time: float) -> bool:
        """
        Détecte si le pattern correspond à une chute
        """
        # Pattern 1: Décélération brutale depuis une vitesse élevée
        if (prev_speed > self.speed_threshold_high and 
            current_speed < self.speed_threshold_low and
            acceleration < self.acceleration_threshold):
            return True
            
        # Pattern 2: Arrêt soudain après mouvement
        if (prev_speed > 8.0 and  # Vitesse modérée à vélo
            current_speed < 1.0 and  # Quasi-immobile
            acceleration < -5.0):  # Décélération importante
            return True
            
        # Pattern 3: Vitesse anormalement élevée puis arrêt
        # (peut indiquer une glissade ou perte de contrôle)
        if (prev_speed > 25.0 and  # Vitesse très élevée
            current_speed < 3.0):   # Arrêt quasi-total
            return True
            
        return False
    
    def _classify_fall_type(self, prev_speed: float, current_speed: float, 
                          acceleration: float) -> str:
        """
        Classifie le type de chute détectée
        """
        if prev_speed > 20.0:
            return "chute_haute_vitesse"
        elif prev_speed > 10.0:
            return "chute_velo"
        elif acceleration < -10.0:
            return "impact_brutal"
        else:
            return "chute_generale"
    
    def _assess_fall_severity(self, prev_speed: float, acceleration: float) -> str:
        """
        Évalue la sévérité de la chute
        """
        severity_score = 0
        
        # Score basé sur la vitesse avant chute
        if prev_speed > 20.0:
            severity_score += 3
        elif prev_speed > 15.0:
            severity_score += 2
        elif prev_speed > 10.0:
            severity_score += 1
            
        # Score basé sur la décélération
        if acceleration < -12.0:
            severity_score += 3
        elif acceleration < -8.0:
            severity_score += 2
        elif acceleration < -5.0:
            severity_score += 1
            
        # Déterminer la sévérité
        if severity_score >= 5:
            return "critique"
        elif severity_score >= 3:
            return "grave"
        elif severity_score >= 1:
            return "modérée"
        else:
            return "légère"
    
    def check_post_fall_status(self, current_position: Tuple[float, float]) -> Optional[Dict]:
        """
        Vérifie le statut après une chute détectée
        """
        if not self.fall_detected or not self.fall_detection_time:
            return None
            
        current_time = time.time()
        time_since_fall = current_time - self.fall_detection_time
        
        # Calculer si la personne bouge depuis la chute
        if len(self.position_history) >= 2:
            recent_movement = self._calculate_recent_movement()
            
            # Si immobile depuis longtemps après chute = urgence
            if (time_since_fall > self.stationary_time and 
                recent_movement < 5.0):  # Moins de 5m de mouvement
                
                return {
                    'type': 'post_fall_emergency',
                    'time_since_fall': time_since_fall,
                    'movement_since_fall': recent_movement,
                    'status': 'immobile_prolongé',
                    'urgency': 'maximale'
                }
                
        return None
    
    def _calculate_recent_movement(self) -> float:
        """
        Calcule le mouvement total sur les dernières positions
        """
        if len(self.position_history) < 2:
            return 0.0
            
        total_distance = 0.0
        for i in range(1, len(self.position_history)):
            distance = self._haversine_distance(
                self.position_history[i-1]['position'],
                self.position_history[i]['position']
            )
            total_distance += distance
            
        return total_distance
    
    def reset_fall_detection(self):
        """Reset du détecteur après intervention"""
        self.fall_detected = False
        self.fall_detection_time = None
        self.logger.info("Détecteur de chute réinitialisé")
    
    def simulate_fall(self, fall_type: str = "chute_velo") -> Dict:
        """
        Simule une chute pour les tests
        """
        current_time = time.time()
        
        # Simuler différents types de chute
        if fall_type == "chute_velo":
            prev_speed = 18.5  # km/h à vélo
            current_speed = 0.2
            acceleration = -9.2
        elif fall_type == "chute_haute_vitesse":
            prev_speed = 28.0
            current_speed = 0.0
            acceleration = -15.5
        else:
            prev_speed = 12.0
            current_speed = 0.5
            acceleration = -6.8
            
        fall_info = {
            'type': 'fall_detected',
            'fall_type': fall_type,
            'previous_speed': prev_speed,
            'current_speed': current_speed,
            'acceleration': acceleration,
            'detection_time': current_time,
            'severity': self._assess_fall_severity(prev_speed, acceleration),
            'position': (48.8566 + random.uniform(-0.001, 0.001), 
                        2.3522 + random.uniform(-0.001, 0.001))
        }
        
        self.fall_detected = True
        self.fall_detection_time = current_time
        
        self.logger.warning(f"🧪 SIMULATION - Chute détectée: {fall_type}")
        
        return fall_info