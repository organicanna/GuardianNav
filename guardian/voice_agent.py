import speech_recognition as sr  # type: ignore

class VoiceAgent:
    def __init__(self, keywords=None):
        if keywords is None:
            keywords = ["aide", "help", "stop", "emergency"]
        self.keywords = [k.lower() for k in keywords]
        self.recognizer = sr.Recognizer()
        self.micro = sr.Microphone()

    def listen_for_keywords(self):
        with self.micro as source:
            print("En attente d'un mot clé vocal...")
            audio = self.recognizer.listen(source, phrase_time_limit=5)
        try:
            text = self.recognizer.recognize_google(audio, language="fr-FR").lower()
            print(f"Vous avez dit : {text}")
            for key in self.keywords:
                if key in text:
                    return True
            return False
        except sr.UnknownValueError:
            print("Impossible de comprendre l'audio.")
            return False
        except sr.RequestError:
            print("Erreur de service de reconnaissance vocale.")
            return False