# Tests GuardianNav

Ce dossier contient tous les tests pour le système Guardian.

## 📋 Structure des Tests

### 🎯 Tests de Calibration IA (NOUVEAU)
- **`urgency_scenarios/`** - Suite complète de tests pour calibrer l'évaluation des urgences
  - **38 scénarios** réels catégorisés (Faible, Modérée, Élevée, Critique)
  - **Tests automatisés** avec rapports détaillés
  - **Mode interactif** pour tests rapides
  - **Statistiques** et visualisation
  - 📖 Voir `tests/urgency_scenarios/README.md` pour détails complets
  - 🚀 Démarrage rapide : `python3 tests/urgency_scenarios/INDEX.py`

### 🧪 Tests Fonctionnels Principaux
- **`test_whatsapp.py`** - Test de l'intégration WhatsApp dans les emails d'urgence
- **`test_email_content.py`** - Test du contenu des emails avec localisation et situation réelles
- **`test_hybrid_approach.py`** - Test de l'approche hybride Gemini + TTS + Système d'urgence

### 🤖 Tests IA et Agents
- **`test_gemini_simple.py`** - Test simple de l'analyse d'urgence avec Gemini 2.5 Flash  
- **`test_guardian_fall_response.py`** - Test de la réponse Guardian aux chutes détectées
- **`test_static_agent.py`** - Test de l'agent statique GPS

### 🎤 Tests Voix et Audio
- **`test_voice_agent.py`** - Test de l'agent vocal
- **`test_voice_conversation.py`** - Test des conversations vocales
- **`test_speech_agent.py`** - Test de l'agent de reconnaissance vocale

### 🛡️ Tests Sécurité et Détection
- **`test_fall_detector.py`** - Test du détecteur de chute
- **`test_evacuation_routes.py`** - Test des routes d'évacuation

### ⚙️ Tests Configuration
- **`test_api_config.py`** - Test de la configuration des clés API

## 🚀 Exécution des Tests

### Test individuel
```bash
cd /path/to/GuardianNav-main
python3 tests/test_whatsapp.py
```

### Tests par catégorie
```bash
# Tests d'emails d'urgence
python3 tests/test_whatsapp.py
python3 tests/test_email_content.py

# Tests IA
python3 tests/test_gemini_simple.py
python3 tests/test_hybrid_approach.py

# Tests vocaux
python3 tests/test_voice_agent.py
python3 tests/test_voice_conversation.py
```

### Tous les tests
```bash
# Exécuter tous les tests (à implémenter)
python3 -m pytest tests/ -v
```

## 📝 Notes

- Tous les tests nécessitent un fichier `api_keys.yaml` configuré
- Certains tests nécessitent une connexion internet pour les APIs
- Les tests d'email nécessitent une configuration Gmail OAuth2 valide
- Les tests vocaux nécessitent un microphone et le modèle Vosk

## 🔧 Maintenance

Tests récemment ajoutés/mis à jour :
- ✅ `test_whatsapp.py` - Intégration WhatsApp (Oct 2025)
- ✅ `test_email_content.py` - Validation contenu email (Oct 2025)

Tests à maintenir :
- 🟡 Vérifier la compatibilité avec les nouvelles APIs
- 🟡 Mettre à jour les tests si les modules évoluent