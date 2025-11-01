# Installation des Modèles Guardian

## 🎤 Modèle de Reconnaissance Vocale Vosk

Guardian utilise le modèle **Vosk français** pour la reconnaissance vocale offline.

### Installation Automatique (Recommandée)

```bash
# Script d'installation automatique
python3 setup_models.py
```

### Installation Manuelle

1. **Téléchargement du modèle français :**
```bash
# Créer le dossier models
mkdir -p models

# Télécharger le modèle Vosk français (100MB)
cd models
wget https://alphacephei.com/vosk/models/vosk-model-small-fr-0.22.zip

# Extraire le modèle  
unzip vosk-model-small-fr-0.22.zip
rm vosk-model-small-fr-0.22.zip
```

2. **Vérification de l'installation :**
```bash
# Le modèle doit être dans ce chemin :
ls models/vosk-model-small-fr-0.22/
# → am/  conf/  graph/  ivector/  README
```

## 🌍 Autres Modèles Disponibles

### Modèles Multilingues Vosk

```bash
# Anglais (39MB)
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip

# Espagnol (39MB)  
wget https://alphacephei.com/vosk/models/vosk-model-small-es-0.42.zip

# Allemand (45MB)
wget https://alphacephei.com/vosk/models/vosk-model-small-de-0.15.zip

# Italien (48MB)
wget https://alphacephei.com/vosk/models/vosk-model-small-it-0.22.zip
```

## 🔧 Configuration Guardian

Après installation, configurez Guardian dans `guardian/config.py` :

```python
VOICE_CONFIG = {
    "model_path": "models/vosk-model-small-fr-0.22",  # Français
    # "model_path": "models/vosk-model-small-en-us-0.15",  # Anglais
    # "model_path": "models/vosk-model-small-es-0.42",     # Espagnol
}
```

## ✅ Test de Fonctionnement

```bash
# Tester la reconnaissance vocale
cd web
python3 web_interface_simple.py
# → http://localhost:5001

# Test en ligne de commande
python3 -c "
from guardian.voice_agent import VoiceRecognizer
recognizer = VoiceRecognizer()
print('Modèle Vosk chargé avec succès !')
"
```

## 📊 Informations Modèles

| Langue | Taille | Précision | Usage |
|--------|--------|-----------|--------|
| Français | 100MB | 90%+ | **Guardian défaut** |
| Anglais | 39MB | 85%+ | International |
| Espagnol | 39MB | 80%+ | Europe |
| Allemand | 45MB | 85%+ | Europe |

## 🚫 Pourquoi pas sur GitHub ?

- **Taille** : 100MB dépasse les limites pratiques Git
- **Performance** : Clone plus rapide sans les modèles  
- **Flexibilité** : Choix du modèle selon la langue
- **Updates** : Modèles mis à jour indépendamment du code

## 🆘 Résolution de Problèmes

### Erreur "Model not found"
```bash
# Vérifier le chemin
ls -la models/vosk-model-small-fr-0.22/
```

### Erreur "Permission denied"
```bash
chmod -R 755 models/
```

### Modèle corrompu
```bash
# Re-télécharger
rm -rf models/vosk-model-small-fr-0.22/
# Puis réinstaller via les étapes ci-dessus
```

---

**Guardian v3.1** - Reconnaissance vocale offline français optimisée