#!/usr/bin/env python3
"""
Test rapide du système IA de GuardianNav
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from guardian.intelligent_advisor import IntelligentAdvisor, SmartResponseSystem

def test_ai_system():
    """Test du système d'IA"""
    print("🧪 Test du système d'IA GuardianNav")
    print("="*50)
    
    # Initialiser le système IA
    advisor = IntelligentAdvisor()
    smart_system = SmartResponseSystem(advisor)
    
    # Test 1: Réponse "non"
    print("\n📋 Test 1: Réponse 'non'")
    response = smart_system.process_emergency_response("non", "alerte_declenchee")
    print(f"Type: {response['type']}")
    print(f"Message: {response['message']}")
    print(f"Urgence: {response['urgency']}")
    
    # Test 2: Description d'urgence médicale
    print("\n📋 Test 2: Urgence médicale")
    description = "Je suis tombé et j'ai mal à la jambe, je ne peux pas me lever"
    response = smart_system.process_emergency_response(description)
    print(f"Type: {response['type']}")
    print(f"Urgence: {response['urgency']}")
    if 'analysis' in response:
        analysis = response['analysis']
        print(f"Type d'urgence: {analysis['emergency_type']}")
        print(f"Actions immédiates: {analysis['immediate_actions']}")
        print("\nConseils:")
        for i, conseil in enumerate(analysis['advice'], 1):
            print(f"  {i}. {conseil}")
    
    # Test 3: Situation de sécurité
    print("\n📋 Test 3: Problème de sécurité")
    description = "Je pense qu'on me suit, j'ai peur"
    response = smart_system.process_emergency_response(description)
    if 'analysis' in response:
        analysis = response['analysis']
        print(f"Type d'urgence: {analysis['emergency_type']}")
        print(f"Niveau d'urgence: {analysis['urgency_level']}")
        print("Actions immédiates:")
        for action in analysis['immediate_actions']:
            print(f"  • {action}")
    
    # Test 4: Personne perdue
    print("\n📋 Test 4: Personne perdue")
    description = "Je suis perdu, je ne reconnais pas l'endroit où je suis"
    response = smart_system.process_emergency_response(description)
    if 'analysis' in response:
        analysis = response['analysis']
        print(f"Type d'urgence: {analysis['emergency_type']}")
        print("Conseils principaux:")
        for conseil in analysis['advice'][:3]:  # Premiers 3 conseils
            print(f"  📍 {conseil}")
    
    print("\n✅ Tests terminés!")

if __name__ == "__main__":
    test_ai_system()