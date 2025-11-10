"""
Hybrid Voice Agent for Guardian
Intelligent fallback: Gemini 2.0 Audio (WiFi) → Vosk Local (Offline)

Architecture:
1. Détecte la connexion Internet
2. Si WiFi → Gemini 2.0 Audio (analyse vocale complète avec intonation)
3. Si HORS LIGNE → Vosk local (transcription texte uniquement)
4. Fallback automatique et transparent pour l'utilisateur
"""

import logging
import os
import json
import requests
import time
from typing import Dict, Any, Optional, Tuple
from pathlib import Path

# Vosk pour reconnaissance locale
try:
    import vosk
    import sounddevice as sd
    import numpy as np
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False

# Gemini pour analyse cloud
try:
    from google import genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


class HybridVoiceAgent:
    """
    Agent vocal hybride avec fallback automatique
    
    Mode ONLINE (WiFi):
        - Gemini 2.0 Audio API
        - Analyse complète: transcription + intonation + contexte émotionnel
        - Détection stress/panique dans la voix
        
    Mode OFFLINE (Sans WiFi):
        - Vosk local (modèle fr-0.22)
        - Transcription texte seulement
        - Analyse basée sur les mots-clés
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.config = config or {}
        
        # Configuration Gemini Audio
        gemini_config = self.config.get('google_cloud', {}).get('gemini', {})
        self.gemini_api_key = gemini_config.get('api_key')
        self.gemini_model = 'gemini-2.0-flash-exp'  # Modèle avec support audio
        
        # Configuration Vosk
        self.vosk_model_path = self._get_vosk_model_path()
        self.vosk_model = None
        self.vosk_recognizer = None
        
        # État actuel
        self.is_online = self._check_internet_connection()
        self.mode = "ONLINE" if self.is_online else "OFFLINE"
        
        # Initialisation
        self._initialize_engines()
        
        self.logger.info(f"🎤 Hybrid Voice Agent initialisé en mode {self.mode}")
        self.logger.info(f"   • Gemini 2.0 Audio: {'✅ Disponible' if self.gemini_api_key else '❌ Non configuré'}")
        self.logger.info(f"   • Vosk Local: {'✅ Disponible' if VOSK_AVAILABLE else '❌ Non installé'}")
    
    def _get_vosk_model_path(self) -> str:
        """Retourne le chemin vers le modèle Vosk"""
        current_dir = Path(__file__).parent.parent
        return str(current_dir / "models" / "vosk-model-small-fr-0.22")
    
    def _check_internet_connection(self, timeout=3) -> bool:
        """
        Vérifie si une connexion Internet est disponible
        Teste plusieurs endpoints pour fiabilité
        """
        test_urls = [
            "https://www.google.com",
            "https://generativelanguage.googleapis.com",
            "https://1.1.1.1",  # Cloudflare DNS
        ]
        
        for url in test_urls:
            try:
                response = requests.get(url, timeout=timeout)
                if response.status_code == 200:
                    return True
            except (requests.ConnectionError, requests.Timeout):
                continue
        
        return False
    
    def _initialize_engines(self):
        """Initialise les moteurs de reconnaissance disponibles"""
        
        # Initialiser Vosk (toujours, pour fallback)
        if VOSK_AVAILABLE:
            try:
                if os.path.exists(self.vosk_model_path):
                    self.vosk_model = vosk.Model(self.vosk_model_path)
                    self.vosk_recognizer = vosk.KaldiRecognizer(self.vosk_model, 16000)
                    self.logger.info("✅ Vosk initialisé (fallback offline prêt)")
                else:
                    self.logger.warning(f"⚠️ Modèle Vosk non trouvé: {self.vosk_model_path}")
            except Exception as e:
                self.logger.error(f"❌ Erreur initialisation Vosk: {e}")
        else:
            self.logger.warning("⚠️ Vosk non disponible (pip install vosk)")
    
    def analyze_audio(self, audio_data: bytes, sample_rate: int = 16000) -> Dict[str, Any]:
        """
        Analyse l'audio avec fallback intelligent
        
        Args:
            audio_data: Données audio brutes (bytes)
            sample_rate: Taux d'échantillonnage (défaut 16000 Hz)
            
        Returns:
            {
                "transcription": str,
                "emotion_detected": str,  # "calm", "stressed", "panic"
                "confidence": float,
                "method": str,  # "gemini_audio" ou "vosk_local"
                "online": bool
            }
        """
        
        # Vérifier la connexion en temps réel
        self.is_online = self._check_internet_connection(timeout=2)
        
        if self.is_online and self.gemini_api_key:
            # MODE ONLINE: Gemini 2.0 Audio
            return self._analyze_with_gemini_audio(audio_data, sample_rate)
        else:
            # MODE OFFLINE: Vosk local
            return self._analyze_with_vosk(audio_data, sample_rate)
    
    def _analyze_with_gemini_audio(self, audio_data: bytes, sample_rate: int) -> Dict[str, Any]:
        """
        Analyse vocale complète avec Gemini 2.0 Audio
        Détecte: transcription + intonation + émotion + stress
        """
        try:
            self.logger.info("🌐 Mode ONLINE: Utilisation de Gemini 2.0 Audio")
            
            # Configuration du client Gemini
            if not GENAI_AVAILABLE:
                raise ImportError("google-generativeai non installé")
            
            client = genai.Client(api_key=self.gemini_api_key)
            
            # Prompt pour analyse émotionnelle
            prompt = """Analyse cette situation d'urgence en fonction de la voix.
            
