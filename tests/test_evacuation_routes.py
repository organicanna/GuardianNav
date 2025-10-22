#!/usr/bin/env python3
"""
Test des nouvelles fonctionnalités d'évacuation avec Google Directions API
"""

import sys
import os

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from guardian.emergency_locations import EmergencyLocationService
import logging

def test_evacuation_routes():
    """Test des itinéraires d'évacuation"""
    
    # Configuration des logs
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    print("🧪 Test des itinéraires d'évacuation avec Directions API")
    print("=" * 60)
    
    # Initialisation du service
    api_keys_config = {
        'google_maps_api_key': None,  # Mode simulation
        'google_places_api_key': None
    }
    emergency_service = EmergencyLocationService(api_keys_config)
    
    # Position de test (Paris - Châtelet)
    test_location = (48.8566, 2.3522)
    
    print(f"📍 Position de test: {test_location}")
    print()
    
    # Test 1: Trouver des refuges
    print("🔍 Recherche de refuges...")
    refuges = emergency_service.find_emergency_refuges(test_location, radius_m=500)
    
    if refuges:
        print(f"✅ {len(refuges)} refuges trouvés")
        
        # Test 2: Calculer un itinéraire vers le premier refuge
        print("\n🧭 Calcul d'itinéraire d'évacuation...")
        refuge = refuges[0]
        
        route = emergency_service.get_escape_route_to_refuge(
            test_location,
            (refuge['location']['lat'], refuge['location']['lng'])
        )
        
        print(f"📊 Résultat de l'itinéraire:")
        print(f"   Distance: {route['distance']}")
        print(f"   Durée: {route['duration']}")
        print(f"   Étapes: {len(route['steps'])}")
        
        print("\n🚶 Instructions d'évacuation:")
        for step in route['steps']:
            print(f"   {step}")
            
        if route.get('warnings'):
            print(f"\n⚠️ Avertissements: {route['warnings']}")
            
    else:
        print("❌ Aucun refuge trouvé")
    
    print("\n" + "="*60)
    
    # Test 3: Plan d'évacuation complet
    print("📋 Test du plan d'évacuation détaillé...")
    
    evacuation_plan = emergency_service.get_detailed_evacuation_plan(test_location)
    print(evacuation_plan)
    
    print("\n✅ Test terminé")

if __name__ == "__main__":
    test_evacuation_routes()