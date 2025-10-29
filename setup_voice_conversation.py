#!/usr/bin/env python3
"""
INSTALLATION AUTOMATIQUE - GuardianNav Conversation Vocale
🚀 Installe toutes les dépendances et télécharge le modèle Vosk français
"""

import os
import sys
import subprocess
import urllib.request
import zipfile
from pathlib import Path

def run_command(command, description):
    """Exécute une commande avec gestion d'erreur"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Réussi")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Erreur:")
        print(f"   {e.stderr}")
        return False

def install_python_dependencies():
    """Installe les dépendances Python"""
    print("📦 **INSTALLATION DES DÉPENDANCES PYTHON**")
    print("-" * 50)
    
    # Vérifier pip
    if not run_command("pip --version", "Vérification de pip"):
        print("❌ pip n'est pas disponible")
        return False
        
    # Installer les dépendances vocales
    success = run_command(
        "pip install -r requirements_voice.txt",
        "Installation des dépendances vocales"
    )
    
    if success:
        print("✅ Toutes les dépendances Python sont installées")
    else:
        print("⚠️ Certaines dépendances ont échoué - La démo fonctionnera en mode dégradé")
        
    return success

def download_vosk_model():
    """Télécharge le modèle Vosk français"""
    print("\n🎤 **TÉLÉCHARGEMENT DU MODÈLE VOSK FRANÇAIS**")
    print("-" * 50)
    
    model_name = "vosk-model-small-fr-0.22"
    model_zip = f"{model_name}.zip"
    model_url = f"https://alphacephei.com/vosk/models/{model_zip}"
    
    # Vérifier si le modèle existe déjà
    if os.path.exists(model_name):
        print(f"✅ Modèle {model_name} déjà présent")
        return True
        
    print(f"📥 Téléchargement depuis: {model_url}")
    print("⏳ Cela peut prendre quelques minutes (≈ 40 MB)...")
    
    try:
        # Télécharger le fichier
        urllib.request.urlretrieve(model_url, model_zip)
        print(f"✅ Téléchargement de {model_zip} terminé")
        
        # Décompresser
        print("📂 Décompression du modèle...")
        with zipfile.ZipFile(model_zip, 'r') as zip_ref:
            zip_ref.extractall()
            
        # Nettoyer le fichier zip
        os.remove(model_zip)
        print(f"✅ Modèle {model_name} installé et prêt")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du téléchargement: {e}")
        print("💡 Vous pouvez télécharger manuellement depuis:")
        print(f"   {model_url}")
        return False

def verify_installation():
    """Vérifie que l'installation est complète"""
    print("\n🔍 **VÉRIFICATION DE L'INSTALLATION**")
    print("-" * 50)
    
    # Vérifier les modules Python
    modules_to_check = [
        ('sounddevice', 'Capture audio'),
        ('vosk', 'Reconnaissance vocale'),
        ('pygame', 'Lecture audio'),
        ('yaml', 'Configuration'),
        ('google.cloud.texttospeech', 'Google TTS'),
    ]
    
    python_ok = True
    for module, description in modules_to_check:
        try:
            if '.' in module:
                # Import avec sous-modules
                parts = module.split('.')
                imported = __import__(parts[0])
                for part in parts[1:]:
                    imported = getattr(imported, part)
            else:
                __import__(module)
            print(f"✅ {module}: {description}")
        except ImportError:
            print(f"❌ {module}: {description}")
            python_ok = False
            
    # Vérifier le modèle Vosk
    model_ok = os.path.exists("vosk-model-small-fr-0.22")
    if model_ok:
        print("✅ vosk-model-small-fr-0.22: Modèle de reconnaissance français")
    else:
        print("❌ vosk-model-small-fr-0.22: Modèle de reconnaissance français")
        
    print()
    if python_ok and model_ok:
        print("🎉 **INSTALLATION COMPLÈTE ET FONCTIONNELLE**")
        print("✅ GuardianNav Conversation Vocale est prêt à l'emploi !")
        return True
    else:
        print("⚠️ **INSTALLATION PARTIELLE**")
        if not python_ok:
            print("❌ Certaines dépendances Python manquent")
        if not model_ok:
            print("❌ Le modèle de reconnaissance vocale manque")
        print("💡 La démo fonctionnera en mode dégradé")
        return False

def show_next_steps(installation_complete):
    """Affiche les prochaines étapes"""
    print("\n🚀 **PROCHAINES ÉTAPES**")
    print("=" * 50)
    
    if installation_complete:
        print("🎯 **CONFIGURATION DES APIS (OPTIONNEL):**")
        print("   1. Copiez api_keys_template.yaml vers api_keys.yaml")
        print("   2. Remplissez vos clés Google Cloud (Vertex AI, TTS)")
        print("   3. Activez les APIs dans Google Cloud Console")
        print()
        
    print("🎙️ **LANCER LA CONVERSATION VOCALE:**")
    print("   python demo_voice_conversation.py")
    print()
    
    print("🔧 **TESTS INDIVIDUELS:**")
    print("   python -m guardian.voice_conversation_agent")
    print("   python tests/test_speech_agent.py")
    print()
    
    if not installation_complete:
        print("⚠️ **EN CAS DE PROBLÈME:**")
        print("   • Vérifiez votre connexion internet")
        print("   • Réinstallez avec: pip install --upgrade -r requirements_voice.txt")
        print("   • Téléchargez manuellement le modèle Vosk si nécessaire")
        print()

def main():
    """Installation automatique complète"""
    print("🛠️ INSTALLATION GUARDIANNAV CONVERSATION VOCALE")
    print("=" * 60)
    print("🎙️ Installation des dépendances et du modèle français")
    print("=" * 60)
    print()
    
    # Vérifications préalables
    print(f"🐍 Python version: {sys.version}")
    print(f"📂 Répertoire de travail: {os.getcwd()}")
    print()
    
    # Demander confirmation
    response = input("🚀 Continuer l'installation automatique ? (Entrée pour oui, 'n' pour non): ")
    if response.lower().strip() in ['n', 'non', 'no']:
        print("❌ Installation annulée")
        return
        
    print()
    
    # Étapes d'installation
    steps_completed = 0
    
    # 1. Dépendances Python
    if install_python_dependencies():
        steps_completed += 1
        
    # 2. Modèle Vosk
    if download_vosk_model():
        steps_completed += 1
        
    # 3. Vérification
    installation_complete = verify_installation()
    
    # Résumé final
    print("\n" + "=" * 60)
    print("📊 **RÉSUMÉ DE L'INSTALLATION**")
    print(f"✅ Étapes réussies: {steps_completed}/2")
    
    if installation_complete:
        print("🎉 Installation complète et fonctionnelle !")
    else:
        print("⚠️ Installation partielle - Mode dégradé disponible")
        
    # Prochaines étapes
    show_next_steps(installation_complete)
    
    print("🙏 **Merci d'avoir installé GuardianNav Conversation Vocale !**")

if __name__ == "__main__":
    main()