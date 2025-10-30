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
    """Charge l'agent GuardianNav avec configuration et diagnostics"""
    try:
        # Charger la configuration
        print("📁 Chargement de api_keys.yaml...")
        with open('api_keys.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Vérifier la configuration Gemini
        google_config = config.get('google_cloud', {})
        gemini_config = google_config.get('gemini', {})
        
        print(f"🔍 Configuration trouvée:")
        print(f"   - Gemini enabled: {gemini_config.get('enabled', False)}")
        print(f"   - API key présente: {bool(gemini_config.get('api_key'))}")
        if gemini_config.get('api_key'):
            key = gemini_config.get('api_key')
            print(f"   - API key: {key[:20]}...{key[-4:] if len(key) > 24 else key}")
        print(f"   - Modèle: {gemini_config.get('model', 'non spécifié')}")
        
        # Importer et initialiser l'agent
        from guardian.gemini_agent import VertexAIAgent
        agent = VertexAIAgent(config)
        
        print(f"🤖 Agent initialisé:")
        print(f"   - Type API: {agent.api_type}")
        print(f"   - Disponible: {agent.is_available}")
        print(f"   - Clé configurée: {bool(agent.api_key and agent.api_key != 'YOUR_VERTEX_AI_API_KEY')}")
        
        return agent, True
        
    except FileNotFoundError:
        print("❌ Fichier api_keys.yaml non trouvé")
        return None, False
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
    """Analyse la situation avec l'IA Gemini - VRAIE API SEULEMENT"""
    if not agent:
        print("❌ Agent non disponible")
        return "**ERREUR** : Agent GuardianNav non initialisé correctement"
    
    # Vérifier que l'agent est correctement configuré
    if not hasattr(agent, 'api_key') or not agent.api_key or agent.api_key == "YOUR_VERTEX_AI_API_KEY":
        print("❌ Clé API Gemini manquante ou invalide")
        print("💡 Vérifiez votre fichier api_keys.yaml")
        return "**ERREUR** : Clé API Gemini non configurée. Vérifiez api_keys.yaml"
    
    print(f"🧠 [Analyse IA Gemini en cours... API: {agent.api_type}]")
    print(f"🔑 Clé API configurée: {agent.api_key[:20]}..." if len(agent.api_key) > 20 else "🔑 Clé API très courte")
    print(f"🎯 Modèle: {agent.model_name}")
    
    try:
        response = agent._make_api_request(situation_text)
        
        if response and 'candidates' in response:
            ai_text = response['candidates'][0]['content']['parts'][0]['text']
            
            # Vérifier que ce n'est pas une réponse simulée
            if 'simulation' in ai_text.lower() or '**ANALYSE D\'URGENCE - NIVEAU' in ai_text:
                print("⚠️ Réponse simulée détectée - problème avec l'API")
                print("💡 L'API Gemini n'est pas accessible avec cette clé")
                return f"**ERREUR API** : {ai_text}\n\n**NOTE**: L'API Gemini ne fonctionne pas correctement"
            
            print("✅ Réponse RÉELLE de l'IA Gemini reçue")
            return ai_text
        else:
            print("❌ Pas de réponse valide de l'API Gemini")
            return "**ERREUR API** : L'API Gemini n'a pas retourné de réponse valide"
            
    except Exception as e:
        print(f"❌ Erreur lors de l'appel à l'API Gemini: {e}")
        return f"**ERREUR API** : Impossible de joindre l'API Gemini - {e}"

# Cette fonction est maintenant supprimée - on utilise SEULEMENT l'API Gemini réelle

def display_scenario_intro():
    """Affiche l'introduction du scénario"""
    print("🎭 DÉMO GUARDIANNAV - SCÉNARIO CAMILLE (RECONNAISSANCE VOCALE)")
    print("="*70)
    print("👤 **PERSONNAGE :** Camille")
    print("📍 **LOCALISATION :** Près des locaux Google")  
    print("🕙 **HEURE :** 22h00")
    print("📅 **DATE :** Vendredi 31 octobre 2025")
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
        
        # Test de connectivité API
        if agent.is_available:
            print("🔧 Test de connectivité à l'API Gemini...")
            test_response = analyze_situation_with_ai(agent, "Test de connexion. Répondez juste 'API OK'.")
            if "API OK" in test_response or "ok" in test_response.lower():
                print("✅ API Gemini fonctionne correctement")
            else:
                print("⚠️ Test API échoué, vérifiez votre clé API")
                print(f"Réponse test: {test_response[:100]}...")
        else:
            print("❌ ATTENTION: L'agent n'est pas disponible")
            print("💡 La démo utilisera des messages d'erreur au lieu de l'IA")
            
            choice = input("\n❓ Continuer quand même ? (o/N): ").lower()
            if choice != 'o':
                print("🛑 Démo annulée - Configurez d'abord votre API Gemini")
                return
    else:
        print("⚠️ Agent en mode simulation")
        print("❌ ERREUR: Impossible de charger l'agent GuardianNav")
        return
    
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
    
    # Construction du prompt contextualisé et optimisé pour Gemini
    full_prompt = f"""Tu es GuardianNav, un assistant IA spécialisé en sécurité personnelle. Une femme nommée Camille t'appelle à l'aide.

CONTEXTE DE LA SITUATION:
• Personne: Camille (femme)
• Moment: 22h00, vendredi 31 octobre 2025 (heure tardive)
• Lieu: Près des locaux Google dans une zone urbaine
• Situation: "{situation_vocale}"

MISSION: Analyse cette situation d'urgence et réponds directement à Camille de manière professionnelle, rassurante mais ferme.

FORMAT DE RÉPONSE (en français):
**NIVEAU D'URGENCE:** [1-10]/10

**ANALYSE DE LA SITUATION:**
[Analyse claire en 2-3 phrases]

**ACTIONS IMMÉDIATES:**
1. [Action prioritaire n°1]
2. [Action prioritaire n°2] 
3. [Action prioritaire n°3]

**CONSEILS DE SÉCURITÉ:**
• [Conseil pratique immédiat]
• [Conseil de déplacement]
• [Conseil de communication]

**NUMÉROS D'URGENCE:**
[Numéro approprié à la situation]

**MESSAGE PERSONNEL:**
Camille, [message rassurant et encourageant personnalisé]

Réponds uniquement dans ce format. Sois précise, empathique et professionnelle."""
    
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
        
        follow_prompt = f"""Tu es GuardianNav. Camille te donne une mise à jour sur sa situation de sécurité.

RAPPEL DU CONTEXTE:
• Camille était près des locaux Google à 22h, se sentait suivie
• Tu lui as déjà donné des conseils de sécurité
• Elle vient de te répondre par reconnaissance vocale

MISE À JOUR DE CAMILLE: "{follow_up_vocal}"

MISSION: Réponds à cette mise à jour de manière professionnelle et bienveillante.

FORMAT DE RÉPONSE:
**ÉVALUATION:** [Sa situation actuelle]

**PROCHAINES ÉTAPES:**
• [Action immédiate si nécessaire]
• [Conseil pour la suite]
• [Recommandation de sécurité]

**MESSAGE:**
[Message personnel encourageant et rassurant adapté à sa réponse]

Si elle est en sécurité: félicite-la et donne des conseils pour rentrer.
Si elle est encore en danger: renforce les mesures de sécurité.
Reste concise, empathique et professionnelle."""
        
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