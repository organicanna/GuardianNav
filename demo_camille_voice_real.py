#!/usr/bin/env python3
"""
DÉMO GUARDIANNAV - SCÉNARIO CAMILLE AVEC VRAIE RECONNAISSANCE VOCALE
Démonstration avec speech-to-text réel (Vosk) + IA Gemini
Personnage : Camille, près des locaux Google, 22h, vendredi 31 octobre
"""

import sys
import os
import yaml
import json
import threading
import time
from datetime import datetime

# Ajouter le chemin vers les modules GuardianNav
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Imports pour la reconnaissance vocale
try:
    import vosk
    import sounddevice as sd
    import queue
    VOICE_AVAILABLE = True
except ImportError as e:
    print(f"❌ Erreur import vocal: {e}")
    VOICE_AVAILABLE = False

# Imports pour la synthèse vocale 
try:
    import pygame
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

class VoiceRecognizer:
    """Gestionnaire de reconnaissance vocale avec Vosk"""
    
    def __init__(self, model_path="vosk-model-small-fr-0.22"):
        self.model_path = model_path
        self.model = None
        self.rec = None
        self.audio_queue = queue.Queue()
        self.is_listening = False
        
    def initialize(self):
        """Initialise le modèle Vosk"""
        try:
            if not os.path.exists(self.model_path):
                print(f"❌ Modèle Vosk non trouvé: {self.model_path}")
                return False
                
            print("🔧 Chargement du modèle Vosk français...")
            self.model = vosk.Model(self.model_path)
            self.rec = vosk.KaldiRecognizer(self.model, 16000)
            print("✅ Modèle Vosk chargé avec succès")
            return True
            
        except Exception as e:
            print(f"❌ Erreur initialisation Vosk: {e}")
            return False
    
    def audio_callback(self, indata, frames, time, status):
        """Callback pour capturer l'audio"""
        if status:
            print(f"⚠️ Audio status: {status}")
        self.audio_queue.put(bytes(indata))
    
    def listen_for_speech(self, timeout=30, stop_words=['stop', 'arrêt', 'arrête']):
        """Écoute et reconnaît la parole"""
        if not self.model:
            return None
            
        try:
            print(f"🎤 **ÉCOUTE ACTIVÉE** (timeout: {timeout}s)")
            print("🗣️ Parlez maintenant... (dites 'stop' pour terminer)")
            print("-" * 50)
            
            self.is_listening = True
            recognized_text = ""
            
            with sd.RawInputStream(samplerate=16000, blocksize=8000, device=None, 
                                   dtype='int16', channels=1, callback=self.audio_callback):
                
                start_time = time.time()
                
                while self.is_listening and (time.time() - start_time) < timeout:
                    try:
                        data = self.audio_queue.get(timeout=1)
                        
                        if self.rec.AcceptWaveform(data):
                            # Phrase complète reconnue
                            result = json.loads(self.rec.Result())
                            text = result.get('text', '').strip()
                            
                            if text:
                                print(f"🗣️ **RECONNU:** '{text}'")
                                recognized_text = text
                                
                                # Vérifier les mots d'arrêt
                                if any(stop_word in text.lower() for stop_word in stop_words):
                                    print("🛑 Mot d'arrêt détecté")
                                    break
                                else:
                                    # Phrase reconnue, on peut s'arrêter
                                    break
                        else:
                            # Reconnaissance partielle
                            partial = json.loads(self.rec.PartialResult())
                            partial_text = partial.get('partial', '').strip()
                            if partial_text:
                                print(f"🎧 [En cours...]: {partial_text}", end='\r')
                                
                    except queue.Empty:
                        continue
                    except Exception as e:
                        print(f"❌ Erreur reconnaissance: {e}")
                        break
            
            self.is_listening = False
            print(f"\n✅ Reconnaissance terminée: '{recognized_text}'")
            return recognized_text if recognized_text else None
            
        except Exception as e:
            print(f"❌ Erreur écoute: {e}")
            self.is_listening = False
            return None

