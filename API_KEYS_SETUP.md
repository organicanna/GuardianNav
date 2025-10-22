# Configuration des clés API pour GuardianNav

## 🚨 SÉCURITÉ IMPORTANTE

**⚠️ NE JAMAIS COMMITTER le fichier `api_keys.yaml` avec de vraies clés !**

Ce dépôt contient un fichier `api_keys_template.yaml` qui sert de modèle. Le vrai fichier `api_keys.yaml` est automatiquement ignoré par Git pour protéger vos clés secrètes.

## 📋 Installation des clés API

### 1. Créer votre fichier de configuration
```bash
cp api_keys_template.yaml api_keys.yaml
```

### 2. Obtenir les clés API nécessaires

#### **Google Cloud Platform APIs**
1. Créez un projet sur [Google Cloud Console](https://console.cloud.google.com/)
2. Activez les APIs nécessaires :
   - **Google Maps API** pour la géolocalisation
   - **Google Translate API** pour la traduction
   - **Google Natural Language API** pour l'analyse IA
   - **Google Speech-to-Text API** pour reconnaissance vocale
   - **Google Text-to-Speech API** pour réponses vocales

3. Créez des clés API dans "APIs & Services > Credentials"

#### **Services de notification**
- **Twilio** : [Console Twilio](https://console.twilio.com/) pour SMS d'urgence
- **SendGrid** : [SendGrid](https://sendgrid.com/) pour emails d'urgence

#### **APIs de transport (optionnel)**
- **API RATP** : Pour info transports en commun Paris
- **What3Words** : Pour localisation précise
- **Citymapper** : Pour itinéraires optimisés

### 3. Configurer vos contacts d'urgence

Modifiez la section `emergency_contacts` avec vos vrais contacts :
```yaml
emergency_contacts:
  - name: "Votre Contact"
    phone: "+33123456789"
    email: "contact@example.com"
    relation: "famille"
```

### 4. Tester la configuration

```bash
python tests/test_api_config.py
```

## 🔒 Sécurité

- ✅ `api_keys.yaml` est dans `.gitignore`
- ✅ Seul le template est versionné
- ✅ Vos clés restent locales et privées
- ⚠️ Ne partagez jamais vos clés API
- 🔄 Régénérez les clés si compromises

## 🆘 Mode dégradé

GuardianNav fonctionne même sans toutes les clés API :
- **Sans clés** : Mode simulation avec fonctionnalités de base
- **Clés partielles** : Fonctionnalités disponibles selon les APIs configurées
- **Toutes les clés** : Fonctionnalités complètes avec services externes

## 📞 Support

Si vous avez des questions sur la configuration des API, consultez :
- [Documentation Google Cloud](https://cloud.google.com/docs)
- [Guide Twilio](https://www.twilio.com/docs)
- [Documentation SendGrid](https://docs.sendgrid.com/)