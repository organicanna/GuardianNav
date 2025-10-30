#!/usr/bin/env python3
"""
Test du contenu d'email avec localisation et situation réelles
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import yaml
from guardian.gmail_emergency_agent import GmailEmergencyAgent

def test_email_content():
    """Test le contenu de l'email avec les vraies informations"""
    
    print("📧 TEST CONTENU EMAIL AVEC VRAIES INFORMATIONS")
    print("="*50)
    
    # Charger la configuration
    with open('api_keys.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Créer l'agent Gmail
    gmail_agent = GmailEmergencyAgent(config)
    
    if not gmail_agent.is_available:
        print("❌ Gmail Agent non disponible")
        return
    
    # Informations de test réelles
    user_name = "Camille Dupont"
    real_location = "8 rue de Londres, 75009 Paris (bureaux Google France), près de la gare Saint-Lazare"
    real_situation = "À l'aide ! Quelqu'un me suit depuis le métro, j'ai très peur"
    user_phone = "+33612345678"
    location_coords = (48.8756, 2.3264)  # Coordonnées exactes Google France
    
    print(f"👤 Utilisateur: {user_name}")
    print(f"📍 Localisation: {real_location}")
    print(f"⚠️ Situation: {real_situation}")
    print(f"📞 Téléphone: {user_phone}")
    print()
    
    # Générer l'email
    try:
        subject, html_body, text_body = gmail_agent.create_emergency_email(
            recipient_email="test@example.com",
            user_name=user_name,
            location=real_location,
            situation=real_situation,
            location_coords=location_coords,
            emergency_type="🚨 Alerte Guardian - Situation d'urgence",
            urgency_level="élevée",
            user_phone=user_phone
        )
        
        print("✅ EMAIL GÉNÉRÉ AVEC SUCCÈS")
        print(f"📝 Sujet: {subject}")
        print(f"📄 Taille HTML: {len(html_body)} caractères")
        print(f"📄 Taille texte: {len(text_body)} caractères")
        print()
        
        # Vérifications du contenu
        print("🔍 VÉRIFICATIONS DU CONTENU:")
        
        # Vérifier la localisation
        if real_location in html_body:
            print("✅ Localisation exacte trouvée dans l'email")
        else:
            print("❌ Localisation exacte MANQUANTE dans l'email")
            print(f"   Recherché: {real_location}")
        
        # Vérifier la situation
        if real_situation in html_body:
            print("✅ Situation rapportée trouvée dans l'email")
        else:
            print("❌ Situation rapportée MANQUANTE dans l'email")
            print(f"   Recherché: {real_situation}")
        
        # Vérifier WhatsApp
        whatsapp_count = html_body.count('WhatsApp')
        wame_count = html_body.count('wa.me')
        phone_count = html_body.count(user_phone.replace('+', ''))
        
        print(f"💬 'WhatsApp' trouvé: {whatsapp_count} fois")
        print(f"🔗 'wa.me' trouvé: {wame_count} fois") 
        print(f"📞 Numéro '{user_phone}' trouvé: {phone_count} fois")
        
        # Vérifier les coordonnées
        if str(location_coords[0]) in html_body and str(location_coords[1]) in html_body:
            print("✅ Coordonnées GPS trouvées dans l'email")
        else:
            print("⚠️ Coordonnées GPS non trouvées dans l'email")
        
        # Afficher un extrait de l'email
        print("\n📄 EXTRAIT DE L'EMAIL (200 premiers caractères du HTML):")
        print("-" * 60)
        print(html_body[:500] + "..." if len(html_body) > 500 else html_body)
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur génération email: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_email_content()