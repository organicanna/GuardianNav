import vosk
import sounddevice as sd
import queue
import json
import logging
from typing import List, Optional

class VoiceAgent:
    def __init__(self, keywords: List[str] = None, model_path: str = None, samplerate: int = 16000):
        """
        Initialise l'agent vocal
        
        Args:
            keywords: Liste des mots clés à détecter
            model_path: Chemin vers le modèle Vosk
            samplerate: Fréquence d'échantillonnage audio
        """
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        if keywords is None:
            keywords = ["aide", "stop", "urgence", "secours"]
        self.keywords = [k.lower() for k in keywords]
        self.logger.info(f"Mots clés configurés: {self.keywords}")
        
        if model_path is None:
            raise ValueError("Veuillez fournir le chemin vers le modèle Vosk.")
            
        try:
            self.logger.info(f"Chargement du modèle Vosk depuis: {model_path}")
            self.model = vosk.Model(model_path)
            self.logger.info("Modèle Vosk chargé avec succès")
        except Exception as e:
            self.logger.error(f"Erreur lors du chargement du modèle: {e}")
            raise ValueError(f"Modèle Vosk non trouvé à {model_path}. Télécharge-le sur alphacephei.com/vosk/models")
            
        self.samplerate = samplerate
        self.q = queue.Queue()
        self.logger.info(f"Agent vocal initialisé - Fréquence: {samplerate}Hz")

    def callback(self, indata, frames, time, status):
        self.q.put(bytes(indata))

    def listen_for_keywords(self) -> Optional[bool]:
        """
        Écoute les mots clés vocaux
        
        Returns:
            bool: True si mot clé détecté, False sinon, None en cas d'erreur
        """
        try:
            self.logger.debug("En attente d'un mot clé vocal...")
            
            with sd.RawInputStream(samplerate=self.samplerate, blocksize=8000, dtype='int16',
                                   channels=1, callback=self.callback):
                rec = vosk.KaldiRecognizer(self.model, self.samplerate)
                
                while True:
                    try:
                        data = self.q.get(timeout=5.0)  # Timeout pour éviter le blocage
                        
                        if rec.AcceptWaveform(data):
                            result = rec.Result()
                            text = json.loads(result).get("text", "").lower()
                            
                            if text.strip():  # Ignorer les résultats vides
                                self.logger.info(f"Texte reconnu: '{text}'")
                                
                                for key in self.keywords:
                                    if key in text:
                                        self.logger.info(f"Mot clé détecté: '{key}' dans '{text}'")
                                        return True
                                        
                                return False
                                
                    except queue.Empty:
                        # Timeout atteint, continuer l'écoute
                        continue
                        
        except Exception as e:
            self.logger.error(f"Erreur lors de l'écoute vocale: {e}")
            return None