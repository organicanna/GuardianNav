"""
Test de calibration des niveaux d'urgence avec Gemini
Permet de valider que l'IA évalue correctement chaque scénario
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire parent au path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from guardian.gemini_agent import GeminiAgent
from tests.urgency_scenarios.scenarios_data import get_all_scenarios, get_statistics, SCENARIOS
import yaml
import time
from typing import Dict, List
from datetime import datetime


class UrgencyCalibrationTester:
    """Testeur de calibration des niveaux d'urgence"""
    
    def __init__(self):
        """Initialise le testeur avec le GeminiAgent"""
        # Charger la configuration
        config_path = project_root / "config" / "api_keys.yaml"
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Initialiser l'agent Gemini
        self.agent = GeminiAgent(api_keys_config=self.config)
        
        # Résultats des tests
        self.results = []
        self.summary = {
            "total": 0,
            "correct": 0,
            "tolerance_ok": 0,  # ±1 niveau
            "incorrect": 0,
            "errors": 0
        }
    
    def test_scenario(self, scenario: Dict, tolerance: int = 1) -> Dict:
        """
        Test un scénario individuel
        
        Args:
            scenario: Dictionnaire du scénario
            tolerance: Marge de tolérance acceptée (±1 par défaut)
        
        Returns:
            Résultat du test avec évaluation
        """
        print(f"\n{'='*80}")
        print(f"🧪 Test: {scenario['description'][:60]}...")
        print(f"{'='*80}")
        
        try:
            # Analyser avec Gemini
            analysis = self.agent.analyze_emergency_situation(
                context=scenario['description'],
                location=(48.8566, 2.3522),  # Paris par défaut
                user_input=scenario['description'],
                time_of_day="jour"
            )
            
            # Extraire les résultats
            niveau_obtenu = analysis.get('urgency_level', 0)
            categorie_obtenue = analysis.get('urgency_category', 'Inconnue')
            
            # Calculer les écarts
            ecart_niveau = abs(niveau_obtenu - scenario['niveau_attendu'])
            
            # Déterminer si c'est correct
            is_exact = (niveau_obtenu == scenario['niveau_attendu'])
            is_tolerance_ok = (ecart_niveau <= tolerance)
            
            # Afficher les résultats
            print(f"\n📊 RÉSULTATS:")
            print(f"  Niveau attendu:   {scenario['niveau_attendu']}/10 ({scenario['categorie']})")
            print(f"  Niveau obtenu:    {niveau_obtenu}/10 ({categorie_obtenue})")
            print(f"  Écart:            {ecart_niveau} niveau(x)")
            
            if is_exact:
                print(f"  ✅ PARFAIT - Niveau exact!")
                status = "exact"
            elif is_tolerance_ok:
                print(f"  ✓ OK - Dans la tolérance (±{tolerance})")
                status = "tolerance_ok"
            else:
                print(f"  ❌ ERREUR - Écart trop important!")
                status = "incorrect"
            
            # Vérifier l'envoi d'email
            email_serait_envoye = (niveau_obtenu >= 6)
            email_correct = (email_serait_envoye == scenario['email_attendu'])
            
            print(f"\n📧 Email aux proches:")
            print(f"  Attendu:  {'OUI' if scenario['email_attendu'] else 'NON'}")
            print(f"  Obtenu:   {'OUI' if email_serait_envoye else 'NON'}")
            print(f"  {'✅ Correct' if email_correct else '❌ Incorrect'}")
            
            print(f"\n💡 Analyse IA:")
            print(f"  Type: {analysis.get('emergency_type', 'N/A')}")
            print(f"  Services: {analysis.get('emergency_services', 'N/A')}")
            print(f"  Conseil: {analysis.get('specific_advice', 'N/A')[:80]}...")
            
            result = {
                "scenario": scenario['description'],
                "category_type": scenario.get('category_type', 'unknown'),
                "niveau_attendu": scenario['niveau_attendu'],
                "categorie_attendue": scenario['categorie'],
                "niveau_obtenu": niveau_obtenu,
                "categorie_obtenue": categorie_obtenue,
                "ecart": ecart_niveau,
                "status": status,
                "email_attendu": scenario['email_attendu'],
                "email_obtenu": email_serait_envoye,
                "email_correct": email_correct,
                "analysis": analysis
            }
            
            return result
            
        except Exception as e:
            print(f"❌ ERREUR lors du test: {e}")
            return {
                "scenario": scenario['description'],
                "status": "error",
                "error": str(e)
            }
    
    def run_all_tests(self, delay_between_tests: float = 1.0, max_tests: int = None):
        """
        Exécute tous les tests de scénarios
        
        Args:
            delay_between_tests: Délai entre chaque test (pour éviter rate limiting)
            max_tests: Nombre maximum de tests (None = tous)
        """
        scenarios = get_all_scenarios()
        
        if max_tests:
            scenarios = scenarios[:max_tests]
        
        print(f"\n{'='*80}")
        print(f"🚀 DÉMARRAGE DES TESTS DE CALIBRATION")
        print(f"{'='*80}")
        print(f"📝 Nombre de scénarios: {len(scenarios)}")
        print(f"⏱️  Délai entre tests: {delay_between_tests}s")
        print(f"🤖 Agent Gemini: {'Disponible' if self.agent.is_available else 'Simulation'}")
        
        for i, scenario in enumerate(scenarios, 1):
            print(f"\n\n{'#'*80}")
            print(f"# Test {i}/{len(scenarios)}")
            print(f"{'#'*80}")
            
            result = self.test_scenario(scenario)
            self.results.append(result)
            
            # Mettre à jour le résumé
            self.summary['total'] += 1
            if result.get('status') == 'exact':
                self.summary['correct'] += 1
            elif result.get('status') == 'tolerance_ok':
                self.summary['tolerance_ok'] += 1
            elif result.get('status') == 'incorrect':
                self.summary['incorrect'] += 1
            else:
                self.summary['errors'] += 1
            
            # Pause entre les tests
            if i < len(scenarios):
                time.sleep(delay_between_tests)
        
        self._print_final_report()
    
    def _print_final_report(self):
        """Affiche le rapport final des tests"""
        print(f"\n\n{'='*80}")
        print(f"📊 RAPPORT FINAL - CALIBRATION DES URGENCES")
        print(f"{'='*80}")
        
        total = self.summary['total']
        correct = self.summary['correct']
        tolerance_ok = self.summary['tolerance_ok']
        incorrect = self.summary['incorrect']
        errors = self.summary['errors']
        
        print(f"\n📈 Statistiques globales:")
        print(f"  Total testé:        {total}")
        print(f"  ✅ Parfait (exact): {correct} ({correct/total*100:.1f}%)")
        print(f"  ✓ OK (±1):          {tolerance_ok} ({tolerance_ok/total*100:.1f}%)")
        print(f"  ❌ Incorrect:       {incorrect} ({incorrect/total*100:.1f}%)")
        print(f"  ⚠️  Erreurs:         {errors}")
        
        # Taux de réussite total
        success_rate = (correct + tolerance_ok) / total * 100 if total > 0 else 0
        print(f"\n🎯 Taux de réussite global: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print(f"   🌟 EXCELLENT - Calibration très précise!")
        elif success_rate >= 75:
            print(f"   ✅ BON - Calibration correcte")
        elif success_rate >= 60:
            print(f"   ⚠️  MOYEN - Calibration à améliorer")
        else:
            print(f"   ❌ FAIBLE - Calibration nécessite ajustements")
        
        # Analyse par catégorie
        print(f"\n📂 Analyse par catégorie de scénario:")
        categories = {}
        for result in self.results:
            cat = result.get('category_type', 'unknown')
            if cat not in categories:
                categories[cat] = {'total': 0, 'correct': 0, 'tolerance_ok': 0}
            
            categories[cat]['total'] += 1
            if result.get('status') == 'exact':
                categories[cat]['correct'] += 1
            elif result.get('status') == 'tolerance_ok':
                categories[cat]['tolerance_ok'] += 1
        
        for cat, stats in categories.items():
            success = (stats['correct'] + stats['tolerance_ok']) / stats['total'] * 100
            print(f"  {cat:15s}: {success:5.1f}% ({stats['correct']+stats['tolerance_ok']}/{stats['total']})")
        
        # Problèmes identifiés
        print(f"\n❌ Scénarios problématiques (écart > 1):")
        problematic = [r for r in self.results if r.get('status') == 'incorrect']
        
        if not problematic:
            print(f"  ✅ Aucun problème majeur détecté!")
        else:
            for result in problematic:
                print(f"\n  • {result['scenario'][:60]}...")
                print(f"    Attendu: {result['niveau_attendu']}/10, Obtenu: {result['niveau_obtenu']}/10 (écart: {result['ecart']})")
    
    def run_category_test(self, category: str, delay: float = 1.0):
        """Test uniquement une catégorie spécifique"""
        if category not in SCENARIOS:
            print(f"❌ Catégorie '{category}' inconnue")
            print(f"📂 Catégories disponibles: {', '.join(SCENARIOS.keys())}")
            return
        
        scenarios = SCENARIOS[category]
        print(f"\n🎯 Test de la catégorie: {category.upper()}")
        print(f"📝 Nombre de scénarios: {len(scenarios)}")
        
        for i, scenario in enumerate(scenarios, 1):
            scenario['category_type'] = category
            print(f"\n{'#'*80}")
            print(f"# Test {i}/{len(scenarios)} - Catégorie: {category}")
            print(f"{'#'*80}")
            
            result = self.test_scenario(scenario)
            self.results.append(result)
            
            self.summary['total'] += 1
            if result.get('status') == 'exact':
                self.summary['correct'] += 1
            elif result.get('status') == 'tolerance_ok':
                self.summary['tolerance_ok'] += 1
            elif result.get('status') == 'incorrect':
                self.summary['incorrect'] += 1
            else:
                self.summary['errors'] += 1
            
            if i < len(scenarios):
                time.sleep(delay)
        
        self._print_final_report()
    
    def export_results(self, filename: str = None):
        """Exporte les résultats dans un fichier JSON"""
        import json
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"urgency_test_results_{timestamp}.json"
        
        output_path = project_root / "tests" / "urgency_scenarios" / filename
        
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": self.summary,
            "results": self.results,
            "agent_available": self.agent.is_available
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Résultats exportés: {output_path}")


def main():
    """Fonction principale"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test de calibration des urgences Guardian")
    parser.add_argument('--category', '-c', type=str, help='Tester uniquement une catégorie')
    parser.add_argument('--max-tests', '-m', type=int, help='Nombre maximum de tests')
    parser.add_argument('--delay', '-d', type=float, default=1.0, help='Délai entre tests (secondes)')
    parser.add_argument('--export', '-e', action='store_true', help='Exporter les résultats en JSON')
    
    args = parser.parse_args()
    
    # Créer le testeur
    tester = UrgencyCalibrationTester()
    
    # Afficher les statistiques des scénarios
    stats = get_statistics()
    print("\n📊 Base de données de scénarios:")
    print(f"  Total: {stats['total']}")
    print(f"  Faible (1-3): {stats['faible']}")
    print(f"  Modérée (4-5): {stats['moderee']}")
    print(f"  Élevée (6-7): {stats['elevee']}")
    print(f"  Critique (8-10): {stats['critique']}")
    print(f"  Avec email: {stats['avec_email']}")
    print(f"  Sans email: {stats['sans_email']}")
    
    # Lancer les tests
    if args.category:
        tester.run_category_test(args.category, delay=args.delay)
    else:
        tester.run_all_tests(delay_between_tests=args.delay, max_tests=args.max_tests)
    
    # Exporter si demandé
    if args.export:
        tester.export_results()


if __name__ == "__main__":
    main()
