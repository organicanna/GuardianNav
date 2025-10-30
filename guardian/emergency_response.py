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
# from guardian.emergency_email_generator import EmergencyEmailGenerator  # Désactivé - utilise ses propres templates

class EmergencyResponse:
    """Système de réponse d'urgence avec notifications et escalade"""
    
    def __init__(self, config: Dict[str, Any], api_keys_config: Dict[str, Any] = None):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.config = config
        self.emergency_contacts = config.get('emergency_contacts', [])
        self.email_config = config.get('email', {})
        
        # Générateur d'emails visuels désactivé - utilise ses propres templates
        # self.email_generator = EmergencyEmailGenerator(api_keys_config)
        
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
    
    def send_visual_emergency_alert(self, 
                                  location: tuple, 
                                  emergency_type: str,
                                  urgency_level: str,
                                  situation_details: str,
                                  person_name: str = "Utilisateur GuardianNav",
                                  additional_info: Dict[str, Any] = None):
        """
        Envoie un email visuel d'urgence enrichi avec carte et géolocalisation
        
        Args:
            location: (latitude, longitude)
            emergency_type: Type d'urgence 
            urgency_level: Niveau d'urgence (critique, élevée, modérée)
            situation_details: Description de la situation
            person_name: Nom de la personne en urgence
            additional_info: Informations supplémentaires (chute, vitesse, etc.)
        """
        
        if not self.email_config.get('enabled', False):
            self.logger.info("Emails désactivés - Simulation d'envoi d'email visuel d'urgence")
            self._simulate_visual_email_alert(location, emergency_type, urgency_level)
            return
        
        try:
            # Utiliser un template simple au lieu du générateur complexe
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif;">
                <h2 style="color: #d32f2f;">🚨 ALERTE D'URGENCE</h2>
                <p><strong>Personne:</strong> {person_name}</p>
                <p><strong>Type:</strong> {emergency_type}</p>
                <p><strong>Niveau:</strong> {urgency_level.upper()}</p>
                <p><strong>Localisation:</strong> {location}</p>
                <p><strong>Détails:</strong> {situation_details}</p>
                {f"<p><strong>Info:</strong> {additional_info}</p>" if additional_info else ""}
                <p><a href="https://www.google.com/maps?q={location[0]},{location[1]}">Voir sur Google Maps</a></p>
            </body>
            </html>
            """
            
            # Préparer l'email
            subject = f"🚨 URGENCE {urgency_level.upper()} - {person_name} a besoin d'aide"
            
            # Envoyer à tous les contacts d'urgence
            for contact in self.emergency_contacts:
                self._send_html_email(
                    to_email=contact.get('email'),
                    to_name=contact.get('name', 'Contact d\'urgence'),
                    subject=subject,
                    html_content=html_content
                )
                
            self.logger.info(f"Emails visuels d'urgence envoyés à {len(self.emergency_contacts)} contacts")
            
        except Exception as e:
            self.logger.error(f"Erreur envoi email visuel d'urgence: {e}")
            # Fallback vers email texte simple
            self.send_location_to_contacts(location, f"{emergency_type}: {situation_details}")
    
    def _send_html_email(self, to_email: str, to_name: str, subject: str, html_content: str):
        """Envoie un email HTML formaté"""
        
        try:
            # Créer le message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email_config['from_email']
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Version HTML
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # Version texte de secours
            text_content = self._html_to_text_fallback(html_content)
            text_part = MIMEText(text_content, 'plain', 'utf-8')
            msg.attach(text_part)
            
            # Envoyer
            with smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port']) as server:
                server.starttls()
                server.login(self.email_config['from_email'], self.email_config['password'])
                server.send_message(msg)
            
            self.logger.info(f"Email HTML envoyé à {to_name} ({to_email})")
            
        except Exception as e:
            self.logger.error(f"Erreur envoi email HTML à {to_email}: {e}")
    
    def _html_to_text_fallback(self, html_content: str) -> str:
        """Convertit le HTML en texte simple pour fallback"""
        
        # Extraction simple des informations principales
        import re
        
        # Supprimer les balises HTML
        text = re.sub(r'<[^>]+>', '', html_content)
        
        # Nettoyer les espaces multiples
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _simulate_visual_email_alert(self, location: tuple, emergency_type: str, urgency_level: str):
        """Simule l'envoi d'un email visuel pour démonstration"""
        
        lat, lon = location
        maps_url = f"https://maps.google.com/?q={lat},{lon}"
        what3words = "simulation.exemple.mots"  # Simulé
        
        print(f"\n📧 SIMULATION - Email visuel d'urgence:")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"🚨 ALERTE URGENCE {urgency_level.upper()}")
        print(f"📋 Type: {emergency_type}")
        print(f"📍 Position: {lat:.6f}, {lon:.6f}")
        print(f"🎯 What3Words: {what3words}")
        print(f"🗺️  Carte: {maps_url}")
        print(f"📧 Envoyé à: {len(self.emergency_contacts)} contacts")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        # Afficher un aperçu de l'email pour chaque contact
        for i, contact in enumerate(self.emergency_contacts, 1):
            print(f"   {i}. {contact.get('name', 'Contact')} ({contact.get('email', 'email@example.com')})")
    
    def generate_preview_email(self) -> str:
        """Génère un aperçu d'email pour tests et prévisualisation"""
        
        # Générateur désactivé - retourner un message simple
        return "<html><body><h2>Test Email - EmergencyResponse</h2><p>Système opérationnel</p></body></html>"
    
    def send_fall_emergency_alert(self, location: tuple, fall_info: Dict[str, Any]):
        """Envoie une alerte spécialisée pour les chutes"""
        
        fall_type = fall_info.get('fall_type', 'chute_generale')
        severity = fall_info.get('severity', 'modérée')
        
        # Traduire le type de chute
        fall_types_fr = {
            'chute_velo': '🚴 Chute à vélo',
            'chute_haute_vitesse': '🏃 Chute à haute vitesse',
            'impact_brutal': '💥 Impact brutal',
            'chute_generale': '⚠️ Chute détectée'
        }
        
        emergency_type = fall_types_fr.get(fall_type, 'Chute détectée')
        
        # Déterminer le niveau d'urgence
        urgency_mapping = {
            'légère': 'modérée',
            'modérée': 'modérée', 
            'grave': 'élevée',
            'critique': 'critique'
        }
        
        urgency_level = urgency_mapping.get(severity, 'élevée')
        
        # Description de la situation
        situation = f"Chute détectée par les capteurs GuardianNav. "
        if fall_info.get('previous_speed'):
            situation += f"Vitesse avant chute: {fall_info['previous_speed']:.1f} km/h. "
        if fall_info.get('acceleration'):
            situation += f"Décélération: {fall_info['acceleration']:.1f} m/s². "
        situation += "La personne ne répond pas aux sollicitations."
        
        # Envoyer l'alerte visuelle
        self.send_visual_emergency_alert(
            location=location,
            emergency_type=emergency_type,
            urgency_level=urgency_level,
            situation_details=situation,
            additional_info=fall_info
        )