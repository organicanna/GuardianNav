"""
Démonstration de la synthèse vocale GuardianNav
Teste la nouvelle fonctionnalité de synthèse vocale avec Google TTS
"""
import sys
import time
import yaml
from pathlib import Path

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def demo_speech_integration():
    """Démonstration complète de l'intégration vocale"""
    
    print("🎤 DÉMONSTRATION SYNTHÈSE VOCALE GUARDIANNAV")
    print("=" * 55)
    print("Cette démonstration teste la nouvelle fonctionnalité")
    print("de synthèse vocale intégrée à GuardianNav.\n")
    
    # Charger la configuration
    try:
        from guardian.guardian_agent import GuardianOrchestrator
        from guardian.config import Config
        
        config = Config()
        
        # Charger les clés API
        try:
            with open('api_keys.yaml', 'r', encoding='utf-8') as f:
                api_keys_config = yaml.safe_load(f)
            print("✅ Clés API chargées")
        except Exception as e:
            print(f"⚠️  Clés API non disponibles: {e}")
            print("🔄 Utilisation du mode simulation")
            api_keys_config = {}
        
        # Créer l'orchestrateur avec synthèse vocale
        print("\n🤖 Initialisation de GuardianNav avec synthèse vocale...")
        
        # Configuration minimale pour la démo
        demo_config = {
            'emergency_response': {
                'timeout_seconds': 30,
                'emergency_contacts': [
                    {
                        'name': 'Contact Démo',
                        'email': 'demo@example.com',
                        'phone': '+33123456789'
                    }
                ],
                'email': {
                    'enabled': False  # Désactivé pour la démo
                }
            }
        }
        
        orchestrator = GuardianOrchestrator(demo_config)
        
        # Tester la disponibilité de la synthèse vocale
        if orchestrator.speech_agent.is_available():
            print("🔊 Synthèse vocale disponible")
            
            if orchestrator.speech_agent.tts_client:
                print("🌐 Google Text-to-Speech configuré")
            else:
                print("🎭 Mode simulation activé")
        else:
            print("❌ Synthèse vocale non disponible")
            return
        
        # Démonstration des différents types de messages
        print("\n" + "="*55)
        print("🎭 DÉMONSTRATION DES MESSAGES VOCAUX")
        print("="*55)
        
        # 1. Message de bienvenue
        print("\n1️⃣ Message de bienvenue")
        orchestrator.speech_agent.speak_alert("info", "Bienvenue dans GuardianNav avec synthèse vocale intégrée.")
        time.sleep(3)
        
        # 2. Simulation d'alerte d'immobilité
        print("\n2️⃣ Alerte d'immobilité")
        orchestrator.current_position = (48.8566, 2.3522)  # Position Paris
        
        print("   📍 Simulation: Immobilité prolongée détectée")
        alert_message = "Immobilité prolongée détectée. Tout va bien ? Répondez oui ou non."
        print(f"   🔊 Synthèse: '{alert_message}'")
        orchestrator.speech_agent.speak_alert("immobilization", alert_message)
        time.sleep(4)
        
        # 3. Simulation de réponse positive
        print("\n3️⃣ Réponse positive simulée")
        print("   ✅ Simulation: Utilisateur répond 'oui'")
        confirmation_message = "OK, merci de votre réponse. Surveillance continue."
        print(f"   🔊 Synthèse: '{confirmation_message}'")
        orchestrator.speech_agent.speak_alert("confirmation", confirmation_message)
        time.sleep(3)
        
        # 4. Simulation de chute
        print("\n4️⃣ Détection de chute")
        fall_info = {
            'fall_type': 'chute_velo',
            'severity': 'modérée',
            'previous_speed': 25.3,
            'acceleration': -9.2,
            'position': (48.8566, 2.3522)
        }
        
        print("   🚴 Simulation: Chute à vélo détectée")
        print(f"   📊 Vitesse: {fall_info['previous_speed']} km/h")
        print(f"   📊 Décélération: {fall_info['acceleration']} m/s²")
        
        orchestrator.speech_agent.speak_fall_alert(fall_info)
        time.sleep(4)
        
        # 5. Question post-chute
        print("\n5️⃣ Question post-chute")
        injury_question = "Êtes-vous blessé ? Répondez oui ou non dans les 30 secondes."
        print(f"   🔊 Synthèse: '{injury_question}'")
        orchestrator.speech_agent.speak_alert("emergency", injury_question)
        time.sleep(4)
        
        # 6. Simulation de réponse négative (blessé)
        print("\n6️⃣ Réponse 'oui' - Blessure confirmée")
        print("   🚨 Simulation: Utilisateur confirme être blessé")
        emergency_message = "URGENCE CONFIRMÉE. Blessure après chute. Je déclenche immédiatement les secours."
        print(f"   🔊 Synthèse: '{emergency_message}'")
        orchestrator.speech_agent.speak_alert("emergency", emergency_message)
        time.sleep(4)
        
        # 7. Instructions d'urgence
        print("\n7️⃣ Instructions d'urgence")
        emergency_instructions = [
            "Vos contacts d'urgence ont été alertés",
            "Votre position a été partagée",
            "Restez calme, les secours arrivent"
        ]
        
        print("   📋 Instructions d'urgence vocales:")
        for instruction in emergency_instructions:
            print(f"      • {instruction}")
        
        orchestrator.speech_agent.speak_emergency_instructions(emergency_instructions)
        time.sleep(4)
        
        # 8. Test des priorités
        print("\n8️⃣ Test des niveaux de priorité")
        
        priorities = [
            ("normal", "Message de priorité normale"),
            ("urgent", "Message de priorité urgente"),
            ("critical", "Message de priorité critique")
        ]
        
        for priority, message in priorities:
            print(f"   🔊 Priorité {priority}: {message}")
            orchestrator.speech_agent.speak(message, priority)
            time.sleep(2.5)
        
        # Conclusion
        print("\n" + "="*55)
        print("✅ DÉMONSTRATION TERMINÉE")
        print("="*55)
        
        conclusion_message = "Démonstration de synthèse vocale GuardianNav terminée avec succès."
        orchestrator.speech_agent.speak_alert("info", conclusion_message)
        
        print("\n🎉 La synthèse vocale GuardianNav est opérationnelle!")
        print("🔊 L'agent peut maintenant parler en plus d'afficher du texte")
        print("🌐 Google Text-to-Speech intégré pour une qualité optimale")
        print("🎭 Mode simulation disponible si API non configuré")
        print("\n📝 Fonctionnalités ajoutées:")
        print("   • Synthèse vocale pour toutes les alertes")
        print("   • Messages d'urgence avec priorité")  
        print("   • Instructions vocales spécialisées")
        print("   • Alertes de chute personnalisées")
        print("   • Confirmations et feedbacks vocaux")
        
    except Exception as e:
        print(f"\n❌ Erreur lors de la démonstration: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Fonction principale"""
    try:
        demo_speech_integration()
    except KeyboardInterrupt:
        print("\n\n⏹️ Démonstration interrompue par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}")

if __name__ == "__main__":
    main()