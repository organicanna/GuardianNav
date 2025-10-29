#!/usr/bin/env python3
"""
Test de la conversation vocale GuardianNav
Vérifie le bon fonctionnement de toutes les composantes
"""

import sys
import os
import time
from pathlib import Path

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_voice_conversation_components():
    """Test des composants de conversation vocale"""
    print("🧪 **TEST DES COMPOSANTS DE CONVERSATION VOCALE**")
    print("=" * 60)
    
    results = {}
    
    # Test 1: Imports des modules
    print("\n1️⃣ **Test des imports**")
    try:
        from guardian.voice_conversation_agent import VoiceConversationAgent
        print("✅ VoiceConversationAgent importé")
        results['voice_agent_import'] = True
    except ImportError as e:
        print(f"❌ Erreur import VoiceConversationAgent: {e}")
        results['voice_agent_import'] = False
        
    # Test 2: Dépendances vocales
    print("\n2️⃣ **Test des dépendances vocales**")
    dependencies = [
        ('sounddevice', 'Capture audio'),
        ('vosk', 'Reconnaissance vocale'),
        ('pygame', 'Lecture audio'),
        ('yaml', 'Configuration')
    ]
    
    for module, desc in dependencies:
        try:
            __import__(module)
            print(f"✅ {module}: {desc}")
            results[f'dep_{module}'] = True
        except ImportError:
            print(f"❌ {module}: {desc}")
            results[f'dep_{module}'] = False
            
    # Test 3: APIs Google Cloud (optionnel)
    print("\n3️⃣ **Test des APIs Google Cloud**")
    google_apis = [
        ('google.cloud.texttospeech', 'Text-to-Speech'),
        ('google.cloud.speech', 'Speech-to-Text'),
        ('google.cloud.aiplatform', 'Vertex AI')
    ]
    
    for api, desc in google_apis:
        try:
            parts = api.split('.')
            module = __import__(parts[0])
            for part in parts[1:]:
                module = getattr(module, part)
            print(f"✅ {api}: {desc}")
            results[f'api_{api}'] = True
        except (ImportError, AttributeError):
            print(f"⚠️ {api}: {desc} (optionnel)")
            results[f'api_{api}'] = False
            
    # Test 4: Modèle Vosk
    print("\n4️⃣ **Test du modèle Vosk**")
    vosk_paths = [
        "vosk-model-small-fr-0.22",
        "../vosk-model-small-fr-0.22"
    ]
    
    vosk_found = False
    for path in vosk_paths:
        if os.path.exists(path):
            print(f"✅ Modèle Vosk trouvé: {path}")
            results['vosk_model'] = path
            vosk_found = True
            break
            
    if not vosk_found:
        print("❌ Modèle Vosk non trouvé")
        print("💡 Téléchargez avec: python setup_voice_conversation.py")
        results['vosk_model'] = False
        
    # Test 5: Configuration API
    print("\n5️⃣ **Test de la configuration**")
    try:
        import yaml
        with open('api_keys.yaml', 'r') as f:
            config = yaml.safe_load(f)
        print("✅ Fichier api_keys.yaml trouvé")
        
        google_config = config.get('google_cloud', {})
        if google_config.get('vertex_ai', {}).get('api_key'):
            print("✅ Clé Vertex AI configurée")
        else:
            print("⚠️ Clé Vertex AI non configurée (mode simulation)")
            
        results['config'] = True
    except FileNotFoundError:
        print("⚠️ Fichier api_keys.yaml non trouvé (mode simulation)")
        results['config'] = False
    except Exception as e:
        print(f"❌ Erreur configuration: {e}")
        results['config'] = False
        
    return results

def test_voice_agent_initialization():
    """Test d'initialisation de l'agent vocal"""
    print("\n🚀 **TEST D'INITIALISATION DE L'AGENT VOCAL**")
    print("-" * 50)
    
    try:
        from guardian.voice_conversation_agent import VoiceConversationAgent
        
        # Configuration de test
        import yaml
        try:
            with open('api_keys.yaml', 'r') as f:
                config = yaml.safe_load(f)
        except:
            config = {}
            
        # Initialiser l'agent
        print("🔧 Initialisation de VoiceConversationAgent...")
        agent = VoiceConversationAgent(
            api_keys_config=config,
            vosk_model_path="vosk-model-small-fr-0.22" if os.path.exists("vosk-model-small-fr-0.22") else None
        )
        
        # Vérifier le statut
        status = agent.get_status_info()
        print("📊 Statut de l'agent:")
        print(f"   🔊 Synthèse vocale: {'✅' if status['speech_available'] else '❌'}")
        print(f"   🎤 Reconnaissance: {status['recognition_engine']}")
        print(f"   🧠 Vertex AI: {'✅' if status['vertex_ai_available'] else '❌'}")
        
        print("✅ Agent vocal initialisé avec succès")
        return True
        
    except Exception as e:
        print(f"❌ Erreur d'initialisation: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_installation_guide():
    """Affiche le guide d'installation"""
    print("\n📚 **GUIDE D'INSTALLATION RAPIDE**")
    print("=" * 50)
    
    print("🔧 **Installation automatique:**")
    print("   python setup_voice_conversation.py")
    print()
    
    print("🔧 **Installation manuelle:**")
    print("   1. pip install -r requirements_voice.txt")
    print("   2. Télécharger le modèle Vosk français:")
    print("      https://alphacephei.com/vosk/models/vosk-model-small-fr-0.22.zip")
    print("   3. Décompresser dans le dossier du projet")
    print()
    
    print("🔑 **Configuration APIs (optionnel):**")
    print("   1. Copier api_keys_template.yaml vers api_keys.yaml")
    print("   2. Renseigner les clés Google Cloud")
    print()
    
    print("🚀 **Lancer la démo:**")
    print("   python demo_voice_conversation.py")

def main():
    """Test principal"""
    print("🧪 TESTS GUARDIANNAV CONVERSATION VOCALE")
    print("=" * 60)
    
    # Tests des composants
    results = test_voice_conversation_components()
    
    # Test d'initialisation si possible
    if results.get('voice_agent_import', False):
        agent_ok = test_voice_agent_initialization()
    else:
        agent_ok = False
        
    # Résumé des tests
    print("\n📊 **RÉSUMÉ DES TESTS**")
    print("=" * 40)
    
    total_tests = len([k for k in results.keys() if not k.startswith('api_')])
    passed_tests = len([v for k, v in results.items() if v and not k.startswith('api_')])
    
    print(f"✅ Tests réussis: {passed_tests}/{total_tests}")
    
    if agent_ok:
        print("🎉 Agent de conversation vocal fonctionnel !")
        print("🚀 Prêt pour la démo: python demo_voice_conversation.py")
    else:
        print("⚠️ Installation incomplète")
        show_installation_guide()
        
    print("\n🔚 Fin des tests")

if __name__ == "__main__":
    main()