#!/usr/bin/env python3
"""
Script d'installation automatique des modèles Guardian
Télécharge et configure le modèle Vosk français pour la reconnaissance vocale
"""

import os
import urllib.request
import zipfile
import sys
from pathlib import Path

def download_file(url, filename):
    """Télécharge un fichier avec barre de progression"""
    def progress_hook(block_num, block_size, total_size):
        downloaded = block_num * block_size
        if total_size > 0:
            percent = min(100, (downloaded * 100) // total_size)
            bar_length = 50
            filled_length = (percent * bar_length) // 100
            bar = '█' * filled_length + '-' * (bar_length - filled_length)
            print(f'\r[{bar}] {percent}% ({downloaded // 1024 // 1024}MB/{total_size // 1024 // 1024}MB)', end='')
    
    print(f"🔄 Téléchargement de {filename}...")
    urllib.request.urlretrieve(url, filename, progress_hook)
    print("\n✅ Téléchargement terminé!")

def setup_vosk_french_model():
    """Configure le modèle Vosk français pour Guardian"""
    
    print("🎤 Configuration du modèle Vosk français pour Guardian")
    print("=" * 60)
    
    # Créer le dossier models
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)
    
    model_name = "vosk-model-small-fr-0.22"
    model_zip = f"{model_name}.zip"
    model_path = models_dir / model_name
    
    # Vérifier si le modèle existe déjà
    if model_path.exists() and (model_path / "README").exists():
        print(f"✅ Modèle {model_name} déjà installé!")
        return True
    
    try:
        # URL du modèle Vosk français
        model_url = "https://alphacephei.com/vosk/models/vosk-model-small-fr-0.22.zip"
        
        # Télécharger le modèle
        zip_path = models_dir / model_zip
        download_file(model_url, str(zip_path))
        
        # Extraire le modèle
        print("📂 Extraction du modèle...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(models_dir)
        
        # Nettoyer le fichier zip
        zip_path.unlink()
        
        # Vérifier l'installation
        if model_path.exists() and (model_path / "README").exists():
            print("✅ Modèle Vosk français installé avec succès!")
            print(f"📍 Emplacement: {model_path}")
            
            # Afficher la taille
            size_mb = sum(f.stat().st_size for f in model_path.rglob('*') if f.is_file()) // 1024 // 1024
            print(f"📊 Taille: {size_mb}MB")
            
            return True
        else:
            print("❌ Erreur lors de l'extraction du modèle")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du téléchargement: {e}")
        return False

def test_vosk_installation():
    """Test l'installation du modèle Vosk"""
    print("\n🧪 Test de l'installation...")
    
    try:
        # Tester l'import Vosk
        import vosk
        print("✅ Librairie Vosk importée")
        
        # Tester le chargement du modèle
        model_path = "models/vosk-model-small-fr-0.22"
        if os.path.exists(model_path):
            model = vosk.Model(model_path)
            print("✅ Modèle Vosk chargé avec succès")
            return True
        else:
            print("❌ Modèle non trouvé")
            return False
            
    except ImportError:
        print("❌ Vosk n'est pas installé. Exécutez: pip install vosk")
        return False
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

def main():
    """Installation principale"""
    print("🛡️  GUARDIAN - Installation des Modèles")
    print("🎯 Reconnaissance vocale française offline")
    print("=" * 60)
    
    # Installation du modèle Vosk
    if setup_vosk_french_model():
        # Test de l'installation
        if test_vosk_installation():
            print("\n🎉 INSTALLATION RÉUSSIE!")
            print("\n📋 Prochaines étapes:")
            print("1. cd web")
            print("2. python3 web_interface_simple.py")
            print("3. Ouvrir http://localhost:5001")
            print("\n🎤 Guardian est prêt pour la reconnaissance vocale française!")
        else:
            print("\n⚠️  Modèle installé mais test échoué")
            print("Vérifiez que Vosk est installé: pip install vosk")
    else:
        print("\n❌ Échec de l'installation")
        print("Vérifiez votre connexion internet et réessayez")
        sys.exit(1)

if __name__ == "__main__":
    main()