#!/usr/bin/env python3
"""
Script pour tester le système de fallback Guardian
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:5002"
TEST_SITUATIONS = [
    {
        "situation": "J'ai très mal au coeur, ça serre fort",
        "expected_level": 8,
        "description": "Urgence médicale cardiaque"
    },
    {
        "situation": "Il y a quelqu'un de suspect qui me suit",
        "expected_level": 7,
        "description": "Problème de sécurité"
    },
    {
        "situation": "Je suis perdu dans Paris",
        "expected_level": 5,
        "description": "Problème d'orientation"
    },
    {
        "situation": "J'ai de l'anxiété",
        "expected_level": 4,
        "description": "Soutien psychologique"
    },
    {
        "situation": "Bonjour Guardian",
        "expected_level": 3,
        "description": "Situation normale"
    },
    {
        "situation": "Au secours urgence accident",
        "expected_level": 9,
        "description": "Urgence majeure"
    }
]

def test_guardian_api(situation, user_info=None):
    """Test l'API Guardian avec une situation donnée"""
    if user_info is None:
        user_info = {
            "firstName": "TestUser",
            "lastName": "Fallback",
            "phone": "+33612345678"
        }
    
    data = {
        "situation": situation,
        "user_info": user_info,
        "location": "Test Location"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/guardian/analyze", 
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Erreur HTTP {response.status_code}: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion: {e}")
        return None

def main():
    print("🧪 === TEST SYSTÈME FALLBACK GUARDIAN ===")
    print("Analyse des différents types de situations")
    print("=" * 50)
    
    # Vérifier que le serveur est accessible
    try:
        response = requests.get(f"{BASE_URL}/api/status", timeout=5)
        if response.status_code != 200:
            print("❌ Serveur Guardian non accessible")
            return False
    except:
        print("❌ Serveur Guardian non accessible")
        return False
    
    print("✅ Serveur Guardian accessible")
    print()
    
    # Tester chaque situation
    results = []
    for i, test_case in enumerate(TEST_SITUATIONS, 1):
        print(f"📝 Test {i}: {test_case['description']}")
        print(f"💬 Situation: \"{test_case['situation']}\"")
        
        result = test_guardian_api(test_case['situation'])
        
        if result:
            urgency = result.get('urgency_level', 0)
            mode = "Guardian AI" if result.get('guardian_active', False) else "Fallback"
            status = result.get('status', 'unknown')
            
            print(f"🎯 Urgence: {urgency}/10 (attendu: {test_case['expected_level']})")
            print(f"🔧 Mode: {mode}")
            print(f"📊 Statut: {status}")
            
            if result.get('fallback_mode'):
                print("🔄 Mode Fallback activé!")
                print(f"🏥 Type: {result.get('emergency_type', 'Non défini')}")
            
            # Afficher les conseils
            advice = result.get('advice', [])
            if advice and len(advice) > 0:
                print(f"💡 Conseil: {advice[0]}")
            
            # Vérifier la cohérence du niveau d'urgence
            level_ok = abs(urgency - test_case['expected_level']) <= 2
            print(f"✅ Niveau cohérent" if level_ok else f"⚠️ Niveau incohérent")
            
            results.append({
                'test': test_case['description'],
                'situation': test_case['situation'],
                'urgency_actual': urgency,
                'urgency_expected': test_case['expected_level'],
                'mode': mode,
                'status': status,
                'level_ok': level_ok
            })
        else:
            print("❌ Échec du test")
            results.append({
                'test': test_case['description'],
                'status': 'FAILED'
            })
        
        print("-" * 40)
    
    # Résumé
    print("\n📊 === RÉSUMÉ DES TESTS ===")
    success_count = sum(1 for r in results if r.get('level_ok', False))
    total_tests = len(TEST_SITUATIONS)
    
    print(f"Tests réussis: {success_count}/{total_tests}")
    print(f"Précision: {(success_count/total_tests)*100:.1f}%")
    
    # Détail des modes utilisés
    fallback_count = sum(1 for r in results if r.get('mode') == 'Fallback')
    guardian_count = sum(1 for r in results if r.get('mode') == 'Guardian AI')
    
    print(f"Mode Guardian AI: {guardian_count} tests")
    print(f"Mode Fallback: {fallback_count} tests")
    
    if fallback_count > 0:
        print(f"\n🔄 Système de fallback testé et fonctionnel!")
    
    return success_count == total_tests

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)