#!/usr/bin/env python3
"""
Test rapide de l'API Google Places
"""

import yaml
import requests

def test_places_api():
    """Test simple de l'API Google Places"""
    
    # Charger la configuration
    with open('api_keys.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Récupérer la clé API Places
    services = config.get('google_cloud', {}).get('services', {})
    places_key = services.get('places_api_key')
    
    print(f"🔑 Clé Places API: {places_key[:20]}..." if places_key else "❌ Pas de clé API")
    
    if not places_key or places_key.startswith("YOUR_"):
        print("❌ API Places non configurée")
        return
    
    # Test avec les coordonnées de la rue de Londres
    location = "48.8756,2.3264"  # 8 rue de Londres, Paris
    
    places_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    
    params = {
        'location': location,
        'radius': 500,
        'type': 'hospital',
        'language': 'fr',
        'key': places_key
    }
    
    print("🔍 Test de recherche d'hôpitaux à proximité...")
    
    try:
        response = requests.get(places_url, params=params, timeout=10)
        print(f"📡 Statut réponse: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📊 Statut API: {data.get('status')}")
            
            if data['status'] == 'OK':
                results = data.get('results', [])
                print(f"✅ {len(results)} hôpitaux trouvés")
                
                for i, place in enumerate(results[:3]):
                    print(f"  {i+1}. {place.get('name')} - {place.get('vicinity')}")
            else:
                print(f"⚠️ Erreur API: {data.get('status')} - {data.get('error_message', '')}")
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_places_api()