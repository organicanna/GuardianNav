#!/usr/bin/env python3
"""
GMAIL EMAIL AGENT - Envoi d'emails d'urgence via Gmail API
Intégré dans Guardian pour alerter les proches en cas de danger
Utilise des templates HTML intégrés et What3Words pour la localisation précise
"""

import os
import base64
import json
import urllib.parse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import requests
from .what3words_service import What3WordsService


class GmailEmergencyAgent:
    """Agent d'envoi d'emails d'urgence via Gmail API"""
    
    def __init__(self, config):
        """Initialise l'agent Gmail avec la configuration"""
        self.config = config
        self.access_token = None
        self.is_available = False
        
        # Générateur d'emails visuels retiré - on utilise le template simple
        
        # Initialiser le service What3Words
        w3w_key = config.get('google_cloud', {}).get('services', {}).get('what3words_api_key', 'YOUR_WHAT3WORDS_API_KEY')
        self.what3words_service = What3WordsService(w3w_key)
        
        # Services de cartes supprimés - on utilise seulement les liens directs
        
        # Correction: Gmail est dans emergency.gmail, pas google_cloud.gmail
        self.gmail_config = config.get('emergency', {}).get('gmail', {})
        
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
                              location_coords=None, additional_info=None, user_phone=None):
        """Crée un email d'urgence formaté avec EmergencyEmailGenerator"""
        
        current_time = datetime.now().strftime("%d/%m/%Y à %H:%M")
        
        # Obtenir les informations What3Words si on a des coordonnées
        w3w_info = None
        if location_coords and isinstance(location_coords, (list, tuple)) and len(location_coords) >= 2:
            try:
                w3w_info = self.what3words_service.get_location_info(location_coords[0], location_coords[1])
            except Exception as e:
                print(f"⚠️ Erreur What3Words: {e}")
                w3w_info = None
        
        # Sujet d'urgence
        subject = f"📱 Guardian - {user_name} a besoin d'assistance"
        
        # Obtenir le numéro de téléphone de la personne depuis la configuration ou paramètre
        if not user_phone:
            emergency_config = self.config.get('emergency', {})
            user_info = emergency_config.get('user_info', {})
            user_phone = user_info.get('phone', '')
        
        # Utiliser le template unifié pour tous les emails
        html_body = self._create_simple_emergency_email(user_name, location, situation, current_time, location_coords, user_phone)
        
        # Les cartes sont retirées - on garde seulement les liens dans le texte
        
        # Créer la section de localisation avec What3Words et carte
        location_section = f"📍 Localisation: {location}"
        
        if w3w_info:
            location_section += f"""

🗺️ LOCALISATION PRÉCISE:
• Adresse What3Words: {w3w_info['what3words']}
• Coordonnées GPS: {w3w_info['coordinates']['latitude']}, {w3w_info['coordinates']['longitude']}
• Précision: {w3w_info['coordinates']['precision']}
• Lien What3Words: {w3w_info['what3words_url']}
• Lien Google Maps: {w3w_info['maps_url']}

💡 L'adresse What3Words ({w3w_info['what3words']}) est parfaite pour communiquer avec les secours - elle identifie un carré de 3m x 3m précisément."""

        # Version texte brut (fallback)
        text_body = f"""
📱 NOTIFICATION Guardian - Alerte de sécurité

👤 Personne concernée: {user_name}
📅 Date et heure: {current_time}
{location_section}

📋 INFORMATIONS DE LA SITUATION:
"{situation}"

🔍 CONTEXTE:
{user_name} a activé Guardian, son assistant de sécurité personnel, et notre intelligence artificielle a évalué sa situation comme nécessitant une attention particulière. Cette notification automatique vous est envoyée car vous êtes inscrit(e) comme contact d'urgence.

💡 CONSEILS POUR VOUS AIDER:

1. 📞 PREMIER CONTACT (dans les 5 minutes):
   • Appelez {user_name} immédiatement
   • Demandez-lui où elle se trouve exactement
   • Restez calme et rassurant(e) au téléphone

2. 🗣️ SI VOUS L'AVEZ AU TÉLÉPHONE:
   • Encouragez-la à se diriger vers un lieu sûr (magasin, restaurant ouvert, etc.)
   • Proposez de rester en ligne pendant qu'elle se déplace
   • Aidez-la à identifier les lieux sécurisés autour d'elle
   • Si nécessaire, guidez-la vers les transports ou un taxi

3. 📞 SI AUCUNE RÉPONSE:
   • Réessayez après 2-3 minutes
   • Envoyez un SMS: "J'ai reçu ton alerte Guardian, où es-tu ?"
   • Si toujours aucune réponse après 10 minutes, contactez les secours

4. 🆘 QUAND APPELER LES SECOURS:
   • Aucune réponse après 10 minutes d'essais
   • {user_name} vous dit être en danger immédiat
   • Vous entendez des bruits inquiétants au téléphone
   • Elle vous demande explicitement d'appeler les secours

📞 NUMÉROS D'URGENCE (France):
• 17 - Police/Gendarmerie (danger, agression)
• 15 - SAMU (urgence médicale)  
• 18 - Pompiers (accident, secours)
• 112 - Numéro d'urgence européen unique
• Nom: {user_name}
• Dernière position connue: {location}
• Heure de l'alerte: {current_time}
• Nature de la situation: {situation}""" + (f"""
• Adresse What3Words: {w3w_info['what3words']} ⭐ PRIORITAIRE pour les secours
• Coordonnées GPS: {w3w_info['coordinates']['latitude']}, {w3w_info['coordinates']['longitude']}
• Lien direct: {w3w_info['what3words_url']}""" if w3w_info else "") + f"""

🔄 SUIVI:
• Tenez-vous au courant avec les autres contacts d'urgence
• Informez {user_name} dès que vous savez qu'elle va bien
• Conservez cet email comme référence

⚡ Cette alerte a été générée automatiquement par Guardian, un système d'assistance de sécurité basé sur l'intelligence artificielle. {user_name} a volontairement activé ce système et vous a désigné(e) comme contact de confiance.

🛡️ Guardian - Système de sécurité intelligent
📧 Email automatique envoyé le {current_time}
        """
        
        return subject, html_body, text_body
    
    def _generate_whatsapp_links(self, user_name, situation, user_phone=None):
        """Génère le lien WhatsApp pour appeler directement la personne en danger"""
        whatsapp_links = {}
        
        # Obtenir le numéro de téléphone de la personne (priorité au paramètre fourni)
        if not user_phone:
            # Chercher dans la config utilisateur (dans emergency.user_info)
            emergency_config = self.config.get('emergency', {})
            user_info = emergency_config.get('user_info', {})
            user_phone = user_info.get('phone', '')
        
        if user_phone:
            # Nettoyer le numéro (retirer espaces, + en double, etc.)
            clean_phone = user_phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
            if clean_phone.startswith('++'):
                clean_phone = clean_phone[1:]  # Retirer le + en double
            elif not clean_phone.startswith('+'):
                # Si le numéro commence par 0 (format français), le convertir au format international
                if clean_phone.startswith('0'):
                    clean_phone = '+33' + clean_phone[1:]  # Remplacer 0 par +33
                else:
                    clean_phone = '+' + clean_phone
            
            # Message WhatsApp pré-rempli pour appeler la personne
            message = f"Je viens de recevoir une alerte Guardian concernant {user_name}. Je t'appelle immédiatement pour m'assurer que tout va bien !"
            
            # URL WhatsApp (encode le message)
            encoded_message = urllib.parse.quote(message)
            whatsapp_url = f"https://wa.me/{clean_phone.replace('+', '')}?text={encoded_message}"
            
            whatsapp_links[user_name] = {
                'phone': user_phone,
                'clean_phone': clean_phone,
                'url': whatsapp_url,
                'name': user_name
            }
        
        return whatsapp_links
    
    def _create_simple_emergency_email(self, user_name, location, situation, current_time, location_coords=None, user_phone=None):
        """Crée un email d'urgence simple avec liens WhatsApp intégrés"""
        
        # Corps HTML professionnel (version simplifiée)
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Alerte Guardian</title>
        </head>
        <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Arial, sans-serif; background-color: #f5f5f5;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
                
                <!-- Header informatif -->
                <div style="background: linear-gradient(135deg, #007bff, #0056b3); color: white; padding: 30px; text-align: center;">
                    <h1 style="margin: 0; font-size: 28px; font-weight: bold;">📱 NOTIFICATION GUARDIAN</h1>
                    <p style="margin: 10px 0 0 0; font-size: 16px; opacity: 0.9;">Demande d'assistance de sécurité</p>
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
                    </div>"""
        
        # Ajouter la section cartes si on a des coordonnées
        if location_coords and isinstance(location_coords, (list, tuple)) and len(location_coords) >= 2:
            google_maps_url = f"https://www.google.com/maps?q={location_coords[0]},{location_coords[1]}&z=16"
            osm_url = f"https://www.openstreetmap.org/?mlat={location_coords[0]}&mlon={location_coords[1]}&zoom=16"
            
            html_body += f"""
                    
                    <!-- Localisation sur carte -->
                    <div style="background: #e3f2fd; padding: 25px; border-left: 5px solid #1976d2; border-radius: 8px; margin-bottom: 25px;">
                        <h3 style="color: #0d47a1; margin-top: 0; font-size: 18px;">🗺️ Localisation sur carte</h3>
                        <p style="margin: 15px 0; color: #0d47a1; text-align: center; font-weight: 500;">
                            Cliquez sur un des liens ci-dessous pour voir la position exacte:
                        </p>
                        <div style="text-align: center; margin: 20px 0;">
                            <a href="{google_maps_url}" style="display: inline-block; background: #34a853; color: white; padding: 12px 20px; text-decoration: none; border-radius: 6px; font-weight: bold; margin: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                                🗺️ Google Maps
                            </a>
                            <a href="{osm_url}" style="display: inline-block; background: #1976d2; color: white; padding: 12px 20px; text-decoration: none; border-radius: 6px; font-weight: bold; margin: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                                📍 OpenStreetMap
                            </a>
                        </div>
                        <p style="margin: 10px 0; color: #0d47a1; font-size: 13px; text-align: center;">
                            📍 Coordonnées: {location_coords[0]}, {location_coords[1]}
                        </p>
                    </div>"""
        
        
        # Générer les liens WhatsApp pour appeler la personne en danger
        whatsapp_links = self._generate_whatsapp_links(user_name, situation, user_phone)
        
        html_body += f"""
                    
                    <!-- Actions recommandées -->
                    <div style="background: #d4edda; padding: 25px; border-left: 5px solid #28a745; border-radius: 8px; margin-bottom: 25px;">
                        <h3 style="color: #155724; margin-top: 0; font-size: 18px;">🎯 Actions immédiates requises</h3>
                        <ol style="margin: 15px 0; padding-left: 25px; color: #155724;">
                            <li style="margin: 10px 0; font-weight: 500;"><strong>Contactez {user_name} IMMÉDIATEMENT</strong> par téléphone</li>
                            <li style="margin: 10px 0; font-weight: 500;"><strong>Si aucune réponse:</strong> Appelez les secours au <strong style="color: #dc3545;">17 (Police) ou 112 (Urgences)</strong></li>
                            <li style="margin: 10px 0; font-weight: 500;"><strong>Conservez ce message</strong> comme preuve de l'alerte</li>
                        </ol>
                    </div>"""
        
        # Ajouter la section WhatsApp si on a des contacts avec téléphones
        if whatsapp_links:
            html_body += f"""
                    
                    <!-- Appel WhatsApp direct -->
                    <div style="background: #e8f5e8; padding: 25px; border-left: 5px solid #25d366; border-radius: 8px; margin-bottom: 25px;">
                        <h3 style="color: #075e54; margin-top: 0; font-size: 18px;">💬 Appeler {user_name} via WhatsApp</h3>
                        <p style="margin: 15px 0; color: #075e54; font-weight: 500;">
                            <strong>Appelez GRATUITEMENT via WhatsApp :</strong> Cliquez pour ouvrir WhatsApp et appeler {user_name} directement
                        </p>
                        <div style="margin: 20px 0;">"""
            
            for contact_name, contact_info in whatsapp_links.items():
                html_body += f"""
                            <div style="margin: 10px 0; padding: 15px; background: white; border-radius: 8px; border: 1px solid #25d366;">
                                <div style="display: flex; align-items: center; flex-wrap: wrap;">
                                    <div style="flex: 1; min-width: 200px;">
                                        <p style="margin: 0; font-weight: bold; color: #075e54;">👤 {contact_info['name']}</p>
                                        <p style="margin: 5px 0 0 0; color: #666; font-size: 14px;">📞 {contact_info['phone']}</p>
                                    </div>
                                    <div style="flex-shrink: 0;">
                                        <a href="{contact_info['url']}" style="display: inline-block; background: #25d366; color: white; padding: 12px 20px; text-decoration: none; border-radius: 25px; font-weight: bold; margin: 5px;">
                                            � Appeler via WhatsApp
                                        </a>
                                    </div>
                                </div>
                            </div>"""
            
            html_body += f"""
                        </div>
                        <p style="margin: 15px 0 5px 0; color: #075e54; font-size: 13px; text-align: center;">
                            ⚡ Appel gratuit via WhatsApp - Le message sera pré-rempli pour démarrer la conversation
                        </p>
                    </div>"""
        
        html_body += f"""
                </div>
                
                <!-- Footer -->
                <div style="background: #343a40; color: #adb5bd; padding: 20px; text-align: center;">
                    <p style="margin: 0; font-size: 12px;">
                        📱 Alerte automatique Guardian - {current_time}<br>
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
            
            # Créer le message MIME (sans images)
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
                user_name="Test Guardian",
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