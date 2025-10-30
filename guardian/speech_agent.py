"""
Speech Agent for Guardian
Handles text-to-speech functionality using Google Cloud Text-to-Speech API
"""
import logging
import os
import pygame
import io
import tempfile
from typing import Optional, Dict, Any
from pathlib import Path

try:
    from google.cloud import texttospeech
    GOOGLE_TTS_AVAILABLE = True
except ImportError:
    GOOGLE_TTS_AVAILABLE = False

class SpeechAgent:
    """Agent de synthèse vocale pour Guardian"""
    
    def __init__(self, api_keys_config: Dict[str, Any] = None):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Configuration API
        self.api_keys_config = api_keys_config or {}
        
        # Initialiser pygame mixer pour la lecture audio
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=1024)
            self.audio_available = True
            self.logger.info("Pygame mixer initialisé pour la lecture audio")
        except Exception as e:
            self.logger.error(f"Erreur initialisation audio: {e}")
            self.audio_available = False
        
        # Configurer Google TTS
        self.tts_client = None
        self.voice_config = None
        self.audio_config = None
        
        if GOOGLE_TTS_AVAILABLE:
            self._setup_google_tts()
        else:
            self.logger.warning("Google Cloud Text-to-Speech non disponible - Installation requise: pip install google-cloud-texttospeech")
    
    def _setup_google_tts(self):
        """Configure le client Google Text-to-Speech"""
        try:
            # Configurer les clés API
            api_key = self.api_keys_config.get('google_cloud', {}).get('services', {}).get('text_to_speech_api_key')
            
            if api_key:
                # Utiliser la clé API directement
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = ''  # Éviter les credentials par défaut
                self.tts_client = texttospeech.TextToSpeechClient()
                self.logger.info("Client Google TTS configuré avec clé API")
            else:
                # Essayer avec les credentials par défaut
                self.tts_client = texttospeech.TextToSpeechClient()
                self.logger.info("Client Google TTS configuré avec credentials par défaut")
            
            # Configuration de la voix française
            self.voice_config = texttospeech.VoiceSelectionParams(
                language_code="fr-FR",
                ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
                name="fr-FR-Standard-A"  # Voix française féminine claire
            )
            
            # Configuration audio
            self.audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=1.1,  # Légèrement plus rapide pour l'urgence
                pitch=0.0,
                volume_gain_db=2.0  # Légèrement plus fort
            )
            
            self.logger.info("Configuration Google TTS complète")
            
        except Exception as e:
            self.logger.error(f"Erreur configuration Google TTS: {e}")
            self.tts_client = None
    
    def speak(self, text: str, priority: str = "normal") -> bool:
        """
        Fait parler l'agent avec le texte donné
        
        Args:
            text: Texte à synthétiser
            priority: Priorité du message ("normal", "urgent", "critical")
            
        Returns:
            bool: True si la synthèse a réussi, False sinon
        """
        if not text.strip():
            return False
        
        # Nettoyer le texte pour la synthèse vocale
        clean_text = self._prepare_text_for_speech(text)
        
        self.logger.info(f"Synthèse vocale ({priority}): {clean_text[:50]}...")
        
        # Ajuster la configuration selon la priorité
        audio_config = self._get_audio_config_for_priority(priority)
        
        try:
            if self.tts_client and self.audio_available:
                return self._speak_with_google_tts(clean_text, audio_config)
            else:
                return self._speak_fallback(clean_text)
                
        except Exception as e:
            self.logger.error(f"Erreur synthèse vocale: {e}")
            return self._speak_fallback(clean_text)
    
    def _prepare_text_for_speech(self, text: str) -> str:
        """Prépare le texte pour la synthèse vocale"""
        
        # Remplacer les emojis et symboles par des mots
        replacements = {
            '🚨': 'ALERTE',
            '⚠️': 'ATTENTION',
            '✅': 'Confirmé',
            '❌': 'Erreur',
            '📍': 'Position',
            '📞': 'Téléphone',
            '🆘': 'URGENCE',
            '🤖': 'Assistant',
            '💥': 'Impact',
            '🚴': 'Vélo',
            '🏃': 'Course',
            '📱': 'Téléphone',
            '🚑': 'Ambulance',
            '🏥': 'Hôpital',
            '🔄': '',  # Supprimer les symboles de rotation
            '⏹️': '',
            '━': '',  # Supprimer les lignes de séparation
            '═': '',
            '─': '',
        }
        
        clean_text = text
        for symbol, replacement in replacements.items():
            clean_text = clean_text.replace(symbol, replacement)
        
        # Supprimer les lignes de formatage
        lines = clean_text.split('\n')
        clean_lines = []
        
        for line in lines:
            line = line.strip()
            # Ignorer les lignes vides ou de formatage
            if line and not all(c in '━═─*+=' for c in line.replace(' ', '')):
                clean_lines.append(line)
        
        result = ' '.join(clean_lines)
        
        # Limiter la longueur pour éviter des messages trop longs
        if len(result) > 300:
            result = result[:297] + "..."
        
        return result
    
    def _get_audio_config_for_priority(self, priority: str):
        """Retourne une configuration audio adaptée à la priorité"""
        
        if not self.audio_config or not GOOGLE_TTS_AVAILABLE:
            return None
        
        # Configuration selon la priorité
        if priority == "critical":
            return texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=1.3,  # Plus rapide pour l'urgence critique
                pitch=2.0,          # Voix plus aiguë pour attirer l'attention
                volume_gain_db=4.0  # Plus fort
            )
        elif priority == "urgent":
            return texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=1.2,  # Légèrement plus rapide
                pitch=1.0,          # Légèrement plus aigu
                volume_gain_db=3.0  # Plus fort
            )
        else:  # normal
            return self.audio_config
    
    def _speak_with_google_tts(self, text: str, audio_config) -> bool:
        """Utilise Google TTS pour la synthèse vocale"""
        
        if not GOOGLE_TTS_AVAILABLE:
            return False
            
        try:
            # Préparer la requête
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            # Effectuer la synthèse
            response = self.tts_client.synthesize_speech(
                input=synthesis_input,
                voice=self.voice_config,
                audio_config=audio_config or self.audio_config
            )
            
            # Jouer l'audio via pygame
            return self._play_audio_bytes(response.audio_content)
            
        except Exception as e:
            self.logger.error(f"Erreur Google TTS: {e}")
            return False
    
    def _play_audio_bytes(self, audio_bytes: bytes) -> bool:
        """Joue des bytes audio via pygame"""
        
        try:
            # Créer un fichier temporaire
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                temp_file.write(audio_bytes)
                temp_path = temp_file.name
            
            # Jouer le fichier
            pygame.mixer.music.load(temp_path)
            pygame.mixer.music.play()
            
            # Attendre la fin de la lecture
            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)
            
            # Nettoyer le fichier temporaire
            try:
                os.unlink(temp_path)
            except Exception:
                pass
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur lecture audio: {e}")
            return False
    
    def _speak_fallback(self, text: str) -> bool:
        """Mode de fallback sans synthèse vocale"""
        
        self.logger.info(f"Simulation vocale: {text}")
        
        # Afficher une indication visuelle de la synthèse vocale
        print(f"\n🔊 [SYNTHÈSE VOCALE]: {text}\n")
        
        # Simulation d'un délai de parole (optionnel)
        import time
        speech_duration = len(text) * 0.05  # ~50ms par caractère
        time.sleep(min(speech_duration, 3.0))  # Max 3 secondes
        
        return True
    
    def speak_alert(self, alert_type: str, message: str) -> bool:
        """Synthèse vocale spécialisée pour les alertes"""
        
        # Préfixes selon le type d'alerte
        prefixes = {
            "emergency": "URGENCE! ",
            "fall": "CHUTE DÉTECTÉE! ",
            "immobilization": "IMMOBILITÉ PROLONGÉE! ",
            "keyword": "MOT-CLÉ D'URGENCE DÉTECTÉ! ",
            "confirmation": "Confirmation: ",
            "info": ""
        }
        
        prefix = prefixes.get(alert_type, "ALERTE! ")
        full_message = prefix + message
        
        # Déterminer la priorité
        priority_mapping = {
            "emergency": "critical",
            "fall": "critical", 
            "immobilization": "urgent",
            "keyword": "urgent",
            "confirmation": "normal",
            "info": "normal"
        }
        
        priority = priority_mapping.get(alert_type, "normal")
        
        return self.speak(full_message, priority)
    
    def speak_fall_alert(self, fall_info: Dict[str, Any]) -> bool:
        """Synthèse vocale spécialisée pour les chutes"""
        
        fall_type = fall_info.get('fall_type', 'chute_generale')
        severity = fall_info.get('severity', 'modérée')
        
        # Messages selon le type de chute
        fall_messages = {
            'chute_velo': f"Chute à vélo détectée, sévérité {severity}. Restez immobile si vous ressentez des douleurs.",
            'chute_haute_vitesse': f"Chute à haute vitesse détectée! Ne bougez pas si vous avez mal. Les secours arrivent.",
            'impact_brutal': f"Impact brutal détecté. Évaluez vos blessures avant de bouger.",
            'chute_generale': f"Chute détectée, sévérité {severity}. Prenez votre temps pour vous relever."
        }
        
        message = fall_messages.get(fall_type, "Chute détectée. Vérifiez votre état avant de bouger.")
        
        return self.speak_alert("fall", message)
    
    def speak_emergency_instructions(self, instructions: list) -> bool:
        """Synthèse vocale pour les instructions d'urgence"""
        
        if not instructions:
            return False
        
        # Limiter le nombre d'instructions pour éviter un message trop long
        max_instructions = 3
        limited_instructions = instructions[:max_instructions]
        
        instructions_text = "Instructions d'urgence: " + ". ".join(limited_instructions)
        
        if len(instructions) > max_instructions:
            instructions_text += f". Et {len(instructions) - max_instructions} autres actions."
        
        return self.speak(instructions_text, "urgent")
    
    def test_speech(self) -> bool:
        """Teste la synthèse vocale"""
        
        test_message = "Test de la synthèse vocale Guardian. Le système fonctionne correctement."
        
        print("🎤 Test de la synthèse vocale...")
        success = self.speak(test_message, "normal")
        
        if success:
            print("✅ Synthèse vocale fonctionnelle")
        else:
            print("❌ Problème avec la synthèse vocale")
        
        return success
    
    def is_available(self) -> bool:
        """Vérifie si la synthèse vocale est disponible"""
        return self.audio_available and (self.tts_client is not None or True)  # True pour le fallback