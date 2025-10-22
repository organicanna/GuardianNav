#!/usr/bin/env python3
"""
Test des nouvelles fonctionnalités d'urgence : refuges, transports et alertes
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from guardian.emergency_locations import EmergencyLocationService
from guardian.emergency_response import EmergencyResponse
from guardian.intelligent_advisor import IntelligentAdvisor, SmartResponseSystem

def test_emergency_locations():
    """Test du système de localisation d'urgence"""
    print("🧪 Test du système de localisation d'urgence")
    print("="*60)
    
    # Position exemple (République, Paris)
    test_location = (48.8675, 2.3635)
    
    # Initialiser le service
    api_config = {}
    location_service = EmergencyLocationService(api_config)
    
    # Test 1: Refuges d'urgence
    print("\n📍 Test 1: Recherche de refuges d'urgence")
    refuges = location_service.find_emergency_refuges(test_location)
    print(f"Refuges trouvés: {len(refuges)}")
    for refuge in refuges[:3]:
        status = "🟢 OUVERT" if refuge.get('is_open') else "🔴 FERMÉ"
        print(f"  • {refuge['name']} ({refuge['distance_m']}m) {status}")
    
    # Test 2: Transports d'urgence
    print("\n🚇 Test 2: Recherche de transports d'urgence")
    transports = location_service.find_emergency_transport(test_location)
    
    for transport_type, options in transports.items():
        if options:
            print(f"\n{transport_type.upper()}:")
            for option in options[:2]:  # Max 2 par type
                if 'distance_m' in option:
                    print(f"  • {option['name']} ({option['distance_m']}m)")
    
    # Test 3: Message formaté
    print("\n📋 Test 3: Message d'urgence formaté")
    message = location_service.format_emergency_locations_message(refuges[:3], transports)
    print(message)

def test_danger_scenarios():
    """Test des scénarios de danger"""
    print("\n\n🚨 Test des scénarios de danger")
    print("="*60)
    
    advisor = IntelligentAdvisor()
    smart_system = SmartResponseSystem(advisor)
    
    # Scénarios de test
    scenarios = [
        "Quelqu'un me suit depuis 10 minutes, j'ai peur",
        "Je pense qu'on m'a agressé, je suis blessé",
        "Un homme me menace et demande mon téléphone",
        "Je suis perdu dans une zone dangereuse la nuit",
        "Ma voiture est en panne dans un endroit isolé"
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n📋 Scénario {i}: {scenario}")
        response = smart_system.process_emergency_response(scenario)
        
        if 'analysis' in response:
            analysis = response['analysis']
            print(f"   Type: {analysis['emergency_type']}")
            print(f"   Urgence: {analysis['urgency_level']}")
            print("   Actions immédiates:")
            for action in analysis['immediate_actions'][:2]:
                print(f"     • {action}")

def test_emergency_messages():
    """Test des messages d'urgence"""
    print("\n\n📧 Test des messages d'urgence")
    print("="*60)
    
    # Configuration test
    config = {
        'emergency_contacts': [
            {'name': 'Contact Test', 'email': 'test@example.com', 'phone': '+33123456789'}
        ],
        'email': {'enabled': False}  # Mode simulation
    }
    
    emergency_system = EmergencyResponse(config)
    test_location = (48.8675, 2.3635)
    
    print("\n📱 Test 1: Alerte de danger immédiat")
    emergency_system.send_immediate_danger_alert(test_location, "Agression en cours")
    
    print("\n📍 Test 2: Alerte avec refuges")
    refuges_info = """
🏠 REFUGES SÛRS:
   • Le Refuge Bar (150m) 🟢 OUVERT
   • Pharmacie de Garde (320m) 🟢 OUVERT

🚇 TRANSPORTS D'URGENCE:
   🚇 Métro République (250m) - Lignes: 3, 5, 8, 9, 11
   🚌 Bus République (180m) - Prochains: 2 min, 8 min
"""
    emergency_system.send_location_with_refuges_info(test_location, refuges_info, "Aide requise avec refuges")

def main():
    """Fonction principale de test"""
    print("🚨 GuardianNav - Test des fonctionnalités d'urgence avancées")
    print("="*70)
    
    try:
        test_emergency_locations()
        test_danger_scenarios()
        test_emergency_messages()
        
        print("\n" + "="*70)
        print("✅ Tous les tests terminés avec succès!")
        print("\n🔧 Pour utiliser ces fonctionnalités:")
        print("   1. Configurez vos clés API dans api_keys.yaml")
        print("   2. Ajoutez vos contacts d'urgence dans config.yaml") 
        print("   3. Le système détectera automatiquement les situations de danger")
        print("   4. Les refuges et transports seront trouvés automatiquement")
        
    except Exception as e:
        print(f"❌ Erreur durant les tests: {e}")

if __name__ == "__main__":
    main()