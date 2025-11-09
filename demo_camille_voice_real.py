#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Démonstration Guardian avec Camille
Fichier de test pour la démonstration du système Guardian
avec reconnaissance vocale et interface web

Usage:
python demo_camille_voice_real.py
"""

import os
import sys
import time
import json
import logging
import subprocess
from pathlib import Path

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('guardian_demo.log')
    ]
)
logger = logging.getLogger(__name__)

def banner():
    """Affiche le banner de démonstration"""
    print("\n" + "="*60)
    print("🛡️  GUARDIAN DÉMONSTRATION - CAMILLE")
    print("="*60)
    print("Version: 1.2.0")
    print("Mode: Démonstration web complète")
    print("Utilisatrice test: Camille Dupont")
    print("Location: Google France - 8 rue de Londres, 75009 Paris")
    print("="*60 + "\n")

def check_prerequisites():
    """Vérifie les prérequis pour la démonstration"""
    logger.info("🔍 Vérification des prérequis...")
    
    # Vérifier Python
    python_version = sys.version_info
    if python_version.major < 3 or python_version.minor < 8:
        logger.error("❌ Python 3.8+ requis")
        return False
    
    logger.info(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Vérifier les dépendances
    required_packages = [
        'flask',
        'flask-socketio',
        'vosk',
        'sounddevice',
        'numpy',
        'pyyaml',
        'google-generativeai',
        'requests'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            logger.info(f"✅ {package}")
        except ImportError:
            logger.warning(f"❌ {package} manquant")
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"Packages manquants: {missing_packages}")
        logger.info("Installez avec: pip install " + " ".join(missing_packages))
        return False
    
    # Vérifier le modèle Vosk
    vosk_model_path = Path(__file__).parent / "models" / "vosk-model-small-fr-0.22"
    if not vosk_model_path.exists():
        logger.warning(f"⚠️  Modèle Vosk non trouvé: {vosk_model_path}")
        logger.info("Le modèle sera téléchargé automatiquement si nécessaire")
    else:
        logger.info("✅ Modèle Vosk français disponible")
    
    # Vérifier la configuration
    config_path = Path(__file__).parent / "config" / "api_keys.yaml"
    if not config_path.exists():
        logger.warning(f"⚠️  Configuration non trouvée: {config_path}")
        logger.info("Certaines fonctionnalités peuvent être limitées")
    else:
        logger.info("✅ Configuration Guardian disponible")
    
    return True

def setup_demo_environment():
    """Configure l'environnement de démonstration"""
    logger.info("⚙️  Configuration de l'environnement de démonstration...")
    
    # Données utilisateur de démonstration
    demo_user = {
        'firstName': 'Camille',
        'lastName': 'Dupont', 
        'fullName': 'Camille Dupont',
        'phone': '+33 6 12 34 56 78',
        'email': 'camille.dupont@example.com',
        'location': '8 rue de Londres, 75009 Paris',
        'coordinates': (48.8756, 2.3264),  # Google France
        'emergency_contacts': [
            {'name': 'Marie Dupont', 'phone': '+33 6 87 65 43 21', 'relation': 'Mère'},
            {'name': 'Pierre Dupont', 'phone': '+33 6 11 22 33 44', 'relation': 'Père'},
            {'name': 'Service Urgences', 'phone': '112', 'relation': 'Secours'}
        ]
    }
    
    # Scénarios de test prédéfinis
    demo_scenarios = [
        {
            'name': 'Urgence médicale',
            'situation': 'Je ressens une douleur intense à la poitrine et j\'ai du mal à respirer',
            'expected_urgency': 9,
            'expected_actions': ['Appeler le 15 (SAMU)', 'Rester calme', 'Ne pas se déplacer']
        },
        {
            'name': 'Problème de sécurité',
            'situation': 'Je pense qu\'on me suit depuis plusieurs rues, j\'ai peur',
            'expected_urgency': 7,
            'expected_actions': ['Se diriger vers un lieu public', 'Appeler le 17 si nécessaire']
        },
        {
            'name': 'Orientation',
            'situation': 'Je suis perdue dans le quartier, je ne trouve pas mon chemin',
            'expected_urgency': 4,
            'expected_actions': ['Utiliser le GPS', 'Demander de l\'aide dans un commerce']
        },
        {
            'name': 'Stress',
            'situation': 'Je me sens très anxieuse et j\'ai une crise d\'angoisse',
            'expected_urgency': 5,
            'expected_actions': ['Respirer calmement', 'Trouver un endroit calme']
        }
    ]
    
    return demo_user, demo_scenarios

