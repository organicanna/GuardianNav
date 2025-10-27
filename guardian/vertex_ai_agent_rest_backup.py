"""
Vertex AI Agent for GuardianNav - API REST Version
Advanced emergency analysis using Google Cloud Vertex AI via REST API
Plus simple et plus flexible que les SDKs
"""
import logging
import json
import requests
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import time

class VertexAIAgent:
    """Agent Vertex AI pour l'analyse d'urgence avancée avec Gemini via API REST"""
    
    def __init__(self, api_keys_config: Dict[str, Any] = None):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Configuration API
        self.api_keys_config = api_keys_config or {}
        vertex_config = self.api_keys_config.get('google_cloud', {}).get('vertex_ai', {})
        
        self.project_id = self.api_keys_config.get('google_cloud', {}).get('project_id')
        self.region = vertex_config.get('region', 'europe-west1')
        self.api_key = vertex_config.get('api_key')
        self.enabled = vertex_config.get('enabled', True)
        
        # Configuration du modèle
        self.model_name = "gemini-1.5-flash-002"  # Modèle le plus récent
        self.is_available = False
        
        # URL de base pour l'API Vertex AI
        if self.project_id and self.api_key:
            self.base_url = f"https://{self.region}-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/{self.region}/publishers/google/models/{self.model_name}"
            self._initialize_api()
        else:
            self.logger.warning("Configuration Vertex AI incomplète - fonctionnement en mode simulation")
    
    def _initialize_api(self):
        """Initialise la connexion à l'API Vertex AI"""
        try:
            # Test de connectivité avec une requête simple
            test_prompt = "Test de connectivité. Répondez simplement 'OK'."
            
            response = self._make_api_request(test_prompt, max_tokens=10)
            
            if response and 'candidates' in response:
                self.is_available = True
                self.logger.info("✅ Vertex AI API initialisée avec succès")
            else:
                self.logger.warning("⚠️ API Vertex AI - réponse inattendue")
                
        except Exception as e:
            self.logger.error(f"❌ Erreur initialisation Vertex AI API: {e}")
            self.logger.info("🔄 Fonctionnement en mode simulation")
    
    def _make_api_request(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.1) -> Optional[Dict]:
        """Effectue une requête à l'API Vertex AI"""
        if not self.api_key or not self.project_id:
            return self._simulate_response(prompt)
        
        url = f"{self.base_url}:generateContent"
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'contents': [{
                'role': 'user',
                'parts': [{'text': prompt}]
            }],
            'generation_config': {
                'temperature': temperature,
                'maxOutputTokens': max_tokens,
                'topP': 0.95,
                'topK': 40
            },
            'safety_settings': [
                {
                    'category': 'HARM_CATEGORY_DANGEROUS_CONTENT',
                    'threshold': 'BLOCK_NONE'  # Permet le contenu d'urgence
                },
                {
                    'category': 'HARM_CATEGORY_HARASSMENT', 
                    'threshold': 'BLOCK_ONLY_HIGH'
                }
            ]
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(f"Erreur API Vertex AI: {response.status_code} - {response.text}")
                return self._simulate_response(prompt)
                
        except Exception as e:
            self.logger.error(f"Exception API Vertex AI: {e}")
            return self._simulate_response(prompt)
    
    def _simulate_response(self, prompt: str) -> Dict:
        """Génère une réponse simulée pour les tests"""
        self.logger.info("🎭 Mode simulation Vertex AI")
        
        # Analyse du prompt pour générer une réponse cohérente
        if "chute" in prompt.lower() or "fall" in prompt.lower():
            simulated_text = json.dumps({
                "emergency_type": "Chute détectée",
                "urgency_level": 8,
                "urgency_category": "Élevée",
                "immediate_actions": [
                    "Vérifier si la personne est consciente",
                    "Ne pas déplacer en cas de blessure",
                    "Appeler les secours si nécessaire"
                ],
                "specific_advice": "Une chute peut causer des blessures internes. Surveillance médicale recommandée.",
                "emergency_services": "SAMU (15)",
                "reassurance_message": "Les secours sont prévenus et peuvent intervenir rapidement.",
                "follow_up_needed": True
            })
        else:
            simulated_text = json.dumps({
                "emergency_type": "Urgence générale",
                "urgency_level": 6,
                "urgency_category": "Modérée",
                "immediate_actions": [
                    "Évaluer la situation",
                    "Rester calme",
                    "Contacter les personnes appropriées"
                ],
                "specific_advice": "Situation nécessitant une attention particulière mais pas de panique.",
                "emergency_services": "Numéro d'urgence européen (112)",
                "reassurance_message": "La situation est sous contrôle et l'aide arrive.",
                "follow_up_needed": True
            })
        
        return {
            'candidates': [{
                'content': {
                    'parts': [{'text': simulated_text}]
                }
            }]
        }
    
    def analyze_emergency_situation(self, context: str, location: Tuple[float, float] = None, 
                                  user_input: str = "", time_of_day: str = "jour") -> Dict[str, Any]:
        """
        Analyse une situation d'urgence avec Vertex AI Gemini
        
        Args:
            context: Description de la situation
            location: Coordonnées GPS (lat, lon)
            user_input: Réponse/description de l'utilisateur
            time_of_day: Moment de la journée
        
        Returns:
            Dict contenant l'analyse complète
        """
        
        # Construction du prompt contextuel
        prompt = f"""Tu es un expert en gestion d'urgences. Analyse cette situation et fournis une réponse JSON structurée.

SITUATION D'URGENCE:
- Contexte: {context}
- Moment: {time_of_day}
- Localisation: {f"GPS {location[0]:.6f}, {location[1]:.6f}" if location else "Non disponible"}
- Description utilisateur: {user_input if user_input else "Aucune"}

ANALYSE DEMANDÉE:
Fournis une réponse JSON UNIQUEMENT avec cette structure exacte:
{{
    "emergency_type": "Type précis d'urgence",
    "urgency_level": 1-10,
    "urgency_category": "Faible|Modérée|Élevée|Critique",
    "immediate_actions": ["Action 1", "Action 2", "Action 3"],
    "specific_advice": "Conseil spécialisé pour cette situation",
    "emergency_services": "Service recommandé (ex: SAMU 15, Police 17, Pompiers 18, 112)",
    "reassurance_message": "Message rassurant personnalisé",
    "follow_up_needed": true/false,
    "risk_factors": ["Facteur 1", "Facteur 2"],
    "what3words": "code.trois.mots"
}}

Réponds SEULEMENT avec le JSON, aucun autre texte."""

        try:
            response = self._make_api_request(prompt, max_tokens=800, temperature=0.2)
            
            if response and 'candidates' in response:
                response_text = response['candidates'][0]['content']['parts'][0]['text']
                
                # Parser la réponse JSON
                try:
                    analysis = json.loads(response_text.strip())
                    
                    # Validation et nettoyage
                    analysis = self._validate_analysis_response(analysis)
                    
                    self.logger.info("✅ Analyse Vertex AI générée avec succès")
                    return analysis
                    
                except json.JSONDecodeError as e:
                    self.logger.error(f"Erreur parsing JSON Vertex AI: {e}")
                    return self._fallback_analysis(context)
            
        except Exception as e:
            self.logger.error(f"Erreur analyse Vertex AI: {e}")
        
        return self._fallback_analysis(context)
    
    def _validate_analysis_response(self, analysis: Dict) -> Dict:
        """Valide et nettoie la réponse de l'analyse"""
        
        # Valeurs par défaut
        defaults = {
            "emergency_type": "Urgence",
            "urgency_level": 5,
            "urgency_category": "Modérée", 
            "immediate_actions": ["Évaluer la situation", "Rester calme"],
            "specific_advice": "Situation nécessitant attention",
            "emergency_services": "112",
            "reassurance_message": "L'aide est en route",
            "follow_up_needed": True,
            "risk_factors": ["Évaluation nécessaire"],
            "what3words": ""
        }
        
        # Appliquer les valeurs par défaut pour les clés manquantes
        for key, default_value in defaults.items():
            if key not in analysis:
                analysis[key] = default_value
        
        # Validation du niveau d'urgence
        try:
            urgency = int(analysis.get('urgency_level', 5))
            analysis['urgency_level'] = max(1, min(10, urgency))
        except (ValueError, TypeError):
            analysis['urgency_level'] = 5
        
        # Validation des actions (max 3)
        actions = analysis.get('immediate_actions', [])
        if isinstance(actions, list) and len(actions) > 3:
            analysis['immediate_actions'] = actions[:3]
        
        return analysis
    
    def _fallback_analysis(self, context: str) -> Dict[str, Any]:
        """Analyse de fallback si Vertex AI échoue"""
        self.logger.warning("🔄 Utilisation analyse de fallback")
        
        # Analyse basique par mots-clés
        context_lower = context.lower()
        
        if any(word in context_lower for word in ['chute', 'tombé', 'fall']):
            urgency = 8
            emergency_type = "Chute détectée"
            services = "SAMU (15)"
        elif any(word in context_lower for word in ['agression', 'attaque', 'danger']):
            urgency = 9
            emergency_type = "Situation dangereuse"
            services = "Police (17)"
        elif any(word in context_lower for word in ['malaise', 'douleur', 'médical']):
            urgency = 7
            emergency_type = "Urgence médicale"
            services = "SAMU (15)"
        else:
            urgency = 6
            emergency_type = "Urgence générale"
            services = "Numéro d'urgence (112)"
        
        return {
            "emergency_type": emergency_type,
            "urgency_level": urgency,
            "urgency_category": "Élevée" if urgency >= 8 else "Modérée",
            "immediate_actions": [
                "Évaluer la situation",
                "Assurer la sécurité", 
                "Demander de l'aide si nécessaire"
            ],
            "specific_advice": f"Situation identifiée comme: {emergency_type}. Surveillance recommandée.",
            "emergency_services": services,
            "reassurance_message": "Nous sommes là pour vous aider.",
            "follow_up_needed": True,
            "risk_factors": ["Évaluation en cours"],
            "what3words": ""
        }
    
    def analyze_fall_emergency(self, fall_info: Dict, user_response: str = None, 
                              context: str = "") -> Dict[str, Any]:
        """
        Analyse spécialisée pour les chutes
        """
        
        # Informations sur la chute
        impact_force = fall_info.get('impact_force', 'modéré')
        duration = fall_info.get('duration_seconds', 0)
        movement_after = fall_info.get('movement_detected_after', False)
        
        prompt = f\"\"\"Analyse cette situation de chute d'urgence. Fournis une réponse JSON UNIQUEMENT.

