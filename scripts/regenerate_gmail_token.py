#!/usr/bin/env python3
"""
Script pour régénérer le refresh token Gmail
"""

import os
import sys
import yaml
from pathlib import Path

# Ajouter le répertoire parent au PYTHONPATH
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Scopes nécessaires pour Gmail
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def regenerate_gmail_token():
    """Régénère le refresh token Gmail"""
    
    # Charger la configuration
    config_path = parent_dir / 'config' / 'api_keys.yaml'
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    gmail_config = config['emergency']['gmail']
    
    # Créer les credentials OAuth2
    client_config = {
        "installed": {
            "client_id": gmail_config['client_id'],
            "client_secret": gmail_config['client_secret'],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost"]
        }
    }
    
    print("🔐 Démarrage de l'authentification Gmail...")
    print("📝 Une fenêtre de navigateur va s'ouvrir pour autoriser l'accès")
    print("")
    
    try:
        # Créer le flow OAuth2
        flow = InstalledAppFlow.from_client_config(
            client_config,
            scopes=SCOPES
        )
        
        # Lancer le serveur local pour recevoir l'autorisation
        credentials = flow.run_local_server(
            port=8080,
            prompt='consent',
            success_message='✅ Autorisation réussie ! Vous pouvez fermer cette fenêtre.'
        )
        
        # Récupérer le refresh token
        refresh_token = credentials.refresh_token
        
        if not refresh_token:
            print("❌ Erreur: Pas de refresh token reçu")
            print("💡 Essayez de révoquer l'accès depuis https://myaccount.google.com/permissions")
            return False
        
        print(f"\n✅ Nouveau refresh token généré:")
        print(f"📋 {refresh_token[:20]}...{refresh_token[-20:]}")
        
        # Mettre à jour le fichier de configuration
        config['emergency']['gmail']['refresh_token'] = refresh_token
        
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        print(f"\n✅ Configuration mise à jour dans: {config_path}")
        print("\n🎉 Refresh token Gmail régénéré avec succès !")
        print("🔄 Redémarrez le serveur Guardian pour appliquer les changements")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur lors de la génération du token: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("🔧 RÉGÉNÉRATION DU REFRESH TOKEN GMAIL")
    print("=" * 60)
    print()
    
    success = regenerate_gmail_token()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ SUCCÈS - Token régénéré")
        print("=" * 60)
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("❌ ÉCHEC - Vérifiez les erreurs ci-dessus")
        print("=" * 60)
        sys.exit(1)
