#!/usr/bin/env python3
"""
🛡️  GUARDIAN - Assistant de Sécurité Personnelle
Point d'entrée principal pour lancer l'application
"""
import sys
import subprocess
import os
from pathlib import Path

def main():
    """Lancement du serveur web Guardian"""
    
    # Chemin vers le script web
    current_dir = Path(__file__).parent
    web_script = current_dir / "web" / "web_interface_simple.py"
    
    if not web_script.exists():
        print("❌ Erreur: web_interface_simple.py introuvable")
        sys.exit(1)
    
    print("🛡️  GUARDIAN - Assistant de Sécurité Personnelle")
    print("=" * 50)
    print("🌐 Lancement de l'interface web...")
    
    # Lancer le serveur web
    try:
        subprocess.run([sys.executable, str(web_script)])
    except KeyboardInterrupt:
        print("\n\n👋 Arrêt de Guardian")
        print("Merci d'avoir utilisé Guardian !")

if __name__ == "__main__":
    main()