import speech_recognition as sr  # type: ignore

class VoiceAgent: #définition de l'agent vocal
    def __init__(self, keywords=None):
        if keywords is None:
            keywords = ["aide", "help", "stop", "emergency"] #définition de la liste par défaut des mots-clés
        self.keywords = [k.lower() for k in keywords] #transformation mot en miniscule pour comparaison
        self.recognizer = sr.Recognizer() #reconnaisseur vocal puis speech-to-text
        self.micro = sr.Microphone() #microphone comme source audio

    def listen_for_keywords(self): #écoute du micro et si mot-clé, renvoie mot clé
        with self.micro as source: #ouverture micro
            print("En attente d'un mot clé vocal...") #notification à l'utilisateur de l'écoute
            audio = self.recognizer.listen(source, phrase_time_limit=5) #enregistrement d'une durée de 5 secondes max : protection donnée
        try:
            text = self.recognizer.recognize_google(audio, language="fr-FR").lower() #envoi audio à Google Speech Recognition
            print(f"Vous avez dit : {text}") #demande vérification par notification
            for key in self.keywords: #parcours les mots clés définis précédemment
                if key in text: #si le mot prononcé fait partie des mots clés
                    return True 
            return False
        except sr.UnknownValueError: #gestion des erreurs si la voix n'est pas comprise
            print("Impossible de comprendre l'audio.")
            return False
        except sr.RequestError: #s'il y a une erreur de service
            print("Erreur de service de reconnaissance vocale.")
            return False