def test_web_interface():
    """Lance l'interface web de démonstration"""
    logger.info("🌐 Lancement de l'interface web Guardian...")
    
    web_dir = Path(__file__).parent / "web"
    web_script = web_dir / "web_interface_simple.py"
    
    if not web_script.exists():
        logger.error(f"❌ Interface web non trouvée: {web_script}")
        return False
    
    try:
        # Lancer l'interface web en arrière-plan
        logger.info("🚀 Démarrage du serveur web...")
        
        # Change to web directory
        original_dir = os.getcwd()
        os.chdir(web_dir)
        
        # Start web server
        process = subprocess.Popen(
            [sys.executable, "web_interface_simple.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Attendre un peu pour que le serveur démarre
        time.sleep(3)
        
        # Vérifier si le processus est encore en vie
        if process.poll() is None:
            logger.info("✅ Serveur web démarré avec succès")
            logger.info("🌐 Interface disponible sur: http://localhost:5001")
            logger.info("📱 Interface conversation: http://localhost:5001/conversation")
            logger.info("🎤 Interface test vocal: http://localhost:5001/voice-test")
            logger.info("🗺️  Interface carte: http://localhost:5001/map")
            logger.info("🚨 Interface urgence: http://localhost:5001/emergency")
            
            return True, process
        else:
            stdout, stderr = process.communicate()
            logger.error("❌ Échec du démarrage du serveur")
            logger.error(f"STDOUT: {stdout}")
            logger.error(f"STDERR: {stderr}")
            return False, None
            
    except Exception as e:
        logger.error(f"❌ Erreur lors du lancement: {e}")
        return False, None
    finally:
        os.chdir(original_dir)

def run_demo_tests():
    """Exécute les tests de démonstration"""
    logger.info("🧪 Exécution des tests de démonstration...")
    
    demo_user, demo_scenarios = setup_demo_environment()
    
    print(f"\n👤 Utilisatrice de démonstration:")
    print(f"   Nom: {demo_user['fullName']}")
    print(f"   Téléphone: {demo_user['phone']}")
    print(f"   Localisation: {demo_user['location']}")
    
    print(f"\n📋 Scénarios de test disponibles:")
    for i, scenario in enumerate(demo_scenarios, 1):
        print(f"   {i}. {scenario['name']}")
        print(f"      Situation: {scenario['situation']}")
        print(f"      Urgence attendue: {scenario['expected_urgency']}/10")
        print()
    
    return True

def interactive_demo():
    """Mode démonstration interactive"""
    logger.info("🎮 Mode démonstration interactive")
    
    print("\n" + "="*60)
    print("🎮 MODE DÉMONSTRATION INTERACTIVE")
    print("="*60)
    print("1. Interface web complète")
    print("2. Tests de scénarios prédéfinis")
    print("3. Test reconnaissance vocale")
    print("4. Test système complet")
    print("0. Quitter")
    print("="*60)
    
    while True:
        try:
            choice = input("\n👆 Votre choix (0-4): ").strip()
            
            if choice == "0":
                print("🔒 Fin de la démonstration Guardian")
                break
            elif choice == "1":
                success, process = test_web_interface()
                if success:
                    input("\n⏳ Appuyez sur Entrée pour arrêter le serveur web...")
                    if process:
                        process.terminate()
                        process.wait()
                        logger.info("🛑 Serveur web arrêté")
            elif choice == "2":
                run_demo_tests()
            elif choice == "3":
                logger.info("🎤 Test de reconnaissance vocale - À implémenter")
                print("⚠️  Test vocal à implémenter dans l'interface web")
            elif choice == "4":
                logger.info("🔍 Test système complet")
                if check_prerequisites():
                    run_demo_tests()
                    test_web_interface()
            else:
                print("❌ Choix invalide, veuillez réessayer")
                
        except KeyboardInterrupt:
            print("\n🔒 Interruption utilisateur - Fin de la démonstration")
            break
        except Exception as e:
            logger.error(f"❌ Erreur dans le mode interactif: {e}")
            print("❌ Une erreur est survenue, veuillez réessayer")

def main():
    """Fonction principale de démonstration"""
    banner()
    
    logger.info("🚀 Démarrage de la démonstration Guardian")
    
    # Vérifier les prérequis
    if not check_prerequisites():
        logger.error("❌ Prérequis non satisfaits")
        return 1
    
    try:
        # Mode démonstration
        if len(sys.argv) > 1 and sys.argv[1] == "--auto":
            # Mode automatique
            logger.info("🤖 Mode automatique")
            run_demo_tests()
            success, process = test_web_interface()
            if success:
                logger.info("✅ Démonstration terminée avec succès")
                if process:
                    process.terminate()
        else:
            # Mode interactif
            interactive_demo()
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("🔒 Démonstration interrompue par l'utilisateur")
        return 0
    except Exception as e:
        logger.error(f"❌ Erreur lors de la démonstration: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)