# 🎤 Système Vocal Hybride Guardian

## 🎯 Vue d'ensemble

Guardian utilise un **système vocal hybride intelligent** qui s'adapte automatiquement à la disponibilité du réseau :

```
┌────────────────────────────────────────────────────────┐
│            GUARDIAN HYBRID VOICE SYSTEM                │
├────────────────────────────────────────────────────────┤
│                                                        │
│  ┌──────────┐                                          │
│  │  AUDIO   │                                          │
│  │ CAPTURE  │                                          │
│  └────┬─────┘                                          │
│       │                                                │
│       ├─── Détection connexion Internet                │
│       │                                                │
│  ┌────▼────────┐              ┌──────────────┐        │
│  │   AVEC WiFi │              │  SANS WiFi   │        │
│  └────┬────────┘              └──────┬───────┘        │
│       │                              │                │
│  ┌────▼──────────────┐        ┌──────▼──────────┐     │
│  │ Gemini 2.0 Audio  │        │  Vosk Local     │     │
│  │ ✅ Transcription   │        │ ✅ Transcription │     │
│  │ ✅ Intonation      │        │ ❌ Intonation    │     │
│  │ ✅ Émotion         │        │ ⚠️ Mots-clés    │     │
│  │ ✅ Stress vocal    │        │ ⚠️ Heuristique  │     │
│  └───────┬───────────┘        └────────┬────────┘     │
│          │                             │              │
│          └──────────┬──────────────────┘              │
│                     │                                 │
│              ┌──────▼───────┐                          │
│              │   ANALYSE    │                          │
│              │  D'URGENCE   │                          │
│              └──────────────┘                          │
└────────────────────────────────────────────────────────┘
```

---

## 📊 Comparaison des modes

| Caractéristique | Gemini 2.0 Audio (Online) | Vosk Local (Offline) |
|----------------|---------------------------|----------------------|
| **Connexion requise** | ✅ WiFi obligatoire | ❌ Fonctionne sans Internet |
| **Transcription** | ✅ Excellente (IA avancée) | ✅ Bonne (modèle fr-0.22) |
| **Analyse intonation** | ✅ OUI (ton, stress, panique) | ❌ NON (texte uniquement) |
| **Détection émotion** | ✅ Voix tremblante, pleurs, cris | ⚠️ Mots-clés uniquement |
| **Latence** | ~1-2 secondes (réseau) | ~100ms (local) |
| **Coût** | 💰 API payante (minimal) | 💚 Gratuit |
| **Précision urgence** | 🎯 Très élevée (+2-3 pts si stress) | 🎯 Moyenne (basée sur texte) |

---

## 🔧 Configuration

### Fichier `config/api_keys.yaml`

```yaml
google_cloud:
  gemini:
    api_key: VOTRE_CLE_API_GEMINI
    model: gemini-2.0-flash-exp
    
    # Configuration hybride
    hybrid_voice:
      enabled: true              # Active le système hybride
      audio_analysis: true       # Analyse vocale (si online)
      offline_fallback: true     # Fallback Vosk automatique
```

---

## 🚀 Utilisation

### Exemple 1 : Détection automatique

```python
from guardian.hybrid_voice_agent import HybridVoiceAgent

# Initialisation
agent = HybridVoiceAgent(config)

# Analyse audio (détecte automatiquement WiFi)
result = agent.analyze_audio(audio_bytes)

print(result)
# {
#     "transcription": "Je pense que quelqu'un me suit",
#     "emotion_detected": "stressed",
#     "urgency_boost": +2,  # +2 points si stress détecté
#     "method": "gemini_audio",  # ou "vosk_local"
#     "online": True
# }
```

### Exemple 2 : Vérification du statut

```python
status = agent.get_status()
print(status)
# {
#     "mode": "ONLINE",
#     "online": True,
#     "gemini_available": True,
#     "vosk_available": True,
#     "current_method": "gemini_audio"
# }
```

---

## 🎯 Scénarios d'utilisation

### Scénario 1 : Femme suivie avec WiFi ✅

