#!/usr/bin/env python3
"""
TEST DEBUG VERTEX AI AGENT
Debug du problème de parsing JSON avec la nouvelle API Google GenAI
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yaml
from guardian.gemini_agent import VertexAIAgent

def test_vertex_ai_debug():
    """Test de debugging de l'agent Vertex AI"""
    print("🔍 DEBUG VERTEX AI AGENT")
    print("="*50)
    
    # Charger la configuration
    try:
        with open('api_keys.yaml', 'r') as f:
            config = yaml.safe_load(f)
    except Exception as e:
        print(f"❌ Erreur chargement config: {e}")
        return
        
    # Créer l'agent
    agent = VertexAIAgent(config)
    
    print(f"🔧 Agent créé:")
    print(f"   API Type: {agent.api_type}")
    print(f"   API Key: {agent.api_key[:10] if agent.api_key else 'None'}...")
    print(f"   Model: {agent.model_name}")
    print(f"   Available: {agent.is_available}")
    print(f"   Enabled: {agent.enabled}")
    
    if hasattr(agent, 'use_genai_client'):
        print(f"   Use GenAI Client: {agent.use_genai_client}")
    
    # Test simple
    print("\n🧪 Test simple...")
    test_prompt = "Je suis en danger - aidez-moi!"
    
    print(f"📝 Prompt: {test_prompt}")
    
    try:
        # Appel direct à _make_api_request
        response = agent._make_api_request(test_prompt)
        
        print("✅ Réponse brute reçue:")
        print(f"   Type: {type(response)}")
        print(f"   Contenu: {response}")
        
        if response and isinstance(response, dict):
            if 'candidates' in response:
                candidate = response['candidates'][0]
                content = candidate['content']['parts'][0]['text']
                print(f"\n📄 Texte extrait: {content[:100]}...")
            else:
                print("   ❌ Pas de 'candidates' dans la réponse")
        
    except Exception as e:
        print(f"❌ Erreur dans le test: {e}")
        print(f"   Type: {type(e).__name__}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_vertex_ai_debug()