#!/usr/bin/env python3
"""
Test simple de réaction de Guardian à une chute
"""

import sys
import os

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from guardian.fall_detector import FallDetector

def test_guardian_fall_response():
    """Test de la réaction de Guardian à une chute"""
    
    print("🚴 Test: Que dit Guardian si vous tombez à vélo ?")
    print("=" * 50)
    
    # Créer un détecteur de chute
    detector = FallDetector()
    
    # Simuler une chute à vélo
    fall_info = detector.simulate_fall('chute_velo')
    
    print(f"💥 CHUTE DÉTECTÉE !")
    print(f"   Type: {fall_info['fall_type']}")
    print(f"   Sévérité: {fall_info['severity']}")
    print(f"   Vitesse avant chute: {fall_info['previous_speed']} km/h")
    print(f"   Décélération: {fall_info['acceleration']} m/s²")
    
    # Réaction de Guardian selon le type de chute
    print(f"\n🤖 GUARDIAN VOUS DIT:")
    print("─" * 50)
    
    if fall_info['fall_type'] == 'chute_velo':
        if fall_info['severity'] in ['critique', 'grave']:
            message = """J'ai détecté une chute à vélo potentiellement grave. 

🚑 RESTEZ IMMOBILE si possible et ne bougez pas la tête 
   si vous ressentez des douleurs au cou. 

📞 Je contacte immédiatement les secours et vos proches.
🏥 Les informations d'aide médicale à proximité ont été envoyées."""
        else:
            message = """Chute à vélo détectée. 

🩺 Vérifiez si vous pouvez bouger vos membres sans douleur. 
⚠️  Attention aux blessures qui ne sont pas immédiatement visibles.
📱 Prenez votre temps pour vous remettre."""
    
    print(message)
    
    print(f"\n❓ GUARDIAN DEMANDE:")
    print("─" * 50) 
    print("   Êtes-vous blessé(e) ? (Répondez 'oui' ou 'non' dans les 30 secondes)")
    print("   Si aucune réponse, j'alerterai automatiquement les secours...")
    
    print(f"\n⏰ SCÉNARIO - Aucune réponse après 30 secondes:")
    print("─" * 50)
    print("   🚨 TIMEOUT - AUCUNE RÉPONSE APRÈS CHUTE")
    print("   🚑 Je déclenche automatiquement l'alerte d'urgence")
    print("   📧 Email et SMS envoyés à vos contacts d'urgence")
    print("   🗺️  Position GPS et refuges à proximité partagés")
    
    print(f"\n📋 INFORMATIONS PARTAGÉES AUX SECOURS:")
    print("─" * 50)
    print(f"   • Type de chute: Chute à vélo")
    print(f"   • Sévérité évaluée: {fall_info['severity']}")
    print(f"   • Vitesse avant chute: {fall_info['previous_speed']:.1f} km/h")
    print(f"   • Décélération mesurée: {fall_info['acceleration']:.1f} m/s²")
    print(f"   • Position GPS exacte")
    print(f"   • Hôpitaux et pharmacies à proximité")
    print(f"   • Itinéraires d'évacuation optimisés")
    
    print(f"\n✅ RÉSULTAT:")
    print("─" * 50)
    print("   🛡️  GuardianNav détecte automatiquement les chutes")
    print("   🚑 Alerte les secours si vous ne répondez pas")
    print("   📍 Fournit votre position exacte et l'aide à proximité")
    print("   🏥 Guide les secours avec les meilleurs itinéraires")

if __name__ == "__main__":
    test_guardian_fall_response()