```
Situation : "Je pense que quelqu'un me suit depuis 10 minutes"
Audio : Voix tremblante, respiration rapide

┌─────────────────────────────────────────┐
│ MODE : ONLINE (Gemini 2.0 Audio)        │
├─────────────────────────────────────────┤
│ Transcription : "quelqu'un me suit..."  │
│ Intonation : STRESS ÉLEVÉ               │
│ Émotion : panic                         │
│ Urgence de base : 7/10                  │
│ Bonus vocal : +3 (voix paniquée)        │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━       │
│ URGENCE FINALE : 10/10 ⚠️               │
│ → Email + Police 17 IMMÉDIAT            │
└─────────────────────────────────────────┘
```

### Scénario 2 : Femme suivie SANS WiFi ⚠️

```
Situation : "Je pense que quelqu'un me suit depuis 10 minutes"
Audio : Voix tremblante (NON détectée)

┌─────────────────────────────────────────┐
│ MODE : OFFLINE (Vosk Local)             │
├─────────────────────────────────────────┤
│ Transcription : "quelqu'un me suit..."  │
│ Intonation : NON DISPONIBLE             │
│ Mots-clés : "suivie" détecté            │
│ Urgence de base : 7/10                  │
│ Bonus texte : +2 (mot-clé "suivie")     │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━       │
│ URGENCE FINALE : 9/10 ⚠️                │
│ → Email + Police 17                     │
└─────────────────────────────────────────┘
```

**Différence** : En mode offline, on perd +1 point (pas de détection vocale du stress), mais reste critique (9/10).

### Scénario 3 : Crevaison vélo (pas d'urgence)

```
Situation : "J'ai crevé à vélo, mais ça va"
Audio : Voix calme, ton normal

┌─────────────────────────────────────────┐
│ MODE : ONLINE (Gemini 2.0 Audio)        │
├─────────────────────────────────────────┤
│ Transcription : "crevé à vélo..."       │
│ Intonation : CALME                      │
│ Émotion : calm                          │
│ Urgence de base : 2/10                  │
│ Bonus vocal : +0 (voix normale)         │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━       │
│ URGENCE FINALE : 2/10 ✅                │
│ → Aucun email, conseils seulement      │
└─────────────────────────────────────────┘
```

---

## 📈 Impact sur la calibration d'urgence

### Bonus d'urgence selon l'émotion vocale

| Émotion détectée | Bonus | Exemple |
|------------------|-------|---------|
| **Calme** | +0 | Voix normale, pas de stress |
| **Stressé** | +2 | Voix légèrement tremblante |
| **Panique** | +3 | Respiration rapide, voix aiguë |
| **Pleurs** | +3 | Sanglots audibles |
| **Cris** | +4 | Volume élevé, détresse |

### Exemples d'ajustement

```
Sans analyse vocale (Vosk):
- "Je suis suivie" → 7/10 (texte seulement)

Avec analyse vocale (Gemini Audio):
- "Je suis suivie" (calme) → 7/10 + 0 = 7/10
- "Je suis suivie" (stressée) → 7/10 + 2 = 9/10 ⚠️
- "Je suis suivie" (panique) → 7/10 + 3 = 10/10 🚨
```

---

## 🛠️ Installation des dépendances

### Gemini 2.0 Audio (Mode Online)

```bash
pip install google-generativeai
```

### Vosk (Mode Offline)

```bash
pip install vosk sounddevice numpy
```

**Modèle Vosk français** :
```bash
cd models
wget https://alphacephei.com/vosk/models/vosk-model-small-fr-0.22.zip
unzip vosk-model-small-fr-0.22.zip
```

---

## ⚙️ Détails techniques

### Détection de connexion

Le système teste plusieurs endpoints :
1. `https://www.google.com`
2. `https://generativelanguage.googleapis.com` (API Gemini)
3. `https://1.1.1.1` (Cloudflare DNS)

Timeout : 2-3 secondes maximum

### Fallback automatique

```python
def analyze_audio(audio_data):
    # Vérification connexion
    if self._check_internet_connection():
        try:
            # Tentative Gemini Audio
            return self._analyze_with_gemini_audio(audio_data)
        except Exception as e:
            # Si échec → Fallback Vosk
            return self._analyze_with_vosk(audio_data)
    else:
        # Pas de connexion → Vosk direct
        return self._analyze_with_vosk(audio_data)
```

