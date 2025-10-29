"""
Système de recherche de refuges et transports d'urgence pour GuardianNav
"""
import requests
import logging
import json
from typing import List, Dict, Tuple, Optional, Any
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
                {
                    'name': 'Le Refuge Bar', 
                    'distance_m': 150, 
                    'is_open': True,
                    'location': {'lat': lat + 0.0015, 'lng': lon + 0.0010},
                    'address': '12 Rue de la Paix'
                },
                {
                    'name': 'Café de la Paix', 
                    'distance_m': 280, 
                    'is_open': True,
                    'location': {'lat': lat - 0.0020, 'lng': lon + 0.0025},
                    'address': '45 Avenue des Champs'
                },
                {
                    'name': 'Brasserie du Centre', 
                    'distance_m': 420, 
                    'is_open': False,
                    'location': {'lat': lat + 0.0030, 'lng': lon - 0.0015},
                    'address': '78 Boulevard Saint-Michel'
                }
            ],
            'pharmacy': [
                {
                    'name': 'Pharmacie de Garde', 
                    'distance_m': 320, 
                    'is_open': True,
                    'location': {'lat': lat + 0.0020, 'lng': lon + 0.0015},
                    'address': '67 Place de la République'
                },
                {
                    'name': 'Pharmacie Centrale', 
                    'distance_m': 480, 
                    'is_open': False,
                    'location': {'lat': lat - 0.0030, 'lng': lon + 0.0010},
                    'address': '89 Rue de la Liberté'
                }
            ],
            'police': [
                {
                    'name': 'Commissariat Central', 
                    'distance_m': 800, 
                    'is_open': True,
                    'location': {'lat': lat + 0.0050, 'lng': lon - 0.0040},
                    'address': '1 Place du Châtelet'
                }
            ],
            'hospital': [
                {
                    'name': 'Hôpital Saint-Jean', 
                    'distance_m': 1200, 
                    'is_open': True,
                    'location': {'lat': lat - 0.0080, 'lng': lon + 0.0060},
                    'address': '156 Boulevard de l\'Hôpital'
                }
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
    
    def get_escape_route_to_refuge(self, start_location: Tuple[float, float], refuge_location: Tuple[float, float]) -> Dict[str, Any]:
        """
        Calcule un itinéraire d'évacuation vers un refuge en utilisant l'API Directions
        
        Args:
            start_location: Position actuelle (lat, lon)
            refuge_location: Position du refuge (lat, lon)
            
        Returns:
            Dict avec itinéraire et instructions
        """
        try:
            if not self.maps_api_key:
                return self._simulate_escape_route(start_location, refuge_location)
            
            url = "https://maps.googleapis.com/maps/api/directions/json"
            
            start_lat, start_lon = start_location
            end_lat, end_lon = refuge_location
            
            params = {
                'origin': f"{start_lat},{start_lon}",
                'destination': f"{end_lat},{end_lon}",
                'mode': 'walking',  # Mode piéton pour évacuation
                'alternatives': 'true',  # Plusieurs itinéraires possibles
                'avoid': 'highways',  # Éviter autoroutes (pas accessibles à pied)
                'language': 'fr',
                'key': self.maps_api_key
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if data.get('status') == 'OK' and data.get('routes'):
                route = data['routes'][0]  # Meilleur itinéraire
                
                return {
                    'duration': route['legs'][0]['duration']['text'],
                    'distance': route['legs'][0]['distance']['text'],
                    'steps': self._format_escape_steps(route['legs'][0]['steps']),
                    'polyline': route['overview_polyline']['points'],
                    'warnings': route.get('warnings', [])
                }
            else:
                self.logger.warning(f"Erreur API Directions: {data.get('status', 'Inconnue')}")
                return self._simulate_escape_route(start_location, refuge_location)
                
        except Exception as e:
            self.logger.error(f"Erreur calcul itinéraire d'évacuation: {e}")
            return self._simulate_escape_route(start_location, refuge_location)
    
    def _format_escape_steps(self, steps: List[Dict]) -> List[str]:
        """Formate les étapes d'évacuation en instructions claires"""
        formatted_steps = []
        
        for i, step in enumerate(steps[:5]):  # Max 5 étapes principales
            instruction = step.get('html_instructions', '')
            distance = step.get('distance', {}).get('text', '')
            
            # Nettoyer les instructions HTML
            import re
            clean_instruction = re.sub('<[^<]+?>', '', instruction)
            
            formatted_steps.append(f"{i+1}. {clean_instruction} ({distance})")
        
        return formatted_steps
    
    def _simulate_escape_route(self, start: Tuple[float, float], end: Tuple[float, float]) -> Dict[str, Any]:
        """Simule un itinéraire d'évacuation pour les tests"""
        distance_m = self._calculate_distance(start, end)
        
        return {
            'duration': f"{max(1, distance_m // 80)} min",  # ~80m/min marche rapide
            'distance': f"{distance_m}m",
            'steps': [
                "1. Sortez immédiatement de votre position actuelle",
                "2. Dirigez-vous vers la rue principale la plus proche", 
                "3. Suivez la direction du refuge en restant visible",
                "4. Évitez les ruelles sombres et isolées",
                "5. Arrivée au refuge - demandez de l'aide"
            ],
            'polyline': 'simulation_polyline',
            'warnings': ['Itinéraire simulé - utilisez votre jugement sur le terrain']
        }

    def format_emergency_locations_message(self, refuges: List[Dict], transports: Dict[str, List], current_location: Tuple[float, float] = None) -> str:
        """Formate un message avec les lieux d'urgence et itinéraires"""
        
        message = "🆘 **LIEUX SÛRS ET TRANSPORTS D'URGENCE À PROXIMITÉ**\n\n"
        
        # Refuges avec itinéraires
        if refuges:
            message += "🏠 **REFUGES SÛRS:**\n"
            for i, refuge in enumerate(refuges[:3]):  # Top 3 avec itinéraires
                status = "🟢 OUVERT" if refuge.get('is_open') else "🔴 FERMÉ"
                message += f"   • {refuge['name']} ({refuge['distance_m']}m) {status}\n"
                
                # Ajouter itinéraire pour le refuge le plus proche
                if i == 0 and current_location and 'location' in refuge:
                    route = self.get_escape_route_to_refuge(
                        current_location, 
                        (refuge['location']['lat'], refuge['location']['lng'])
                    )
                    
                    message += f"     🏃 Temps d'évacuation: {route['duration']}\n"
                    if route.get('warnings'):
                        message += f"     ⚠️ {route['warnings'][0]}\n"
        
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
    
    def get_detailed_evacuation_plan(self, current_location: Tuple[float, float]) -> str:
        """
        Génère un plan d'évacuation détaillé avec plusieurs options
        
        Args:
            current_location: Position actuelle (lat, lon)
            
        Returns:
            Message avec plan d'évacuation complet
        """
        try:
            # Trouver les 3 meilleurs refuges
            refuges = self.find_emergency_refuges(current_location, radius_m=2000)
            
            if not refuges:
                return "❌ Aucun refuge sûr trouvé dans un rayon de 2km"
                
            message = "🚨 **PLAN D'ÉVACUATION D'URGENCE** 🚨\n\n"
            
            # Plan pour les 3 meilleurs refuges
            for i, refuge in enumerate(refuges[:3]):
                message += f"**Option {i+1}: {refuge['name']}**\n"
                
                route = self.get_escape_route_to_refuge(
                    current_location,
                    (refuge['location']['lat'], refuge['location']['lng'])
                )
                
                message += f"📍 Distance: {route['distance']} - Temps: {route['duration']}\n"
                message += f"📞 Adresse: {refuge.get('address', 'Non disponible')}\n"
                
                # Instructions d'évacuation étape par étape
                message += "🏃 **INSTRUCTIONS D'ÉVACUATION:**\n"
                for step in route['steps']:
                    message += f"   {step}\n"
                
                # Avertissements
                if route.get('warnings'):
                    message += f"⚠️ **Attention:** {route['warnings'][0]}\n"
                    
                message += "\n" + "="*50 + "\n\n"
            
            # Conseils généraux d'évacuation
            message += "🔥 **CONSEILS D'ÉVACUATION:**\n"
            message += "• Restez calme et suivez les instructions\n"
            message += "• Gardez votre téléphone chargé et allumé\n"
            message += "• Évitez les zones sombres et isolées\n"
            message += "• Signalez-vous aux forces de l'ordre si vous les croisez\n"
            message += "• Une fois en sécurité, contactez vos proches\n"
            
            return message
            
        except Exception as e:
            self.logger.error(f"Erreur génération plan d'évacuation: {e}")
            return "❌ Erreur lors de la génération du plan d'évacuation"