#!/usr/bin/env python3
"""
GMAIL EMAIL AGENT - Envoi d'emails d'urgence via Gmail API
Intégré dans GuardianNav pour alerter les proches en cas de danger
Utilise EmergencyEmailGenerator pour créer des emails visuels riches
"""

import os
import base64
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import requests
from .emergency_email_generator import EmergencyEmailGenerator


class GmailEmergencyAgent:
    """Agent d'envoi d'emails d'urgence via Gmail API"""
    
    def __init__(self, config):
        """Initialise l'agent Gmail avec la configuration"""
        self.config = config
        self.gmail_config = config.get('google_cloud', {}).get('gmail', {})
        self.access_token = None
        self.is_available = False
        
        # Initialiser le générateur d'emails visuels
        self.email_generator = EmergencyEmailGenerator(config)
        
        # Vérifier la configuration Gmail
        if self.gmail_config.get('enabled', False):
            self.client_id = self.gmail_config.get('client_id')
            self.client_secret = self.gmail_config.get('client_secret')
            self.refresh_token = self.gmail_config.get('refresh_token')
            
            if all([self.client_id, self.client_secret, self.refresh_token]) and \
               self.refresh_token != "YOUR_REFRESH_TOKEN":
                self.is_available = True
                print("📧 Gmail API configuré pour emails d'urgence")
            else:
                print("⚠️ Configuration Gmail incomplète ou tokens manquants")
        else:
            print("❌ Gmail API désactivé")
    
    def refresh_access_token(self):
        """Actualise le token d'accès OAuth2"""
        if not self.is_available:
            return False
            
        try:
            url = "https://oauth2.googleapis.com/token"
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'refresh_token': self.refresh_token,
                'grant_type': 'refresh_token'
            }
            
            response = requests.post(url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data.get('access_token')
            
            return bool(self.access_token)
            
        except Exception as e:
            print(f"❌ Erreur refresh token Gmail: {e}")
            return False
    
    def create_emergency_email(self, recipient_email, user_name, location, situation, emergency_contacts=None, 
                              emergency_type="🚨 Situation d'urgence", urgency_level="élevée", 
                              location_coords=None, additional_info=None):
        """Crée un email d'urgence formaté avec EmergencyEmailGenerator"""
        
        current_time = datetime.now().strftime("%d/%m/%Y à %H:%M")
        
        # Sujet d'urgence
        subject = f"🚨 ALERTE SÉCURITÉ - {user_name} demande de l'aide"
        
        # Utiliser EmergencyEmailGenerator pour créer un email visuel riche
        if location_coords and isinstance(location_coords, (list, tuple)) and len(location_coords) >= 2:
            # Si on a des coordonnées GPS précises, utiliser le générateur avancé
            html_body = self.email_generator.generate_emergency_email_html(
                location=location_coords,
                emergency_type=emergency_type,
                urgency_level=urgency_level,
                situation_details=situation,
                person_name=user_name,
                additional_info=additional_info
            )
        else:
            # Fallback vers un template simple si pas de coordonnées GPS
            html_body = self._create_simple_emergency_email(user_name, location, situation, current_time)
        
        # Version texte brut (fallback)
        text_body = f"""
🚨 ALERTE SÉCURITÉ - GuardianNav

👤 Personne: {user_name}
📅 Date: {current_time}
📍 Localisation: {location}

⚠️ SITUATION RAPPORTÉE:
"{situation}"

🎯 ACTIONS IMMÉDIATES:
1. Contactez {user_name} IMMÉDIATEMENT par téléphone
2. Si aucune réponse: Appelez les secours (17, 15, 18, 112)
3. Conservez ce message comme preuve de l'alerte

📞 Numéros d'urgence France:
• 17 - Police/Gendarmerie
• 15 - SAMU
• 18 - Pompiers  
• 112 - Urgence UE

🛡️ Alerte automatique GuardianNav - {current_time}
        """
        
        return subject, html_body, text_body
    
    def _create_simple_emergency_email(self, user_name, location, situation, current_time):
        """Crée un email d'urgence simple (fallback sans coordonnées GPS)"""
        
        # Corps HTML professionnel (version simplifiée)
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Alerte GuardianNav</title>
        </head>
        <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Arial, sans-serif; background-color: #f5f5f5;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
                
                <!-- Header d'urgence -->
                <div style="background: linear-gradient(135deg, #dc3545, #c82333); color: white; padding: 30px; text-align: center;">
                    <h1 style="margin: 0; font-size: 28px; font-weight: bold;">🚨 ALERTE SÉCURITÉ</h1>
                    <p style="margin: 10px 0 0 0; font-size: 16px; opacity: 0.9;">Demande d'aide via GuardianNav</p>
                </div>
                
                <div style="padding: 30px;">
                    <!-- Informations d'urgence -->
                    <div style="background: #fff3cd; padding: 25px; border-left: 5px solid #dc3545; border-radius: 8px; margin-bottom: 25px;">
                        <h2 style="color: #dc3545; margin-top: 0; font-size: 20px;">📍 Informations d'urgence</h2>
                        
                        <table style="width: 100%; border-collapse: collapse;">
                            <tr>
                                <td style="padding: 8px 0; font-weight: bold; color: #495057;">👤 Personne:</td>
                                <td style="padding: 8px 0; color: #212529;">{user_name}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; font-weight: bold; color: #495057;">📅 Date et heure:</td>
                                <td style="padding: 8px 0; color: #212529;">{current_time}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; font-weight: bold; color: #495057;">📍 Localisation:</td>
                                <td style="padding: 8px 0; color: #212529;">{location}</td>
                            </tr>
                        </table>
                        
                        <p style="margin: 20px 0 10px 0; font-weight: bold; color: #495057;">⚠️ Situation rapportée:</p>
                        <div style="background: white; padding: 18px; border: 1px solid #dee2e6; border-radius: 4px; font-style: italic; color: #212529;">
                            "{situation}"
                        </div>
                    </div>
                    
                    <!-- Actions recommandées -->
                    <div style="background: #d4edda; padding: 25px; border-left: 5px solid #28a745; border-radius: 8px; margin-bottom: 25px;">
                        <h3 style="color: #155724; margin-top: 0; font-size: 18px;">🎯 Actions immédiates requises</h3>
                        <ol style="margin: 15px 0; padding-left: 25px; color: #155724;">
                            <li style="margin: 10px 0; font-weight: 500;"><strong>Contactez {user_name} IMMÉDIATEMENT</strong> par téléphone</li>
                            <li style="margin: 10px 0; font-weight: 500;"><strong>Si aucune réponse:</strong> Appelez les secours au <strong style="color: #dc3545;">17 (Police) ou 112 (Urgences)</strong></li>
                            <li style="margin: 10px 0; font-weight: 500;"><strong>Conservez ce message</strong> comme preuve de l'alerte</li>
                        </ol>
                    </div>
                </div>
                
                <!-- Footer -->
                <div style="background: #343a40; color: #adb5bd; padding: 20px; text-align: center;">
                    <p style="margin: 0; font-size: 12px;">
                        📱 Alerte automatique GuardianNav - {current_time}<br>
                        🛡️ Système de sécurité personnelle
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_body
    
    def send_email(self, recipient_email, subject, html_body, text_body):
        """Envoie un email via Gmail API"""
        
        if not self.is_available:
            return {
                'success': False,
                'error': 'Gmail API non configuré'
            }
        
        try:
            # Actualiser le token d'accès
            if not self.refresh_access_token():
                return {
                    'success': False,
                    'error': 'Impossible de renouveler le token d\'accès'
                }
            
            # Créer le message MIME
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = "noreply@guardiannav.com"
            message['To'] = recipient_email
            
            # Ajouter les versions texte et HTML
            text_part = MIMEText(text_body, 'plain', 'utf-8')
            html_part = MIMEText(html_body, 'html', 'utf-8')
            
            message.attach(text_part)
            message.attach(html_part)
            
            # Encoder en base64 pour l'API Gmail
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            # Envoyer via l'API Gmail
            url = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'raw': raw_message
            }
            
            print(f"📤 Envoi email d'urgence Gmail à {recipient_email}...")
            
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            print(f"✅ Email d'urgence envoyé avec succès (ID: {result.get('id', 'N/A')})")
            
            return {
                'success': True,
                'message_id': result.get('id'),
                'recipient': recipient_email,
                'subject': subject
            }
            
        except Exception as e:
            error_msg = f"Erreur envoi Gmail: {e}"
            print(f"❌ {error_msg}")
            return {
                'success': False,
                'error': error_msg,
                'recipient': recipient_email
            }
    
    def send_to_emergency_contacts(self, user_name, location, situation, location_coords=None, emergency_type="🚨 Situation d'urgence", urgency_level="élevée"):
        """Envoie un email d'urgence à tous les contacts d'urgence configurés"""
        
        if not self.is_available:
            print("❌ Gmail non configuré - impossible d'envoyer des emails d'urgence")
            return False
        
        # Obtenir les contacts d'urgence de la configuration
        emergency_contacts = self.config.get('emergency_contacts', [])
        
        if not emergency_contacts:
            print("⚠️ Aucun contact d'urgence configuré")
            return False
        
        success_count = 0
        total_contacts = len(emergency_contacts)
        
        print(f"📧 Envoi d'emails d'urgence à {total_contacts} contact(s)...")
        
        for contact in emergency_contacts:
            try:
                contact_email = contact.get('email')
                contact_name = contact.get('name', 'Contact d\'urgence')
                
                if not contact_email:
                    print(f"⚠️ Email manquant pour {contact_name}")
                    continue
                
                # Créer l'email d'urgence
                subject, html_body, text_body = self.create_emergency_email(
                    recipient_email=contact_email,
                    user_name=user_name,
                    location=location,
                    situation=situation,
                    location_coords=location_coords,
                    emergency_type=emergency_type,
                    urgency_level=urgency_level
                )
                
                # Envoyer l'email
                result = self.send_email(contact_email, subject, html_body, text_body)
                
                if result.get('success'):
                    success_count += 1
                    print(f"✅ Email envoyé à {contact_name} ({contact_email})")
                else:
                    print(f"❌ Échec envoi à {contact_name}: {result.get('error')}")
                    
            except Exception as e:
                print(f"❌ Erreur contact {contact.get('name', 'inconnu')}: {e}")
        
        print(f"📊 Résultat: {success_count}/{total_contacts} emails envoyés avec succès")
        return success_count > 0


def test_gmail_agent():
    """Test de l'agent Gmail d'urgence"""
    
    try:
        import yaml
        
        with open('api_keys.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        agent = GmailEmergencyAgent(config)
        
        print(f"\n🧪 Test Agent Gmail d'urgence")
        print(f"Configuration: {'✅ Valide' if agent.is_available else '❌ Invalide'}")
        
        if agent.is_available:
            print("🔄 Test de génération d'email...")
            
            subject, html_body, text_body = agent.create_emergency_email(
                recipient_email="test@example.com",
                user_name="Test GuardianNav",
                location="Paris, France",
                situation="Test de fonctionnement du système d'urgence",
                location_coords=(48.8566, 2.3522)
            )
            
            print(f"✅ Email généré:")
            print(f"   - Sujet: {subject}")
            print(f"   - HTML: {len(html_body)} caractères")
            print(f"   - Texte: {len(text_body)} caractères")
            
    except FileNotFoundError:
        print("❌ Fichier api_keys.yaml non trouvé")
    except Exception as e:
        print(f"❌ Erreur test: {e}")


if __name__ == "__main__":
    test_gmail_agent()