### Détection d'émotion par mots-clés (Fallback)

En mode offline, analyse textuelle :

```python
# Panique (+3 points)
panic_keywords = [
    'au secours', 'aidez-moi', 'vite', 'urgent',
    'je vais mourir', 'aide', 's\'il vous plaît'
]

# Stress (+2 points)
stress_keywords = [
    'suivie', 'menacé', 'peur', 'perdu',
    'angoissé', 'inquiet', 'mal', 'saigne'
]
```

---

## 📋 Recommandations

### Pour une utilisation optimale

1. ✅ **Toujours installer Vosk** (fallback essentiel)
2. ✅ **Activer Gemini Audio** si connexion fiable
3. ✅ **Tester en mode avion** pour valider le fallback
4. ⚠️ **Prévoir 4G/5G** pour zones sans WiFi

### Cas d'usage

| Situation | Mode recommandé | Raison |
|-----------|----------------|--------|
| Domicile | Gemini Audio | WiFi stable |
| Extérieur urbain | Gemini Audio | 4G/5G disponible |
| Campagne/montagne | Vosk Local | Réseau instable |
| Mode avion | Vosk Local | Offline obligatoire |
| Urgence critique | Les deux | Redondance |

---

## 🔐 Sécurité & Confidentialité

### Gemini 2.0 Audio (Online)

- ⚠️ Audio envoyé à Google Cloud
- 🔒 Chiffrement HTTPS
- 📝 Logs Google (conformité RGPD)
- ⏱️ Traitement temps réel (pas de stockage)

### Vosk Local (Offline)

- ✅ 100% local (aucune donnée envoyée)
- ✅ Confidentialité totale
- ✅ Pas de logs externes
- ✅ RGPD compliant

**Recommandation** : Pour confidentialité maximale, utiliser `offline_fallback: true` uniquement.

---

## 📊 Tests et validation

### Test de fallback

```bash
# Désactiver WiFi manuellement
# Lancer Guardian
python web/start_web_server.py

# Vérifier les logs
# 📱 Mode OFFLINE: Utilisation de Vosk local ✅
```

### Test d'analyse vocale

```python
# Test avec intonation stressée
result = agent.analyze_audio(stressed_audio)
assert result['emotion_detected'] == 'stressed'
assert result['urgency_boost'] >= 2

# Test mode calme
result = agent.analyze_audio(calm_audio)
assert result['emotion_detected'] == 'calm'
assert result['urgency_boost'] == 0
```

---

## 🆘 FAQ

**Q : Que se passe-t-il si je perds le WiFi pendant une urgence ?**
R : Le système bascule automatiquement sur Vosk local en <2 secondes. Vous perdez l'analyse vocale mais gardez la transcription.

**Q : Puis-je forcer le mode offline ?**
R : Oui, mettez `hybrid_voice.enabled: false` dans la config.

**Q : Vosk est-il aussi précis que Gemini ?**
R : Pour la transcription : ~85% vs ~95%. Pour l'émotion : mots-clés uniquement vs analyse vocale complète.

**Q : Quel est le coût de Gemini Audio ?**
R : ~$0.00025 par minute d'audio (très faible). Voir [tarifs Google](https://ai.google.dev/pricing).

**Q : Peut-on utiliser les deux en parallèle ?**
R : Non, le système choisit automatiquement le meilleur selon la connexion.

---

## 🚀 Roadmap

### Améliorations futures

- [ ] Analyse multi-langue (en, es, de)
- [ ] Détection bruit ambiant (cris, sirènes)
- [ ] Mode hybride simultané (Vosk + Gemini)
- [ ] Cache intelligent (dernières analyses)
- [ ] Compression audio optimisée

---

## 📞 Support

Pour toute question :
- 📧 Email : support@guardianav.com
- 📚 Documentation : `/docs/`
- 🐛 Issues : GitHub Issues

---

**Version** : 1.0.0
**Dernière mise à jour** : 10 novembre 2025
