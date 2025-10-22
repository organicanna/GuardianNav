"""
Emergency Response System for GuardianNav
Handles contact notifications and emergency escalation
"""
import smtplib
import logging
import time
from typing import List, Dict, Any
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmergencyResponse:
    """Système de réponse d'urgence avec notifications et escalade"""
    
    def __init__(self, config: Dict[str, Any]):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.config = config
        self.emergency_contacts = config.get('emergency_contacts', [])
        self.email_config = config.get('email', {})
        
    def send_immediate_danger_alert(self, location: tuple, situation: str = ""):
        """Envoie une alerte de danger immédiat aux contacts proches"""
        self.logger.critical(f"ALERTE DANGER IMMÉDIAT: {location}")
        
        lat, lon = location
        maps_url = f"https://maps.google.com/?q={lat},{lon}"
        
        # Message d'urgence critique
        urgent_message = f"""
🚨 ALERTE URGENCE CRITIQUE - GUARDIANNAV 🚨

VOTRE CONTACT EST EN DANGER IMMÉDIAT !

📍 Position: {lat}, {lon}
🗺️ Carte: {maps_url}
⚠️ Situation: {situation}
🕐 Heure: {time.strftime('%Y-%m-%d %H:%M:%S')}

⚡ ACTIONS IMMÉDIATES REQUISES:
1. Appelez cette personne MAINTENANT
2. Si pas de réponse, appelez le 17 (Police)
3. Rendez-vous sur place si possible
4. Partagez cette alerte avec d'autres proches

Cette alerte a été déclenchée automatiquement par le système de sécurité.
"""
        
        # Envoyer à tous les contacts avec priorité haute
        for contact in self.emergency_contacts:
            self._send_urgent_email(contact, "🚨 DANGER IMMÉDIAT - ASSISTANCE REQUISE", urgent_message)
            self._send_urgent_sms(contact, location, situation)
        
        self.logger.info("Alertes de danger immédiat envoyées à tous les contacts")

    def send_location_to_contacts(self, location: tuple, situation: str = ""):
        """Envoie la localisation aux contacts d'urgence"""
        self.logger.info(f"Envoi de localisation d'urgence: {location}")
        
        lat, lon = location
        maps_url = f"https://maps.google.com/?q={lat},{lon}"
        
        message = f"""
ALERTE GUARDIANNAV - ASSISTANCE REQUISE

Localisation: {lat}, {lon}
Lien Google Maps: {maps_url}
Situation: {situation}
Heure: {time.strftime('%Y-%m-%d %H:%M:%S')}

Cette personne pourrait avoir besoin d'aide.
Merci de vérifier sa situation.
"""
        
        for contact in self.emergency_contacts:
            self._send_email(contact, "ALERTE GUARDIANNAV", message)
            self._send_sms_notification(contact, location)
            
    def send_location_with_refuges_info(self, location: tuple, refuges_info: str, situation: str = ""):
        """Envoie la localisation avec informations sur les refuges et transports"""
        self.logger.info(f"Envoi localisation avec refuges: {location}")
        
        lat, lon = location
        maps_url = f"https://maps.google.com/?q={lat},{lon}"
        
        enhanced_message = f"""
🚨 ALERTE GUARDIANNAV - ASSISTANCE AVEC REFUGES 🚨

📍 LOCALISATION: {lat}, {lon}
🗺️ Lien Google Maps: {maps_url}
⚠️ Situation: {situation}
🕐 Heure: {time.strftime('%Y-%m-%d %H:%M:%S')}

{refuges_info}

💡 CONSEILS POUR AIDER:
1. Appelez cette personne pour vérifier sa situation
2. Guidez-la vers le refuge le plus proche si nécessaire
3. Restez en contact jusqu'à ce qu'elle soit en sécurité
4. Appelez les services d'urgence si pas de nouvelles

Cette alerte contient des informations de sécurité actualisées.
"""
        
        for contact in self.emergency_contacts:
            self._send_email(contact, "🚨 ALERTE AVEC REFUGES - GUARDIANNAV", enhanced_message)
            self._send_sms_notification(contact, location)
    
    def send_confirmation_alert(self, alert_state: str):
        """Envoie une notification de confirmation d'état"""
        self.logger.info(f"Envoi de notification de confirmation: {alert_state}")
        
        message = f"""
NOTIFICATION GUARDIANNAV

État: {alert_state}
Heure: {time.strftime('%Y-%m-%d %H:%M:%S')}

Tout semble normal.
"""
        
        # Envoi optionnel aux contacts selon la configuration
        if self.config.get('notify_on_confirmation', False):
            for contact in self.emergency_contacts:
                self._send_email(contact, "GuardianNav - Confirmation", message)
    
    def _send_email(self, contact: Dict[str, str], subject: str, message: str):
        """Envoie un email à un contact"""
        try:
            if not self.email_config.get('enabled', False):
                self.logger.debug("Email désactivé dans la configuration")
                return
                
            msg = MIMEMultipart()
            msg['From'] = self.email_config['from_email']
            msg['To'] = contact['email']
            msg['Subject'] = subject
            
            msg.attach(MIMEText(message, 'plain'))
            
            # Configuration SMTP (à adapter selon votre fournisseur)
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['from_email'], self.email_config['password'])
            
            text = msg.as_string()
            server.sendmail(self.email_config['from_email'], contact['email'], text)
            server.quit()
            
            self.logger.info(f"Email envoyé à {contact['email']}")
            
        except Exception as e:
            self.logger.error(f"Erreur envoi email à {contact.get('email', 'inconnu')}: {e}")
    
    def _send_urgent_email(self, contact: Dict[str, str], subject: str, message: str):
        """Envoie un email urgent avec priorité haute"""
        try:
            if not self.email_config.get('enabled', False):
                self.logger.debug("Email urgent désactivé dans la configuration")
                return
                
            msg = MIMEMultipart()
            msg['From'] = self.email_config['from_email']
            msg['To'] = contact['email']
            msg['Subject'] = subject
            msg['X-Priority'] = '1'  # Priorité haute
            msg['X-MSMail-Priority'] = 'High'
            msg['Importance'] = 'High'
            
            msg.attach(MIMEText(message, 'plain'))
            
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['from_email'], self.email_config['password'])
            
            text = msg.as_string()
            server.sendmail(self.email_config['from_email'], contact['email'], text)
            server.quit()
            
            self.logger.critical(f"EMAIL URGENT envoyé à {contact['email']}")
            
        except Exception as e:
            self.logger.error(f"Erreur envoi email urgent à {contact.get('email', 'inconnu')}: {e}")

    def _send_urgent_sms(self, contact: Dict[str, str], location: tuple, situation: str):
        """Envoie un SMS d'urgence (avec Twilio ou simulation)"""
        lat, lon = location
        
        # Message SMS court mais informatif
        sms_message = f"🚨 ALERTE GUARDIANNAV 🚨\nVotre contact est en danger!\nPosition: {lat:.4f},{lon:.4f}\nSituation: {situation[:50]}...\nAppelez immédiatement!"
        
        self.logger.critical(f"SMS URGENT simulé à {contact.get('phone', 'inconnu')}: {sms_message}")
        
        # Intégration Twilio (à décommenter si vous avez un compte)
        """
        try:
            from twilio.rest import Client
            
            account_sid = self.config.get('twilio', {}).get('account_sid')
            auth_token = self.config.get('twilio', {}).get('auth_token')
            twilio_number = self.config.get('twilio', {}).get('phone_number')
            
            if account_sid and auth_token:
                client = Client(account_sid, auth_token)
                
                message = client.messages.create(
                    body=sms_message,
                    from_=twilio_number,
                    to=contact.get('phone')
                )
                
                self.logger.critical(f"SMS URGENT Twilio envoyé à {contact['phone']}: {message.sid}")
        except ImportError:
            self.logger.warning("Twilio non installé, SMS en mode simulation")
        except Exception as e:
            self.logger.error(f"Erreur SMS Twilio: {e}")
        """

    def _send_sms_notification(self, contact: Dict[str, str], location: tuple):
        """Envoie une notification SMS (simulation pour l'instant)"""
        self.logger.info(f"SMS simulé envoyé à {contact.get('phone', 'inconnu')}")
        # Ici, vous pourriez intégrer un service SMS comme Twilio
        
    def escalate_emergency(self, location: tuple, no_response_duration: int):
        """Escalade l'urgence après absence de réponse"""
        self.logger.warning(f"Escalade d'urgence après {no_response_duration}s sans réponse")
        
        # Simulation d'appel aux services d'urgence
        self.logger.critical("SIMULATION: Appel automatique aux services d'urgence")
        
        # Notification intensive aux contacts
        self.send_location_to_contacts(
            location, 
            f"URGENCE - Aucune réponse depuis {no_response_duration} secondes"
        )