"""
Vertex AI Agent for GuardianNav
Advanced emergency analysis using Google Cloud Vertex AI and Gemini
"""
import logging
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import os

try:
    import vertexai
    from vertexai.generative_models import GenerativeModel, Part, SafetySetting, HarmCategory
    VERTEX_AI_AVAILABLE = True
except ImportError:
    VERTEX_AI_AVAILABLE = False

class VertexAIAgent:
    """Agent Vertex AI pour l'analyse d'urgence avancée avec Gemini"""
    
    def __init__(self, api_keys_config: Dict[str, Any] = None):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Configuration API
        self.api_keys_config = api_keys_config or {}
        self.project_id = self.api_keys_config.get('google_cloud', {}).get('project_id')
        self.location = "europe-west1"  # Région Europe pour latence optimale
        
        # Modèles Vertex AI
        self.gemini_model = None
        self.is_available = False
        
        if VERTEX_AI_AVAILABLE and self.project_id:
            self._initialize_vertex_ai()
        else:
            self.logger.warning("Vertex AI non disponible - Vérifiez l'installation et la configuration")
    
    def _initialize_vertex_ai(self):
        """Initialise Vertex AI et les modèles"""
        try:
            # Initialiser Vertex AI
            vertexai.init(project=self.project_id, location=self.location)
            
            # Configuration de sécurité pour les urgences (moins restrictive)
            safety_settings = [
                SafetySetting(
                    category=HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                    threshold=SafetySetting.HarmBlockThreshold.BLOCK_ONLY_HIGH
                ),
                SafetySetting(
                    category=HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                    threshold=SafetySetting.HarmBlockThreshold.BLOCK_ONLY_HIGH
                ),
                SafetySetting(
                    category=HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                    threshold=SafetySetting.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
                ),
                SafetySetting(
                    category=HarmCategory.HARM_CATEGORY_HARASSMENT,
                    threshold=SafetySetting.HarmBlockThreshold.BLOCK_ONLY_HIGH
                ),
            ]
            
            # Initialiser Gemini Pro
            self.gemini_model = GenerativeModel(
                "gemini-1.5-flash-002",  # Modèle le plus récent
                safety_settings=safety_settings,
                system_instruction=self._get_system_instruction()
            )
            
            self.is_available = True
            self.logger.info(f"Vertex AI initialisé - Projet: {self.project_id}, Région: {self.location}")
            
        except Exception as e:
            self.logger.error(f"Erreur initialisation Vertex AI: {e}")
            self.is_available = False
    
    def _get_system_instruction(self) -> str:
        """Instructions système pour Gemini spécialisé urgences"""
        return """Tu es l'assistant IA de GuardianNav, un système de sécurité personnel avancé.

RÔLE : Expert en analyse de situations d'urgence et conseils de sécurité.

EXPERTISE :
- Médecine d'urgence et premiers secours
- Sécurité urbaine et prévention des risques
- Navigation et transport en urgence
- Psychologie de crise et communication d'urgence

CONTEXTE FRANÇAIS :
- Numéros d'urgence France (15: SAMU, 17: Police, 18: Pompiers, 112: Urgence européenne)
- Système de santé français
- Transports publics français (RATP, SNCF)
- Législation française sur l'assistance à personne en danger

CONSIGNES :
1. TOUJOURS prioriser la sécurité de la personne
2. Donner des conseils clairs, courts et actionnables
3. Adapter les conseils au contexte (lieu, heure, situation)
4. Mentionner les services d'urgence appropriés
5. Être rassurant mais réaliste
6. Répondre en français exclusivement

STYLE :
- Direct et professionnel
- Empathique sans être alarmiste
- Instructions numérotées quand approprié
- Mentionner les risques importants"""

    def analyze_emergency_situation(self, 
                                  situation_description: str,
                                  context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyse une situation d'urgence avec Gemini et retourne des conseils
        
        Args:
            situation_description: Description de la situation par l'utilisateur
            context: Contexte additionnel (position, vitesse, type d'alerte, etc.)
            
        Returns:
            Dict avec analyse, conseils, niveau d'urgence, actions immédiates
        """
        if not self.is_available:
            return self._fallback_analysis(situation_description, context)
        
        try:
            # Construire le prompt d'analyse
            prompt = self._build_emergency_prompt(situation_description, context)
            
            # Générer la réponse avec Gemini
            response = self.gemini_model.generate_content(prompt)
            
            # Parser et structurer la réponse
            return self._parse_gemini_response(response.text, situation_description, context)
            
        except Exception as e:
            self.logger.error(f"Erreur analyse Vertex AI: {e}")
            return self._fallback_analysis(situation_description, context)
    
    def _build_emergency_prompt(self, situation: str, context: Dict[str, Any] = None) -> str:
        """Construit le prompt d'analyse pour Gemini"""
        
        current_time = datetime.now()
        base_prompt = f"""ANALYSE D'URGENCE - {current_time.strftime('%H:%M %d/%m/%Y')}

SITUATION RAPPORTÉE :
"{situation}"

CONTEXTE TECHNIQUE :"""
        
        if context:
            if context.get('position'):
                lat, lon = context['position']
                base_prompt += f"\n- Position GPS: {lat:.6f}, {lon:.6f}"
            
            if context.get('trigger_type'):
                base_prompt += f"\n- Type d'alerte: {context['trigger_type']}"
            
            if context.get('fall_info'):
                fall = context['fall_info']
                base_prompt += f"\n- Chute détectée: {fall.get('fall_type', 'inconnue')}"
                base_prompt += f"\n- Sévérité: {fall.get('severity', 'inconnue')}"
                if fall.get('previous_speed'):
                    base_prompt += f"\n- Vitesse avant chute: {fall['previous_speed']:.1f} km/h"
                if fall.get('acceleration'):
                    base_prompt += f"\n- Décélération: {fall['acceleration']:.1f} m/s²"
            
            if context.get('duration'):
                base_prompt += f"\n- Durée situation: {context['duration']} secondes"
            
            if context.get('time_of_day'):
                base_prompt += f"\n- Moment: {context['time_of_day']}"
        
        base_prompt += f"""

ANALYSE REQUISE :
1. NIVEAU D'URGENCE : Évalue de 1-10 la criticité
2. TYPE D'URGENCE : Catégorise (médical, sécurité, accident, etc.)
3. RISQUES IDENTIFIÉS : Liste les dangers potentiels
4. ACTIONS IMMÉDIATES : 3-5 actions concrètes prioritaires
5. SERVICES À CONTACTER : Quel numéro d'urgence si nécessaire
6. CONSEILS SPÉCIFIQUES : Adaptés à la situation exacte

FORMAT RÉPONSE JSON :
{{
    "urgency_level": <1-10>,
    "urgency_category": "<catégorie>",
    "emergency_type": "<type d'urgence>",
    "risks_identified": ["<risque1>", "<risque2>"],
    "immediate_actions": ["<action1>", "<action2>", "<action3>"],
    "emergency_services": "<numéro si nécessaire ou 'Aucun'>",
    "specific_advice": "<conseils personnalisés>",
    "reassurance_message": "<message rassurant>",
    "follow_up_needed": <true/false>
}}

ANALYSE :"""
        
        return base_prompt
    
    def _parse_gemini_response(self, response_text: str, situation: str, context: Dict = None) -> Dict[str, Any]:
        """Parse et valide la réponse de Gemini"""
        
        try:
            # Nettoyer la réponse pour extraire le JSON
            cleaned_response = response_text.strip()
            
            # Chercher le JSON dans la réponse
            json_start = cleaned_response.find('{')
            json_end = cleaned_response.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_content = cleaned_response[json_start:json_end]
                analysis = json.loads(json_content)
            else:
                # Fallback si pas de JSON valide
                return self._extract_analysis_from_text(response_text, situation)
            
            # Valider et enrichir la réponse
            validated_analysis = self._validate_analysis(analysis)
            
            # Ajouter des métadonnées
            validated_analysis.update({
                'ai_source': 'vertex_ai_gemini',
                'analysis_timestamp': datetime.now().isoformat(),
                'context_used': bool(context),
                'raw_situation': situation
            })
            
            return validated_analysis
            
        except json.JSONDecodeError as e:
            self.logger.warning(f"Erreur parsing JSON Gemini: {e}")
            return self._extract_analysis_from_text(response_text, situation)
        except Exception as e:
            self.logger.error(f"Erreur traitement réponse Gemini: {e}")
            return self._fallback_analysis(situation, context)
    
    def _extract_analysis_from_text(self, text: str, situation: str) -> Dict[str, Any]:
        """Extrait l'analyse d'un texte libre quand le JSON échoue"""
        
        # Analyse basique par mots-clés
        text_lower = text.lower()
        
        # Déterminer le niveau d'urgence
        if any(word in text_lower for word in ['critique', 'vital', 'grave', 'danger', 'immédiat']):
            urgency_level = 8
            urgency_category = "critique"
        elif any(word in text_lower for word in ['urgent', 'important', 'rapide', 'vite']):
            urgency_level = 6
            urgency_category = "élevée"
        else:
            urgency_level = 4
            urgency_category = "modérée"
        
        # Extraire les actions (lignes avec des tirets ou numéros)
        actions = []
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if (line.startswith('-') or line.startswith('•') or 
                any(line.startswith(f"{i}.") for i in range(1, 10))):
                actions.append(line.lstrip('-.•0123456789 '))
        
        return {
            'urgency_level': urgency_level,
            'urgency_category': urgency_category,
            'emergency_type': 'Analyse textuelle',
            'immediate_actions': actions[:5],
            'specific_advice': text[:300] + "..." if len(text) > 300 else text,
            'ai_source': 'vertex_ai_text_extraction',
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    def _validate_analysis(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Valide et normalise l'analyse de Gemini"""
        
        validated = {
            'urgency_level': max(1, min(10, analysis.get('urgency_level', 5))),
            'urgency_category': analysis.get('urgency_category', 'modérée'),
            'emergency_type': analysis.get('emergency_type', 'Situation d\'urgence'),
            'risks_identified': analysis.get('risks_identified', []),
            'immediate_actions': analysis.get('immediate_actions', [])[:5],  # Max 5 actions
            'emergency_services': analysis.get('emergency_services', 'Aucun'),
            'specific_advice': analysis.get('specific_advice', 'Restez calme et évaluez la situation.'),
            'reassurance_message': analysis.get('reassurance_message', 'Nous analysons votre situation.'),
            'follow_up_needed': analysis.get('follow_up_needed', True)
        }
        
        return validated
    
    def _fallback_analysis(self, situation: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyse de fallback quand Vertex AI n'est pas disponible"""
        
        situation_lower = situation.lower()
        
        # Analyse par mots-clés
        if any(word in situation_lower for word in ['chute', 'tombé', 'accident', 'blessé', 'mal', 'douleur']):
            return {
                'urgency_level': 7,
                'urgency_category': 'élevée',
                'emergency_type': 'Accident/Blessure',
                'immediate_actions': [
                    'Ne bougez pas si vous avez mal au cou ou au dos',
                    'Évaluez vos blessures progressivement',
                    'Appelez le 15 si douleurs importantes',
                    'Restez au chaud et hydraté'
                ],
                'specific_advice': 'Après un accident, il est important de ne pas précipiter les mouvements.',
                'ai_source': 'fallback_analysis'
            }
        elif any(word in situation_lower for word in ['perdu', 'peur', 'aide', 'secours']):
            return {
                'urgency_level': 5,
                'urgency_category': 'modérée',
                'emergency_type': 'Détresse/Aide',
                'immediate_actions': [
                    'Restez calme et respirez profondément',
                    'Décrivez votre situation et position',
                    'Restez en contact avec vos proches',
                    'Cherchez un lieu sûr si possible'
                ],
                'specific_advice': 'Nous sommes là pour vous aider. Décrivez votre situation.',
                'ai_source': 'fallback_analysis'
            }
        else:
            return {
                'urgency_level': 4,
                'urgency_category': 'modérée',
                'emergency_type': 'Situation générale',
                'immediate_actions': [
                    'Évaluez votre état et votre environnement',
                    'Contactez vos proches si nécessaire',
                    'Restez dans un lieu sûr'
                ],
                'specific_advice': 'Prenez le temps d\'évaluer votre situation calmement.',
                'ai_source': 'fallback_analysis'
            }
    
    def analyze_fall_emergency(self, fall_info: Dict[str, Any], user_response: str = None) -> Dict[str, Any]:
        """Analyse spécialisée pour les chutes avec contexte technique"""
        
        context = {
            'trigger_type': 'chute_detectee',
            'fall_info': fall_info,
            'time_of_day': datetime.now().strftime('%H:%M')
        }
        
        if user_response:
            situation = f"Chute détectée par capteurs. Utilisateur dit: '{user_response}'"
        else:
            situation = f"Chute de type {fall_info.get('fall_type', 'inconnue')} détectée automatiquement par les capteurs. Aucune réponse de l'utilisateur."
        
        analysis = self.analyze_emergency_situation(situation, context)
        
        # Enrichir avec des conseils spécifiques aux chutes
        analysis['fall_specific_advice'] = self._get_fall_specific_advice(fall_info)
        
        return analysis
    
    def _get_fall_specific_advice(self, fall_info: Dict[str, Any]) -> List[str]:
        """Conseils spécifiques selon le type de chute"""
        
        fall_type = fall_info.get('fall_type', 'chute_generale')
        severity = fall_info.get('severity', 'modérée')
        
        if fall_type == 'chute_velo':
            return [
                "Vérifiez votre casque et retirez-le délicatement si fissuré",
                "Examinez vos mains, genoux et coudes",
                "Testez vos articulations avant de vous relever",
                "Vérifiez l'état de votre vélo avant de repartir"
            ]
        elif fall_type == 'chute_haute_vitesse':
            return [
                "NE BOUGEZ PAS immédiatement après l'impact", 
                "Vérifiez votre conscience et orientation",
                "Testez votre vision et audition",
                "Appelez immédiatement le 15 si confusion"
            ]
        elif fall_type == 'impact_brutal':
            return [
                "Restez immobile et respirez calmement",
                "Vérifiez l'absence de douleur au cou/dos",
                "Testez la mobilité de vos doigts et orteils",
                "N'hésitez pas à appeler les secours si doute"
            ]
        else:
            return [
                "Prenez votre temps avant de vous relever",
                "Levez-vous progressivement en plusieurs étapes",
                "Vérifiez l'absence de vertiges",
                "Hydratez-vous après la chute"
            ]
    
    def get_personalized_emergency_message(self, analysis: Dict[str, Any]) -> str:
        """Génère un message personnalisé basé sur l'analyse"""
        
        urgency = analysis.get('urgency_level', 5)
        advice = analysis.get('specific_advice', '')
        
        if urgency >= 8:
            prefix = "🚨 URGENCE CRITIQUE 🚨\n"
        elif urgency >= 6:
            prefix = "⚠️ SITUATION URGENTE ⚠️\n"
        else:
            prefix = "ℹ️ Situation à surveiller\n"
        
        actions_text = ""
        actions = analysis.get('immediate_actions', [])
        if actions:
            actions_text = "\n📋 ACTIONS IMMÉDIATES:\n"
            for i, action in enumerate(actions[:3], 1):
                actions_text += f"   {i}. {action}\n"
        
        return f"{prefix}{advice}{actions_text}"
    
    def test_vertex_ai_connection(self) -> Dict[str, Any]:
        """Teste la connexion Vertex AI"""
        
        if not self.is_available:
            return {
                'success': False,
                'message': 'Vertex AI non configuré',
                'details': 'Vérifiez l\'installation et la configuration du projet'
            }
        
        try:
            test_analysis = self.analyze_emergency_situation(
                "Test de connexion Vertex AI pour GuardianNav", 
                {'trigger_type': 'test_system'}
            )
            
            return {
                'success': True,
                'message': 'Vertex AI opérationnel',
                'details': f"Projet: {self.project_id}, Région: {self.location}",
                'test_analysis': test_analysis
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Erreur test Vertex AI: {e}',
                'details': 'Vérifiez les permissions et la configuration'
            }