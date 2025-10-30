"""
SMS Agent for Guardian
Handles emergency SMS notifications via Twilio
"""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

try:
    from twilio.rest import Client
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False

class SMSAgent:
    """Agent SMS pour l'envoi de notifications d'urgence via Twilio"""
    
    def __init__(self, api_keys_config: Dict[str, Any] = None):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Configuration API
        self.api_keys_config = api_keys_config or {}
        self.twilio_config = self.api_keys_config.get('notification_services', {}).get('twilio', {})
        
        # Client Twilio
        self.twilio_client = None
        self.is_available = False
        
        if TWILIO_AVAILABLE:
            self._setup_twilio()
        else:
            self.logger.warning("Twilio non installé - SMS en mode simulation")
    
    def _setup_twilio(self):
        """Configure le client Twilio"""
        try:
            account_sid = self.twilio_config.get('account_sid')
            auth_token = self.twilio_config.get('auth_token')
            self.twilio_phone = self.twilio_config.get('phone_number')
            
            if not account_sid or account_sid.startswith('YOUR_'):
                self.logger.info("Twilio non configuré - SMS en mode simulation")
                return
                
            if not auth_token or auth_token.startswith('YOUR_'):
                self.logger.info("Twilio auth_token non configuré - SMS en mode simulation")
                return
                
            if not self.twilio_phone or self.twilio_phone.startswith('YOUR_'):
                self.logger.info("Numéro Twilio non configuré - SMS en mode simulation")
                return
            
            # Créer le client Twilio
            self.twilio_client = Client(account_sid, auth_token)
            self.is_available = True
            self.logger.info("Twilio SMS configuré et disponible")
            
        except Exception as e:
            self.logger.error(f"Erreur configuration Twilio: {e}")
            self.is_available = False
    
    def send_emergency_sms(self, contacts: List[Dict], emergency_context: Dict) -> bool:
        """
        Envoie un SMS d'urgence à la liste de contacts
        
        Args:
            contacts: Liste des contacts d'urgence
            emergency_context: Contexte de l'urgence (localisation, type, etc.)
        
        Returns:
            bool: True si au moins un SMS envoyé avec succès
        """
        if not contacts:
            self.logger.warning("Aucun contact pour envoi SMS")
            return False
        
        # Générer le message SMS
        sms_message = self._generate_emergency_sms_message(emergency_context)
        
        success_count = 0
        for contact in contacts:
            if self._send_sms_to_contact(contact, sms_message):
                success_count += 1
        
        return success_count > 0
    
    def _send_sms_to_contact(self, contact: Dict, message: str) -> bool:
        """Envoie un SMS à un contact spécifique"""
        phone = contact.get('phone')
        name = contact.get('name', 'Contact')
        
        if not phone:
            self.logger.warning(f"Pas de numéro pour {name}")
            return False
        
        try:
            if self.is_available and self.twilio_client:
                # Envoi réel via Twilio
                message_obj = self.twilio_client.messages.create(
                    body=message,
                    from_=self.twilio_phone,
                    to=phone
                )
                self.logger.critical(f"🚨 SMS URGENCE envoyé à {name} ({phone}): {message_obj.sid}")
                return True
            else:
                # Mode simulation
                self.logger.info(f"📱 [SIMULATION] SMS à {name} ({phone}):")
                self.logger.info(f"   Message: {message[:100]}...")
                return True
                
        except Exception as e:
            self.logger.error(f"Erreur envoi SMS à {name}: {e}")
            return False
    
    def _generate_emergency_sms_message(self, emergency_context: Dict) -> str:
        """Génère le message SMS d'urgence"""
        
        # Informations de base
        user_name = emergency_context.get('user_name', 'Votre proche')
        emergency_type = emergency_context.get('emergency_type', 'Urgence')
        location = emergency_context.get('location', {})
        timestamp = datetime.now().strftime("%H:%M le %d/%m")
        
        # Construire l'adresse
        address = location.get('address', 'Position inconnue')
        what3words = location.get('what3words', '')
        
        # Message SMS optimisé (160 caractères max pour éviter les frais)
        if what3words:
            message = f"🚨 URGENCE Guardian\\n{user_name} - {emergency_type}\\n📍 {address}\\n🎯 {what3words}\\n🕐 {timestamp}"
        else:
            message = f"🚨 URGENCE Guardian\\n{user_name} - {emergency_type}\\n📍 {address}\\n🕐 {timestamp}"
        
        # Ajouter numéros d'urgence si la place le permet
        if len(message) < 120:
            message += "\\n🚨 Police: 17, SAMU: 15"
        
        return message
    
    def send_confirmation_sms(self, contacts: List[Dict], message: str = None) -> bool:
        """Envoie un SMS de confirmation/mise à jour"""
        if not contacts:
            return False
        
        if not message:
            message = f"✅ Guardian: Situation résolue à {datetime.now().strftime('%H:%M')}. Merci pour votre attention."
        
        success_count = 0
        for contact in contacts:
            if self._send_sms_to_contact(contact, message):
                success_count += 1
        
        return success_count > 0
    
    def test_sms_connection(self) -> Dict[str, Any]:
        """Test la connexion Twilio et retourne le statut"""
        test_result = {
            'twilio_available': TWILIO_AVAILABLE,
            'configured': self.is_available,
            'phone_number': self.twilio_phone if self.is_available else None,
            'test_success': False,
            'error': None
        }
        
        if not self.is_available:
            test_result['error'] = "Twilio non configuré"
            return test_result
        
        try:
            # Test simple de connexion (sans envoi)
            account = self.twilio_client.api.accounts(self.twilio_config.get('account_sid')).fetch()
            test_result['test_success'] = True
            test_result['account_name'] = account.friendly_name
            self.logger.info("Test connexion Twilio réussi")
            
        except Exception as e:
            test_result['error'] = str(e)
            self.logger.error(f"Test Twilio échoué: {e}")
        
        return test_result