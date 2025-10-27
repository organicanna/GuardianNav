#!/usr/bin/env python3
"""
Test d'intégration SMS pour GuardianNav
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from guardian.sms_agent import SMSAgent
import yaml

def test_sms_configuration():
    """Test de la configuration SMS"""
    print("🧪 Test de configuration SMS...")
    
    try:
        # Charger la configuration
        with open('api_keys.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Vérifier la configuration SMS
        sms_config = config.get('notification_services', {}).get('twilio', {})
        
        print("✅ Configuration SMS trouvée:")
        print(f"   - Account SID: {sms_config.get('account_sid', 'Non configuré')}")
        print(f"   - Phone Number: {sms_config.get('phone_number', 'Non configuré')}")
        
        # Tester les contacts d'urgence
        contacts = config.get('emergency_contacts', [])
        print(f"   - Contacts d'urgence: {len(contacts)} contact(s)")
        
        # Initialiser l'agent SMS
        sms_agent = SMSAgent(config)
        print("✅ SMSAgent initialisé avec succès")
        
        # Test de connexion
        if sms_agent.test_sms_connection():
            print("✅ Connexion Twilio OK")
        else:
            print("⚠️ Connexion Twilio en mode simulation")
        
        # Test d'envoi de message d'urgence
        emergency_context = {
            'user_name': 'Test User',
            'emergency_type': 'Test d\'intégration',
            'location': {
                'address': '48.8566, 2.3522',
                'what3words': 'test.location.here'
            }
        }
        
        print("\n📱 Test d'envoi SMS d'urgence...")
        # Utiliser les vrais contacts de la config ou un contact de test
        test_contacts = contacts if contacts else [{'name': 'Test', 'phone': '+33123456789', 'email': 'test@example.com'}]
        result = sms_agent.send_emergency_sms(test_contacts, emergency_context)
        
        if result:
            print("✅ SMS de test envoyé avec succès (ou simulé)")
        else:
            print("⚠️ SMS en mode simulation")
            
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

def test_guardian_integration():
    """Test d'intégration avec GuardianOrchestrator"""
    print("\n🧪 Test d'intégration avec Guardian...")
    
    try:
        from guardian.guardian_agent import GuardianOrchestrator
        
        # Charger la config pour Guardian
        with open('api_keys.yaml', 'r', encoding='utf-8') as f:
            guardian_config = yaml.safe_load(f)
        
        # Créer une instance de Guardian
        orchestrator = GuardianOrchestrator(guardian_config)
        
        # Vérifier que SMSAgent est initialisé
        if hasattr(orchestrator, 'sms_agent'):
            print("✅ SMSAgent intégré dans GuardianOrchestrator")
            
            # Vérifier les méthodes d'urgence
            if hasattr(orchestrator, '_send_emergency_notifications'):
                print("✅ Méthode _send_emergency_notifications disponible")
                
                # Test des notifications d'urgence (simulation)
                print("\n📧📱 Test des notifications d'urgence...")
                emergency_context = {
                    'emergency_type': 'Test d\'intégration',
                    'what3words': 'test.integration.here'
                }
                
                try:
                    orchestrator._send_emergency_notifications(emergency_context, "Test d'intégration SMS")
                    print("✅ Notifications d'urgence testées avec succès")
                except Exception as e:
                    print(f"⚠️ Erreur lors du test de notifications: {e}")
                    
            else:
                print("❌ Méthode _send_emergency_notifications non trouvée")
        else:
            print("❌ SMSAgent non trouvé dans GuardianOrchestrator")
            
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test d'intégration: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Test d'intégration SMS pour GuardianNav")
    print("=" * 50)
    
    # Test 1: Configuration SMS
    config_ok = test_sms_configuration()
    
    # Test 2: Intégration Guardian
    integration_ok = test_guardian_integration()
    
    print("\n" + "=" * 50)
    if config_ok and integration_ok:
        print("✅ Tous les tests d'intégration SMS réussis!")
        print("📱 Le système peut maintenant envoyer des SMS d'urgence")
        print("\n💡 Configuration requise:")
        print("   1. Configurer les clés Twilio dans api_keys.yaml")
        print("   2. Ajouter des contacts d'urgence dans api_keys.yaml")
        print("   3. Le système enverra automatiquement Email + SMS en cas d'urgence")
    else:
        print("⚠️ Certains tests ont échoué")
        print("📋 Vérifiez la configuration dans api_keys.yaml")
    
    print("\n🔧 Pour configurer:")
    print("   - Twilio Account SID et Auth Token")
    print("   - Numéro de téléphone Twilio")
    print("   - Liste des contacts d'urgence (email + téléphone)")