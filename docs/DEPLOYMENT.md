# Guide de Déploiement Local - Guardian

> Guide complet pour installer et configurer Guardian sur votre machine locale

## Prérequis Système

### Configuration Minimale
- **OS** : macOS 10.15+, Windows 10+, Ubuntu 18.04+ 
- **Python** : 3.9 ou supérieur
- **RAM** : 4GB minimum (8GB recommandé)
- **Espace disque** : 2GB libres
- **Microphone** : Requis pour la reconnaissance vocale
- **Connexion Internet** : Pour les APIs Google

### Outils Requis
```bash
# Vérifier Python
python3 --version  # Doit être ≥ 3.9

# Vérifier pip
pip3 --version

# Vérifier git
git --version
```

## 📥 Installation Étape par Étape

### 1. Cloner le Repository

```bash
# Cloner depuis GitHub
git clone https://github.com/organicanna/GuardianNav.git
cd GuardianNav

# Vérifier la structure
ls -la
# Vous devez voir : guardian/, web/, config/, models/, etc.
```

### 2. Créer l'Environnement Virtuel

```bash
# Créer l'environnement virtuel
python3 -m venv .venv

# Activer l'environnement
# Sur macOS/Linux :
source .venv/bin/activate

# Sur Windows :
.venv\Scripts\activate

# Vérifier l'activation (le prompt doit afficher (.venv))
which python  # Doit pointer vers .venv/bin/python
```

### 3. Installer les Dépendances

```bash
# Mise à jour pip
pip install --upgrade pip

# Installation des dépendances principales
pip install -r requirements.txt

# Vérification des modules critiques
python3 -c "
import sys
modules = ['flask', 'vosk', 'pygame', 'requests', 'yaml']
for module in modules:
    try:
        __import__(module)
        print(f' {module}')
    except ImportError as e:
        print(f' {module}: {e}')
"
```

### 4. Télécharger le Modèle Vosk

```bash
# Le modèle français Vosk (100MB)
# Méthode 1: Script automatique (recommandé)
python scripts/download_vosk_model.py

# Méthode 2: Téléchargement manuel
wget https://alphacephei.com/vosk/models/vosk-model-small-fr-0.22.zip
unzip vosk-model-small-fr-0.22.zip
mv vosk-model-small-fr-0.22 models/

# Vérification
ls models/vosk-model-small-fr-0.22/
# Doit contenir: am/, conf/, graph/, ivector/
```

##  Configuration des APIs

### 5. Créer le Fichier de Configuration

```bash
# Copier le template
cp config/api_keys.yaml.example config/api_keys.yaml

# Éditer avec vos clés
nano config/api_keys.yaml  # ou votre éditeur préféré
```

### 6. Configuration des Clés API

#### Google Gemini API (Gratuite)
```yaml
# Dans config/api_keys.yaml
google_genai_api_key: "VOTRE_CLE_GEMINI"
```

