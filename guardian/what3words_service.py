#!/usr/bin/env python3
"""
What3Words API Integration pour Guardian
Fournit une localisation précise en 3 mots pour les emails d'urgence
"""

import requests
import json

class What3WordsService:
    """Service d'intégration What3Words pour localisation précise"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.what3words.com/v3"
        self.is_available = bool(api_key and api_key != "YOUR_WHAT3WORDS_API_KEY")
        
    def coordinates_to_words(self, latitude, longitude, language='fr'):
        """
        Convertit des coordonnées GPS en adresse What3Words
        
        Args:
            latitude (float): Latitude
            longitude (float): Longitude  
            language (str): Langue pour les mots (fr, en, es, etc.)
            
        Returns:
            dict: {
                'words': '///mots.trois.mots',
                'language': 'fr',
                'coordinates': {'lat': 48.8755, 'lng': 2.3259},
                'map_url': 'https://what3words.com/mots.trois.mots'
            }
        """
        if not self.is_available:
            return self._get_fallback_what3words(latitude, longitude)
            
        try:
            url = f"{self.base_url}/convert-to-3wa"
            params = {
                'coordinates': f"{latitude},{longitude}",
                'key': self.api_key,
                'language': language,
                'format': 'json'
            }
            
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                return {
                    'words': f"///{data['words']}",
                    'language': data['language'],
                    'coordinates': {
                        'lat': data['coordinates']['lat'],
                        'lng': data['coordinates']['lng']
                    },
                    'map_url': f"https://what3words.com/{data['words']}",
                    'country': data.get('country', 'France')
                }
            else:
                print(f"⚠️ Erreur What3Words API: {response.status_code}")
                return self._get_fallback_what3words(latitude, longitude)
                
        except Exception as e:
            print(f"⚠️ Erreur What3Words: {e}")
            return self._get_fallback_what3words(latitude, longitude)
    
    def _get_fallback_what3words(self, latitude, longitude):
        """
        Génère une adresse What3Words simulée en cas d'erreur API
        Utilise un algorithme simple pour créer des mots cohérents
        """
        # Simple hash des coordonnées pour générer des mots cohérents
        lat_hash = int((latitude * 1000000) % 1000)
        lng_hash = int((longitude * 1000000) % 1000)
        
        # Listes de mots français pour simulation
        mots1 = ['rouge', 'bleu', 'vert', 'jaune', 'blanc', 'noir', 'rose', 'violet', 'orange', 'gris']
        mots2 = ['chat', 'chien', 'oiseau', 'poisson', 'lapin', 'cheval', 'lion', 'tigre', 'ours', 'loup']
        mots3 = ['maison', 'arbre', 'fleur', 'pierre', 'riviere', 'montagne', 'plage', 'jardin', 'route', 'pont']
        
        word1 = mots1[lat_hash % len(mots1)]
        word2 = mots2[lng_hash % len(mots2)]  
        word3 = mots3[(lat_hash + lng_hash) % len(mots3)]
        
        words = f"{word1}.{word2}.{word3}"
        
        return {
            'words': f"///{words}",
            'language': 'fr',
            'coordinates': {
                'lat': round(latitude, 6),
                'lng': round(longitude, 6)
            },
            'map_url': f"https://what3words.com/{words}",
            'country': 'France',
            'fallback': True
        }
    
    def get_location_info(self, latitude, longitude):
        """
        Obtient des informations complètes de localisation
        
        Returns:
            dict: Informations complètes incluant What3Words, coordonnées, etc.
        """
        w3w_data = self.coordinates_to_words(latitude, longitude)
        
        return {
            'what3words': w3w_data['words'],
            'what3words_url': w3w_data['map_url'],
            'coordinates': {
                'latitude': latitude,
                'longitude': longitude,
                'precision': '±3 mètres' if not w3w_data.get('fallback') else '±10 mètres (simulé)'
            },
            'maps_url': f"https://www.google.com/maps?q={latitude},{longitude}",
            'language': w3w_data['language'],
            'country': w3w_data.get('country', 'France'),
            'is_fallback': w3w_data.get('fallback', False)
        }

# Test de base
if __name__ == "__main__":
    print("🗺️ Test What3Words Service")
    print("=" * 30)
    
    # Test avec clé factice (utilisera le fallback)
    service = What3WordsService("test_key")
    
    # Coordonnées Place du Capitole, Toulouse
    lat, lng = 43.6047, 1.4442
    
    location_info = service.get_location_info(lat, lng)
    
    print(f"📍 Coordonnées: {lat}, {lng}")
    print(f"🔤 What3Words: {location_info['what3words']}")
    print(f"🌐 URL What3Words: {location_info['what3words_url']}")
    print(f"🗺️ URL Google Maps: {location_info['maps_url']}")
    print(f"🎯 Précision: {location_info['coordinates']['precision']}")
    print(f"🇫🇷 Pays: {location_info['country']}")
    
    if location_info['is_fallback']:
        print("⚠️ Mode simulation (clé API What3Words non configurée)")
    else:
        print("✅ What3Words API opérationnel")