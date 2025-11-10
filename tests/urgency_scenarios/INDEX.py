"""
Script de visualisation de la structure du dossier de tests
"""

def print_structure():
    structure = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║          🧪 GUARDIAN - SUITE DE TESTS DE CALIBRATION DES URGENCES          ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

📂 tests/urgency_scenarios/
│
├── 📄 __init__.py                        # Package Python (imports)
│
├── 📊 scenarios_data.py                  # ⭐ BASE DE DONNÉES
│   └── 38 scénarios réels catégorisés
│       • 10 Faible (1-3)     → Pas d'email
│       • 10 Modérée (4-5)    → Pas d'email
│       • 8 Élevée (6-7)      → Email envoyé
│       • 10 Critique (8-10)  → Email + SMS + Alertes
│
├── 🧪 test_urgency_calibration.py        # ⭐ TESTS AUTOMATISÉS
│   ├── Lance tous les tests
│   ├── Génère des rapports détaillés
│   ├── Export JSON des résultats
│   └── Usage:
│       python3 test_urgency_calibration.py [OPTIONS]
│         --category <cat>    Tester une catégorie
│         --max-tests <n>     Limiter le nombre
│         --delay <s>         Délai entre tests
│         --export            Exporter en JSON
│
├── 🎮 interactive_trainer.py             # ⭐ MODE INTERACTIF
│   ├── Entraîneur interactif
│   ├── Tests rapides prédéfinis
│   ├── Analyse de situations custom
│   └── Usage:
│       python3 interactive_trainer.py
│       python3 interactive_trainer.py --quick
│       python3 interactive_trainer.py --test "situation"
│
├── 📊 demo_scenarios.py                  # ⭐ DÉMONSTRATION
│   ├── Affiche tous les scénarios
│   ├── Statistiques détaillées
│   ├── Exemples par niveau
│   └── Usage:
│       python3 demo_scenarios.py --stats
│       python3 demo_scenarios.py --examples
│       python3 demo_scenarios.py --all
│
├── 📖 README.md                          # Documentation complète
│   ├── Architecture détaillée
│   ├── Guide d'utilisation
│   ├── Interprétation des résultats
│   └── Bonnes pratiques
│
├── 🚀 QUICKSTART.md                      # Démarrage rapide
│   ├── Commandes essentielles
│   ├── Exemples d'utilisation
│   └── Résolution de problèmes
│
└── 📋 INDEX.py                           # Ce fichier (visualisation)

═══════════════════════════════════════════════════════════════════════════════

🎯 WORKFLOW RECOMMANDÉ

1️⃣  Découverte
    python3 demo_scenarios.py --stats
    → Voir les 38 scénarios et leur distribution

2️⃣  Tests rapides
    python3 interactive_trainer.py --quick
    → Tester 5 scénarios clés en quelques secondes

3️⃣  Tests par catégorie
    python3 test_urgency_calibration.py --category faible --export
    → Valider une catégorie spécifique

4️⃣  Tests complets
    python3 test_urgency_calibration.py --delay 2.0 --export
    → Test complet avec rapport détaillé

5️⃣  Tests custom
    python3 interactive_trainer.py
    → Mode interactif pour vos propres situations

═══════════════════════════════════════════════════════════════════════════════

📊 RÉSULTATS ATTENDUS

✅ Taux de réussite cible : >90%
   • Niveau exact : ~70%
   • Dans tolérance (±1) : ~25%
   • Incorrect : <5%

🎯 Critères de validation :
   • Crevaison vélo → Niveau 2 (Faible) → Pas d'email ✓
   • Chute avec douleur → Niveau 6 (Élevée) → Email envoyé ✓
   • Détresse respiratoire → Niveau 10 (Critique) → Alerte complète ✓

═══════════════════════════════════════════════════════════════════════════════

💡 AIDE RAPIDE

Voir ce message :
    python3 INDEX.py

Statistiques :
    python3 demo_scenarios.py --stats

Tests rapides :
    python3 interactive_trainer.py --quick

Documentation :
    cat README.md
    cat QUICKSTART.md

═══════════════════════════════════════════════════════════════════════════════
"""
    print(structure)


if __name__ == "__main__":
    print_structure()