**Obtenir la clé** :
1. Aller sur [ai.google.dev](https://ai.google.dev/)
2. Cliquer "Get API Key"  
3. Créer un nouveau projet
4. Copier la clé générée

#### Gmail API (Pour emails d'urgence)
```yaml
# Dans config/api_keys.yaml
gmail:
  credentials_path: "config/gmail_credentials.json"
  enabled: true
```

**Configuration Gmail** :
1. Aller sur [console.cloud.google.com](https://console.cloud.google.com/)
2. Créer un projet ou sélectionner un existant
3. Activer l'API Gmail
4. Créer des identifiants OAuth 2.0
5. Télécharger le JSON et le placer dans `config/gmail_credentials.json`

#### Google Maps API (Pour navigation)
```yaml
# Dans config/api_keys.yaml  
google_maps_api_key: "VOTRE_CLE_MAPS"
```

**Obtenir la clé** :
1. Aller sur [console.cloud.google.com](https://console.cloud.google.com/)
2. Activer "Maps JavaScript API" et "Directions API"
3. Créer une clé API
4. Restreindre aux domaines localhost

### 7. Configuration Complète

```yaml
# Exemple config/api_keys.yaml complet
google_genai_api_key: "AIzaSyC..."
google_maps_api_key: "AIzaSyD..." 

gmail:
  credentials_path: "config/gmail_credentials.json"
  enabled: true

# Contacts d'urgence
emergency_contacts:
  - name: "Marie Dupont"
    email: "marie@example.com" 
    phone: "+33612345678"
    relation: "famille"
    priority: 1
    
  - name: "Jean Martin"
    email: "jean@example.com"
    phone: "+33698765432" 
    relation: "ami"
    priority: 2

# Configuration utilisateur par défaut
user_profile:
  name: "Votre Nom"
  phone: "+33600000000"
  emergency_message: "Message d'urgence automatique"
```

##  Lancement de l'Application

### 8. Test de Configuration

```bash
# Test des dépendances
python scripts/test_dependencies.py

# Test des APIs  
python scripts/test_apis.py

# Test du microphone
python scripts/test_audio.py
```

### 9. Démarrage du Serveur

```bash
# Lancement simple
python3 run.py

# Ou avec logs détaillés  
python3 run.py --debug

# Ou en arrière-plan
nohup python3 run.py > logs/guardian.log 2>&1 &
```

**Sortie attendue** :
```
  GUARDIAN - Assistant de Sécurité Personnelle
==================================================
 Vosk disponible pour reconnaissance vocale locale
📁 Chargement de api_keys.yaml...
 Gmail API configuré pour emails d'urgence
 Guardian Agent:  Disponible
 Gmail Agent:  Configuré
 Modèle Vosk chargé avec succès
🚀 Démarrage de Guardian Web Interface Simple
💡 Ouvrez votre navigateur sur: http://localhost:5010
```

## 🌐 Accès aux Interfaces

### URLs Principales
- **🏠 Accueil** : http://localhost:5010
- **🎮 Démo Interactive** : http://localhost:5010/demo  
- **🗺️ Carte Navigation** : http://localhost:5010/map
- **🚨 Urgence Rapide** : http://localhost:5010/emergency

### Test Fonctionnel
1. **Ouvrir** http://localhost:5010
2. **Remplir** le formulaire utilisateur (nom, prénom, téléphone)
3. **Cliquer** "Lancer la Démonstration Guardian" 
4. **Tester** la reconnaissance vocale avec "Je suis en danger"
5. **Vérifier** la réponse IA et les actions d'urgence

## 🔧 Résolution de Problèmes

### Erreurs Courantes

#### Problème : `ModuleNotFoundError: No module named 'vosk'`
```bash
# Solution
pip install vosk sounddevice

# Si problème persistant
pip install --force-reinstall vosk
```

#### Problème : `No such file or directory: vosk-model`  
```bash
# Vérifier l'emplacement
ls models/
# Doit contenir vosk-model-small-fr-0.22/

# Re-télécharger si nécessaire
python scripts/download_vosk_model.py
```

#### Problème : Microphone non détecté
```bash
# Tester les périphériques audio
python3 -c "
import sounddevice as sd
print('Périphériques disponibles:')
print(sd.query_devices())
"

# Autoriser l'accès micro sur macOS
# Aller dans Préférences Système > Sécurité > Microphone
```

#### Problème : API Google non fonctionnelle
```bash
# Tester la clé Gemini
python3 -c "
import google.generativeai as genai
genai.configure(api_key='VOTRE_CLE')
model = genai.GenerativeModel('gemini-2.5-flash')
print(' Gemini API fonctionne')
"
```

### Logs et Debugging

```bash
# Voir les logs en temps réel
tail -f logs/guardian.log

# Nettoyer les logs anciens  
python scripts/cleanup.py

# Mode debug avancé
export GUARDIAN_DEBUG=1
python3 run.py
```

## 📊 Performance et Optimisation

### Ressources Système
- **Mémoire** : ~200MB au repos, ~500MB en utilisation
- **CPU** : ~5% au repos, ~15-25% lors de reconnaissance vocale
- **Réseau** : Uniquement pour les APIs (< 1MB/minute)

### Optimisation
```bash
# Réduire la mémoire Vosk (modèle plus petit)
wget https://alphacephei.com/vosk/models/vosk-model-small-fr-pguyot-0.3.zip

# Cache DNS pour accélérer les APIs
echo "8.8.8.8 generativelanguage.googleapis.com" >> /etc/hosts
```

## 🔒 Sécurité

### Protection des Clés API
```bash
# Permissions restrictives
chmod 600 config/api_keys.yaml
chmod 600 config/gmail_credentials.json

# Ne jamais commiter les clés
echo "config/api_keys.yaml" >> .gitignore
echo "config/gmail_credentials.json" >> .gitignore
```

### Utilisation Locale Seulement
-  Reconnaissance vocale **offline** (Vosk)
-  Données **jamais stockées** 
-  Communications **chiffrées** (HTTPS APIs)
- ⚠️ **Pas de production** (serveur développement Flask)

## 📱 Utilisation

### Commandes Vocales Supportées
- **Urgence** : "Au secours", "J'ai mal", "Je suis en danger"
- **Navigation** : "Où suis-je ?", "Comment rentrer ?"
- **Test** : "Test du système", "Ma position"
- **Info** : "Hôpital le plus proche", "Qui contacter ?"

### Exemple Session
```
👤 "J'ai mal au cœur, ça serre fort"
 "URGENCE CARDIAQUE détectée ! Niveau 9/10. 
     Asseyez-vous immédiatement. J'alerte le SAMU et vos proches."
 Email automatique envoyé aux contacts d'urgence
📱 Localisation partagée : "8 rue de Londres, 75009 Paris"  
⏱️ Temps total : 4.2 secondes
```

## 🆘 Support

### Documentation
- **Architecture** : `docs/ARCHITECTURE.md`
- **Code** : `docs/CODE_EXPLANATION.md` 
- **APIs** : `docs/API_REFERENCE.md`

### Aide
- **GitHub Issues** : [Issues](https://github.com/organicanna/GuardianNav/issues)
- **Discussions** : [Discussions](https://github.com/organicanna/GuardianNav/discussions)

---

**Version** : 2025.10.31  
**Testé sur** : macOS 14+, Ubuntu 22.04, Windows 11  
**Temps d'installation** : ~15 minutes