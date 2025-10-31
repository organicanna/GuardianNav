#!/usr/bin/env python3
"""
Guardian - Assistant de Sécurité Personnelle
Point d'entrée principal - Lance l'interface web
"""

import os
import sys

def main():
    """Point d'entrée principal"""
    print("🛡️  GUARDIAN - Assistant de Sécurité Personnelle")
    print("="*50)
    print("🌐 Lancement de l'interface web...")
    
    # Changer vers le dossier web et lancer le serveur
    web_dir = os.path.join(os.path.dirname(__file__), 'web')
    os.chdir(web_dir)
    
    # Lancer le serveur web directement
    import subprocess
    web_script = os.path.join(web_dir, 'start_web_server.py')
    subprocess.run([sys.executable, web_script])

if __name__ == "__main__":
    main()