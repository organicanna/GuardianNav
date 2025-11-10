# Guide d'utilisation rapide - Tests de calibration Guardian

## 🚀 Démarrage rapide

### 1. Voir les statistiques des scénarios

```bash
cd tests/urgency_scenarios
python3 demo_scenarios.py --stats
```

### 2. Voir des exemples par niveau

```bash
python3 demo_scenarios.py --examples
```

### 3. Voir tout

```bash
python3 demo_scenarios.py --all
```

## 🧪 Lancer les tests

### Tests complets (tous les scénarios)

```bash
python3 test_urgency_calibration.py
```

**Attention** : Cela peut prendre du temps car chaque scénario fait un appel à l'API Gemini.

### Tests par catégorie

```bash
# Tester uniquement les scénarios "faible"
python3 test_urgency_calibration.py --category faible

# Autres catégories disponibles
python3 test_urgency_calibration.py --category moderee
python3 test_urgency_calibration.py --category elevee
python3 test_urgency_calibration.py --category critique
python3 test_urgency_calibration.py --category ambigus
python3 test_urgency_calibration.py --category psychologique
```

### Tests limités

```bash
# Tester seulement 5 scénarios
python3 test_urgency_calibration.py --max-tests 5

# Avec export JSON
python3 test_urgency_calibration.py --max-tests 5 --export
```

### Délai entre tests

```bash
# Ajouter 2 secondes de délai entre chaque test
python3 test_urgency_calibration.py --delay 2.0
```

## 🎮 Mode interactif

### Lancer le mode interactif

```bash
python3 interactive_trainer.py
```

Puis entrez vos propres situations pour voir comment Guardian les analyse.

**Commandes dans le mode interactif** :
- `examples` : Voir des exemples de scénarios
- `stats` : Statistiques de la session
- `quit` ou `exit` : Quitter

### Tests rapides prédéfinis

```bash
python3 interactive_trainer.py --quick
```

Teste 5 scénarios clés en quelques secondes.

### Tester une situation spécifique

```bash
python3 interactive_trainer.py --test "Je suis tombé à vélo et j'ai crevé"
```

## 📊 Interpréter les résultats

### Résultat d'un test individuel

```
📊 RÉSULTATS:
  Niveau attendu:   2/10 (Faible)
  Niveau obtenu:    2/10 (Faible)
  Écart:            0 niveau(x)
  ✅ PARFAIT - Niveau exact!

📧 Email aux proches:
  Attendu:  NON
  Obtenu:   NON
  ✅ Correct
```

### Rapport final

```
📈 Statistiques globales:
  Total testé:        38
  ✅ Parfait (exact): 30 (78.9%)
  ✓ OK (±1):          6 (15.8%)
  ❌ Incorrect:       2 (5.3%)

🎯 Taux de réussite global: 94.7%
   🌟 EXCELLENT - Calibration très précise!
```

## 🔧 Ajouter vos propres scénarios

Éditez `scenarios_data.py` et ajoutez dans la catégorie appropriée :

```python
"faible": [
    {
        "description": "Votre nouvelle situation",
        "niveau_attendu": 2,
        "categorie": "Faible",
        "justification": "Pourquoi ce niveau",
        "email_attendu": False,
        "services_urgence": "Aucun"
    },
]
```

Puis relancez les tests :

```bash
python3 test_urgency_calibration.py --category faible
```

## ❓ Résolution de problèmes

### "API rate limit exceeded"

Ajoutez un délai plus long :
```bash
python3 test_urgency_calibration.py --delay 3.0
```

### "Gemini API error"

Le système basculera automatiquement en mode simulation. Vérifiez votre clé API dans `config/api_keys.yaml`.

### Tests trop lents

Limitez le nombre de tests :
```bash
python3 test_urgency_calibration.py --max-tests 10
```

## 📁 Fichiers générés

Les résultats exportés sont sauvegardés dans :
```
tests/urgency_scenarios/urgency_test_results_YYYYMMDD_HHMMSS.json
```

Format JSON :
```json
{
  "timestamp": "2025-11-10T10:00:00",
  "summary": {
    "total": 38,
    "correct": 30,
    "tolerance_ok": 6,
    "incorrect": 2
  },
  "results": [...]
}
```

## 🎯 Objectifs de qualité

- **>90%** : 🌟 Excellent
- **75-90%** : ✅ Bon  
- **60-75%** : ⚠️ Moyen (ajustements nécessaires)
- **<60%** : ❌ Faible (revoir la logique)

## 📚 En savoir plus

Consultez le README.md complet pour plus de détails sur :
- L'architecture des tests
- Comment modifier la calibration
- Intégration CI/CD
- Contribution de nouveaux scénarios
