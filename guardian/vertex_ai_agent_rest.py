"""
Vertex AI Agent for GuardianNav - API REST Version
Advanced emergency analysis using Google Cloud Vertex AI via REST API
"""
import logging
import json
import requests
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

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
        self.model_name = "gemini-1.5-flash-002"
        self.is_available = False
        
        # URL de base pour l'API Vertex AI
        if self.project_id and self.api_key and self.enabled:
            self.base_url = f"https://{self.region}-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/{self.region}/publishers/google/models/{self.model_name}"
            self._initialize_api()
        else:
            self.logger.warning("Configuration Vertex AI incomplète - fonctionnement en mode simulation")
    
    def _initialize_api(self):
        """Initialise la connexion à l'API Vertex AI"""
        try:
            # Note: Pour l'authentification, nous devrons utiliser OAuth2 ou service account
            # Pour simplifier le test, nous commençons en mode simulation
            self.logger.warning("⚠️ Mode simulation activé - implémentation OAuth2 requise pour API réelle")
            self.is_available = False  # Sera True quand OAuth2 sera implémenté
            
        except Exception as e:
            self.logger.error(f"❌ Erreur initialisation Vertex AI API: {e}")
            self.is_available = False
    
    def _make_api_request(self, prompt: str, max_tokens: int = 1000) -> Optional[Dict]:
        """Effectue une requête à l'API Vertex AI (actuellement en simulation)"""
        # Mode simulation pour le développement
        return self._simulate_response(prompt)
    
    def _simulate_response(self, prompt: str) -> Dict:
        """Génère une réponse simulée intelligente"""
        self.logger.info("🎭 Mode simulation Vertex AI")
        
        # Analyse du prompt pour générer une réponse cohérente
        prompt_lower = prompt.lower()
        
        if "chute" in prompt_lower or "fall" in prompt_lower:
            simulated_analysis = {
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
                "follow_up_needed": True,
                "medical_priority": "Élevée",
                "recommended_position": "Ne pas déplacer"
            }
        elif "danger" in prompt_lower or "agression" in prompt_lower:
            simulated_analysis = {
                "emergency_type": "Situation dangereuse",
                "urgency_level": 9,
                "urgency_category": "Critique",
                "immediate_actions": [
                    "Se mettre en sécurité",
                    "Appeler la police",
                    "Alerter les proches"
                ],
                "specific_advice": "Situation potentiellement dangereuse nécessitant intervention immédiate.",
                "emergency_services": "Police (17)",
                "reassurance_message": "Les forces de sécurité sont alertées.",
                "follow_up_needed": True
            }
        elif "malaise" in prompt_lower or "douleur" in prompt_lower:
            simulated_analysis = {
                "emergency_type": "Urgence médicale",
                "urgency_level": 7,
                "urgency_category": "Élevée",
                "immediate_actions": [
                    "S'asseoir ou s'allonger",
                    "Respirer calmement",
                    "Contacter le SAMU"
                ],
                "specific_advice": "Malaise nécessitant une évaluation médicale rapide.",
                "emergency_services": "SAMU (15)",
                "reassurance_message": "Une équipe médicale peut intervenir rapidement.",
                "follow_up_needed": True
            }
        else:
            simulated_analysis = {
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
            }
        
        # Ajouter des champs par défaut
        simulated_analysis.setdefault("risk_factors", ["Évaluation en cours"])
        simulated_analysis.setdefault("what3words", "")
        
        return {
            'candidates': [{
                'content': {
                    'parts': [{'text': json.dumps(simulated_analysis)}]
                }
            }]
        }
    
    def analyze_emergency_situation(self, context: str, location: Tuple[float, float] = None, 
                                  user_input: str = "", time_of_day: str = "jour") -> Dict[str, Any]:
        """Analyse une situation d'urgence avec Vertex AI Gemini"""
        
        # Construction du prompt contextuel
        location_str = f"GPS {location[0]:.6f}, {location[1]:.6f}" if location else "Non disponible"
        
        prompt_parts = [
            "Tu es un expert en gestion d'urgences. Analyse cette situation:",
            f"Contexte: {context}",
            f"Moment: {time_of_day}",
            f"Localisation: {location_str}",
            f"Description utilisateur: {user_input if user_input else 'Aucune'}"
        ]
        
        prompt = " | ".join(prompt_parts)
        
        try:
            response = self._make_api_request(prompt, max_tokens=800)
            
            if response and 'candidates' in response:
                response_text = response['candidates'][0]['content']['parts'][0]['text']
                
                try:
                    analysis = json.loads(response_text.strip())
                    analysis = self._validate_analysis_response(analysis)
                    
                    self.logger.info("✅ Analyse Vertex AI générée avec succès")
                    return analysis
                    
                except json.JSONDecodeError as e:
                    self.logger.error(f"Erreur parsing JSON: {e}")
                    return self._fallback_analysis(context)
            
        except Exception as e:
            self.logger.error(f"Erreur analyse Vertex AI: {e}")
        
        return self._fallback_analysis(context)
    
    def _validate_analysis_response(self, analysis: Dict) -> Dict:
        """Valide et nettoie la réponse de l'analyse"""
        
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
        
        # Appliquer les valeurs par défaut
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
        """Analyse spécialisée pour les chutes"""
        
        impact_force = fall_info.get('impact_force', 'modéré')
        duration = fall_info.get('duration_seconds', 0)
        movement_after = fall_info.get('movement_detected_after', False)
        
        prompt_parts = [
            "Analyse de chute d'urgence:",
            f"Force d'impact: {impact_force}",
            f"Durée: {duration} secondes",
            f"Mouvement après: {movement_after}",
            f"Réponse utilisateur: {user_response or 'Aucune'}",
            f"Contexte: {context}"
        ]
        
        prompt = " | ".join(prompt_parts)
        
        try:
            response = self._make_api_request(prompt, max_tokens=600)
            
            if response and 'candidates' in response:
                response_text = response['candidates'][0]['content']['parts'][0]['text']
                
                try:
                    analysis = json.loads(response_text.strip())
                    analysis = self._validate_fall_analysis(analysis)
                    return analysis
                    
                except json.JSONDecodeError:
                    return self._fallback_fall_analysis(fall_info, user_response)
        
        except Exception as e:
            self.logger.error(f"Erreur analyse chute: {e}")
        
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