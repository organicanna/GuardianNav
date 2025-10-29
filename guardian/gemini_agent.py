"""
Vertex AI Agent for GuardianNav - Enhanced with Google GenAI
Advanced emergency analysis using Google Generative AI and Vertex AI
"""
import logging
import json
import requests
import os
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

try:
    from google import genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

class VertexAIAgent:
    """Agent Vertex AI pour l'analyse d'urgence avancée avec Gemini via API REST"""
    
    def __init__(self, api_keys_config: Dict[str, Any] = None):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Configuration API - Prioriser Gemini sur Vertex AI
        self.api_keys_config = api_keys_config or {}
        google_config = self.api_keys_config.get('google_cloud', {})
        
        # Configuration Gemini (prioritaire)
        gemini_config = google_config.get('gemini', {})
        vertex_config = google_config.get('vertex_ai', {})
        
        # Utiliser Gemini si disponible, sinon Vertex AI
        if gemini_config.get('enabled', False) and gemini_config.get('api_key'):
            self.api_key = gemini_config.get('api_key')
            self.model_name = gemini_config.get('model', 'gemini-1.5-flash-latest')
            self.base_url = gemini_config.get('base_url', 'https://generativelanguage.googleapis.com/v1beta')
            self.api_type = 'gemini'
            self.logger.info("Configuration: API Gemini (Generative Language)")
        else:
            # Fallback vers Vertex AI
            self.api_key = vertex_config.get('api_key')
            self.model_name = "gemini-1.5-flash-002"
            self.region = vertex_config.get('region', 'europe-west1')
            self.api_type = 'vertex'
            self.logger.info("Configuration: Vertex AI (fallback)")
            
        self.project_id = google_config.get('project_id')
        self.enabled = gemini_config.get('enabled', vertex_config.get('enabled', True))
        
        self.is_available = False
        
        # Initialiser l'API si configuration complète
        if self.api_key and self.enabled:
            self._initialize_api()
        else:
            self.logger.warning("Configuration API incomplète - fonctionnement en mode simulation")
    
    def _initialize_api(self):
        """Initialise la connexion à l'API Gemini/Vertex AI"""
        try:
            # Initialiser le client Google GenAI si disponible
            if self.api_type == 'gemini' and GENAI_AVAILABLE:
                self._initialize_genai_client()
            
            # Test de connectivité simple
            test_prompt = "Test. Répondez juste 'OK'."
            
            response = self._make_api_request(test_prompt, max_tokens=5)
            
            if response and 'candidates' in response:
                # Vérifier que ce n'est pas une simulation
                response_text = response['candidates'][0]['content']['parts'][0]['text']
                if response_text and 'simulation' not in response_text.lower():
                    self.is_available = True
                    self.logger.info(f"✅ API {self.api_type.upper()} connectée avec succès")
                    return
                    
            # Si on arrive ici, c'est une simulation ou erreur
            self.is_available = False
            self.logger.info(f"⚠️ Mode simulation activé pour {self.api_type.upper()}")
                
        except Exception as e:
            self.logger.error(f"Erreur initialisation API {self.api_type}: {e}")
            self.is_available = False
    
    def _initialize_genai_client(self):
        """Initialise le client Google GenAI moderne"""
        try:
            if self.api_key and GENAI_AVAILABLE:
                # Configurer la variable d'environnement
                os.environ['GEMINI_API_KEY'] = self.api_key
                
                # Créer le client
                self.genai_client = genai.Client()
                self.use_genai_client = True
                self.logger.info("✅ Client Google GenAI initialisé")
            else:
                self.use_genai_client = False
                self.logger.info("⚠️ Client Google GenAI non disponible - utilisation REST")
        except Exception as e:
            self.logger.error(f"Erreur initialisation client GenAI: {e}")
            self.use_genai_client = False
    
    def _make_api_request(self, prompt: str, max_tokens: int = 1000) -> Optional[Dict]:
        """Effectue une requête à l'API Gemini"""
        if not self.api_key or self.api_key == "YOUR_VERTEX_AI_API_KEY":
            self.logger.info("API Key non configurée - mode simulation")
            return self._simulate_response(prompt)
        
        # Utiliser le client Google GenAI moderne si disponible
        if hasattr(self, 'use_genai_client') and self.use_genai_client and hasattr(self, 'genai_client'):
            return self._make_genai_request(prompt, max_tokens)
        
        # Construire l'URL selon le type d'API (méthode REST classique)
        try:
            if self.api_type == 'gemini':
                api_url = f"{self.base_url}/models/{self.model_name}:generateContent?key={self.api_key}"
            else:
                # Vertex AI (fallback)
                api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={self.api_key}"
            
            headers = {
                'Content-Type': 'application/json'
            }
            
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "temperature": 0.1,
                    "maxOutputTokens": max_tokens,
                    "topP": 0.8,
                    "topK": 10
                },
                "safetySettings": [
                    {
                        "category": "HARM_CATEGORY_HARASSMENT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_HATE_SPEECH",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    }
                ]
            }
            
            self.logger.debug(f"Requête API {self.api_type}: {api_url[:50]}...")
            response = requests.post(api_url, headers=headers, json=payload, timeout=15)
            
            self.logger.debug(f"Réponse API: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                self.logger.info("API Gemini: Réponse reçue avec succès")
                return result
            elif response.status_code == 400:
                error_detail = response.text
                self.logger.warning(f"API Gemini erreur 400 (Bad Request): {error_detail[:200]}...")
                self.logger.info("Passage en mode simulation")
                return self._simulate_response(prompt)
            elif response.status_code == 403:
                self.logger.warning("API Gemini: Clé invalide ou API non activée - mode simulation")
                return self._simulate_response(prompt)
            else:
                self.logger.warning(f"API Gemini erreur {response.status_code}: {response.text[:100]}...")
                return self._simulate_response(prompt)
                
        except requests.exceptions.RequestException as e:
            self.logger.warning(f"Erreur réseau API Gemini: {e} - mode simulation")
            return self._simulate_response(prompt)
        except Exception as e:
            self.logger.warning(f"Erreur API Gemini: {e} - mode simulation")
            return self._simulate_response(prompt)
    
    def _make_genai_request(self, prompt: str, max_tokens: int = 1000) -> Optional[Dict]:
        """Effectue une requête avec le nouveau client Google GenAI"""
        try:
            self.logger.info("🚀 Utilisation du client Google GenAI moderne")
            
            # Générer le contenu avec le nouveau client
            # Utiliser gemini-2.5-flash qui fonctionne
            response = self.genai_client.models.generate_content(
                model="gemini-2.5-flash", 
                contents=prompt
            )
            
            # Convertir la réponse au format attendu
            if response and hasattr(response, 'text'):
                formatted_response = {
                    "candidates": [
                        {
                            "content": {
                                "parts": [
                                    {
                                        "text": response.text
                                    }
                                ]
                            },
                            "finishReason": "STOP"
                        }
                    ]
                }
                self.logger.info("✅ Réponse Google GenAI reçue avec succès")
                return formatted_response
            else:
                self.logger.warning("⚠️ Réponse Google GenAI vide")
                return self._simulate_response(prompt)
                
        except Exception as e:
            self.logger.warning(f"❌ Erreur Google GenAI: {e} - basculement vers simulation")
            
            # Diagnostics spécifiques pour aider l'utilisateur
            error_str = str(e)
            if "403" in error_str or "PERMISSION_DENIED" in error_str:
                self.logger.info("💡 Clé API invalide ou service bloqué")
            elif "404" in error_str or "not found" in error_str.lower():
                self.logger.info("💡 Modèle non trouvé - essayez avec une clé API valide")
            elif "quota" in error_str.lower():
                self.logger.info("💡 Quota API dépassé")
                
            return self._simulate_response(prompt)
    
    def _simulate_response(self, prompt: str) -> Dict:
        """Génère une réponse simulée intelligente basée sur l'analyse contextuelle"""
        self.logger.info("Mode simulation Vertex AI - Analyse contextuelle avancée")
        
        # Analyse approfondie du prompt pour une réponse très réaliste
        prompt_lower = prompt.lower()
        
        # Détection de mots-clés et contextes
        urgency_indicators = {
            'critique': ['inconscient', 'sang', 'arrêt cardiaque', 'ne respire plus', 'accident grave'],
            'élevée': ['chute', 'douleur intense', 'blessé', 'cassé', 'fracture', 'malaise'],
            'modérée': ['perdu', 'peur', 'inquiet', 'mal', 'problème'],
            'faible': ['conseil', 'information', 'aide', 'question']
        }
        
        medical_keywords = ['douleur', 'mal', 'blessé', 'sang', 'chute', 'malaise', 'étourdissement']
        security_keywords = ['danger', 'agression', 'menace', 'peur', 'suspect']
        location_keywords = ['perdu', 'égaré', 'ne sais pas où', 'trouve plus']
        
        # Analyser le niveau d'urgence
        urgency_level = 3  # par défaut
        urgency_category = "Modérée"
        
        for level, keywords in urgency_indicators.items():
            if any(word in prompt_lower for word in keywords):
                if level == 'critique':
                    urgency_level = 9
                    urgency_category = "Critique"
                elif level == 'élevée':
                    urgency_level = 7
                    urgency_category = "Élevée"
                elif level == 'modérée':
                    urgency_level = 5
                    urgency_category = "Modérée"
                else:
                    urgency_level = 2
                    urgency_category = "Faible"
                break
        
        # Générer une réponse contextuelle très détaillée
        if any(word in prompt_lower for word in ['chute', 'tombé', 'chu', 'glissé']):
            body_parts = ['bras', 'jambe', 'dos', 'tête', 'cheville', 'poignet', 'genou']
            injured_part = next((part for part in body_parts if part in prompt_lower), "corps")
            
            simulated_analysis = {
                "emergency_type": f"Traumatisme suite à chute - {injured_part}",
                "urgency_level": min(urgency_level + 2, 10),
                "urgency_category": "Élevée",
                "immediate_actions": [
                    f"Évaluer la douleur du {injured_part}",
                    "Immobiliser la zone si fracture suspectée",
                    "Appliquer de la glace si possible"
                ],
                "specific_advice": f"Chute avec impact sur le {injured_part}. Si douleur intense ou déformation visible, consultation médicale urgente recommandée. Surveillez les signes de commotion si impact à la tête.",
                "emergency_services": "SAMU (15) si douleur sévère",
                "reassurance_message": "La plupart des chutes peuvent être traitées efficacement. Restez calme et évaluez précisément vos symptômes.",
                "recommended_actions": [
                    "Tester la mobilité progressivement",
                    "Surveiller l'évolution de la douleur",
                    "Consulter si symptômes persistent"
                ]
            }
        elif any(word in prompt_lower for word in security_keywords):
            threat_level = "élevée" if any(word in prompt_lower for word in ['agression', 'menace', 'danger immédiat']) else "modérée"
            
            simulated_analysis = {
                "emergency_type": f"Situation de sécurité - menace {threat_level}",
                "urgency_level": 9 if threat_level == "élevée" else 7,
                "urgency_category": "Critique" if threat_level == "élevée" else "Élevée",
                "immediate_actions": [
                    "Éloignez-vous de la source de danger",
                    "Dirigez-vous vers un lieu public sûr",
                    "Contactez immédiatement les forces de l'ordre"
                ],
                "specific_advice": f"Situation de sécurité nécessitant une réaction immédiate. Priorité absolue : votre sécurité personnelle. Ne prenez aucun risque inutile.",
                "emergency_services": "Police (17) ou Urgences (112)",
                "reassurance_message": "Les forces de sécurité sont formées pour gérer ces situations. Votre sécurité est la priorité.",
                "safety_tips": [
                    "Restez dans des zones éclairées et fréquentées",
                    "Gardez votre téléphone accessible",
                    "Signalez votre position aux autorités"
                ]
            }
        elif any(word in prompt_lower for word in medical_keywords):
            # Analyse des symptômes médicaux
            symptoms = []
            if 'douleur' in prompt_lower:
                symptoms.append('douleur')
            if 'malaise' in prompt_lower:
                symptoms.append('malaise')
            if 'étourdissement' in prompt_lower:
                symptoms.append('étourdissement')
                
            intensity_words = ['intense', 'sévère', 'insupportable', 'très fort']
            is_severe = any(word in prompt_lower for word in intensity_words)
            
            simulated_analysis = {
                "emergency_type": f"Urgence médicale - {', '.join(symptoms) if symptoms else 'symptômes divers'}",
                "urgency_level": min(urgency_level + (3 if is_severe else 1), 10),
                "urgency_category": "Critique" if is_severe else "Élevée",
                "immediate_actions": [
                    "Trouvez une position confortable (assis ou allongé)",
                    "Contrôlez votre respiration (inspirations lentes et profondes)",
                    "Évaluez l'intensité des symptômes sur 10"
                ],
                "specific_advice": f"Symptômes médicaux {'sévères' if is_severe else 'modérés'} nécessitant {'une intervention immédiate' if is_severe else 'une évaluation médicale'}. {'Appelez le 15 maintenant' if is_severe else 'Surveillez l évolution et consultez si aggravation'}.",
                "emergency_services": "SAMU (15)" if is_severe else "Médecin traitant ou SOS Médecins",
                "reassurance_message": "Les équipes médicales sont spécialisées dans la gestion de ces symptômes. Une prise en charge adaptée est disponible.",
                "monitoring_advice": [
                    "Notez l'heure d'apparition des symptômes",
                    "Surveillez l'évolution (amélioration/aggravation)",
                    "Préparez vos antécédents médicaux"
                ]
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
        
        # Construction d'un prompt structuré pour Gemini
        prompt = f"""Tu es un assistant d'urgence spécialisé. Analyse la situation suivante et réponds uniquement avec un JSON valide contenant ces champs exacts:

Situation: {context}
Moment: {time_of_day}
Localisation: {location_str}
Description: {user_input if user_input else 'Aucune information supplémentaire'}

Réponds UNIQUEMENT avec ce JSON (sans autre texte):
{{
  "emergency_type": "type d'urgence détecté",
  "urgency_level": nombre de 1 à 10,
  "urgency_category": "Faible/Modérée/Élevée/Critique",
  "specific_advice": "conseil personnalisé en français",
  "immediate_actions": ["action1", "action2", "action3"],
  "emergency_services": "service d'urgence recommandé",
  "reassurance_message": "message rassurant"
}}"""
        
        try:
            response = self._make_api_request(prompt, max_tokens=800)
            
            if response and 'candidates' in response:
                response_text = response['candidates'][0]['content']['parts'][0]['text']
                
                try:
                    analysis = json.loads(response_text.strip())
                    analysis = self._validate_analysis_response(analysis)
                    
                    self.logger.info("Analyse Vertex AI générée avec succès")
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
        self.logger.warning("Utilisation analyse de fallback")
        
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
    
    def test_vertex_ai_connection(self) -> Dict[str, Any]:
        """Test la connexion Vertex AI avec retour détaillé (compatibilité)"""
        try:
            # Test de base
            connection_ok = self.test_connection()
            
            if connection_ok and self.is_available:
                return {
                    "success": True,
                    "available": True,
                    "details": f"Modèle: {self.model_name}, Région: {self.region}",
                    "message": "Vertex AI REST API connectée avec succès"
                }
            else:
                return {
                    "success": False,
                    "available": False,
                    "details": f"Mode simulation - Modèle: {self.model_name}",
                    "message": "Vertex AI en mode simulation (clé API manquante ou OAuth2 non implémenté)"
                }
        
        except Exception as e:
            return {
                "success": False,
                "available": False,
                "details": "Erreur de connexion",
                "message": f"Erreur de connexion: {e}"
            }