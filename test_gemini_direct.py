#!/usr/bin/env python3
"""
TEST DIRECT API GEMINI - GENERATIVE LANGUAGE
Teste directement l'API Google Generative AI sans passer par l'agent
"""

import yaml
import os
from google import genai

def load_api_key():
    """Charge la clé API depuis api_keys.yaml"""
    try:
        with open('api_keys.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Essayer plusieurs endroits pour la clé API
        gemini_key = None
        
        # 1. Section gemini
        if 'google_cloud' in config and 'gemini' in config['google_cloud']:
            gemini_key = config['google_cloud']['gemini'].get('api_key')
        
        # 2. Section vertex_ai
        if not gemini_key and 'google_cloud' in config and 'vertex_ai' in config['google_cloud']:
            gemini_key = config['google_cloud']['vertex_ai'].get('api_key')
            
        return gemini_key
        
    except Exception as e:
        print(f"❌ Erreur lecture config: {e}")
        return None

def test_gemini_api():
    """Test direct de l'API Gemini avec la nouvelle bibliothèque google-genai"""
    print("🧪 TEST DIRECT API GEMINI")
    print("="*50)
    
    # Charger la clé API
    api_key = load_api_key()
    if not api_key:
        print("❌ Clé API non trouvée dans api_keys.yaml")
        return False
        
    print(f"🔑 Clé API trouvée: {api_key[:10]}...")
    
    try:
        # Configurer la variable d'environnement pour l'API
        os.environ['GEMINI_API_KEY'] = api_key
        
        # Créer le client Gemini
        client = genai.Client()
        print("✅ Client Gemini créé avec succès")
        
        # Test de génération de contenu
        print("\n🤖 Test de génération de contenu...")
        
        prompt = """Je suis en situation d'urgence : je me suis perdu dans Paris la nuit et j'ai peur. 
        Analyse cette situation et donne-moi :
        1. Le niveau d'urgence (1-10)
        2. Le type de situation 
        3. Des conseils immédiats
        Réponds en français de manière concise."""
        
        print("🔄 Envoi de la requête à Gemini...")
        
        response = client.models.generate_content(
            model="gemini-1.5-flash", 
            contents=prompt
        )
        
        print("✅ Réponse de Gemini:")
        print("-" * 40)
        print(response.text)
        print("-" * 40)
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur API Gemini: {e}")
        print(f"   Type d'erreur: {type(e).__name__}")
        
        # Diagnostics spécifiques
        if "API_KEY_INVALID" in str(e) or "invalid" in str(e).lower():
            print("💡 Diagnostic: Clé API invalide")
            print("   - Vérifiez votre clé sur https://aistudio.google.com/app/apikey")
            print("   - Assurez-vous que l'API Generative Language est activée")
        elif "quota" in str(e).lower():
            print("💡 Diagnostic: Quota dépassé")
        elif "permission" in str(e).lower() or "403" in str(e):
            print("💡 Diagnostic: Permissions insuffisantes")
        elif "404" in str(e) or "not found" in str(e).lower():
            print("💡 Diagnostic: Modèle non trouvé - essayons gemini-2.0-flash-exp")
        
        # Essayer avec un autre modèle
        if "not found" in str(e).lower() or "404" in str(e):
            try:
                print("🔄 Essai avec gemini-2.0-flash-exp...")
                client = genai.Client()
                response = client.models.generate_content(
                    model="gemini-2.0-flash-exp", 
                    contents=prompt
                )
                print("✅ Réponse de Gemini (modèle expérimental):")
                print("-" * 40)
                print(response.text)
                print("-" * 40)
                return True
            except Exception as e2:
                print(f"❌ Échec aussi avec le modèle expérimental: {e2}")
        
        return False

def test_api_key_format():
    """Test du format de la clé API"""
    print("\n🔍 VÉRIFICATION FORMAT CLÉ API")
    print("="*40)
    
    api_key = load_api_key()
    if not api_key:
        print("❌ Pas de clé API")
        return False
        
    # Vérifications de base
    checks = [
        ("Longueur correcte (>30 caractères)", len(api_key) > 30),
        ("Commence par 'AIza'", api_key.startswith('AIza')),
        ("Contient seulement des caractères valides", api_key.replace('AIza', '').replace('-', '').replace('_', '').isalnum()),
        ("Pas d'espaces", ' ' not in api_key)
    ]
    
    all_good = True
    for check, result in checks:
        status = "✅" if result else "❌"
        print(f"{status} {check}")
        if not result:
            all_good = False
            
    return all_good

if __name__ == "__main__":
    print("🚀 DIAGNOSTIC COMPLET API GEMINI")
    print("="*50)
    
    # Test du format de clé
    format_ok = test_api_key_format()
    
    # Test de l'API si le format est correct
    if format_ok:
        api_ok = test_gemini_api()
        
        print(f"\n🎯 RÉSULTAT FINAL:")
        print(f"   Format clé API: {'✅' if format_ok else '❌'}")
        print(f"   Test API: {'✅' if api_ok else '❌'}")
        
        if api_ok:
            print("🎉 L'API Gemini fonctionne parfaitement !")
        else:
            print("⚠️ L'API Gemini ne fonctionne pas - vérifiez votre clé")
    else:
        print("❌ Format de clé API invalide - impossible de tester l'API")