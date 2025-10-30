#!/usr/bin/env python3
"""
Test Runner pour Guardian
Exécute tous les tests ou des catégories spécifiques
"""

import sys
import os
import subprocess
from pathlib import Path

def run_test(test_file, description=""):
    """Exécute un test spécifique"""
    print(f"\n🧪 Exécution: {test_file}")
    if description:
        print(f"   📝 {description}")
    print("-" * 50)
    
    try:
        result = subprocess.run([sys.executable, str(test_file)], 
                              capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print(f"✅ {test_file.name} - RÉUSSI")
            if result.stdout:
                print(result.stdout[-500:])  # Dernières 500 caractères
        else:
            print(f"❌ {test_file.name} - ÉCHEC")
            if result.stderr:
                print(f"Erreur: {result.stderr[-300:]}")
            if result.stdout:
                print(f"Sortie: {result.stdout[-200:]}")
                
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print(f"⏰ {test_file.name} - TIMEOUT (60s)")
        return False
    except Exception as e:
        print(f"💥 {test_file.name} - ERREUR: {e}")
        return False

def run_tests_category(category):
    """Exécute les tests d'une catégorie"""
    tests_dir = Path("tests")
    
    categories = {
        "email": [
            ("test_whatsapp.py", "Test intégration WhatsApp"),
            ("test_email_content.py", "Test contenu emails")
        ],
        "ai": [
            ("test_gemini_simple.py", "Test Gemini IA"),
            ("test_hybrid_approach.py", "Test approche hybride"),
            ("test_guardian_fall_response.py", "Test réponse chute")
        ],
        "voice": [
            ("test_voice_agent.py", "Test agent vocal"),
            ("test_voice_conversation.py", "Test conversation vocale"),
            ("test_speech_agent.py", "Test reconnaissance vocale")
        ],
        "security": [
            ("test_fall_detector.py", "Test détecteur chute"),
            ("test_evacuation_routes.py", "Test routes évacuation"),
            ("test_static_agent.py", "Test agent statique")
        ],
        "config": [
            ("test_api_config.py", "Test configuration API")
        ]
    }
    
    if category not in categories:
        print(f"❌ Catégorie inconnue: {category}")
        print(f"   Disponibles: {', '.join(categories.keys())}")
        return False
    
    print(f"🚀 TESTS CATÉGORIE: {category.upper()}")
    print("=" * 60)
    
    success_count = 0
    total_count = 0
    
    for test_name, description in categories[category]:
        test_file = tests_dir / test_name
        if test_file.exists():
            total_count += 1
            if run_test(test_file, description):
                success_count += 1
        else:
            print(f"⚠️ Test non trouvé: {test_name}")
    
    print(f"\n📊 RÉSULTATS CATÉGORIE {category.upper()}:")
    print(f"   ✅ Réussis: {success_count}/{total_count}")
    print(f"   ❌ Échecs: {total_count - success_count}")
    
    return success_count == total_count

def run_all_tests():
    """Exécute tous les tests"""
    print("🚀 EXÉCUTION DE TOUS LES TESTS GUARDIAN")
    print("=" * 70)
    
    categories = ["email", "ai", "voice", "security", "config"]
    results = {}
    
    for category in categories:
        results[category] = run_tests_category(category)
    
    print(f"\n📊 RÉSULTATS GLOBAUX:")
    print("=" * 30)
    for category, success in results.items():
        status = "✅ RÉUSSI" if success else "❌ ÉCHEC"
        print(f"   {category.upper()}: {status}")
    
    total_success = sum(results.values())
    total_categories = len(results)
    
    print(f"\n🎯 SCORE GLOBAL: {total_success}/{total_categories} catégories réussies")
    
    if total_success == total_categories:
        print("🎉 TOUS LES TESTS RÉUSSIS !")
        return True
    else:
        print("⚠️ Certains tests ont échoué")
        return False

def main():
    """Point d'entrée principal"""
    if len(sys.argv) < 2:
        print("🧪 TEST RUNNER GUARDIAN")
        print("=" * 30)
        print("Usage:")
        print("  python3 run_tests.py all              # Tous les tests")
        print("  python3 run_tests.py email            # Tests emails")
        print("  python3 run_tests.py ai               # Tests IA")  
        print("  python3 run_tests.py voice            # Tests vocaux")
        print("  python3 run_tests.py security         # Tests sécurité")
        print("  python3 run_tests.py config           # Tests config")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "all":
        success = run_all_tests()
    else:
        success = run_tests_category(command)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()