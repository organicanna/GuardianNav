#!/usr/bin/env python3
"""
Test des différentes API Google pour l'IA
"""

import requests
import json
import yaml

def test_gemini_api():
    """Test de l'API Gemini directe avec clé API"""
    print("🧪 Test de l'API Gemini directe...")
    
    try:
        # Charger la clé API
        with open('api_keys.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        # Récupérer la clé API Vertex AI (on va l'utiliser pour Gemini)
        vertex_config = config.get('google_cloud', {}).get('vertex_ai', {})
        api_key = vertex_config.get('api_key')
        
        if not api_key or api_key == "YOUR_VERTEX_AI_API_KEY":
            print("❌ Clé API non configurée")
            return False
        
        print(f"✅ Clé API trouvée: {api_key[:20]}...")
        
        # Essayer l'API Gemini directe
        gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}"
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        payload = {
            "contents": [{
                "parts": [{"text": "Test de connectivité. Répondez simplement 'OK' en JSON: {\"status\": \"OK\"}"}]
            }],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 50
            }
        }
        
        print("🔄 Test de l'API Gemini...")
        response = requests.post(gemini_url, headers=headers, json=payload, timeout=10)
        
        print(f"📊 Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API Gemini fonctionne!")
            
            if 'candidates' in result:
                content = result['candidates'][0]['content']['parts'][0]['text']
                print(f"📝 Réponse: {content}")
                return True
            else:
                print(f"⚠️ Format de réponse inattendu: {result}")
                return False
        
        elif response.status_code == 403:
            print("❌ Erreur 403: Clé API invalide ou permissions insuffisantes")
            print("💡 Vérifiez que l'API Generative Language est activée dans Google Cloud Console")
            return False
        
        elif response.status_code == 400:
            print("❌ Erreur 400: Requête malformée")
            print(f"📋 Réponse: {response.text}")
            return False
        
        else:
            print(f"❌ Erreur {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_vertex_ai_oauth():
    """Test Vertex AI avec OAuth (nécessite authentification)"""
    print("\n🧪 Test de Vertex AI avec OAuth...")
    
    try:
        with open('api_keys.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        project_id = config.get('google_cloud', {}).get('project_id')
        vertex_config = config.get('google_cloud', {}).get('vertex_ai', {})
        region = vertex_config.get('region', 'europe-west1')
        
        print(f"📋 Project ID: {project_id}")
        print(f"📋 Région: {region}")
        
        # URL Vertex AI
        vertex_url = f"https://{region}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{region}/publishers/google/models/gemini-1.5-flash-002:generateContent"
        
        print("❌ Vertex AI nécessite OAuth2 ou service account")
        print("💡 Pas possible avec une simple clé API")
        
        return False
        
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

if __name__ == "__main__":
    print("🎯 Test des APIs Google AI")
    print("=" * 50)
    
    # Test 1: API Gemini directe (plus simple)
    gemini_ok = test_gemini_api()
    
    # Test 2: API Vertex AI (plus complexe)
    vertex_ok = test_vertex_ai_oauth()
    
    print("\n" + "=" * 50)
    print("📊 Résultats:")
    print(f"   API Gemini directe: {'✅ OK' if gemini_ok else '❌ Échec'}")
    print(f"   API Vertex AI: {'✅ OK' if vertex_ok else '❌ Échec (normal)'}")
    
    if gemini_ok:
        print("\n🎉 Solution recommandée:")
        print("   • Utiliser l'API Gemini directe")
        print("   • Plus simple que Vertex AI")
        print("   • Même modèle Gemini 1.5 Flash")
        print("   • Authentification par clé API uniquement")
        
        print("\n🔧 Configuration:")
        print("   1. Activer l'API 'Generative Language' dans Google Cloud Console")
        print("   2. Créer une clé API avec permissions Generative Language")
        print("   3. Modifier vertex_ai_agent_rest.py pour utiliser l'API Gemini")
    else:
        print("\n💡 Pour utiliser l'IA:")
        print("   1. Vérifier la clé API dans api_keys.yaml")
        print("   2. Activer l'API Generative Language")
        print("   3. Ou continuer en mode simulation")