#!/usr/bin/env python3
"""
Test rapide de la méthode test_vertex_ai_connection
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from guardian.vertex_ai_agent_rest import VertexAIAgent
import yaml

def test_method():
    try:
        with open('api_keys.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        agent = VertexAIAgent(config)
        
        # Vérifier si la méthode existe
        has_method = hasattr(agent, 'test_vertex_ai_connection')
        print(f"Has test_vertex_ai_connection method: {has_method}")
        
        if has_method:
            result = agent.test_vertex_ai_connection()
            print(f"Test result: {result}")
            print("✅ Méthode corrigée avec succès")
        else:
            print("❌ Méthode manquante")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_method()