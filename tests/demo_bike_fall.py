#!/usr/bin/env python3
"""
Test de démonstration d'une chute à vélo avec GuardianNav complet
"""

import sys
import os

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from guardian.guardian_agent import GuardianOrchestrator
from guardian.config import Config
import time
import threading

def simulate_bike_fall():
    """Simule une chute à vélo réaliste"""
    
    print("🚴 DÉMONSTRATION: Chute à vélo avec GuardianNav")
    print("="*60)
    
    # Charger la configuration
    config_loader = Config()
    config = config_loader.load()
    
    # Initialiser l'orchestrateur
    orchestrator = GuardianOrchestrator(config)
    
    print("🛡️ GuardianNav initialisé et en surveillance")
    print("📍 Simulation: Vous êtes à vélo dans Paris")
    print()
    
    # Laisser le système s'initialiser
    time.sleep(2)
    
    # Simuler une chute après quelques secondes
    def trigger_fall():
        time.sleep(5)
        print("\n" + "="*60)
        print("💥 SIMULATION DE CHUTE À VÉLO")
        print("="*60)
        
        # Déclencher une chute via le détecteur
        fall_info = orchestrator.fall_detector.simulate_fall("chute_velo")
        orchestrator.handle_fall_detection(fall_info)
    
    # Démarrer la simulation de chute en arrière-plan
    fall_thread = threading.Thread(target=trigger_fall, daemon=True)
    fall_thread.start()
    
    print("⏳ Démarrage de la surveillance... (chute simulée dans 5 secondes)")
    print("📱 Vous pourrez répondre 'oui' ou 'non' quand Guardian vous demandera")
    print("⏹️  Appuyez sur Ctrl+C pour arrêter")
    print()
    
    try:
        # Démarrer juste la surveillance des entrées pour la démonstration
        orchestrator._start_input_monitor()
        
        # Garder le programme actif
        while not orchestrator.shutdown_event.is_set():
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Arrêt de la démonstration")
        orchestrator.shutdown()
    
    print("👋 Démonstration terminée")

if __name__ == "__main__":
    simulate_bike_fall()