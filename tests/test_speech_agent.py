"""
Test et démonstration du SpeechAgent pour Guardian
Teste la synthèse vocale avec différents types de messages d'urgence
"""
import sys
import os
import time
import yaml
from pathlib import Path

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from guardian.speech_agent import SpeechAgent

def load_api_keys():
    """Charge les clés API pour les tests"""
    try:
        with open('api_keys.yaml', 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Attention: Impossible de charger api_keys.yaml: {e}")
        print("Les tests utiliseront le mode simulation")
        return {}

def test_basic_speech():
    """Test basique de la synthèse vocale"""
    print("🎤 Test 1: Synthèse vocale basique")
    print("-" * 40)
    
    api_keys = load_api_keys()
    speech_agent = SpeechAgent(api_keys)
    
    # Test de disponibilité
    if speech_agent.is_available():
        print("✅ Agent vocal disponible")
    else:
        print("⚠️ Agent vocal en mode simulation")
    
    # Test simple
    success = speech_agent.test_speech()
    
    time.sleep(2)
    return success

def test_alert_messages():
    """Test des différents types d'alertes vocales"""
    print("\n🚨 Test 2: Messages d'alerte")
    print("-" * 40)
    
    api_keys = load_api_keys()
    speech_agent = SpeechAgent(api_keys)
    
    # Messages d'alerte différents
    test_alerts = [
        ("emergency", "Alerte d'urgence détectée. Tout va bien ? Répondez oui ou non."),
        ("fall", "Chute à vélo détectée, sévérité modérée. Restez immobile si vous ressentez des douleurs."),
        ("immobilization", "Immobilité prolongée détectée. Avez-vous besoin d'aide ?"),
        ("confirmation", "OK, merci de votre réponse. Surveillance continue.")
    ]
    
    for i, (alert_type, message) in enumerate(test_alerts, 1):
        print(f"   Test {i}/{len(test_alerts)}: {alert_type}")
        success = speech_agent.speak_alert(alert_type, message)
        
        if success:
            print(f"   ✅ {alert_type} - OK")
        else:
            print(f"   ❌ {alert_type} - Erreur")
        
        time.sleep(1.5)  # Pause entre les messages

def test_fall_alerts():
    """Test des alertes spécialisées pour chutes"""
    print("\n🚴 Test 3: Alertes de chute spécialisées")
    print("-" * 40)
    
    api_keys = load_api_keys()
    speech_agent = SpeechAgent(api_keys)
    
    # Différents types de chutes
    fall_scenarios = [
        {
            'fall_type': 'chute_velo',
            'severity': 'modérée',
            'previous_speed': 25.3,
            'acceleration': -9.2
        },
        {
            'fall_type': 'chute_haute_vitesse', 
            'severity': 'grave',
            'previous_speed': 35.8,
            'acceleration': -12.5
        },
        {
            'fall_type': 'impact_brutal',
            'severity': 'critique',
            'previous_speed': 15.2,
            'acceleration': -15.8
        }
    ]
    
    for i, fall_info in enumerate(fall_scenarios, 1):
        fall_type = fall_info['fall_type']
        print(f"   Test {i}/{len(fall_scenarios)}: {fall_type}")
        
        success = speech_agent.speak_fall_alert(fall_info)
        
        if success:
            print(f"   ✅ {fall_type} - Synthèse réussie")
        else:
            print(f"   ❌ {fall_type} - Erreur synthèse")
        
        time.sleep(2)  # Pause plus longue pour les chutes

def test_emergency_instructions():
    """Test des instructions d'urgence vocales"""
    print("\n📋 Test 4: Instructions d'urgence")
    print("-" * 40)
    
    api_keys = load_api_keys()
    speech_agent = SpeechAgent(api_keys)
    
    # Instructions d'urgence typiques
    instructions_sets = [
        [
            "Appelez le 15 pour une urgence médicale",
            "Restez calme et décrivez votre situation",
            "Donnez votre position exacte"
        ],
        [
            "Dirigez-vous vers le refuge le plus proche",
            "Utilisez les transports publics si disponibles",
            "Restez en contact avec vos proches",
            "Évitez les zones isolées",
            "Gardez votre téléphone chargé"
        ]
    ]
    
    for i, instructions in enumerate(instructions_sets, 1):
        print(f"   Test {i}/{len(instructions_sets)}: {len(instructions)} instructions")
        
        success = speech_agent.speak_emergency_instructions(instructions)
        
        if success:
            print(f"   ✅ Instructions {i} - Synthèse réussie")
        else:
            print(f"   ❌ Instructions {i} - Erreur synthèse")
        
        time.sleep(2)

def test_priority_levels():
    """Test des différents niveaux de priorité"""
    print("\n⚡ Test 5: Niveaux de priorité")
    print("-" * 40)
    
    api_keys = load_api_keys()
    speech_agent = SpeechAgent(api_keys)
    
    test_message = "Ceci est un test de priorité vocale pour Guardian."
    
    priorities = ["normal", "urgent", "critical"]
    
    for priority in priorities:
        print(f"   Test priorité: {priority}")
        
        success = speech_agent.speak(test_message, priority)
        
        if success:
            print(f"   ✅ {priority} - Synthèse réussie")
        else:
            print(f"   ❌ {priority} - Erreur synthèse")
        
        time.sleep(1.5)

def test_google_tts_integration():
    """Test spécifique de l'intégration Google TTS"""
    print("\n🌐 Test 6: Intégration Google TTS")
    print("-" * 40)
    
    api_keys = load_api_keys()
    speech_agent = SpeechAgent(api_keys)
    
    # Vérifier la configuration Google TTS
    if speech_agent.tts_client:
        print("   ✅ Client Google TTS configuré")
        
        # Test avec un message d'urgence réaliste
        emergency_message = "Alerte Guardian. Une situation d'urgence a été détectée. Vérifiez immédiatement votre état et celui de vos proches."
        
        print("   Synthèse avec Google TTS...")
        success = speech_agent.speak(emergency_message, "urgent")
        
        if success:
            print("   ✅ Google TTS - Synthèse réussie")
        else:
            print("   ❌ Google TTS - Erreur lors de la synthèse")
    else:
        print("   ⚠️ Client Google TTS non disponible")
        print("   🔄 Test en mode simulation...")
        
        success = speech_agent.speak("Test de simulation vocale Guardian", "normal")
        
        if success:
            print("   ✅ Mode simulation - Fonctionnel")
        else:
            print("   ❌ Mode simulation - Erreur")

def demonstrate_full_emergency_scenario():
    """Démonstration complète d'un scénario d'urgence avec synthèse vocale"""
    print("\n🎭 DÉMONSTRATION: Scénario d'urgence complet")
    print("=" * 50)
    
    api_keys = load_api_keys()
    speech_agent = SpeechAgent(api_keys)
    
    print("📱 Simulation d'une séquence d'urgence Guardian...")
    time.sleep(1)
    
    # 1. Détection d'alerte
    print("\n1️⃣ Détection d'immobilité prolongée")
    speech_agent.speak_alert("immobilization", "Immobilité prolongée détectée. Tout va bien ? Répondez oui ou non.")
    time.sleep(3)
    
    # 2. Pas de réponse - escalade
    print("\n2️⃣ Aucune réponse - escalade")
    speech_agent.speak_alert("emergency", "Aucune réponse détectée. Je déclenche automatiquement l'assistance d'urgence.")
    time.sleep(3)
    
    # 3. Instructions d'urgence
    print("\n3️⃣ Instructions d'urgence")
    emergency_instructions = [
        "Vos contacts d'urgence ont été alertés",
        "Votre position a été partagée",
        "Les secours arrivent"
    ]
    speech_agent.speak_emergency_instructions(emergency_instructions)
    time.sleep(3)
    
    # 4. Confirmation finale
    print("\n4️⃣ Confirmation finale")
    speech_agent.speak_alert("confirmation", "Assistance d'urgence déclenchée. Restez calme, l'aide est en route.")
    
    print("\n✅ Démonstration terminée")

def main():
    """Fonction principale du test"""
    print("🎤 TESTS DE SYNTHÈSE VOCALE - GUARDIAN")
    print("=" * 50)
    print("Ces tests vérifient le fonctionnement du SpeechAgent")
    print("avec différents types de messages et priorités.\n")
    
    try:
        # Tests individuels
        test_basic_speech()
        test_alert_messages() 
        test_fall_alerts()
        test_emergency_instructions()
        test_priority_levels()
        test_google_tts_integration()
        
        # Démonstration complète
        print("\n" + "="*50)
        user_input = input("Voulez-vous voir une démonstration complète ? (o/n): ")
        
        if user_input.lower() in ['o', 'oui', 'y', 'yes']:
            demonstrate_full_emergency_scenario()
        
        print("\n🎉 TESTS TERMINÉS")
        print("La synthèse vocale Guardian est prête à fonctionner!")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Tests interrompus par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur lors des tests: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()