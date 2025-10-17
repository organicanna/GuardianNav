from guardian.voice_agent import VoiceAgent

MODEL_PATH = "/Users/anna/Desktop/GuardianNav/vosk-model-small-fr-0.22"

agent = VoiceAgent(
    keywords=["aide", "stop", "urgence", "secours"],
    model_path=MODEL_PATH
)

print("Parlez, je vous écoute…")
while True:
    if agent.listen_for_keywords():
        print("Mot clé détecté !")
        break
    else:
        print("Aucun mot clé détecté, recommencez…")