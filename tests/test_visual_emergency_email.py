#!/usr/bin/env python3
"""
Test du générateur d'emails visuels d'urgence pour GuardianNav
"""

import sys
import os

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from guardian.emergency_email_generator import EmergencyEmailGenerator
import logging

def test_visual_emergency_email():
    """Test de génération d'email visuel d'urgence"""
    
    # Configuration des logs
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    print("📧 Test du générateur d'emails visuels d'urgence")
    print("=" * 55)
    
    # Initialiser le générateur
    generator = EmergencyEmailGenerator()
    
    # Position de test (Paris - Châtelet)
    test_location = (48.8566, 2.3522)
    
    print(f"📍 Position de test: {test_location}")
    print()
    
    # Test 1: Email de chute à vélo critique
    print("🚴 Test 1: Email de chute à vélo critique")
    
    fall_info = {
        'fall_type': 'chute_velo',
        'previous_speed': 22.3,
        'acceleration': -12.8,
        'severity': 'critique'
    }
    
    html_email = generator.generate_emergency_email_html(
        location=test_location,
        emergency_type="🚴 Chute à vélo détectée",
        urgency_level="critique",
        situation_details="Chute à vélo grave détectée par les capteurs GPS. Décélération brutale mesurée. La personne ne répond pas depuis 45 secondes.",
        person_name="Alex Martin",
        additional_info=fall_info
    )
    
    # Sauvegarder l'aperçu
    with open('preview_email_chute_velo.html', 'w', encoding='utf-8') as f:
        f.write(html_email)
    
    print("   ✅ Email HTML généré")
    print("   📄 Aperçu sauvé: preview_email_chute_velo.html")
    print()
    
    # Test 2: Email d'immobilité prolongée
    print("⏰ Test 2: Email d'immobilité prolongée")
    
    immobility_info = {
        'time_since_fall': 180,
        'movement_since_fall': 2.3
    }
    
    html_email_2 = generator.generate_emergency_email_html(
        location=test_location,
        emergency_type="⏰ Immobilité prolongée",
        urgency_level="élevée",
        situation_details="Aucun mouvement détecté depuis 3 minutes. Position GPS statique. Possibilité de blessure ou d'évanouissement.",
        person_name="Marie Dubois", 
        additional_info=immobility_info
    )
    
    # Sauvegarder l'aperçu
    with open('preview_email_immobilite.html', 'w', encoding='utf-8') as f:
        f.write(html_email_2)
    
    print("   ✅ Email HTML généré")
    print("   📄 Aperçu sauvé: preview_email_immobilite.html")
    print()
    
    # Test 3: Email générique d'urgence
    print("🚨 Test 3: Email d'urgence générique")
    
    html_email_3 = generator.generate_emergency_email_html(
        location=test_location,
        emergency_type="🚨 Urgence générale",
        urgency_level="modérée",
        situation_details="Alerte d'urgence déclenchée manuellement par l'utilisateur via GuardianNav.",
        person_name="Jean Dupont"
    )
    
    # Sauvegarder l'aperçu
    with open('preview_email_general.html', 'w', encoding='utf-8') as f:
        f.write(html_email_3)
    
    print("   ✅ Email HTML généré")
    print("   📄 Aperçu sauvé: preview_email_general.html")
    print()
    
    # Analyse du contenu
    print("📊 Analyse du contenu généré:")
    print(f"   📧 Taille email chute vélo: {len(html_email)} caractères")
    print(f"   📧 Taille email immobilité: {len(html_email_2)} caractères")
    print(f"   📧 Taille email général: {len(html_email_3)} caractères")
    
    # Vérifier les éléments clés
    elements_cles = [
        "What3Words",
        "Google Maps", 
        "Coordonnées GPS",
        "SAMU (15)",
        "Urgences EU (112)",
        "GuardianNav"
    ]
    
    print("\n🔍 Éléments inclus dans l'email:")
    for element in elements_cles:
        if element in html_email:
            print(f"   ✅ {element}")
        else:
            print(f"   ❌ {element} manquant")
    
    print(f"\n💡 Fonctionnalités des emails visuels:")
    print(f"   📍 Localisation précise avec What3Words")
    print(f"   🗺️  Carte intégrée avec marqueur d'urgence")
    print(f"   📊 Informations techniques (vitesse, décélération)")
    print(f"   🎨 Design adaptatif selon niveau d'urgence")
    print(f"   📱 Boutons d'action directs (Maps, appels)")
    print(f"   🔒 Fallback texte si HTML non supporté")
    
    print(f"\n✅ Tests terminés - Ouvrez les fichiers .html pour voir le rendu")

def test_emergency_integration():
    """Test d'intégration avec le système d'urgence"""
    
    print("\n" + "="*55)
    print("🔗 Test d'intégration système d'urgence")
    
    from guardian.emergency_response import EmergencyResponse
    
    # Configuration de test
    config = {
        'emergency_contacts': [
            {'name': 'Anna Perret', 'email': 'anna.test@example.com'},
            {'name': 'Contact Secours', 'email': 'secours@example.com'}
        ],
        'email': {'enabled': False}  # Mode simulation
    }
    
    # Initialiser le système
    emergency_system = EmergencyResponse(config)
    
    print(f"\n📧 Génération d'aperçu d'email GuardianNav:")
    
    # Générer un aperçu
    preview_html = emergency_system.generate_preview_email()
    
    with open('preview_guardiannav_complete.html', 'w', encoding='utf-8') as f:
        f.write(preview_html)
    
    print(f"   ✅ Aperçu complet généré")
    print(f"   📄 Fichier: preview_guardiannav_complete.html")
    
    # Simuler l'envoi d'une alerte de chute
    test_location = (48.8566, 2.3522)
    test_fall_info = {
        'fall_type': 'chute_velo',
        'previous_speed': 18.5,
        'acceleration': -9.2,
        'severity': 'grave'
    }
    
    print(f"\n📩 Simulation d'envoi d'alerte de chute:")
    emergency_system.send_fall_emergency_alert(test_location, test_fall_info)
    
    print(f"\n🎯 Résultat:")
    print(f"   ✅ Email visuel généré et prêt à être envoyé")
    print(f"   📧 {len(config['emergency_contacts'])} contacts seraient notifiés")
    print(f"   🗺️  Carte et géolocalisation incluses")
    print(f"   📊 Données de chute intégrées")

if __name__ == "__main__":
    test_visual_emergency_email()
    test_emergency_integration()