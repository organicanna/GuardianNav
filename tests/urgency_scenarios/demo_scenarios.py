"""
Démonstration rapide de la calibration - Mode simulation
Ne nécessite pas d'appel API
"""

import sys
from pathlib import Path

# Ajouter le répertoire parent au path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tests.urgency_scenarios.scenarios_data import SCENARIOS


def print_scenario_demo():
    """Affiche une démonstration des scénarios"""
    
    print("\n" + "="*80)
    print(" "*20 + "🧪 DÉMONSTRATION DES SCÉNARIOS GUARDIAN")
    print("="*80)
    
    print("\n📊 Base de données complète de scénarios pour calibration IA\n")
    
    # Compter les scénarios
    total = sum(len(scenarios) for scenarios in SCENARIOS.values())
    
    print(f"Total de scénarios : {total}")
    print(f"Catégories : {len(SCENARIOS)}")
    print()
    
    # Afficher par catégorie
    for category_name, scenarios in SCENARIOS.items():
        print(f"\n{'─'*80}")
        print(f"📂 Catégorie: {category_name.upper()} ({len(scenarios)} scénarios)")
        print(f"{'─'*80}\n")
        
        for i, scenario in enumerate(scenarios, 1):
            niveau = scenario['niveau_attendu']
            cat = scenario['categorie']
            desc = scenario['description']
            email = "✉️  Email" if scenario['email_attendu'] else "❌ Pas d'email"
            
            # Barre visuelle du niveau
            bar = "█" * niveau + "░" * (10 - niveau)
            
            # Couleur par catégorie
            if niveau <= 3:
                emoji = "🟢"
            elif niveau <= 5:
                emoji = "🟡"
            elif niveau <= 7:
                emoji = "🟠"
            else:
                emoji = "🔴"
            
            print(f"{i:2d}. {emoji} [{bar}] {niveau:2d}/10 ({cat:10s}) | {email:15s}")
            print(f"    📝 {desc}")
            print(f"    💡 {scenario.get('justification', 'N/A')}")
            
            if scenario.get('services_urgence') != 'Aucun':
                print(f"    🚨 Services: {scenario['services_urgence']}")
            
            print()


def show_statistics():
    """Affiche les statistiques"""
    all_scenarios = []
    for scenarios in SCENARIOS.values():
        all_scenarios.extend(scenarios)
    
    total = len(all_scenarios)
    faible = len([s for s in all_scenarios if s['niveau_attendu'] <= 3])
    moderee = len([s for s in all_scenarios if 4 <= s['niveau_attendu'] <= 5])
    elevee = len([s for s in all_scenarios if 6 <= s['niveau_attendu'] <= 7])
    critique = len([s for s in all_scenarios if s['niveau_attendu'] >= 8])
    
    avec_email = len([s for s in all_scenarios if s['email_attendu']])
    sans_email = len([s for s in all_scenarios if not s['email_attendu']])
    
    print("\n" + "="*80)
    print(" "*30 + "📊 STATISTIQUES")
    print("="*80)
    
    print(f"\n🎯 Distribution des niveaux d'urgence:")
    print(f"  🟢 Faible (1-3):      {faible:2d} scénarios ({faible/total*100:5.1f}%)")
    print(f"  🟡 Modérée (4-5):     {moderee:2d} scénarios ({moderee/total*100:5.1f}%)")
    print(f"  🟠 Élevée (6-7):      {elevee:2d} scénarios ({elevee/total*100:5.1f}%)")
    print(f"  🔴 Critique (8-10):   {critique:2d} scénarios ({critique/total*100:5.1f}%)")
    
    print(f"\n📧 Envoi d'emails aux proches:")
    print(f"  ✉️  Avec email (≥6):   {avec_email:2d} scénarios ({avec_email/total*100:5.1f}%)")
    print(f"  ❌ Sans email (<6):   {sans_email:2d} scénarios ({sans_email/total*100:5.1f}%)")
    
    print(f"\n📦 Total: {total} scénarios")
    
    # Graphique ASCII
    print(f"\n📈 Distribution visuelle:")
    max_count = max(faible, moderee, elevee, critique)
    bar_width = 40
    
    def draw_bar(count, color_emoji):
        width = int(count / max_count * bar_width) if max_count > 0 else 0
        return color_emoji + "█" * width + " " * (bar_width - width) + f" {count}"
    
    print(f"  Faible     : {draw_bar(faible, '🟢')}")
    print(f"  Modérée    : {draw_bar(moderee, '🟡')}")
    print(f"  Élevée     : {draw_bar(elevee, '🟠')}")
    print(f"  Critique   : {draw_bar(critique, '🔴')}")


def show_examples_by_level():
    """Affiche des exemples par niveau"""
    print("\n" + "="*80)
    print(" "*25 + "💡 EXEMPLES PAR NIVEAU D'URGENCE")
    print("="*80)
    
    # Collecter tous les scénarios
    all_scenarios = []
    for scenarios in SCENARIOS.values():
        for scenario in scenarios:
            all_scenarios.append(scenario)
    
    # Grouper par niveau
    by_level = {}
    for scenario in all_scenarios:
        level = scenario['niveau_attendu']
        if level not in by_level:
            by_level[level] = []
        by_level[level].append(scenario)
    
    # Afficher niveau par niveau
    for level in sorted(by_level.keys()):
        scenarios = by_level[level]
        
        # Emoji et catégorie
        if level <= 3:
            emoji, cat_name = "🟢", "FAIBLE"
        elif level <= 5:
            emoji, cat_name = "🟡", "MODÉRÉE"
        elif level <= 7:
            emoji, cat_name = "🟠", "ÉLEVÉE"
        else:
            emoji, cat_name = "🔴", "CRITIQUE"
        
        print(f"\n{emoji} NIVEAU {level}/10 - {cat_name} ({len(scenarios)} scénarios)")
        print("─" * 80)
        
        for scenario in scenarios[:3]:  # Limiter à 3 exemples
            email = "→ Email envoyé" if scenario['email_attendu'] else "→ Pas d'email"
            print(f"  • {scenario['description']}")
            print(f"    {email} | {scenario.get('services_urgence', 'N/A')}")
        
        if len(scenarios) > 3:
            print(f"  ... et {len(scenarios) - 3} autre(s)")


def main():
    """Fonction principale"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Démonstration des scénarios Guardian")
    parser.add_argument('--stats', '-s', action='store_true', help='Afficher les statistiques')
    parser.add_argument('--examples', '-e', action='store_true', help='Exemples par niveau')
    parser.add_argument('--all', '-a', action='store_true', help='Tout afficher')
    
    args = parser.parse_args()
    
    if args.all or (not args.stats and not args.examples):
        print_scenario_demo()
        show_statistics()
        show_examples_by_level()
    else:
        if args.stats:
            show_statistics()
        if args.examples:
            show_examples_by_level()
    
    print("\n" + "="*80)
    print("\n💡 Pour lancer les tests automatisés:")
    print("   python3 test_urgency_calibration.py")
    print("\n🎮 Pour le mode interactif:")
    print("   python3 interactive_trainer.py")
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()
