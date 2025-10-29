#!/usr/bin/env python3
"""
Test Simple de Vertex AI - GuardianNav
🧠 Test direct de l'analyse d'urgence avec Vertex AI Gemini
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_vertex_ai_analysis():
    """Test simple de l'analyse Vertex AI"""
    print("🧠 **TEST VERTEX AI - ANALYSE D'URGENCE**")
    print("=" * 50)
    
    try:
        # Import conditionnel
        try:
            from guardian.gemini_agent import VertexAIAgent
            guardian_available = True
        except ImportError:
            print("⚠️ Module GuardianNav non disponible - Test avec simulation")
            guardian_available = False
            
        # Charger la configuration
        try:
            import yaml
            with open('api_keys.yaml', 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
        except Exception as e:
            print(f"⚠️ Configuration non disponible: {e}")
            config = {}
            
        if guardian_available:
            # Test avec Vertex AI réel
            vertex_agent = VertexAIAgent(config)
            
            print(f"🔧 Vertex AI Status: {'✅ Disponible' if vertex_agent.is_available else '⚠️ Simulation'}")
            print()
            
            # Scénarios de test
            test_scenarios = [
                {
                    'situation': "Je me suis perdu dans Paris la nuit, j'ai peur et je ne connais pas le quartier",
                    'context': {'position': (48.8566, 2.3522), 'time': 'nuit'}
                },
                {
                    'situation': "Je suis tombé de mon vélo et j'ai mal au bras, je pense qu'il est cassé",
                    'context': {'position': (48.8566, 2.3522), 'time': 'jour'}
                },
                {
                    'situation': "Il y a un incendie dans mon immeuble, que dois-je faire ?",
                    'context': {'position': (48.8566, 2.3522), 'time': 'jour'}
                }
            ]
            
            for i, scenario in enumerate(test_scenarios, 1):
                print(f"🧪 **Test {i}: {scenario['situation'][:50]}...**")
                print("-" * 40)
                
                try:
                    # Analyser la situation
                    analysis = vertex_agent.analyze_emergency_situation(
                        scenario['situation'],
                        location=scenario['context']['position'],
                        user_input=scenario['situation']
                    )
                    
                    if analysis:
                        print(f"📊 Niveau d'urgence: {analysis.get('urgency_level', 'N/A')}/10")
                        print(f"🏥 Type d'urgence: {analysis.get('emergency_type', 'Non classifié')}")
                        print(f"💡 Conseil: {analysis.get('specific_advice', 'Aucun conseil disponible')[:100]}...")
                        
                        # Actions recommandées
                        actions = analysis.get('recommended_actions', [])
                        if actions:
                            print("🎯 Actions recommandées:")
                            for action in actions[:3]:  # Limiter à 3 actions
                                print(f"   • {action}")
                    else:
                        print("❌ Analyse non disponible")
                        
                except Exception as e:
                    print(f"❌ Erreur d'analyse: {e}")
                    
                print()
                
        else:
            # Simulation sans GuardianNav
            print("🤖 **MODE SIMULATION - VERTEX AI**")
            print("Les réponses suivantes sont simulées:")
            print()
            
            simulated_responses = [
                {
                    'situation': "Perdu dans Paris la nuit",
                    'urgency': 6,
                    'type': 'Situation de détresse',
                    'advice': "Dirigez-vous vers un lieu éclairé et fréquenté. Utilisez votre smartphone pour la navigation."
                },
                {
                    'situation': "Chute de vélo - bras blessé",
                    'urgency': 7,
                    'type': 'Urgence médicale',
                    'advice': "Consultez immédiatement un médecin. En cas de fracture suspectée, appelez le 15."
                },
                {
                    'situation': "Incendie dans l'immeuble",
                    'urgency': 9,
                    'type': 'Urgence vitale',
                    'advice': "Évacuez immédiatement par l'escalier. Appelez les pompiers (18). Ne prenez pas l'ascenseur."
                }
            ]
            
            for i, response in enumerate(simulated_responses, 1):
                print(f"🧪 **Simulation {i}: {response['situation']}**")
                print(f"📊 Niveau d'urgence: {response['urgency']}/10")
                print(f"🏥 Type d'urgence: {response['type']}")
                print(f"💡 Conseil: {response['advice']}")
                print()
                
        print("✅ **TEST TERMINÉ**")
        return True
        
    except Exception as e:
        print(f"❌ Erreur critique: {e}")
        import traceback
        traceback.print_exc()
        return False

def interactive_vertex_test():
    """Test interactif avec Vertex AI"""
    print("\n🎮 **MODE INTERACTIF - VERTEX AI**")
    print("=" * 40)
    print("💬 Décrivez votre situation d'urgence et recevez une analyse")
    print("🛑 Tapez 'stop' pour terminer")
    print()
    
    try:
        # Import et initialisation
        from guardian.gemini_agent import VertexAIAgent
        
        import yaml
        with open('api_keys.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            
        vertex_agent = VertexAIAgent(config)
        
        while True:
            user_input = input("👤 Votre situation: ").strip()
            
            if not user_input or user_input.lower() in ['stop', 'quit', 'exit']:
                break
                
            print(f"\n🧠 Analyse en cours...")
            
            try:
                analysis = vertex_agent.analyze_emergency_situation(
                    user_input,
                    location=(48.8566, 2.3522)
                )
                
                if analysis:
                    print(f"🤖 **Analyse GuardianNav:**")
                    print(f"   📊 Urgence: {analysis.get('urgency_level', 0)}/10")
                    print(f"   🏥 Type: {analysis.get('emergency_type', 'Non classifié')}")
                    print(f"   💡 Conseil: {analysis.get('specific_advice', 'Aucun conseil')}")
                else:
                    print("❌ Analyse non disponible")
                    
            except Exception as e:
                print(f"❌ Erreur: {e}")
                
            print()
            
        print("👋 Mode interactif terminé")
        
    except ImportError:
        print("❌ Modules GuardianNav non disponibles")
    except Exception as e:
        print(f"❌ Erreur: {e}")

def main():
    """Test principal"""
    print("🧠 TEST VERTEX AI GUARDIANNAV")
    print("=" * 40)
    print("🎯 Test de l'intelligence artificielle d'analyse d'urgence")
    print()
    
    # Test automatique
    success = test_vertex_ai_analysis()
    
    if success:
        response = input("\n🎮 Lancer le mode interactif ? (o/n): ")
        if response.lower() in ['o', 'oui', 'y', 'yes']:
            interactive_vertex_test()
            
    print("\n🔚 Test Vertex AI terminé")

if __name__ == "__main__":
    main()