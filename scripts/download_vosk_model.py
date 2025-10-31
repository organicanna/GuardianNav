#!/usr/bin/env python3
"""
🎤 Téléchargeur Automatique du Modèle Vosk Français
Télécharge et installe automatiquement le modèle Vosk français pour Guardian
"""

import os
import sys
import requests
import zipfile
from pathlib import Path
import shutil

# Configuration
VOSK_MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-small-fr-0.22.zip"
MODEL_NAME = "vosk-model-small-fr-0.22"
MODELS_DIR = Path("models")
DOWNLOAD_DIR = Path("temp_downloads")

def create_directories():
    """Créer les dossiers nécessaires"""
    MODELS_DIR.mkdir(exist_ok=True)
    DOWNLOAD_DIR.mkdir(exist_ok=True)
    print(f"📁 Dossiers créés: {MODELS_DIR}, {DOWNLOAD_DIR}")

def check_existing_model():
    """Vérifier si le modèle existe déjà"""
    model_path = MODELS_DIR / MODEL_NAME
    if model_path.exists() and model_path.is_dir():
        # Vérifier que le modèle est complet
        required_files = ["am", "conf", "graph", "ivector"]
        if all((model_path / f).exists() for f in required_files):
            print(f"✅ Modèle Vosk déjà installé : {model_path}")
            return True
    return False

def download_model():
    """Télécharger le modèle Vosk"""
    zip_path = DOWNLOAD_DIR / f"{MODEL_NAME}.zip"
    
    print(f"📥 Téléchargement du modèle Vosk français...")
    print(f"🔗 URL: {VOSK_MODEL_URL}")
    print(f"📍 Destination: {zip_path}")
    
    try:
        response = requests.get(VOSK_MODEL_URL, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        progress = (downloaded / total_size) * 100
                        print(f"\r📊 Progression: {progress:.1f}% ({downloaded//1024//1024}MB/{total_size//1024//1024}MB)", end='')
        
        print(f"\n✅ Téléchargement terminé: {zip_path}")
        return zip_path
        
    except Exception as e:
        print(f"❌ Erreur de téléchargement: {e}")
        return None

def extract_model(zip_path):
    """Extraire le modèle Vosk"""
    print(f"📦 Extraction du modèle...")
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(DOWNLOAD_DIR)
        
        # Déplacer vers le dossier models/
        extracted_path = DOWNLOAD_DIR / MODEL_NAME
        target_path = MODELS_DIR / MODEL_NAME
        
        if target_path.exists():
            shutil.rmtree(target_path)
        
        shutil.move(str(extracted_path), str(target_path))
        print(f"✅ Modèle installé: {target_path}")
        
        return target_path
        
    except Exception as e:
        print(f"❌ Erreur d'extraction: {e}")
        return None

def validate_model(model_path):
    """Valider l'installation du modèle"""
    required_files = [
        "am/final.mdl",
        "conf/mfcc.conf", 
        "conf/model.conf",
        "graph/HCLr.fst",
        "graph/Gr.fst",
        "ivector/final.ie"
    ]
    
    print(f"🔍 Validation du modèle...")
    
    for file_path in required_files:
        full_path = model_path / file_path
        if not full_path.exists():
            print(f"❌ Fichier manquant: {file_path}")
            return False
        print(f"✅ {file_path}")
    
    print(f"🎉 Modèle Vosk validé avec succès!")
    return True

def cleanup():
    """Nettoyer les fichiers temporaires"""
    if DOWNLOAD_DIR.exists():
        shutil.rmtree(DOWNLOAD_DIR)
        print(f"🧹 Nettoyage terminé: {DOWNLOAD_DIR} supprimé")

def test_vosk_integration():
    """Tester l'intégration Vosk"""
    print(f"🧪 Test d'intégration Vosk...")
    
    try:
        import vosk
        model_path = MODELS_DIR / MODEL_NAME
        model = vosk.Model(str(model_path))
        rec = vosk.KaldiRecognizer(model, 16000)
        print(f"✅ Vosk fonctionne correctement!")
        return True
        
    except ImportError:
        print(f"⚠️ Module vosk non installé. Installer avec: pip install vosk")
        return False
    except Exception as e:
        print(f"❌ Erreur Vosk: {e}")
        return False

def main():
    """Fonction principale"""
    print("🎤 === INSTALLATION MODÈLE VOSK FRANÇAIS ===")
    print("Guardian - Assistant de Sécurité Personnelle")
    print("=" * 50)
    
    try:
        # 1. Créer les dossiers
        create_directories()
        
        # 2. Vérifier si déjà installé
        if check_existing_model():
            choice = input("Réinstaller le modèle ? (y/N): ").lower()
            if choice not in ['y', 'yes', 'oui']:
                print("✅ Installation annulée - Modèle déjà présent")
                return test_vosk_integration()
        
        # 3. Télécharger
        zip_path = download_model()
        if not zip_path:
            return False
        
        # 4. Extraire
        model_path = extract_model(zip_path)
        if not model_path:
            return False
        
        # 5. Valider
        if not validate_model(model_path):
            return False
        
        # 6. Nettoyer
        cleanup()
        
        # 7. Test final
        success = test_vosk_integration()
        
        if success:
            print("\n🎉 === INSTALLATION RÉUSSIE ===")
            print(f"📍 Modèle installé: {model_path}")
            print(f"🚀 Guardian est prêt à utiliser la reconnaissance vocale!")
        
        return success
        
    except KeyboardInterrupt:
        print(f"\n⚠️ Installation interrompue par l'utilisateur")
        cleanup()
        return False
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        cleanup()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)