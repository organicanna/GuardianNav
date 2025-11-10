# Tests de Calibration des Urgences Guardian

Ce dossier contient une suite complète de tests pour calibrer et valider l'évaluation des niveaux d'urgence par l'IA Guardian (Gemini).

## 📂 Structure

```
urgency_scenarios/
├── scenarios_data.py           # Base de données de 40+ scénarios
├── test_urgency_calibration.py # Suite de tests automatisée
├── interactive_trainer.py      # Entraîneur interactif
└── README.md                    # Ce fichier
```

## 🎯 Objectifs

1. **Calibration précise** : S'assurer que Guardian évalue correctement le niveau de danger (1-10)
2. **Prévenir les faux positifs** : Éviter d'alerter les proches pour des incidents mineurs (ex: crevaison)
3. **Détecter les vraies urgences** : Garantir que les situations critiques déclenchent les bonnes alertes
4. **Validation continue** : Tester après chaque modification du prompt ou de la logique

## 📊 Base de données de scénarios

### `scenarios_data.py`

Contient **40+ scénarios réels** répartis en catégories :

#### 🟢 Faible (1-3) - Pas d'urgence
- Crevaison de vélo
- Question d'information
- Problème technique mineur
- **→ Aucun email envoyé**

#### 🟡 Modérée (4-5) - Attention
- Personne perdue
- Petit malaise
- Petite blessure
- **→ Pas d'email (surveillance)**

#### 🟠 Élevée (6-7) - Intervention nécessaire
- Chute avec douleur
- Coupure importante
- Menace de sécurité
- **→ Email envoyé aux proches**

#### 🔴 Critique (8-10) - Danger immédiat
- Détresse respiratoire
- Agression
- Accident grave
- Perte de conscience
- **→ Email + SMS + Alertes complètes**

#### 🤔 Cas ambigus
- Situations à interpréter selon le contexte
- Permet de tester la finesse de l'IA

## 🧪 Utilisation des outils

### 1. Tests automatisés complets

Lance tous les tests et génère un rapport :

```bash
cd tests/urgency_scenarios
python3 test_urgency_calibration.py
```

**Options :**
- `--category faible` : Tester une catégorie spécifique
- `--max-tests 10` : Limiter le nombre de tests
- `--delay 2.0` : Délai entre tests (éviter rate limiting)
- `--export` : Exporter les résultats en JSON

**Exemples :**

```bash
# Tester uniquement les scénarios faibles
python3 test_urgency_calibration.py --category faible

# Tester 5 scénarios avec export
python3 test_urgency_calibration.py --max-tests 5 --export

# Tester les critiques avec délai de 2s
python3 test_urgency_calibration.py --category critique --delay 2.0
```

### 2. Entraîneur interactif

Mode interactif pour tester rapidement :

```bash
python3 interactive_trainer.py
```

**Commandes :**
- Entrez une situation : analyse immédiate
- `examples` : Voir des exemples
- `stats` : Statistiques de session
- `quit` : Quitter

**Tests rapides prédéfinis :**

```bash
python3 interactive_trainer.py --quick
```

**Test d'une situation spécifique :**

```bash
python3 interactive_trainer.py --test "Je suis tombé à vélo et j'ai crevé"
```

## 📈 Interprétation des résultats

### Rapport de test

```
📊 RAPPORT FINAL - CALIBRATION DES URGENCES
══════════════════════════════════════════

📈 Statistiques globales:
  Total testé:        40
  ✅ Parfait (exact): 28 (70.0%)
  ✓ OK (±1):          10 (25.0%)
  ❌ Incorrect:       2 (5.0%)
  ⚠️  Erreurs:         0

🎯 Taux de réussite global: 95.0%
   🌟 EXCELLENT - Calibration très précise!
```

### Critères de qualité

- **>90%** : 🌟 Excellent
- **75-90%** : ✅ Bon
- **60-75%** : ⚠️ Moyen (ajustements nécessaires)
- **<60%** : ❌ Faible (revoir la logique)

## 🔧 Ajustement de la calibration

Si les tests révèlent des problèmes :

### 1. Modifier les mots-clés (simulation mode)

Fichier : `guardian/gemini_agent.py`

```python
# Ajouter des mots-clés pour situations NON urgentes
non_urgent_indicators = [
    'crevaison', 'crevé', 'panne', 'pneu',
    'vélo cassé', 'mécanique', 'ça va', 'pas grave'
]
```

### 2. Ajuster le prompt Gemini (API mode)

Fichier : `guardian/gemini_agent.py`, fonction `analyze_emergency_situation()`

```python
prompt = f"""...
IMPORTANT - Échelle de gravité:
- Niveau 1-3 (Faible): Problèmes mineurs...
- Niveau 4-6 (Modérée): Situations inconfortables...
...
"""
```

### 3. Ajouter de nouveaux scénarios

Fichier : `tests/urgency_scenarios/scenarios_data.py`

```python
"faible": [
    {
        "description": "Nouvelle situation à tester",
        "niveau_attendu": 2,
        "categorie": "Faible",
        "email_attendu": False,
        ...
    },
]
```

## 📊 Statistiques actuelles

La base de données contient :
- **Total** : 40+ scénarios
- **Faible** : 8 scénarios (20%)
- **Modérée** : 7 scénarios (17.5%)
- **Élevée** : 7 scénarios (17.5%)
- **Critique** : 8 scénarios (20%)
- **Ambigus** : 5 scénarios (12.5%)
- **Psychologique** : 3 scénarios (7.5%)

## 🎓 Bonnes pratiques

1. **Tester après chaque modification** du code de calibration
2. **Ajouter des scénarios** basés sur les cas réels rencontrés
3. **Maintenir la balance** entre les catégories
4. **Exporter les résultats** pour suivre l'évolution
5. **Documenter les cas problématiques** pour amélioration

## 🚀 Intégration CI/CD

Pour automatiser les tests :

```bash
# Dans votre pipeline CI/CD
python3 test_urgency_calibration.py --max-tests 20 --export
# Vérifier que le taux de réussite > 80%
```

## 📝 Contribuer

Pour ajouter des scénarios :

1. Éditer `scenarios_data.py`
2. Ajouter le scénario dans la bonne catégorie
3. Définir le niveau attendu (1-10)
4. Indiquer si email doit être envoyé
5. Tester avec `python3 test_urgency_calibration.py --category <votre_categorie>`

## 🐛 Signaler un problème

Si un scénario est mal évalué :

1. Noter la situation exacte
2. Niveau attendu vs obtenu
3. Lancer le mode interactif pour analyser
4. Ajuster les mots-clés ou le prompt
5. Re-tester

---

**Auteur** : Guardian AI Team  
**Dernière mise à jour** : 10 novembre 2025  
**Version** : 1.0.0
