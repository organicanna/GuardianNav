"""
Base de données de scénarios pour entraîner et tester Gemini
Catégorisation précise des niveaux d'urgence selon différentes situations
"""

# Structure: (description, niveau_attendu, catégorie_attendue)
SCENARIOS = {
    # ========== NIVEAU 1-3 : FAIBLE (Pas d'urgence) ==========
    "faible": [
        {
            "description": "Je suis tombé à vélo et j'ai crevé, mais ça va",
            "niveau_attendu": 2,
            "categorie": "Faible",
            "justification": "Incident mécanique sans blessure",
            "email_attendu": False,
            "services_urgence": "Aucun"
        },
        {
            "description": "Mon pneu de vélo a éclaté, je suis sur le bord de la route",
            "niveau_attendu": 2,
            "categorie": "Faible",
            "justification": "Panne mécanique simple",
            "email_attendu": False,
            "services_urgence": "Assistance routière"
        },
        {
            "description": "Je cherche une pharmacie ouverte",
            "niveau_attendu": 1,
            "categorie": "Faible",
            "justification": "Demande d'information",
            "email_attendu": False,
            "services_urgence": "Aucun"
        },
        {
            "description": "J'ai oublié mon parapluie et il pleut",
            "niveau_attendu": 1,
            "categorie": "Faible",
            "justification": "Désagrément mineur",
            "email_attendu": False,
            "services_urgence": "Aucun"
        },
        {
            "description": "Mon téléphone est presque à court de batterie",
            "niveau_attendu": 2,
            "categorie": "Faible",
            "justification": "Problème technique mineur",
            "email_attendu": False,
            "services_urgence": "Aucun"
        },
        {
            "description": "Je voudrais des conseils pour rentrer chez moi",
            "niveau_attendu": 2,
            "categorie": "Faible",
            "justification": "Demande d'orientation",
            "email_attendu": False,
            "services_urgence": "Aucun"
        },
        {
            "description": "J'ai une petite égratignure au doigt",
            "niveau_attendu": 1,
            "categorie": "Faible",
            "justification": "Blessure très mineure",
            "email_attendu": False,
            "services_urgence": "Aucun"
        },
        {
            "description": "Mon vélo a une chaîne cassée, je dois rentrer à pied",
            "niveau_attendu": 2,
            "categorie": "Faible",
            "justification": "Panne mécanique, pas de danger",
            "email_attendu": False,
            "services_urgence": "Réparation vélo"
        },
    ],
    
    # ========== NIVEAU 4-5 : MODÉRÉE (Attention mais pas critique) ==========
    "moderee": [
        {
            "description": "Je suis perdu dans un quartier que je ne connais pas",
            "niveau_attendu": 4,
            "categorie": "Modérée",
            "justification": "Situation inconfortable mais pas dangereuse",
            "email_attendu": False,
            "services_urgence": "Aucun"
        },
        {
            "description": "J'ai mal à la tête depuis ce matin",
            "niveau_attendu": 3,
            "categorie": "Faible",
            "justification": "Symptôme courant non urgent",
            "email_attendu": False,
            "services_urgence": "Médecin traitant"
        },
        {
            "description": "Je me sens un peu étourdi après avoir couru",
            "niveau_attendu": 4,
            "categorie": "Modérée",
            "justification": "Symptôme à surveiller",
            "email_attendu": False,
            "services_urgence": "Repos recommandé"
        },
        {
            "description": "J'ai trébuché et j'ai mal au genou, mais je peux marcher",
            "niveau_attendu": 4,
            "categorie": "Modérée",
            "justification": "Petite blessure sans gravité immédiate",
            "email_attendu": False,
            "services_urgence": "Glace et repos"
        },
        {
            "description": "Il fait nuit et je ne trouve pas mon chemin",
            "niveau_attendu": 5,
            "categorie": "Modérée",
            "justification": "Situation inconfortable, besoin d'aide orientation",
            "email_attendu": False,
            "services_urgence": "Aucun"
        },
        {
            "description": "J'ai raté mon dernier métro, je ne sais pas comment rentrer",
            "niveau_attendu": 4,
            "categorie": "Modérée",
            "justification": "Problème logistique sans danger immédiat",
            "email_attendu": False,
            "services_urgence": "Taxi/VTC"
        },
        {
            "description": "Je me suis tordu la cheville en marchant, ça fait un peu mal",
            "niveau_attendu": 5,
            "categorie": "Modérée",
            "justification": "Blessure mineure à surveiller",
            "email_attendu": False,
            "services_urgence": "Repos et glace"
        },
    ],
    
    # ========== NIVEAU 6-7 : ÉLEVÉE (Nécessite attention) ==========
    "elevee": [
        {
            "description": "Je suis tombé à vélo et j'ai très mal au bras",
            "niveau_attendu": 6,
            "categorie": "Modérée",
            "justification": "Chute avec douleur, consultation recommandée",
            "email_attendu": True,
            "services_urgence": "Médecin ou urgences"
        },
        {
            "description": "Je me suis coupé profondément en cuisinant, ça saigne beaucoup",
            "niveau_attendu": 7,
            "categorie": "Élevée",
            "justification": "Saignement important, intervention nécessaire",
            "email_attendu": True,
            "services_urgence": "Urgences ou SAMU (15)"
        },
        {
            "description": "J'ai chuté dans les escaliers et j'ai du mal à me relever",
            "niveau_attendu": 7,
            "categorie": "Élevée",
            "justification": "Chute sérieuse avec difficulté de mobilité",
            "email_attendu": True,
            "services_urgence": "SAMU (15)"
        },
        {
            "description": "Je ressens une douleur intense dans la poitrine",
            "niveau_attendu": 8,
            "categorie": "Critique",
            "justification": "Symptôme potentiellement cardiaque",
            "email_attendu": True,
            "services_urgence": "SAMU (15) IMMÉDIAT"
        },
        {
            "description": "Je suis seul et je me sens menacé par quelqu'un qui me suit",
            "niveau_attendu": 7,
            "categorie": "Élevée",
            "justification": "Situation de sécurité personnelle",
            "email_attendu": True,
            "services_urgence": "Police (17)"
        },
        {
            "description": "Je pense que quelqu'un me suit depuis 10 minutes",
            "niveau_attendu": 8,
            "categorie": "Élevée",
            "justification": "Harcèlement de rue, danger potentiel, durée inquiétante",
            "email_attendu": True,
            "services_urgence": "Police (17) URGENT"
        },
        {
            "description": "Une personne me suit dans la rue et ça me fait peur",
            "niveau_attendu": 8,
            "categorie": "Élevée",
            "justification": "Sentiment de menace immédiate, besoin d'intervention",
            "email_attendu": True,
            "services_urgence": "Police (17) + Contact proche"
        },
        {
            "description": "Je suis suivie et je n'ose pas rentrer chez moi",
            "niveau_attendu": 9,
            "categorie": "Critique",
            "justification": "Harcèlement grave, sécurité compromise, risque de localisation domicile",
            "email_attendu": True,
            "services_urgence": "Police (17) IMMÉDIAT + Proche"
        },
        {
            "description": "Je me suis brûlé la main avec de l'eau bouillante",
            "niveau_attendu": 6,
            "categorie": "Modérée",
            "justification": "Brûlure nécessitant soins",
            "email_attendu": True,
            "services_urgence": "Urgences ou SOS Médecins"
        },
        {
            "description": "Je suis tombé de ma moto et je ne peux pas bouger ma jambe",
            "niveau_attendu": 8,
            "categorie": "Critique",
            "justification": "Accident avec impossibilité de bouger",
            "email_attendu": True,
            "services_urgence": "SAMU (15) et Pompiers (18)"
        },
    ],
    
    # ========== NIVEAU 8-10 : CRITIQUE (Danger immédiat) ==========
    "critique": [
        {
            "description": "Je ne peux plus respirer correctement",
            "niveau_attendu": 10,
            "categorie": "Critique",
            "justification": "Détresse respiratoire vitale",
            "email_attendu": True,
            "services_urgence": "SAMU (15) URGENT"
        },
        {
            "description": "Quelqu'un m'agresse avec une arme",
            "niveau_attendu": 10,
            "categorie": "Critique",
            "justification": "Danger de mort immédiat",
            "email_attendu": True,
            "services_urgence": "Police (17) URGENT"
        },
        {
            "description": "J'ai été renversé par une voiture, je saigne beaucoup",
            "niveau_attendu": 9,
            "categorie": "Critique",
            "justification": "Accident grave avec hémorragie",
            "email_attendu": True,
            "services_urgence": "SAMU (15) + Pompiers (18)"
        },
        {
            "description": "Je pense avoir une fracture ouverte, l'os est visible",
            "niveau_attendu": 9,
            "categorie": "Critique",
            "justification": "Traumatisme sévère",
            "email_attendu": True,
            "services_urgence": "SAMU (15) URGENT"
        },
        {
            "description": "Mon père est inconscient et ne répond plus",
            "niveau_attendu": 10,
            "categorie": "Critique",
            "justification": "Perte de conscience = urgence vitale",
            "email_attendu": True,
            "services_urgence": "SAMU (15) IMMÉDIAT"
        },
        {
            "description": "J'ai fait un AVC, je ne peux plus parler ni bouger le bras droit",
            "niveau_attendu": 10,
            "categorie": "Critique",
            "justification": "AVC = urgence absolue",
            "email_attendu": True,
            "services_urgence": "SAMU (15) CODE AVC"
        },
        {
            "description": "Je suis bloqué dans un bâtiment en feu",
            "niveau_attendu": 10,
            "categorie": "Critique",
            "justification": "Danger de mort immédiat",
            "email_attendu": True,
            "services_urgence": "Pompiers (18) URGENT"
        },
        {
            "description": "J'ai ingéré des produits toxiques par accident",
            "niveau_attendu": 9,
            "categorie": "Critique",
            "justification": "Intoxication = urgence médicale",
            "email_attendu": True,
            "services_urgence": "Centre antipoison + SAMU (15)"
        },
    ],
    
    # ========== CAS AMBIGUS (à bien calibrer) ==========
    "ambigus": [
        {
            "description": "Je suis tombé dans les escaliers mais je pense que ça va",
            "niveau_attendu": 5,
            "categorie": "Modérée",
            "justification": "Chute mais personne rassurante",
            "email_attendu": False,
            "services_urgence": "Surveillance recommandée"
        },
        {
            "description": "J'ai glissé sous la pluie, j'ai un peu mal partout",
            "niveau_attendu": 4,
            "categorie": "Modérée",
            "justification": "Chute légère avec douleurs diffuses",
            "email_attendu": False,
            "services_urgence": "Repos et surveillance"
        },
        {
            "description": "Mon vélo s'est renversé à cause du vent, j'ai quelques bleus",
            "niveau_attendu": 3,
            "categorie": "Faible",
            "justification": "Incident mineur avec contusions légères",
            "email_attendu": False,
            "services_urgence": "Aucun"
        },
        {
            "description": "Je me sens un peu mal, j'ai des vertiges depuis 10 minutes",
            "niveau_attendu": 6,
            "categorie": "Modérée",
            "justification": "Symptôme persistant à surveiller",
            "email_attendu": True,
            "services_urgence": "SOS Médecins ou médecin"
        },
        {
            "description": "J'ai percuté un poteau à vélo, j'ai mal à l'épaule mais je peux bouger",
            "niveau_attendu": 5,
            "categorie": "Modérée",
            "justification": "Impact avec douleur mais mobilité conservée",
            "email_attendu": False,
            "services_urgence": "Médecin si douleur persiste"
        },
    ],
    
    # ========== SITUATIONS PSYCHOLOGIQUES ==========
    "psychologique": [
        {
            "description": "Je me sens très anxieux et j'ai du mal à respirer à cause du stress",
            "niveau_attendu": 5,
            "categorie": "Modérée",
            "justification": "Crise d'angoisse à gérer",
            "email_attendu": False,
            "services_urgence": "Numéro d'écoute ou médecin"
        },
        {
            "description": "J'ai une crise de panique, mon cœur bat très vite",
            "niveau_attendu": 6,
            "categorie": "Modérée",
            "justification": "Crise de panique nécessitant accompagnement",
            "email_attendu": True,
            "services_urgence": "SOS Médecins ou SAMU si aggravation"
        },
        {
            "description": "Je me sens en danger mais je ne sais pas pourquoi",
            "niveau_attendu": 6,
            "categorie": "Modérée",
            "justification": "Sentiment d'insécurité à prendre au sérieux",
            "email_attendu": True,
            "services_urgence": "Évaluation de la situation"
        },
    ],
}

