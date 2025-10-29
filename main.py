#!/usr/bin/env python3
"""
GuardianNav - Agent de sécurité personnelle basé sur IA
Point d'entrée principal pour lancer le système de surveillance
"""

import sys
import os
import logging
from pathlib import Path

# Ajouter le répertoire du projet au PYTHONPATH
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from guardian.guardian_agent import main as guardian_main

def setup_logging():
    """Configure le système de logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('guardiannav.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def main():
    """Point d'entrée principal"""
    print("=" * 50)
    print("GuardianNav - Agent de sécurité personnelle")
    print("=" * 50)
    
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Démarrage de GuardianNav...")
        guardian_main()
    except KeyboardInterrupt:
        logger.info("Arrêt demandé par l'utilisateur")
        print("\nArrêt de GuardianNav...")
    except Exception as e:
        logger.error(f"Erreur critique: {e}")
        print(f"Erreur: {e}")
        sys.exit(1)
    finally:
        logger.info("GuardianNav arrêté")
        print("Au revoir !")

if __name__ == "__main__":
    main()