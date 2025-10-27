# 📱 Configuration SMS pour GuardianNav

GuardianNav peut maintenant envoyer des **SMS d'urgence** en plus des emails grâce à l'intégration Twilio.

## 🚀 Fonctionnalités SMS

- ✅ **SMS automatiques** lors de toutes les urgences détectées
- ✅ **Messages personnalisés** selon le type d'urgence
- ✅ **Localisation GPS** incluse dans les SMS
- ✅ **Mode simulation** sans clés Twilio
- ✅ **Support multilingue** (français)

## 📋 Configuration requise

### 1. Compte Twilio

1. Créer un compte sur [twilio.com](https://www.twilio.com)
2. Obtenir votre **Account SID** et **Auth Token**
3. Acheter un numéro de téléphone Twilio

### 2. Configuration dans `api_keys.yaml`

```yaml
# Notifications SMS via Twilio
notification_services:
  twilio:
    account_sid: "YOUR_TWILIO_ACCOUNT_SID"
    auth_token: "YOUR_TWILIO_AUTH_TOKEN"
    phone_number: "+33123456789"  # Votre numéro Twilio

# Contacts d'urgence (requis pour SMS)
emergency_contacts:
  - name: "Papa"
    email: "papa@example.com"
    phone: "+33612345678"
  - name: "Maman"
    email: "maman@example.com"
    phone: "+33687654321"
```

### 3. Installation des dépendances

```bash
pip install twilio>=8.10.0
```

## 🔧 Types de SMS d'urgence

### SMS de danger immédiat
```
🚨 URGENCE - [Nom]

DANGER IMMÉDIAT détecté !

📍 Position: 48.8566, 2.3522
🏥 Aide proche: Police 500m
⏰ 18:45

Contactez immédiatement !
```

### SMS de chute détectée
```
🚨 URGENCE - [Nom]

CHUTE DÉTECTÉE !

📍 Position: 48.8566, 2.3522
🏥 Hôpital 800m
⏰ 18:45

Vérifiez son état !
```

### SMS d'urgence standard
```
🆘 URGENCE - [Nom]

Assistance demandée

📍 Position: 48.8566, 2.3522
🏥 Aide proche disponible
⏰ 18:45

Prenez contact rapidement
```

## 🛠️ Intégration technique

### Nouvel agent SMS : `SMSAgent`

```python
from guardian.sms_agent import SMSAgent

# Initialisation
sms_agent = SMSAgent(config)

# Envoi d'urgence
emergency_context = {
    'user_name': 'Jean Dupont',
    'emergency_type': 'CHUTE DÉTECTÉE',
    'location': {
        'address': '48.8566, 2.3522',
        'what3words': 'exemple.lieu.ici'
    }
}

sms_agent.send_emergency_sms(contacts, emergency_context)
```

### Intégration dans GuardianOrchestrator

Toutes les fonctions d'urgence ont été mises à jour :
- ✅ `_handle_vertex_ai_critical_emergency()`
- ✅ `_handle_vertex_ai_high_emergency()`
- ✅ `_handle_vertex_ai_standard_emergency()`
- ✅ `_handle_immediate_danger_situation()`
- ✅ `_trigger_fall_emergency_response()`
- ✅ `_handle_standard_emergency()`
- ✅ `_trigger_emergency_assistance()`

## 🧪 Test de l'intégration

Lancez le script de test pour vérifier la configuration :

```bash
python test_sms_integration.py
```

### Résultat attendu :
```
🚀 Test d'intégration SMS pour GuardianNav
✅ Configuration SMS trouvée
✅ SMSAgent initialisé avec succès
✅ Connexion Twilio OK
✅ SMS de test envoyé avec succès
✅ SMSAgent intégré dans GuardianOrchestrator
✅ Tous les tests d'intégration SMS réussis!
```

## 🔒 Mode simulation

Si Twilio n'est pas configuré ou installé :
- ⚠️ **Mode simulation activé**
- 📝 Messages SMS affichés dans les logs
- ✅ Fonctionnalité email préservée
- 🔄 Système continue de fonctionner

## 💡 Exemples d'usage

### Configuration minimale
```yaml
notification_services:
  twilio:
    account_sid: "ACxxxxx"
    auth_token: "xxxxxx" 
    phone_number: "+33123456789"

emergency_contacts:
  - name: "Urgence"
    email: "urgence@example.com"
    phone: "+33612345678"
```

### Avec plusieurs contacts
```yaml
emergency_contacts:
  - name: "Papa"
    email: "papa@example.com"
    phone: "+33612345678"
  - name: "Maman"  
    email: "maman@example.com"
    phone: "+33687654321"
  - name: "Frère"
    email: "frere@example.com"
    phone: "+33698765432"
```

## 🚨 Important

1. **Numéros internationaux** : Utilisez le format `+33` pour la France
2. **Coûts Twilio** : Chaque SMS est facturé (~0.08€)
3. **Limites** : Respectez les limites de votre compte Twilio
4. **Tests** : Utilisez des numéros validés pour les tests

## 🔗 Liens utiles

- [Documentation Twilio](https://www.twilio.com/docs)
- [Console Twilio](https://console.twilio.com/)
- [Tarifs SMS](https://www.twilio.com/pricing/messaging)

---

✅ **SMS d'urgence maintenant intégrés à GuardianNav !**