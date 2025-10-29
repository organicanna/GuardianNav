#!/usr/bin/env python3
"""
TEST SIMPLE GOOGLE GENAI - EXEMPLE OFFICIEL
Test rapide avec l'exemple officiel de la nouvelle API Google GenAI
"""

import yaml
from google import genai

def load_api_key():
    """Charge la clé API depuis api_keys.yaml"""
    try:
        with open('api_keys.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Chercher la clé API Gemini
        google_config = config.get('google_cloud', {})
        gemini_config = google_config.get('gemini', {})
        vertex_config = google_config.get('vertex_ai', {})
        
        # Prioriser la clé Gemini, sinon Vertex AI
        api_key = gemini_config.get('api_key') or vertex_config.get('api_key')
        
        return api_key
        
    except Exception as e:
        print(f"❌ Erreur lecture config: {e}")
        return None

def main():
    """Test simple avec l'exemple officiel Google GenAI"""
    print("🚀 TEST GOOGLE GENAI - EXEMPLE OFFICIEL")
    print("="*50)
    
    # Charger la clé API
    api_key = load_api_key()
    if not api_key:
        print("❌ Clé API non trouvée dans api_keys.yaml")
        print("💡 Ajoutez votre clé dans la section gemini.api_key")
        return
        
    print(f"🔑 Clé API: {api_key[:10]}...")
    
    try:
        # Code exact de votre exemple
        print("\n🤖 Exécution de l'exemple officiel...")
        
        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model="gemini-2.5-flash", contents="Explain how AI works in a few words"
        )
        
        print("✅ Réponse de Gemini 2.5:")
        print("-" * 30)
        print(response.text)
        print("-" * 30)
        
        print("\n🎉 TEST RÉUSSI ! L'API Google GenAI fonctionne")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        print(f"   Type: {type(e).__name__}")
        
        # Essayer avec un autre modèle si 2.5 n'est pas disponible
        if "not found" in str(e).lower() or "404" in str(e):
            print("\n🔄 Essai avec gemini-1.5-flash...")
            try:
                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model="gemini-1.5-flash", contents="Explain how AI works in a few words"
                )
                print("✅ Réponse de Gemini 1.5:")
                print("-" * 30)
                print(response.text)
                print("-" * 30)
                print("\n🎉 TEST RÉUSSI avec Gemini 1.5 !")
            except Exception as e2:
                print(f"❌ Échec aussi avec 1.5: {e2}")
                print("\n💡 Solutions :")
                print("   1. Vérifiez votre clé API sur https://aistudio.google.com/app/apikey")
                print("   2. Assurez-vous que l'API Generative Language est activée")
                print("   3. Vérifiez votre quota API")

if __name__ == "__main__":
    main()