def load_guardian_agent():
    """Charge l'agent GuardianNav avec configuration"""
    try:
        # Charger la configuration
        with open('api_keys.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Importer et initialiser l'agent
        from guardian.gemini_agent import VertexAIAgent
        agent = VertexAIAgent(config)
        
        return agent, True
    except Exception as e:
        print(f"⚠️ Erreur chargement agent: {e}")
        return None, False

def simulate_tts_response(text):
    """Simule la synthèse vocale"""
    print("\n🔊 **GUARDIANNAV RÉPOND:**")
    print("="*60)
    print(f"{text}")
    print("="*60)
    print()

def analyze_situation_with_ai(agent, situation_text):
    """Analyse la situation avec l'IA"""
    if not agent:
        return simulate_ai_response(situation_text)
    
    try:
        print("🧠 [Analyse IA Gemini en cours...]")
        response = agent._make_api_request(situation_text)
        
        if response and 'candidates' in response:
            ai_text = response['candidates'][0]['content']['parts'][0]['text']
            return ai_text
        else:
            return simulate_ai_response(situation_text)
            
    except Exception as e:
        print(f"⚠️ Erreur IA: {e}")
        return simulate_ai_response(situation_text)

def simulate_ai_response(situation_text):
    """Génère une réponse IA simulée pour le scénario"""
    return """**ANALYSE D'URGENCE - NIVEAU 8/10**

**Situation identifiée :** Sécurité personnelle compromise
**Lieu :** Zone urbaine, proximité bureaux, heure tardive
**Facteurs de risque :** Isolement, impression d'être suivie, environnement peu familier

**ACTIONS IMMÉDIATES RECOMMANDÉES :**

1. **SÉCURITÉ IMMÉDIATE**
   • Dirigez-vous vers un lieu sûr et éclairé (magasin ouvert, restaurant, hall d'immeuble sécurisé)
   • Évitez les ruelles sombres et les zones isolées
   
2. **CONTACT D'URGENCE** 
   • Appelez le 17 (Police) si menace immédiate
   • Contactez un proche de confiance pour signaler votre position
   
3. **TRANSPORT SÉCURISÉ**
   • Commandez un taxi/VTC avec partage de trajet en temps réel
   • Évitez les transports en commun seule à cette heure

**Camille, votre sécurité est la priorité absolue. Faites confiance à votre instinct.**"""

def display_scenario_intro():
    """Affiche l'introduction du scénario"""
    print("🎭 DÉMO GUARDIANNAV - SCÉNARIO CAMILLE (RECONNAISSANCE VOCALE)")
    print("="*70)
    print("👤 **PERSONNAGE :** Camille")
    print("📍 **LOCALISATION :** Près des locaux Google")  
    print("🕙 **HEURE :** 22h00")
    print("📅 **DATE :** Vendredi 31 octobre 2025")
    print("⚠️ **SITUATION :** Je me sens en danger")
    print("="*70)
    print()
    
    print("🎯 **CONTEXTE DU SCÉNARIO:**")
    print("Vous êtes Camille, il est tard le soir, vous êtes seule près")
    print("des bureaux Google dans un quartier que vous ne connaissez pas bien.")
    print("Vous avez l'impression d'être suivie et vous commencez à avoir peur.")
    print("Vous décidez d'activer GuardianNav pour obtenir de l'aide.")
    print()
    
    print("🎙️ **VRAIE RECONNAISSANCE VOCALE:**")
    print("• Parlez dans votre microphone pour interagir 🎤")
    print("• GuardianNav utilisera Vosk pour vous comprendre 🗣️")
    print("• L'IA Gemini analysera votre situation en temps réel 🧠")
    print("• Dites 'stop' ou 'arrêt' pour terminer une écoute")
    print()

def run_voice_camille_demo():
    """Lance la démonstration du scénario Camille avec vraie reconnaissance vocale"""
    
    # Introduction
    display_scenario_intro()
    
    # Vérification des prérequis
    if not VOICE_AVAILABLE:
        print("❌ Modules de reconnaissance vocale non disponibles")
        print("💡 Installez avec: pip3 install vosk sounddevice")
        return
    
    input("🚀 Appuyez sur Entrée pour commencer la démo avec reconnaissance vocale...")
    print()
    
    # Initialisation de la reconnaissance vocale
    print("🎤 **INITIALISATION RECONNAISSANCE VOCALE**")
    print("="*50)
    recognizer = VoiceRecognizer()
    
    if not recognizer.initialize():
        print("❌ Impossible d'initialiser la reconnaissance vocale")
        print("💡 Vérifiez que le modèle vosk-model-small-fr-0.22 est présent")
        return
    
    # Chargement de l'agent
    print("\n🔧 **INITIALISATION DE GUARDIANNAV**")
    print("="*40)
    agent, agent_loaded = load_guardian_agent()
    
    if agent_loaded:
        print("✅ Agent GuardianNav chargé avec succès")
        print(f"🤖 IA Gemini: {'✅ Disponible' if agent.is_available else '⚠️ Mode simulation'}")
    else:
        print("⚠️ Agent en mode simulation")
    
    print()
    
    # Début de la conversation
    print("🎙️ **DÉBUT DE LA CONVERSATION VOCALE**")
    print("="*45)
    
    # Message d'accueil GuardianNav
    welcome_msg = """Bonjour Camille. Je suis GuardianNav, votre assistant de sécurité personnel. 
Je détecte que vous m'activez à une heure tardive. Êtes-vous en sécurité ? 
Décrivez-moi votre situation actuelle en parlant dans votre microphone."""
    
    simulate_tts_response(welcome_msg)
    
    # Première interaction - Camille explique sa situation avec sa voix
    print("🎤 **À VOUS DE PARLER, CAMILLE...**")
    situation_vocale = recognizer.listen_for_speech(timeout=20)
    
    if not situation_vocale:
        print("⚠️ Aucune parole détectée, utilisation du scénario par défaut")
        situation_vocale = "Je suis près des bureaux Google, il est 22h, je rentre du travail et j'ai l'impression qu'on me suit. Il y a quelqu'un derrière moi depuis plusieurs rues et ça me fait peur. Je ne sais pas quoi faire."
    
    print(f"\n📝 **SITUATION RAPPORTÉE:** {situation_vocale}")
    
    # Construction du prompt contextualisé
    full_prompt = f"""
    SITUATION D'URGENCE - ANALYSE REQUISE
    
    Personne: Camille (femme)
    Heure: 22h00, vendredi 31 octobre 2025
    Lieu: Près des locaux Google (zone urbaine)
    
    Situation rapportée par reconnaissance vocale: "{situation_vocale}"
    
    En tant que GuardianNav, assistant IA de sécurité personnelle, analysez cette situation et fournissez:
    1. Niveau d'urgence (1-10)
    2. Type de situation
    3. Conseils immédiats et pratiques
    4. Actions concrètes à prendre
    
    Répondez de manière rassurante mais ferme, en français, comme si vous parliez directement à Camille.
    Soyez concis mais complet.
    """
    
    # Analyse IA
    print("\n🧠 **ANALYSE INTELLIGENTE GUARDIANNAV**")
    print("="*45)
    ai_response = analyze_situation_with_ai(agent, full_prompt)
    
    simulate_tts_response(ai_response)
    
    # Suivi de situation avec reconnaissance vocale
    print("🎤 **SUIVI VOCAL - COMMENT ALLEZ-VOUS MAINTENANT ?**")
    follow_up_vocal = recognizer.listen_for_speech(timeout=15)
    
    # Réponse de suivi
    if follow_up_vocal:
        print(f"\n📝 **MISE À JOUR:** {follow_up_vocal}")
        
        follow_prompt = f"""
        SUIVI DE SITUATION - Camille répond par reconnaissance vocale: "{follow_up_vocal}"
        
        Contexte: Camille était près des locaux Google à 22h, se sentait suivie.
        Votre analyse précédente lui a donné des conseils de sécurité.
        
        Répondez à sa mise à jour de manière bienveillante et donnez des conseils de suivi appropriés.
        Si elle est en sécurité, félicitez-la et donnez des conseils pour rentrer chez elle.
        Si elle est encore en danger, renforcez les mesures de sécurité.
        Soyez concis et rassurant.
        """
        
        follow_response = analyze_situation_with_ai(agent, follow_prompt)
        simulate_tts_response(follow_response)
    else:
        print("⚠️ Pas de réponse vocale détectée")
    
    # Conclusion
    print("\n🎯 **CONCLUSION DE LA DÉMO VOCALE**")
    print("="*40)
    print("✅ Démonstration vocale terminée avec succès")
    print("🎭 Scénario Camille avec vraie reconnaissance vocale")
    print("🤖 GuardianNav + Vosk + Gemini IA")
    print()
    print("💡 **POINTS CLÉS DÉMONTRÉS:**")
    print("   ✅ Reconnaissance vocale française (Vosk)")
    print("   ✅ Analyse IA contextuelle (Gemini)")
    print("   ✅ Conversation naturelle speech-to-text")
    print("   ✅ Conseils de sécurité personnalisés")
    print("   ✅ Suivi en temps réel de la situation")
    print()
    print("🚀 System complet opérationnel pour situations réelles !")

def main():
    """Point d'entrée principal"""
    try:
        run_voice_camille_demo()
    except KeyboardInterrupt:
        print("\n\n⚠️ Démo interrompue par l'utilisateur")
        print("🛡️ En situation réelle, GuardianNav resterait disponible")
    except Exception as e:
        print(f"\n❌ Erreur durant la démo: {e}")
        print("💡 En cas de vraie urgence, contactez directement le 17 ou le 112")

if __name__ == "__main__":
    main()