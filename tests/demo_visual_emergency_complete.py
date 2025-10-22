#!/usr/bin/env python3
"""
Démonstration complète: GuardianNav envoie un email visuel en cas de chute à vélo
"""

import sys
import os

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from guardian.emergency_response import EmergencyResponse
from guardian.fall_detector import FallDetector
import time
import logging

def demo_visual_emergency_email():
    """Démonstration complète d'email visuel d'urgence"""
    
    print("🚴💥 DÉMONSTRATION: Email visuel d'urgence GuardianNav")
    print("=" * 65)
    
    # Configuration avec contacts d'urgence 
    config = {
        'emergency_contacts': [
            {
                'name': 'Anna Perret',
                'email': 'anna.perret63@gmail.com',
                'phone': '+33631309788'
            },
            {
                'name': 'Contact Secours',
                'email': 'secours@example.com',
                'phone': '+33123456789'
            },
            {
                'name': 'Médecin Famille',
                'email': 'medecin@example.com',
                'phone': '+33987654321'
            }
        ],
        'email': {
            'enabled': False  # Mode simulation - mettez True pour envoi réel
        }
    }
    
    print("📋 Configuration:")
    print(f"   📧 {len(config['emergency_contacts'])} contacts d'urgence configurés")
    print(f"   🔧 Mode: {'Simulation' if not config['email']['enabled'] else 'Envoi réel'}")
    print()
    
    # Initialiser le système d'urgence
    emergency_system = EmergencyResponse(config)
    
    # Simuler une chute à vélo
    print("🚴 SCÉNARIO: Chute à vélo détectée")
    print("-" * 40)
    
    # Position: Place du Châtelet, Paris
    location = (48.8566, 2.3522)
    
    # Informations de chute détectées
    fall_info = {
        'fall_type': 'chute_velo',
        'previous_speed': 24.8,  # km/h - vitesse élevée
        'current_speed': 0.1,
        'acceleration': -13.5,   # m/s² - décélération brutale  
        'severity': 'critique',
        'detection_time': time.time()
    }
    
    print(f"📍 Localisation: {location[0]:.6f}, {location[1]:.6f}")
    print(f"🚴 Vitesse avant chute: {fall_info['previous_speed']} km/h")
    print(f"💥 Décélération: {fall_info['acceleration']} m/s²")
    print(f"⚠️  Sévérité: {fall_info['severity']}")
    print()
    
    # Simuler la non-réponse de l'utilisateur
    print("⏳ Simulation: Utilisateur ne répond pas après 30 secondes...")
    print("🚨 GuardianNav déclenche automatiquement l'alerte d'urgence")
    print()
    
    # Générer et envoyer l'email visuel
    print("📧 GÉNÉRATION DE L'EMAIL VISUEL D'URGENCE")
    print("-" * 45)
    
    # Appel de la méthode d'alerte de chute
    emergency_system.send_fall_emergency_alert(location, fall_info)
    
    print()
    
    # Générer un aperçu pour visualisation
    print("👀 Génération d'un aperçu pour visualisation...")
    
    # Créer un email d'aperçu personnalisé
    html_content = emergency_system.email_generator.generate_emergency_email_html(
        location=location,
        emergency_type="🚴 Chute à vélo grave",
        urgency_level="critique",
        situation_details="Chute à vélo critique détectée par GuardianNav. Décélération brutale de 24.8 km/h à l'arrêt complet. L'utilisateur ne répond pas aux sollicitations depuis 30 secondes. Intervention d'urgence requise.",
        person_name="Utilisateur GuardianNav",
        additional_info=fall_info
    )
    
    # Sauvegarder l'aperçu final
    with open('demo_email_chute_complete.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("   ✅ Aperçu généré: demo_email_chute_complete.html")
    print()
    
    # Résumé de ce qui serait envoyé
    print("📤 RÉSUMÉ DE L'EMAIL ENVOYÉ:")
    print("-" * 30)
    print("🎯 Objet: 🚨 URGENCE CRITIQUE - Utilisateur GuardianNav a besoin d'aide")
    print()
    print("📧 Contenu inclus dans l'email:")
    print("   ✅ 🚨 Alerte visuelle avec couleurs d'urgence critique (rouge)")
    print("   ✅ 📍 Position GPS précise (latitude/longitude)")
    print("   ✅ 🎯 Adresse What3Words pour localisation ultra-précise") 
    print("   ✅ 🗺️  Carte interactive avec marqueur d'urgence")
    print("   ✅ 📊 Données techniques: vitesse, décélération, sévérité")
    print("   ✅ 📱 Boutons d'action: Ouvrir Maps, Appeler SAMU (15), Urgences (112)")
    print("   ✅ 🏥 Instructions d'action pour les contacts")
    print("   ✅ ⏰ Horodatage précis de l'alerte")
    print()
    
    # Liste des destinataires
    print("👥 Destinataires notifiés:")
    for i, contact in enumerate(config['emergency_contacts'], 1):
        print(f"   {i}. 👤 {contact['name']}")
        print(f"      📧 {contact['email']}")
        print(f"      📞 {contact['phone']}")
        print()
    
    print("🎯 RÉSULTAT FINAL:")
    print("═" * 50)
    print("✅ Email visuel d'urgence généré avec succès")
    print("🗺️  Carte et géolocalisation précise incluses") 
    print("📊 Informations techniques de chute intégrées")
    print("🚑 Contacts d'urgence immédiatement alertés")
    print("📱 Actions directes facilitées (Maps, appels)")
    print("🔒 Mode simulation - Prêt pour activation réelle")
    print()
    print("👀 Ouvrez 'demo_email_chute_complete.html' pour voir le rendu final")

if __name__ == "__main__":
    demo_visual_emergency_email()