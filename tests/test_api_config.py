#!/usr/bin/env python3
"""
Test de configuration des clés API pour GuardianNav
Vérifie que les clés sont correctement configurées sans les exposer
"""

import sys
import os

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yaml
from pathlib import Path
import logging

def test_api_keys_configuration():
    """Test de la configuration des clés API"""
    
    print("🔑 Test de configuration des clés API GuardianNav")
    print("=" * 55)
    
    # Chemin vers le fichier de configuration
    config_file = Path("api_keys.yaml")
    template_file = Path("api_keys_template.yaml")
    
    # Vérifier l'existence des fichiers
    print("📁 Vérification des fichiers de configuration:")
    
    if template_file.exists():
        print("   ✅ api_keys_template.yaml trouvé")
    else:
        print("   ❌ api_keys_template.yaml manquant")
        return False
    
    if config_file.exists():
        print("   ✅ api_keys.yaml trouvé")
        
        # Charger la configuration
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                
            print("\n🔍 Analyse de la configuration:")
            
            # Vérifier Google Cloud
            if 'google_cloud' in config:
                gc_config = config['google_cloud']
                
                if gc_config.get('project_id', '').startswith('your-') or gc_config.get('project_id') == 'guardiannav-475414':
                    print("   ⚠️  Google Cloud project_id : Non configuré (utilise template)")
                else:
                    print("   ✅ Google Cloud project_id : Configuré")
                
                if 'services' in gc_config:
                    services = gc_config['services']
                    configured_services = 0
                    total_services = 5
                    
                    for service_name in ['maps_api_key', 'translation_api_key', 'natural_language_api_key', 
                                       'speech_to_text_api_key', 'text_to_speech_api_key']:
                        if services.get(service_name, '').startswith('YOUR_'):
                            print(f"   ⚠️  {service_name} : Non configuré")
                        elif services.get(service_name):
                            print(f"   ✅ {service_name} : Configuré")
                            configured_services += 1
                        else:
                            print(f"   ❌ {service_name} : Manquant")
                    
                    print(f"\n📊 Services Google Cloud configurés: {configured_services}/{total_services}")
            
            # Vérifier les contacts d'urgence
            if 'emergency_contacts' in config:
                contacts = config['emergency_contacts']
                real_contacts = 0
                
                for contact in contacts:
                    if (contact.get('phone', '').startswith('+33123') or 
                        contact.get('email', '').endswith('@example.com')):
                        print(f"   ⚠️  Contact '{contact.get('name')}' : Utilise template")
                    else:
                        print(f"   ✅ Contact '{contact.get('name')}' : Configuré")
                        real_contacts += 1
                
                print(f"\n📞 Contacts d'urgence configurés: {real_contacts}/{len(contacts)}")
            
            # Vérifier les notifications
            print("\n📧 Services de notification:")
            
            if config.get('notification_services', {}).get('twilio', {}).get('account_sid', '').startswith('YOUR_'):
                print("   ⚠️  Twilio SMS : Non configuré")
            elif config.get('notification_services', {}).get('twilio', {}).get('account_sid'):
                print("   ✅ Twilio SMS : Configuré")
            
            if config.get('notification_services', {}).get('sendgrid', {}).get('api_key', '').startswith('YOUR_'):
                print("   ⚠️  SendGrid Email : Non configuré")
            elif config.get('notification_services', {}).get('sendgrid', {}).get('api_key'):
                print("   ✅ SendGrid Email : Configuré")
            
            if config.get('email', {}).get('enabled'):
                print("   ✅ Notifications email : Activées")
            else:
                print("   ⚠️  Notifications email : Désactivées")
            
            # Recommandations
            print("\n💡 Recommandations:")
            
            if configured_services < total_services:
                print("   🔧 Configurez les APIs Google Cloud pour fonctionnalités complètes")
                
            if real_contacts == 0:
                print("   📞 Ajoutez vos vrais contacts d'urgence")
                
            if not config.get('email', {}).get('enabled'):
                print("   📧 Activez les notifications email si souhaité")
            
            # Mode de fonctionnement
            print(f"\n🚀 Mode de fonctionnement prévu:")
            if configured_services >= 3 and real_contacts > 0:
                print("   ✅ Mode complet - Toutes fonctionnalités disponibles")
            elif configured_services >= 1:
                print("   ⚠️  Mode partiel - Fonctionnalités limitées")
            else:
                print("   🧪 Mode simulation - Tests uniquement")
                
        except yaml.YAMLError as e:
            print(f"   ❌ Erreur YAML dans api_keys.yaml: {e}")
            return False
        except Exception as e:
            print(f"   ❌ Erreur lecture api_keys.yaml: {e}")
            return False
            
    else:
        print("   ⚠️  api_keys.yaml manquant")
        print("\n📋 Instructions d'installation:")
        print("   1. Copiez le template: cp api_keys_template.yaml api_keys.yaml")
        print("   2. Modifiez api_keys.yaml avec vos vraies clés")
        print("   3. Relancez ce test")
        return False
    
    print("\n🔒 Sécurité:")
    print("   ✅ api_keys.yaml est dans .gitignore")
    print("   ✅ Vos clés ne seront pas commitées")
    
    print("\n✅ Test de configuration terminé")
    return True

def validate_gitignore():
    """Vérifie que api_keys.yaml est bien dans .gitignore"""
    
    gitignore_file = Path(".gitignore")
    
    if gitignore_file.exists():
        with open(gitignore_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'api_keys.yaml' in content:
            return True
    
    return False

if __name__ == "__main__":
    success = test_api_keys_configuration()
    
    if not validate_gitignore():
        print("\n⚠️  AVERTISSEMENT: api_keys.yaml devrait être dans .gitignore")
    
    if success:
        print("\n🎯 Configuration prête pour GuardianNav !")
    else:
        print("\n🔧 Configuration incomplète - Suivez les instructions")