Détecte:
1. Transcription exacte des paroles
2. Émotion vocale (calme/stressé/panique)
3. Niveau d'urgence (1-10)
4. Indices sonores (voix tremblante, pleurs, cris, etc.)

Réponds en JSON:
{
    "transcription": "texte exact",
    "emotion": "calm|stressed|panic",
    "urgency_level": 5,
    "vocal_indicators": ["voix tremblante", "respiration rapide"],
    "confidence": 0.95
}"""
            
            # Appel API avec audio
            response = client.models.generate_content(
                model=self.gemini_model,
                contents=[
                    prompt,
                    {
                        "mime_type": "audio/wav",
                        "data": audio_data
                    }
                ]
            )
            
            # Parser la réponse
            result = json.loads(response.text)
            
            return {
                "transcription": result.get("transcription", ""),
                "emotion_detected": result.get("emotion", "calm"),
                "urgency_boost": self._calculate_urgency_boost(result.get("emotion")),
                "vocal_indicators": result.get("vocal_indicators", []),
                "confidence": result.get("confidence", 0.0),
                "method": "gemini_audio",
                "online": True
            }
            
        except Exception as e:
            self.logger.error(f"❌ Erreur Gemini Audio: {e}")
            self.logger.info("⚠️ Fallback vers Vosk local...")
            return self._analyze_with_vosk(audio_data, sample_rate)
    
    def _analyze_with_vosk(self, audio_data: bytes, sample_rate: int) -> Dict[str, Any]:
        """
        Analyse locale avec Vosk (transcription texte uniquement)
        Pas d'analyse d'intonation, mais détection par mots-clés
        """
        try:
            self.logger.info("📱 Mode OFFLINE: Utilisation de Vosk local")
            
            if not self.vosk_recognizer:
                raise Exception("Vosk non initialisé")
            
            # Reconnaissance vocale
            self.vosk_recognizer.AcceptWaveform(audio_data)
            result = json.loads(self.vosk_recognizer.Result())
            
            transcription = result.get('text', '').strip()
            
            # Détection d'urgence par mots-clés (sans intonation)
            emotion, urgency_boost = self._detect_emotion_from_text(transcription)
            
            return {
                "transcription": transcription,
                "emotion_detected": emotion,
                "urgency_boost": urgency_boost,
                "vocal_indicators": [],  # Non disponible en mode offline
                "confidence": result.get('confidence', 0.0),
                "method": "vosk_local",
                "online": False
            }
            
        except Exception as e:
            self.logger.error(f"❌ Erreur Vosk: {e}")
            return {
                "transcription": "",
                "emotion_detected": "unknown",
                "urgency_boost": 0,
                "confidence": 0.0,
                "method": "failed",
                "online": False,
                "error": str(e)
            }
    
    def _detect_emotion_from_text(self, text: str) -> Tuple[str, int]:
        """
        Détecte l'émotion à partir du texte (fallback sans analyse vocale)
        
        Returns:
            (emotion, urgency_boost)
            - emotion: "calm", "stressed", "panic"
            - urgency_boost: +0, +2, +3 points d'urgence
        """
        text_lower = text.lower()
        
        # Indicateurs de panique (urgency_boost = +3)
        panic_keywords = [
            'au secours', 'aidez-moi', 'vite', 'urgent',
            'je vais mourir', 'aide', 's\'il vous plaît',
            'je ne peux plus', 'ça fait très mal'
        ]
        
        # Indicateurs de stress (urgency_boost = +2)
        stress_keywords = [
            'suivie', 'suivie depuis', 'menacé', 'peur',
            'je ne sais pas', 'perdu', 'angoissé',
            'inquiet', 'mal', 'saigne'
        ]
        
        # Détection panique
        if any(keyword in text_lower for keyword in panic_keywords):
            return ("panic", 3)
        
        # Détection stress
        if any(keyword in text_lower for keyword in stress_keywords):
            return ("stressed", 2)
        
        # Calme par défaut
        return ("calm", 0)
    
    def _calculate_urgency_boost(self, emotion: str) -> int:
        """
        Calcule le bonus d'urgence en fonction de l'émotion vocale
        """
        emotion_boost = {
            "calm": 0,
            "stressed": 2,
            "panic": 3,
            "crying": 3,
            "screaming": 4
        }
        return emotion_boost.get(emotion, 0)
    
    def get_status(self) -> Dict[str, Any]:
        """Retourne l'état actuel du système"""
        return {
            "mode": self.mode,
            "online": self.is_online,
            "gemini_available": bool(self.gemini_api_key and GENAI_AVAILABLE),
            "vosk_available": bool(self.vosk_model),
            "current_method": "gemini_audio" if self.is_online else "vosk_local"
        }


# Fonction utilitaire pour intégration facile
def create_hybrid_voice_agent(config: Dict[str, Any] = None) -> HybridVoiceAgent:
    """Factory pour créer un agent vocal hybride"""
    return HybridVoiceAgent(config)
