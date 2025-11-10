"""
Tests de calibration des urgences Guardian

Ce package contient une suite complète de tests pour calibrer et valider
l'évaluation des niveaux d'urgence par l'IA Guardian (Gemini).

Modules disponibles:
- scenarios_data: Base de données de 38+ scénarios catégorisés
- test_urgency_calibration: Suite de tests automatisée
- interactive_trainer: Entraîneur interactif pour tests rapides
- demo_scenarios: Démonstration et statistiques des scénarios

Usage rapide:
    # Voir les statistiques
    python3 demo_scenarios.py --stats
    
    # Lancer les tests
    python3 test_urgency_calibration.py
    
    # Mode interactif
    python3 interactive_trainer.py
"""

__version__ = "1.0.0"
__author__ = "Guardian AI Team"

from .scenarios_data import (
    SCENARIOS,
    get_all_scenarios,
    get_scenarios_by_level,
    get_statistics
)

__all__ = [
    'SCENARIOS',
    'get_all_scenarios', 
    'get_scenarios_by_level',
    'get_statistics'
]
