"""
Script d'entraînement interactif pour affiner la calibration de Gemini
Permet de tester rapidement des scénarios et ajuster les prompts
"""

import sys
from pathlib import Path

# Ajouter le répertoire parent au path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from guardian.gemini_agent import GeminiAgent
import yaml


class InteractiveTrainer:
    """Entraîneur interactif pour calibrer Gemini"""
    
    def __init__(self):
        # Charger la configuration
        config_path = project_root / "config" / "api_keys.yaml"
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Initialiser l'agent Gemini
        self.agent = GeminiAgent(api_keys_config=self.config)
        
        print("🤖 Guardian - Entraîneur interactif de calibration")
        print("=" * 60)
        print(f"Agent disponible: {'✅ OUI' if self.agent.is_available else '⚠️  MODE SIMULATION'}")
        print()
    
    def analyze_situation(self, description: str):
        """Analyse une situation et affiche les résultats détaillés"""
        print(f"\n{'='*60}")
        print(f"🔍 Analyse: {description}")
        print(f"{'='*60}")
        
        try:
            analysis = self.agent.analyze_emergency_situation(
                context=description,
                location=(48.8566, 2.3522),
                user_input=description,
                time_of_day="jour"
            )
            
            # Afficher les résultats
            niveau = analysis.get('urgency_level', 0)
            categorie = analysis.get('urgency_category', 'Inconnue')
            
            print(f"\n📊 RÉSULTATS:")
            print(f"  🚨 Niveau d'urgence: {niveau}/10")
            print(f"  📂 Catégorie: {categorie}")
            
            # Indicateur visuel du niveau
            bar = "█" * niveau + "░" * (10 - niveau)
            print(f"  Échelle: [{bar}]")
            
            # Email serait-il envoyé?
            email_envoye = niveau >= 6
            print(f"\n📧 Email aux proches: {'✅ OUI' if email_envoye else '❌ NON'}")
            
            if email_envoye:
                if niveau >= 8:
                    print(f"   → Urgence CRITIQUE - Email + SMS + Alertes")
                else:
                    print(f"   → Urgence ÉLEVÉE - Email envoyé")
            
            print(f"\n💡 Analyse détaillée:")
            print(f"  Type: {analysis.get('emergency_type', 'N/A')}")
            print(f"  Services: {analysis.get('emergency_services', 'Aucun')}")
            print(f"  Conseil: {analysis.get('specific_advice', 'N/A')}")
            
            if 'immediate_actions' in analysis and analysis['immediate_actions']:
                print(f"\n⚡ Actions immédiates:")
                for i, action in enumerate(analysis['immediate_actions'][:3], 1):
                    print(f"    {i}. {action}")
            
            print(f"\n💬 Message rassurant:")
            print(f"  {analysis.get('reassurance_message', 'N/A')}")
            
            return analysis
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return None
    
    def run_interactive_mode(self):
        """Mode interactif - l'utilisateur saisit des scénarios"""
        print("\n🎮 MODE INTERACTIF")
        print("Entrez une situation d'urgence pour tester la calibration.")
        print("Commandes spéciales:")
        print("  - 'quit' ou 'exit' : Quitter")
        print("  - 'examples' : Voir des exemples")
        print("  - 'stats' : Voir les statistiques")
        print()
        
        test_count = 0
        
        while True:
            try:
                # Demander une situation
                print(f"\n{'─'*60}")
                situation = input("💬 Situation (ou commande): ").strip()
                
                if not situation:
                    continue
                
                # Commandes spéciales
                if situation.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Au revoir!")
                    break
                
                if situation.lower() == 'examples':
                    self._show_examples()
                    continue
                
                if situation.lower() == 'stats':
                    print(f"\n📊 Tests effectués: {test_count}")
                    continue
                
                # Analyser la situation
                self.analyze_situation(situation)
                test_count += 1
                
                # Demander feedback
                print(f"\n❓ Ce niveau vous semble-t-il correct? (o/n/commentaire)")
                feedback = input("Feedback: ").strip()
                
                if feedback and feedback.lower() not in ['o', 'oui', 'y', 'yes']:
                    print(f"📝 Feedback enregistré: {feedback}")
                    print(f"   → Considérez d'ajuster les mots-clés dans gemini_agent.py")
                
            except KeyboardInterrupt:
                print("\n\n👋 Interruption - Au revoir!")
                break
            except Exception as e:
                print(f"❌ Erreur: {e}")
    
    def _show_examples(self):
        """Affiche des exemples de scénarios"""
        print("\n📚 EXEMPLES DE SCÉNARIOS:")
        print()
        
        examples = [
            ("Faible", "Je suis tombé à vélo et j'ai crevé"),
            ("Faible", "Mon téléphone est presque à court de batterie"),
            ("Modérée", "Je suis perdu dans un quartier que je ne connais pas"),
            ("Modérée", "J'ai mal à la tête depuis ce matin"),
            ("Élevée", "Je suis tombé à vélo et j'ai très mal au bras"),
            ("Élevée", "Je me suis coupé profondément, ça saigne beaucoup"),
            ("Critique", "Je ne peux plus respirer correctement"),
            ("Critique", "J'ai été renversé par une voiture"),
        ]
        
        for category, example in examples:
            print(f"  [{category:10s}] {example}")
    
    def run_quick_tests(self):
        """Lance quelques tests rapides prédéfinis"""
        print("\n⚡ TESTS RAPIDES")
        print("Testing 5 scénarios clés...\n")
        
        quick_tests = [
            ("Faible", "Je suis tombé à vélo et j'ai crevé", 2),
            ("Modérée", "Je suis perdu dans la ville", 4),
            ("Élevée", "Je suis tombé et j'ai mal au bras", 6),
            ("Élevée", "Je me sens menacé par quelqu'un", 7),
            ("Critique", "Je ne peux plus respirer", 10),
        ]
        
        results = []
        
        for expected_cat, scenario, expected_level in quick_tests:
            print(f"\n{'─'*60}")
            print(f"Test: {scenario}")
            print(f"Attendu: {expected_level}/10 ({expected_cat})")
            
            analysis = self.analyze_situation(scenario)
            
            if analysis:
                obtained_level = analysis.get('urgency_level', 0)
                diff = abs(obtained_level - expected_level)
                
                if diff == 0:
                    status = "✅ PARFAIT"
                elif diff <= 1:
                    status = "✓ OK"
                else:
                    status = f"❌ ÉCART ({diff})"
                
                results.append((scenario, expected_level, obtained_level, status))
                print(f"\nRésultat: {status}")
            
            import time
            time.sleep(1)  # Pause pour éviter rate limiting
        
        # Résumé
        print(f"\n{'='*60}")
        print("📊 RÉSUMÉ DES TESTS RAPIDES")
        print(f"{'='*60}")
        
        for scenario, expected, obtained, status in results:
            print(f"{status:15s} | Attendu: {expected:2d} | Obtenu: {obtained:2d} | {scenario[:40]}")


def main():
    """Fonction principale"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Entraîneur interactif Guardian")
    parser.add_argument('--quick', '-q', action='store_true', help='Tests rapides prédéfinis')
    parser.add_argument('--test', '-t', type=str, help='Tester une situation spécifique')
    
    args = parser.parse_args()
    
    trainer = InteractiveTrainer()
    
    if args.quick:
        trainer.run_quick_tests()
    elif args.test:
        trainer.analyze_situation(args.test)
    else:
        trainer.run_interactive_mode()


if __name__ == "__main__":
    main()
