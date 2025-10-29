#!/usr/bin/env python3
"""
Agent de Conversation Vocale pour GuardianNav
🎤 Reconnaissance vocale (Speech-to-Text) + 🔊 Synthèse vocale (Text-to-Speech) + 🧠 Vertex AI
Permet de parler avec GuardianNav et recevoir des réponses intelligentes de Vertex AI
"""

import logging
import threading
import time
import queue
import json
from typing import Dict, Any, Optional, Callable
import sounddevice as sd

try:
    import vosk
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False

try:
    from google.cloud import speech
    GOOGLE_STT_AVAILABLE = True
except ImportError:
    GOOGLE_STT_AVAILABLE = False

# Imports conditionnels pour éviter les erreurs
try:
    from .speech_agent import SpeechAgent
    from .gemini_agent import VertexAIAgent
    GUARDIAN_MODULES_AVAILABLE = True
except ImportError:
    try:
        # Import direct si les modules relatifs échouent
        import sys
        import os
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent))
        
        from speech_agent import SpeechAgent
        from gemini_agent import VertexAIAgent
        GUARDIAN_MODULES_AVAILABLE = True
    except ImportError:
        GUARDIAN_MODULES_AVAILABLE = False
        print("⚠️ Modules GuardianNav non disponibles - Mode simulation")

