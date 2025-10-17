import vosk
import sounddevice as sd
import queue
import json

class VoiceAgent:
    def __init__(self, keywords=None, model_path=None):
        if keywords is None:
            keywords = ["aide", "stop", "urgence", "secours"]
        self.keywords = [k.lower() for k in keywords]
        if model_path is None:
            raise ValueError("Veuillez fournir le chemin vers le modèle Vosk.")
        try:
            self.model = vosk.Model(model_path)
        except Exception:
            raise ValueError(f"Modèle Vosk non trouvé à {model_path}. Télécharge-le sur alphacephei.com/vosk/models")
        self.samplerate = 16000
        self.q = queue.Queue()

    def callback(self, indata, frames, time, status):
        self.q.put(bytes(indata))

    def listen_for_keywords(self):
        print("En attente d'un mot clé vocal...")
        with sd.RawInputStream(samplerate=self.samplerate, blocksize=8000, dtype='int16',
                               channels=1, callback=self.callback):
            rec = vosk.KaldiRecognizer(self.model, self.samplerate)
            while True:
                data = self.q.get()
                if rec.AcceptWaveform(data):
                    result = rec.Result()
                    text = json.loads(result).get("text", "").lower()
                    print(f"Vous avez dit : {text}")
                    for key in self.keywords:
                        if key in text:
                            return True
                    return False
                # Optionnel : arrêt après le premier résultat ou boucle continue