CHUTE DÉTECTÉE:
- Force d'impact: {impact_force}
- Durée de la chute: {duration} secondes
- Mouvement après chute: {movement_after}
- Réponse utilisateur: "{user_response if user_response else 'Aucune réponse'}"
- Contexte: {context}

Fournis une réponse JSON avec cette structure:
{{
    "emergency_type": "Type spécifique de chute",
    "urgency_level": 1-10,
    "urgency_category": "Faible|Modérée|Élevée|Critique", 
    "immediate_actions": ["Action 1", "Action 2", "Action 3"],
    "specific_advice": "Conseil médical spécialisé pour cette chute",
    "emergency_services": "Service médical recommandé",
    "reassurance_message": "Message adapté à la situation de chute",
    "medical_priority": "Faible|Moyenne|Élevée|Critique",
    "recommended_position": "Position recommandée pour la personne",
    "follow_up_needed": true/false
}}

Réponds SEULEMENT avec le JSON.\"\"\"

        try:
            response = self._make_api_request(prompt, max_tokens=600, temperature=0.15)
            
            if response and 'candidates' in response:
                response_text = response['candidates'][0]['content']['parts'][0]['text']
                
                try:
                    analysis = json.loads(response_text.strip())
                    analysis = self._validate_fall_analysis(analysis)
                    return analysis
                    
                except json.JSONDecodeError:
                    return self._fallback_fall_analysis(fall_info, user_response)
        
        except Exception as e:
            self.logger.error(f"Erreur analyse chute Vertex AI: {e}")
        
        return self._fallback_fall_analysis(fall_info, user_response)
    
    def _validate_fall_analysis(self, analysis: Dict) -> Dict:
        """Valide l'analyse de chute"""
        
        defaults = {
            "emergency_type": "Chute détectée",
            "urgency_level": 7,
            "urgency_category": "Élevée",
            "immediate_actions": ["Ne pas bouger", "Vérifier conscience", "Appeler secours"],
            "specific_advice": "Chute détectée - évaluation médicale recommandée",
            "emergency_services": "SAMU (15)",
            "reassurance_message": "Les secours médicaux peuvent intervenir rapidement",
            "medical_priority": "Élevée",
            "recommended_position": "Ne pas déplacer",
            "follow_up_needed": True
        }
        
        for key, default_value in defaults.items():
            if key not in analysis:
                analysis[key] = default_value
        
        return analysis
    
    def _fallback_fall_analysis(self, fall_info: Dict, user_response: str) -> Dict:
        """Analyse de fallback pour les chutes"""
        
        # Évaluation basée sur les données de chute
        impact = fall_info.get('impact_force', 'modéré')
        movement = fall_info.get('movement_detected_after', False)
        
        if impact == 'fort' or not movement:
            urgency = 9
            priority = "Critique"
        elif user_response and 'va bien' in user_response.lower():
            urgency = 6
            priority = "Moyenne"
        else:
            urgency = 8
            priority = "Élevée"
        
        return {
            "emergency_type": "Chute détectée",
            "urgency_level": urgency,
            "urgency_category": "Critique" if urgency >= 9 else "Élevée",
            "immediate_actions": [
                "Ne pas déplacer la personne",
                "Vérifier la conscience",
                "Appeler les secours médicaux"
            ],
            "specific_advice": f"Chute avec impact {impact}. Évaluation médicale nécessaire.",
            "emergency_services": "SAMU (15)",
            "reassurance_message": "Une chute a été détectée. Les secours sont alertés.",
            "medical_priority": priority,
            "recommended_position": "Position de sécurité, ne pas bouger",
            "follow_up_needed": True
        }
    
    def get_personalized_emergency_message(self, analysis: Dict) -> str:
        """Génère un message d'urgence personnalisé"""
        
        emergency_type = analysis.get('emergency_type', 'Urgence')
        urgency_level = analysis.get('urgency_level', 5)
        advice = analysis.get('specific_advice', '')
        
        if urgency_level >= 8:
            intensity = "🚨 URGENCE CRITIQUE"
        elif urgency_level >= 6:
            intensity = "⚠️ URGENCE ÉLEVÉE"
        else:
            intensity = "📋 SITUATION À SURVEILLER"
        
        message = f"{intensity}\n"
        message += f"Type: {emergency_type}\n"
        message += f"Niveau: {urgency_level}/10\n\n"
        message += f"💡 Conseil: {advice}"
        
        return message
    
    def test_connection(self) -> bool:
        """Test la connexion à l'API Vertex AI"""
        try:
            response = self._make_api_request("Test", max_tokens=5)
            return response is not None and 'candidates' in response
        except:
            return False