class VoiceConversationAgent:
    """Agent de conversation vocale complète pour GuardianNav"""
    
    def __init__(self, api_keys_config: Dict[str, Any] = None, vosk_model_path: str = None):
        """
        Initialise l'agent de conversation vocale
        
        Args:
            api_keys_config: Configuration des clés API Google
            vosk_model_path: Chemin vers le modèle Vosk pour reconnaissance vocale offline
        """
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Configuration
        self.api_keys_config = api_keys_config or {}
        self.vosk_model_path = vosk_model_path or "vosk-model-small-fr-0.22"
        
        # États de conversation
        self.is_listening = False
        self.is_speaking = False
        self.conversation_active = False
        self.audio_queue = queue.Queue()
        
        # Configuration audio
        self.samplerate = 16000
        self.blocksize = 8000
        
        # Initialiser les agents
        self._setup_speech_agents()
        self._setup_recognition_engine()
        
        # Callbacks personnalisables
        self.on_speech_recognized: Optional[Callable[[str], None]] = None
        self.on_ai_response: Optional[Callable[[str], None]] = None
        
    def _setup_speech_agents(self):
        """Initialise les agents de synthèse vocale et IA"""
        try:
            # Agent de synthèse vocale (Text-to-Speech)
            self.speech_agent = SpeechAgent(self.api_keys_config)
            self.logger.info("✅ Agent de synthèse vocale initialisé")
            
            # Agent Vertex AI pour les réponses intelligentes
            self.vertex_ai_agent = VertexAIAgent(self.api_keys_config)
            self.logger.info("✅ Agent Vertex AI initialisé")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur lors de l'initialisation des agents: {e}")
            
    def _setup_recognition_engine(self):
        """Configure le moteur de reconnaissance vocale"""
        self.recognition_engine = None
        self.recognition_type = "simulation"
        
        # Essayer Google Cloud Speech-to-Text d'abord
        if self._setup_google_stt():
            self.recognition_type = "google_stt"
            self.logger.info("🌐 Reconnaissance vocale: Google Cloud Speech-to-Text")
            
        # Fallback vers Vosk (offline)
        elif self._setup_vosk():
            self.recognition_type = "vosk"
            self.logger.info("🖥️ Reconnaissance vocale: Vosk (offline)")
            
        else:
            self.logger.warning("⚠️ Reconnaissance vocale en mode simulation")
            
    def _setup_google_stt(self) -> bool:
        """Configure Google Cloud Speech-to-Text"""
        try:
            if not GOOGLE_STT_AVAILABLE:
                return False
                
            # Vérifier les clés API
            stt_config = self.api_keys_config.get('google_cloud', {}).get('services', {})
            if not stt_config.get('speech_to_text_api_key'):
                return False
                
            self.stt_client = speech.SpeechClient()
            self.stt_config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=self.samplerate,
                language_code="fr-FR",
                enable_automatic_punctuation=True,
                model="latest_long"
            )
            
            self.logger.info("✅ Google Cloud Speech-to-Text configuré")
            return True
            
        except Exception as e:
            self.logger.debug(f"Google STT non disponible: {e}")
            return False
            
    def _setup_vosk(self) -> bool:
        """Configure Vosk pour reconnaissance offline"""
        try:
            if not VOSK_AVAILABLE:
                return False
                
            import os
            if not os.path.exists(self.vosk_model_path):
                return False
                
            self.vosk_model = vosk.Model(self.vosk_model_path)
            self.vosk_recognizer = vosk.KaldiRecognizer(self.vosk_model, self.samplerate)
            
            self.logger.info("✅ Vosk (offline) configuré")
            return True
            
        except Exception as e:
            self.logger.debug(f"Vosk non disponible: {e}")
            return False
    
    def start_conversation(self, greeting_message: str = None):
        """
        Démarre une session de conversation vocale
        
        Args:
            greeting_message: Message d'accueil à prononcer
        """
        if self.conversation_active:
            self.logger.warning("Conversation déjà active")
            return
            
        self.conversation_active = True
        
        # Message d'accueil
        if not greeting_message:
            greeting_message = (
                "Bonjour ! GuardianNav est à votre écoute. "
                "Vous pouvez me parler de votre situation, "
                "je vais analyser et vous proposer des conseils adaptés. "
                "Dites 'stop' pour arrêter la conversation."
            )
            
        self.logger.info("🎙️ Démarrage de la conversation vocale")
        self.speak_message(greeting_message)
        
        # Démarrer l'écoute en arrière-plan
        self.listening_thread = threading.Thread(target=self._listen_continuously, daemon=True)
        self.listening_thread.start()
        
    def stop_conversation(self):
        """Arrête la session de conversation"""
        if not self.conversation_active:
            return
            
        self.conversation_active = False
        self.is_listening = False
        
        farewell_message = "Au revoir ! GuardianNav reste disponible si vous avez besoin d'aide."
        self.speak_message(farewell_message)
        
        self.logger.info("🛑 Conversation vocale arrêtée")
        
    def speak_message(self, message: str, priority: str = "normal"):
        """
        Fait parler GuardianNav
        
        Args:
            message: Message à prononcer
            priority: Priorité du message (normal, urgent, info)
        """
        if self.is_speaking:
            self.logger.debug("Synthèse vocale déjà en cours, message mis en file")
            
        self.is_speaking = True
        
        try:
            # Arrêter l'écoute pendant que GuardianNav parle
            was_listening = self.is_listening
            self.is_listening = False
            
            # Synthèse vocale
            success = self.speech_agent.speak(message, priority)
            
            if success:
                self.logger.info(f"🔊 GuardianNav: {message[:100]}...")
                if self.on_ai_response:
                    self.on_ai_response(message)
            else:
                self.logger.error("❌ Erreur lors de la synthèse vocale")
                
            # Reprendre l'écoute après la synthèse
            if was_listening and self.conversation_active:
                time.sleep(0.5)  # Petite pause
                self.is_listening = True
                
        finally:
            self.is_speaking = False
            
    def _listen_continuously(self):
        """Écoute continue en arrière-plan"""
        self.logger.info("👂 Début de l'écoute continue...")
        
        try:
            with sd.RawInputStream(
                samplerate=self.samplerate, 
                blocksize=self.blocksize, 
                dtype='int16',
                channels=1, 
                callback=self._audio_callback
            ):
                while self.conversation_active:
                    if self.is_listening and not self.is_speaking:
                        recognized_text = self._process_audio_queue()
                        
                        if recognized_text:
                            self._handle_recognized_speech(recognized_text)
                            
                    time.sleep(0.1)  # Éviter une boucle trop intensive
                    
        except Exception as e:
            self.logger.error(f"❌ Erreur dans l'écoute continue: {e}")
            
    def _audio_callback(self, indata, frames, time, status):
        """Callback pour capturer l'audio"""
        if self.is_listening and not self.is_speaking:
            self.audio_queue.put(bytes(indata))
            
    def _process_audio_queue(self) -> Optional[str]:
        """Traite la file audio pour reconnaissance vocale"""
        try:
            # Collecter suffisamment de données audio
            audio_data = b""
            timeout_counter = 0
            
            while timeout_counter < 50:  # ~5 secondes de timeout
                try:
                    chunk = self.audio_queue.get(timeout=0.1)
                    audio_data += chunk
                    
                    # Si on a assez de données, essayer la reconnaissance
                    if len(audio_data) >= self.blocksize * 5:  # ~0.5 secondes d'audio
                        text = self._recognize_speech(audio_data)
                        if text and text.strip():
                            return text.strip()
                            
                except queue.Empty:
                    timeout_counter += 1
                    
            return None
            
        except Exception as e:
            self.logger.error(f"Erreur traitement audio: {e}")
            return None
            
    def _recognize_speech(self, audio_data: bytes) -> Optional[str]:
        """
        Reconnaissance vocale selon le moteur disponible
        
        Args:
            audio_data: Données audio à traiter
            
        Returns:
            Texte reconnu ou None
        """
        try:
            if self.recognition_type == "google_stt":
                return self._recognize_with_google_stt(audio_data)
            elif self.recognition_type == "vosk":
                return self._recognize_with_vosk(audio_data)
            else:
                # Mode simulation
                return self._simulate_recognition()
                
        except Exception as e:
            self.logger.error(f"Erreur reconnaissance vocale: {e}")
            return None
            
    def _recognize_with_google_stt(self, audio_data: bytes) -> Optional[str]:
        """Reconnaissance avec Google Cloud Speech-to-Text"""
        try:
            audio = speech.RecognitionAudio(content=audio_data)
            response = self.stt_client.recognize(config=self.stt_config, audio=audio)
            
            if response.results:
                return response.results[0].alternatives[0].transcript
                
        except Exception as e:
            self.logger.error(f"Erreur Google STT: {e}")
            
        return None
        
    def _recognize_with_vosk(self, audio_data: bytes) -> Optional[str]:
        """Reconnaissance avec Vosk"""
        try:
            if self.vosk_recognizer.AcceptWaveform(audio_data):
                result = self.vosk_recognizer.Result()
                result_dict = json.loads(result)
                return result_dict.get("text", "")
                
        except Exception as e:
            self.logger.error(f"Erreur Vosk: {e}")
            
        return None
        
    def _simulate_recognition(self) -> Optional[str]:
        """Simulation de reconnaissance vocale pour les tests"""
        # En mode simulation, on peut demander à l'utilisateur de taper
        import sys
        if hasattr(sys.stdin, 'isatty') and sys.stdin.isatty():
            try:
                print("\n🎤 [Simulation] Tapez votre message (ou 'stop' pour arrêter):")
                text = input("> ").strip()
                return text if text else None
            except (EOFError, KeyboardInterrupt):
                return "stop"
        return None
        
    def _handle_recognized_speech(self, text: str):
        """
        Traite le texte reconnu et génère une réponse IA
        
        Args:
            text: Texte reconnu par la reconnaissance vocale
        """
        self.logger.info(f"👤 Utilisateur: {text}")
        
        if self.on_speech_recognized:
            self.on_speech_recognized(text)
            
        # Vérifier les commandes d'arrêt
        stop_words = ["stop", "arrêt", "arrête", "terminer", "fini", "au revoir"]
        if any(word in text.lower() for word in stop_words):
            self.stop_conversation()
            return
            
        # Obtenir une réponse de Vertex AI
        self._generate_ai_response(text)
        
    def _generate_ai_response(self, user_input: str):
        """
        Génère une réponse intelligente avec Vertex AI
        
        Args:
            user_input: Message de l'utilisateur
        """
        try:
            # Contexte pour Vertex AI
            context = f"L'utilisateur dit: '{user_input}'"
            
            if self.vertex_ai_agent.is_available:
                # Utiliser Vertex AI pour une réponse intelligente
                analysis = self.vertex_ai_agent.analyze_emergency_situation(
                    context,
                    user_input=user_input,
                    location=(48.8566, 2.3522)  # Position par défaut Paris
                )
                
                # Extraire la réponse personnalisée
                if analysis and 'specific_advice' in analysis:
                    response = analysis['specific_advice']
                    
                    # Ajouter des informations sur l'urgence si nécessaire
                    urgency = analysis.get('urgency_level', 0)
                    if urgency > 7:
                        response = f"⚠️ URGENT: {response}"
                    elif urgency > 4:
                        response = f"⚠️ Attention: {response}"
                        
                else:
                    response = self._generate_fallback_response(user_input)
            else:
                # Réponse de secours sans IA
                response = self._generate_fallback_response(user_input)
                
            # Répondre vocalement
            self.speak_message(response, "urgent" if "URGENT" in response else "normal")
            
        except Exception as e:
            self.logger.error(f"Erreur génération réponse IA: {e}")
            error_response = "Désolé, j'ai des difficultés à analyser votre situation. Pouvez-vous répéter ou être plus précis ?"
            self.speak_message(error_response)
            
    def _generate_fallback_response(self, user_input: str) -> str:
        """
        Génère une réponse de secours sans IA
        
        Args:
            user_input: Message de l'utilisateur
            
        Returns:
            Réponse appropriée
        """
        user_input_lower = user_input.lower()
        
        # Détection de mots-clés d'urgence
        emergency_keywords = {
            'urgence': "Je comprends que c'est urgent. Pouvez-vous me décrire précisément votre situation ?",
            'aide': "Je suis là pour vous aider. Expliquez-moi ce qui se passe.",
            'secours': "Si c'est une urgence vitale, appelez le 15 immédiatement. Sinon, décrivez votre situation.",
            'perdu': "Si vous êtes perdu, essayez d'identifier des repères autour de vous et partagez votre localisation.",
            'mal': "Si vous ressentez une douleur, évaluez son intensité de 1 à 10 et décrivez où ça fait mal.",
            'peur': "Je comprends votre inquiétude. Respirez profondément et décrivez ce qui vous fait peur.",
            'danger': "⚠️ Si vous êtes en danger immédiat, contactez les secours au 112. Sinon, expliquez la situation.",
        }
        
        # Chercher des mots-clés
        for keyword, response in emergency_keywords.items():
            if keyword in user_input_lower:
                return response
                
        # Réponse générique
        return (
            "J'ai bien entendu votre message. Pour mieux vous aider, "
            "pouvez-vous me donner plus de détails sur votre situation ? "
            "Où êtes-vous et que se passe-t-il exactement ?"
        )
        
    def is_available(self) -> bool:
        """Vérifie si l'agent de conversation est disponible"""
        return (
            hasattr(self, 'speech_agent') and 
            self.speech_agent.is_available() and
            self.recognition_type != "simulation"
        )
        
    def get_status_info(self) -> Dict[str, Any]:
        """Retourne les informations sur l'état de l'agent"""
        return {
            'conversation_active': self.conversation_active,
            'is_listening': self.is_listening,
            'is_speaking': self.is_speaking,
            'recognition_engine': self.recognition_type,
            'speech_available': hasattr(self, 'speech_agent') and self.speech_agent.is_available(),
            'vertex_ai_available': hasattr(self, 'vertex_ai_agent') and self.vertex_ai_agent.is_available,
        }

