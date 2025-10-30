#!/usr/bin/env python3
"""
Lanceur pour le serveur web Guardian
Point d'entrée principal pour l'interface web
"""

import os
import sys

# Ajouter le répertoire parent au path pour pouvoir importer guardian
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Changer le répertoire de travail vers le répertoire parent
os.chdir(parent_dir)

# Lancer le serveur web
if __name__ == "__main__":
    from web.web_interface_simple import app, socketio
    
    print("🚀 Démarrage du serveur web Guardian...")
    print("🌐 Interface disponible sur: http://localhost:5001")
    print("📱 Pour arrêter: Ctrl+C")
    
    socketio.run(app, 
                debug=False, 
                host='0.0.0.0', 
                port=5001, 
                allow_unsafe_werkzeug=True)