# Fonction pour obtenir tous les scénarios
def get_all_scenarios():
    """Retourne tous les scénarios dans une liste unique"""
    all_scenarios = []
    for category, scenarios in SCENARIOS.items():
        for scenario in scenarios:
            scenario['category_type'] = category
            all_scenarios.append(scenario)
    return all_scenarios

# Fonction pour obtenir les scénarios par niveau
def get_scenarios_by_level(min_level, max_level):
    """Retourne les scénarios dans une plage de niveaux"""
    all_scenarios = get_all_scenarios()
    return [s for s in all_scenarios if min_level <= s['niveau_attendu'] <= max_level]

# Statistiques
def get_statistics():
    """Retourne des statistiques sur les scénarios"""
    all_scenarios = get_all_scenarios()
    return {
        "total": len(all_scenarios),
        "faible": len([s for s in all_scenarios if s['niveau_attendu'] <= 3]),
        "moderee": len([s for s in all_scenarios if 4 <= s['niveau_attendu'] <= 5]),
        "elevee": len([s for s in all_scenarios if 6 <= s['niveau_attendu'] <= 7]),
        "critique": len([s for s in all_scenarios if s['niveau_attendu'] >= 8]),
        "avec_email": len([s for s in all_scenarios if s['email_attendu']]),
        "sans_email": len([s for s in all_scenarios if not s['email_attendu']]),
    }