def main():
    """Test de l'agent de conversation vocale"""
    print("🎙️ TEST DE L'AGENT DE CONVERSATION VOCALE")
    print("=" * 50)
    
    # Configuration de test
    import yaml
    try:
        with open('api_keys.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except:
        config = {}
        
    # Initialiser l'agent
    voice_agent = VoiceConversationAgent(config)
    
    # Afficher le statut
    status = voice_agent.get_status_info()
    print(f"🔊 Synthèse vocale: {'✅' if status['speech_available'] else '❌'}")
    print(f"🎤 Reconnaissance: {status['recognition_engine']}")
    print(f"🧠 Vertex AI: {'✅' if status['vertex_ai_available'] else '❌'}")
    
    # Callbacks de test
    def on_speech(text):
        print(f"👤 Reconnu: {text}")
        
    def on_response(text):
        print(f"🤖 Réponse: {text[:100]}...")
        
    voice_agent.on_speech_recognized = on_speech
    voice_agent.on_ai_response = on_response
    
    try:
        print("\n🚀 Démarrage de la conversation...")
        voice_agent.start_conversation()
        
        # Maintenir la conversation active
        print("💬 Conversation active - Parlez ou tapez 'stop' pour arrêter")
        while voice_agent.conversation_active:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n👋 Arrêt de la conversation...")
        voice_agent.stop_conversation()

if __name__ == "__main__":
    main()