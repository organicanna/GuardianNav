"""
Système de recherche de refuges et transports d'urgence pour GuardianNav
"""
import requests
import logging
import json
from typing import List, Dict, Tuple, Optional
import yaml
from datetime import datetime

class EmergencyLocationService:
    """Service de localisation d'urgence pour trouver refuges et transports"""
    
    def __init__(self, api_keys_config: dict):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.config = api_keys_config
        self.maps_api_key = api_keys_config.get('google_cloud', {}).get('services', {}).get('maps_api_key')
        
    def find_emergency_refuges(self, location: Tuple[float, float], radius_m: int = 500) -> List[Dict]:
        """
        Trouve des refuges d'urgence à proximité (bars, cafés, commerces ouverts)
        
        Args:
            location: (latitude, longitude)
            radius_m: Rayon de recherche en mètres
            
        Returns:
            Liste des refuges disponibles
        """
        lat, lon = location
        self.logger.info(f"Recherche refuges d'urgence près de {lat}, {lon} (rayon: {radius_m}m)")
        
        refuges = []
        
        # Types de lieux sûrs à rechercher
        safe_place_types = [
            'restaurant', 'bar', 'cafe', 'pharmacy', 'hospital', 
            'police', 'fire_station', 'shopping_mall', 'hotel',
            'gas_station', 'bank'  # Souvent ouverts et avec sécurité
        ]
        
        for place_type in safe_place_types:
            places = self._search_places_nearby(location, place_type, radius_m)
            refuges.extend(places)
        
        # Filtrer et trier par distance
        refuges = self._filter_and_sort_refuges(refuges, location)
        
        self.logger.info(f"Trouvé {len(refuges)} refuges potentiels")
        return refuges[:10]  # Top 10 refuges les plus proches
    
    def find_emergency_transport(self, location: Tuple[float, float], radius_m: int = 1000) -> Dict[str, List]:
        """
        Trouve les moyens de transport d'urgence à proximité
        
        Args:
            location: (latitude, longitude) 
            radius_m: Rayon de recherche en mètres
            
        Returns:
            Dict avec différents types de transport
        """
        lat, lon = location
        self.logger.info(f"Recherche transports d'urgence près de {lat}, {lon}")
        
        transport_options = {
            'bus_stops': self._find_bus_stops(location, radius_m),
            'velib_stations': self._find_velib_stations(location, radius_m),
            'taxi_stands': self._find_taxi_stands(location, radius_m),
            'metro_stations': self._find_metro_stations(location, radius_m),
            'tram_stops': self._find_tram_stops(location, radius_m)
        }
        
        return transport_options
    
    def _search_places_nearby(self, location: Tuple[float, float], place_type: str, radius: int) -> List[Dict]:
        """Recherche des lieux spécifiques avec Google Places API"""
        try:
            if not self.maps_api_key:
                # Simulation si pas de clé API
                return self._simulate_places(location, place_type)
            
            lat, lon = location
            url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            
            params = {
                'location': f"{lat},{lon}",
                'radius': radius,
                'type': place_type,
                'key': self.maps_api_key
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            places = []
            for result in data.get('results', []):
                place = {
                    'name': result.get('name', 'Lieu inconnu'),
                    'type': place_type,
                    'address': result.get('vicinity', ''),
                    'rating': result.get('rating', 0),
                    'is_open': self._check_if_open(result),
                    'location': result['geometry']['location'],
                    'distance_m': self._calculate_distance(location, 
                        (result['geometry']['location']['lat'], result['geometry']['location']['lng']))
                }
                places.append(place)
            
            return places
            
        except Exception as e:
            self.logger.error(f"Erreur recherche places {place_type}: {e}")
            return self._simulate_places(location, place_type)
    
    def _simulate_places(self, location: Tuple[float, float], place_type: str) -> List[Dict]:
        """Simule des lieux pour les tests (quand pas d'API)"""
        lat, lon = location
        
        simulated_places = {
            'bar': [
                {'name': 'Le Refuge Bar', 'distance_m': 150, 'is_open': True},
                {'name': 'Café de la Paix', 'distance_m': 280, 'is_open': True},
                {'name': 'Brasserie du Centre', 'distance_m': 420, 'is_open': False}
            ],
            'pharmacy': [
                {'name': 'Pharmacie de Garde', 'distance_m': 320, 'is_open': True},
                {'name': 'Pharmacie Centrale', 'distance_m': 480, 'is_open': False}
            ],
            'police': [
                {'name': 'Commissariat Central', 'distance_m': 800, 'is_open': True}
            ],
            'hospital': [
                {'name': 'Hôpital Saint-Jean', 'distance_m': 1200, 'is_open': True}
            ]
        }
        
        return simulated_places.get(place_type, [])
    
    def _find_bus_stops(self, location: Tuple[float, float], radius: int) -> List[Dict]:
        """Trouve les arrêts de bus à proximité"""
        # Simulation d'arrêts de bus
        return [
            {
                'name': 'Arrêt République',
                'lines': ['21', '56', '75'],
                'distance_m': 180,
                'next_buses': ['2 min', '8 min', '15 min']
            },
            {
                'name': 'Arrêt Châtelet',
                'lines': ['1', '14', '27'],
                'distance_m': 350,
                'next_buses': ['5 min', '12 min']
            }
        ]
    
    def _find_velib_stations(self, location: Tuple[float, float], radius: int) -> List[Dict]:
        """Trouve les stations Vélib à proximité"""
        try:
            # API officielle Vélib (OpenData Paris)
            url = "https://velib-metropole-opendata.smoove.pro/opendata/Velib_Metropole/station_information.json"
            
            # Pour la demo, simulation
            return [
                {
                    'name': 'Station République',
                    'available_bikes': 5,
                    'available_docks': 12,
                    'distance_m': 220,
                    'is_operational': True
                },
                {
                    'name': 'Station Hôtel de Ville', 
                    'available_bikes': 0,
                    'available_docks': 18,
                    'distance_m': 450,
                    'is_operational': True
                }
            ]
        except Exception as e:
            self.logger.error(f"Erreur API Vélib: {e}")
            return []
    
    def _find_taxi_stands(self, location: Tuple[float, float], radius: int) -> List[Dict]:
        """Trouve les stations de taxi"""
        return [
            {
                'name': 'Station Taxi République',
                'available_taxis': 3,
                'distance_m': 300,
                'phone': '+33142345678'
            }
        ]
    
    def _find_metro_stations(self, location: Tuple[float, float], radius: int) -> List[Dict]:
        """Trouve les stations de métro"""
        return [
            {
                'name': 'République',
                'lines': ['3', '5', '8', '9', '11'],
                'distance_m': 250,
                'accessibility': True,
                'next_trains': ['1 min', '4 min', '7 min']
            }
        ]
    
    def _find_tram_stops(self, location: Tuple[float, float], radius: int) -> List[Dict]:
        """Trouve les arrêts de tramway"""
        return [
            {
                'name': 'Arrêt Tramway République',
                'lines': ['T3a', 'T5'],
                'distance_m': 400,
                'next_trams': ['6 min', '14 min']
            }
        ]
    
    def _check_if_open(self, place_data: dict) -> bool:
        """Vérifie si un lieu est ouvert maintenant"""
        opening_hours = place_data.get('opening_hours', {})
        return opening_hours.get('open_now', False)
    
    def _calculate_distance(self, loc1: Tuple[float, float], loc2: Tuple[float, float]) -> int:
        """Calcule la distance entre deux points (approximation simple)"""
        from math import radians, cos, sin, asin, sqrt
        
        lon1, lat1 = loc1
        lon2, lat2 = loc2
        
        # Formule haversine
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371000  # Rayon de la Terre en mètres
        return int(c * r)
    
    def _filter_and_sort_refuges(self, refuges: List[Dict], location: Tuple[float, float]) -> List[Dict]:
        """Filtre et trie les refuges par pertinence"""
        
        # Priorité aux lieux ouverts
        open_refuges = [r for r in refuges if r.get('is_open', False)]
        closed_refuges = [r for r in refuges if not r.get('is_open', False)]
        
        # Trier par distance
        open_refuges.sort(key=lambda x: x.get('distance_m', 9999))
        closed_refuges.sort(key=lambda x: x.get('distance_m', 9999))
        
        # Priorité : ouverts d'abord, puis fermés
        return open_refuges + closed_refuges
    
    def format_emergency_locations_message(self, refuges: List[Dict], transports: Dict[str, List]) -> str:
        """Formate un message avec les lieux d'urgence"""
        
        message = "🆘 **LIEUX SÛRS ET TRANSPORTS D'URGENCE À PROXIMITÉ**\n\n"
        
        # Refuges
        if refuges:
            message += "🏠 **REFUGES SÛRS:**\n"
            for refuge in refuges[:5]:  # Top 5
                status = "🟢 OUVERT" if refuge.get('is_open') else "🔴 FERMÉ"
                message += f"   • {refuge['name']} ({refuge['distance_m']}m) {status}\n"
        
        message += "\n🚇 **TRANSPORTS D'URGENCE:**\n"
        
        # Métro/Bus
        if transports.get('metro_stations'):
            station = transports['metro_stations'][0]
            message += f"   🚇 Métro {station['name']} ({station['distance_m']}m) - Lignes: {', '.join(station['lines'])}\n"
        
        if transports.get('bus_stops'):
            stop = transports['bus_stops'][0]
            message += f"   🚌 Bus {stop['name']} ({stop['distance_m']}m) - Prochains: {', '.join(stop['next_buses'])}\n"
        
        # Vélib
        if transports.get('velib_stations'):
            station = transports['velib_stations'][0]
            if station['available_bikes'] > 0:
                message += f"   🚴 Vélib {station['name']} ({station['distance_m']}m) - {station['available_bikes']} vélos dispo\n"
        
        # Taxi
        if transports.get('taxi_stands'):
            taxi = transports['taxi_stands'][0]
            message += f"   🚕 Taxi {taxi['name']} ({taxi['distance_m']}m) - Tel: {taxi['phone']}\n"
        
        message += "\n📞 **NUMÉROS D'URGENCE:**\n"
        message += "   • Police: 17\n   • SAMU: 15\n   • Pompiers: 18\n   • Urgence EU: 112"
        
        return message