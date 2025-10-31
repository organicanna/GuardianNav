#!/usr/bin/env python3
"""
🔧 Test des Dépendances Guardian
Vérifie que tous les modules requis sont correctement installés
"""

import sys
import importlib
import subprocess
import platform
from pathlib import Path

# Dépendances critiques
CRITICAL_MODULES = [
    ("yaml", "PyYAML"),
    ("flask", "Flask"),  
    ("vosk", "vosk"),
    ("requests", "requests"),
    ("pygame", "pygame"),
    ("sounddevice", "sounddevice"),
    ("werkzeug", "Werkzeug")
]

# Dépendances optionnelles
OPTIONAL_MODULES = [
    ("google.generativeai", "google-generativeai"),
    ("twilio", "twilio"),
    ("PIL", "Pillow"),
    ("numpy", "numpy")
]

def test_python_version():
    """Vérifier la version Python"""
    print("🐍 Test version Python...")
    
    version = sys.version_info
    min_version = (3, 9)
    
    if version >= min_version:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} (>= 3.9)")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} (< 3.9 requis)")
        return False

def test_module_import(module_name, package_name):
    """Tester l'import d'un module"""
    try:
        importlib.import_module(module_name)
        print(f"✅ {module_name}")
        return True
    except ImportError as e:
        print(f"❌ {module_name} - Manquant")
        print(f"   💡 Installer avec: pip install {package_name}")
        return False

def test_critical_modules():
    """Tester les modules critiques"""
    print("\n🔥 Test modules critiques...")
    
    all_good = True
    for module_name, package_name in CRITICAL_MODULES:
        if not test_module_import(module_name, package_name):
            all_good = False
    
    return all_good

def test_optional_modules():
    """Tester les modules optionnels"""
    print("\n⭐ Test modules optionnels...")
    
    for module_name, package_name in OPTIONAL_MODULES:
        test_module_import(module_name, package_name)

def test_vosk_model():
    """Vérifier le modèle Vosk"""
    print("\n🎤 Test modèle Vosk...")
    
    model_path = Path("models/vosk-model-small-fr-0.22")
    
    if not model_path.exists():
        print("❌ Modèle Vosk français non trouvé")
        print("   💡 Télécharger avec: python scripts/download_vosk_model.py")
        return False
    
    # Vérifier les fichiers critiques
    required_files = [
        "am/final.mdl",
        "conf/model.conf",
        "graph/HCLr.fst",
        "ivector/final.ie"
    ]
    
    for file_path in required_files:
        if not (model_path / file_path).exists():
            print(f"❌ Fichier Vosk manquant: {file_path}")
            return False
    
    print("✅ Modèle Vosk français complet")
    return True

def test_audio_system():
    """Tester le système audio"""
    print("\n🔊 Test système audio...")
    
    try:
        import sounddevice as sd
        devices = sd.query_devices()
        
        # Chercher un micro
        input_devices = [d for d in devices if d['max_input_channels'] > 0]
        
        if not input_devices:
            print("❌ Aucun microphone détecté")
            return False
        
        print(f"✅ {len(input_devices)} microphone(s) détecté(s)")
        
        # Afficher le micro par défaut
        default_input = sd.query_devices(kind='input')
        print(f"   🎤 Micro par défaut: {default_input['name']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur système audio: {e}")
        return False

def test_network_connectivity():
    """Tester la connectivité réseau"""
    print("\n🌐 Test connectivité réseau...")
    
    test_urls = [
        "https://generativelanguage.googleapis.com",
        "https://maps.googleapis.com", 
        "https://accounts.google.com"
    ]
    
    try:
        import requests
        session = requests.Session()
        session.timeout = 5
        
        for url in test_urls:
            try:
                response = session.head(url)
                if response.status_code < 400:
                    print(f"✅ {url}")
                else:
                    print(f"⚠️ {url} - Status {response.status_code}")
            except Exception as e:
                print(f"❌ {url} - {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test réseau: {e}")
        return False

def test_configuration_files():
    """Vérifier les fichiers de configuration"""
    print("\n⚙️ Test fichiers de configuration...")
    
    config_files = {
        "config/api_keys.yaml": "Configuration APIs",
        "requirements.txt": "Dépendances Python",
        "run.py": "Point d'entrée principal"
    }
    
    all_good = True
    for file_path, description in config_files.items():
        if Path(file_path).exists():
            print(f"✅ {file_path} - {description}")
        else:
            print(f"❌ {file_path} - Manquant")
            all_good = False
    
    return all_good

def test_guardian_imports():
    """Tester les imports Guardian spécifiques"""
    print("\n🛡️ Test modules Guardian...")
    
    guardian_modules = [
        "guardian.config",
        "guardian.gemini_agent", 
        "guardian.voice_agent",
        "guardian.guardian_agent"
    ]
    
    all_good = True
    for module in guardian_modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module} - {e}")
            all_good = False
    
    return all_good

def get_system_info():
    """Afficher les informations système"""
    print("\n💻 Informations système...")
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"Architecture: {platform.machine()}")
    print(f"Python: {sys.version}")
    print(f"Répertoire: {Path.cwd()}")

def main():
    """Fonction principale"""
    print("🔧 === TEST DÉPENDANCES GUARDIAN ===")
    print("Vérification complète de l'environnement")
    print("=" * 45)
    
    # Informations système
    get_system_info()
    
    # Tests
    results = {}
    results['python'] = test_python_version()
    results['critical_modules'] = test_critical_modules()  
    results['vosk_model'] = test_vosk_model()
    results['audio'] = test_audio_system()
    results['network'] = test_network_connectivity()
    results['config_files'] = test_configuration_files()
    results['guardian_modules'] = test_guardian_imports()
    
    # Tests optionnels (non bloquants)
    test_optional_modules()
    
    # Résumé
    print("\n" + "=" * 45)
    print("📊 RÉSUMÉ DES TESTS")
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅" if result else "❌"
        print(f"{status} {test_name.replace('_', ' ').title()}")
    
    print(f"\n🎯 Score: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 Environnement Guardian prêt!")
        print("🚀 Vous pouvez lancer: python3 run.py")
        return True
    else:
        print("⚠️ Certains problèmes doivent être résolus")
        print("📚 Consultez DEPLOYMENT.md pour l'aide")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)