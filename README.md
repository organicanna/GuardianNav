# 🛡️ GuardianNav
> **Assistant de sécurité intelligent à commande vocale**  
> "Parlez, on s'occupe du reste" - Système d'urgence avec IA Gemini, reconnaissance vocale française et géolocalisation.

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![AI](https://img.shields.io/badge/AI-Google_Gemini_2.5_Flash-green.svg)](https://ai.google.dev/)
[![Voice](https://img.shields.io/badge/Voice-Vosk_French-orange.svg)](https://alphacephei.com/vosk/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🎯 Vue d'ensemble

**GuardianNav** transforme votre voix en interface d'urgence intelligente. Dites simplement "Au secours, j'ai mal au cœur" et l'IA Gemini analyse votre situation, évalue l'urgence (1-10), guide votre réponse et déclenche automatiquement l'assistance appropriée (SMS famille, email avec carte, services d'urgence).

### ✨ Fonctionnalités principales
- 🎤 **Conversation naturelle** : Interface vocale française (Vosk + Google STT)
- 🤖 **IA contextuelle** : Analyse Gemini 2.5 Flash adaptée à chaque situation  
- ⚡ **Réponse < 7s** : Pipeline STT → IA → TTS → Actions optimisé
- 📱 **Notifications intelligentes** : SMS/Email personnalisés selon urgence
- 📍 **Géolocalisation précise** : GPS + What3Words + services d'urgence
- 🤸 **Détection automatique** : Chutes, immobilité, déviations GPS

---

## 🏗️ Architecture

### 🔄 Pipeline Conversation Vocale
```
🎤 Vosk STT (offline) → 🤖 Gemini Analysis → 🔊 Google TTS → 📱 Actions
   < 0.5s                    < 2s                < 1s        < 3s
```

### 🧠 Différence IA Classique vs GuardianNav
| Aspect | IA Classique | GuardianNav |
|--------|-------------|-------------|
| Interface | 📱 Boutons/Apps | 🗣️ Conversation naturelle |
| Logique | 📋 Règles figées | 🧠 Analyse contextuelle IA |
| Réponse | ⚙️ Générique | 🎯 Personnalisée situation |
| Déclenchement | 🚨 Manuel | 🎤 Vocal automatique |

### 🗂️ Structure Principale
```
guardian/
├── voice_conversation_agent.py    # Pipeline vocal principal
├── gemini_agent.py               # IA Gemini 2.5 Flash  
├── voice_agent.py                # STT multi-engine
├── speech_agent.py               # TTS contextuel
├── guardian_agent.py             # Orchestrateur urgences
├── sms_agent.py                  # Notifications Twilio
└── emergency_response.py         # Emails + cartes
```

---

## 🚀 Installation

### 1️⃣ Clone & Setup
```bash
git clone https://github.com/organicanna/GuardianNav.git
cd GuardianNav
python3.9 -m venv .venv
source .venv/bin/activate  # macOS/Linux
pip install -r requirements_voice.txt
```

### 2️⃣ Configuration APIs (api_keys.yaml)
```yaml
# IA Gemini (GRATUIT - ai.google.dev)
gemini:
  api_key: "VOTRE_CLE_GOOGLE_GENAI"

# Services Google Cloud  
google_cloud:
  text_to_speech:
    api_key: "VOTRE_CLE_TTS"
  maps:
    api_key: "VOTRE_CLE_GOOGLE_MAPS"

# Notifications Twilio
notification_services:
  twilio:
    account_sid: "ACXXXXXXX"
    auth_token: "VOTRE_TOKEN"
    phone_number: "+33123456789"

# Contacts urgence
emergency_contacts:
  - name: "Marie Dupont" 
    phone: "+33612345678"
    email: "marie@gmail.com"
    relation: "fille"
    priority: 1
```

### 3️⃣ Test Installation
```bash
# Test APIs
python debug_gemini.py

# Test audio  
python -c "import sounddevice as sd; print(sd.query_devices())"
```

---

## 💡 Utilisation

### 🎭 Mode Démo (Recommandé)
```bash
python demo_camille_voice_real.py
# Scénario: Urgence bureaux Google, 22h
```

### 🛡️ Mode Production  
```bash
python main.py
# Surveillance complète avec détection automatique
```

### 🗣️ Exemples Conversation

#### Urgence Médicale
```
👤 "J'ai mal à la poitrine, ça serre fort"
🤖 "URGENCE CARDIAQUE ! Asseyez-vous ! J'appelle le SAMU."
📱 Actions: SAMU contacté + SMS famille + Email avec carte
```

#### Navigation
```  
👤 "Je suis perdu dans le métro"
🤖 "Vous êtes à Châtelet. Quelle est votre destination ?"
👤 "République"
🤖 "Prenez la ligne 1 direction Vincennes, 3 stations."
```

#### Sécurité
```
👤 "Quelqu'un me suit depuis 10 minutes"  
🤖 "Dirigez-vous vers le commissariat à 200m. Je guide vos proches."
📍 Actions: Localisation temps réel + Refuges sûrs + Contacts alertés
```

### 🎤 Commandes Vocales
- **Urgences** : "Au secours", "J'ai mal à...", "Je suis en danger"  
- **Info** : "Où suis-je ?", "Hôpital le plus proche"
- **Navigation** : "Comment rentrer ?", "Je suis perdu"
- **Test** : "Test du système", "Ma position"

---

## ⚙️ Configuration

### 🎤 Reconnaissance Vocale (Vosk)
```python
vosk_config = {
    "model_path": "vosk-model-small-fr-0.22",  # Français offline
    "confidence_threshold": 0.7,               # 70% minimum
    "sample_rate": 16000                       # Optimisé français
}
```

### 🤖 IA Gemini Personnalisée
```yaml
# Mots-clés urgence personnalisés
emergency_keywords:
  critical: ["au secours", "samu", "infarctus"]     # Niveau 9-10  
  high: ["j'ai très mal", "je suis tombé"]          # Niveau 7-8
  medium: ["je ne me sens pas bien", "j'ai peur"]   # Niveau 4-6
```

### 🔊 Synthèse Vocale Adaptative
```python
# TTS selon urgence
emergency_voice = {
    "speaking_rate": 1.2,    # +20% rapide
    "pitch": "+3st",         # Aigu attention
    "volume_gain_db": 6.0    # Plus fort
}
```

---

## 📊 Performance

| Métrique | Temps | Technologie |
|----------|-------|-------------|
| 🎤 Reconnaissance | < 0.5s | Vosk offline français |
| 🤖 Analyse IA | < 2s | Gemini 2.5 Flash |
| 🔊 Synthèse vocale | < 1s | Google TTS Neural |
| 📱 Notifications | < 3s | Twilio + Gmail |
| **🎯 Total** | **< 7s** | **Bout en bout** |

---

## 🆘 Urgence & Support

**En cas d'urgence réelle : appelez le 15 (SAMU), 17 (Police), 18 (Pompiers)**

- 🐛 **Issues** : [GitHub Issues](https://github.com/organicanna/GuardianNav/issues)
- 📖 **Doc complète** : [Wiki](https://github.com/organicanna/GuardianNav/wiki)  
- 💬 **Discussions** : [GitHub Discussions](https://github.com/organicanna/GuardianNav/discussions)

---

## 📄 Licence

MIT License - Voir [LICENSE](LICENSE)

---

> **🛡️ GuardianNav - Votre sécurité par la voix**  
> *Développé avec ❤️ pour protéger ce qui compte le plus*