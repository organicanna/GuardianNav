"""
Système d'IA et de conseils intelligents pour GuardianNav
Utilise les APIs Google Cloud pour analyser les situations et donner des conseils
"""

import requests
import logging
import json
import yaml
from typing import Dict, List, Any, Optional
from pathlib import Path

class IntelligentAdvisor:
    """Conseiller intelligent utilisant les APIs Google Cloud"""
    
    def __init__(self, api_keys_file: str = "api_keys.yaml"):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Charger les clés API
        try:
            with open(api_keys_file, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            self.logger.info("Configuration API chargée")
        except FileNotFoundError:
            self.logger.error(f"Fichier {api_keys_file} non trouvé")
            self.config = {}
    
    def analyze_emergency_situation(self, situation_description: str, location: tuple = None) -> Dict[str, Any]:
        """
        Analyse une situation d'urgence et propose des conseils
        
        Args:
            situation_description: Description de la situation
            location: Position GPS (lat, lon)
            
        Returns:
            Dict avec l'analyse et les conseils
        """
        self.logger.info(f"Analyse de situation: {situation_description}")
        
        # 1. Analyser le sentiment et l'urgence avec Google Natural Language API
        sentiment_analysis = self._analyze_sentiment(situation_description)
        
        # 2. Extraire les entités et mots-clés
        entities = self._extract_entities(situation_description)
        
        # 3. Déterminer le type d'urgence
        emergency_type = self._classify_emergency(situation_description, entities)
        
        # 4. Générer des conseils personnalisés
        advice = self._generate_advice(emergency_type, situation_description, location)
        
        # 5. Trouver les services d'urgence à proximité
        nearby_services = self._find_nearby_emergency_services(location) if location else {}
        
        return {
            "situation": situation_description,
            "emergency_type": emergency_type,
            "urgency_level": sentiment_analysis.get("urgency_level", "medium"),
            "sentiment": sentiment_analysis,
            "entities": entities,
            "advice": advice,
            "emergency_services": nearby_services,
            "immediate_actions": self._get_immediate_actions(emergency_type),
            "contacts_to_notify": self._get_relevant_contacts(emergency_type)
        }
    
    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyse le sentiment et l'urgence du texte"""
        try:
            # Simulation d'analyse de sentiment (remplacez par l'API réelle)
            urgent_keywords = [
                "urgence", "danger", "aide", "secours", "mal", "douleur", 
                "accident", "blessé", "perdu", "peur", "menace", "agression"
            ]
            
            text_lower = text.lower()
            urgency_score = sum(1 for keyword in urgent_keywords if keyword in text_lower)
            
            if urgency_score >= 3:
                urgency_level = "high"
            elif urgency_score >= 1:
                urgency_level = "medium"
            else:
                urgency_level = "low"
            
            return {
                "urgency_level": urgency_level,
                "urgency_score": urgency_score,
                "keywords_found": [kw for kw in urgent_keywords if kw in text_lower]
            }
            
        except Exception as e:
            self.logger.error(f"Erreur analyse sentiment: {e}")
            return {"urgency_level": "medium", "urgency_score": 1}
    
    def _extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extrait les entités importantes du texte"""
        try:
            # Simulation d'extraction d'entités (remplacez par Google NL API)
            entities = []
            
            # Recherche de lieux
            location_keywords = ["hôpital", "pharmacie", "commissariat", "rue", "avenue", "place"]
            for keyword in location_keywords:
                if keyword in text.lower():
                    entities.append({
                        "type": "LOCATION", 
                        "name": keyword,
                        "relevance": 0.8
                    })
            
            # Recherche de conditions médicales
            medical_keywords = ["douleur", "mal", "blessure", "sang", "fracture", "malaise"]
            for keyword in medical_keywords:
                if keyword in text.lower():
                    entities.append({
                        "type": "MEDICAL", 
                        "name": keyword,
                        "relevance": 0.9
                    })
            
            return entities
            
        except Exception as e:
            self.logger.error(f"Erreur extraction entités: {e}")
            return []
    
    def _classify_emergency(self, text: str, entities: List[Dict]) -> str:
        """Classifie le type d'urgence"""
        text_lower = text.lower()
        
        # Classification basée sur les mots-clés (ordre par priorité)
        if any(word in text_lower for word in ["tombé", "blessé", "blessure", "sang", "douleur", "mal", "fracture", "accident", "malaise"]):
            return "medical"
        elif any(word in text_lower for word in ["suit", "suivi", "agression", "menace", "vol", "danger", "peur", "menacé"]):
            return "security"
        elif any(word in text_lower for word in ["perdu", "égaré", "chemin", "reconnais pas", "ne sais pas où"]):
            return "lost"
        elif any(word in text_lower for word in ["panne", "problème technique", "téléphone", "batterie"]):
            return "technical"
        else:
            return "general"
    
    def _generate_advice(self, emergency_type: str, description: str, location: tuple) -> List[str]:
        """Génère des conseils personnalisés selon le type d'urgence"""
        
        advice_templates = {
            "medical": [
                "🏥 Reste calme et évalue ta blessure",
                "📞 Si c'est grave, appelle le 15 (SAMU) immédiatement",
                "🩹 Si tu peux, applique une pression sur les saignements",
                "📍 Communique ta position exacte aux secours",
                "👥 Demande de l'aide aux personnes autour de toi"
            ],
            "security": [
                "🚨 Mets-toi en sécurité immédiatement",
                "📞 Appelle le 17 (Police) si tu es en danger",
                "🏃 Dirige-toi vers un lieu public et éclairé",
                "📱 Partage ta localisation avec tes contacts",
                "👀 Mémorise les détails de ce qui s'est passé"
            ],
            "lost": [
                "📍 Reste où tu es, ne t'éloigne pas davantage",
                "📱 Active le GPS et partage ta position",
                "🗺️ Cherche des points de repère autour de toi",
                "👥 Demande ton chemin aux passants ou commerçants",
                "🔋 Économise la batterie de ton téléphone"
            ],
            "technical": [
                "🔧 Évalue si c'est un problème que tu peux résoudre",
                "📞 Contacte l'assistance technique appropriée",
                "📱 Trouve un téléphone ou WiFi alternatif",
                "🚶 Cherche un moyen de transport alternatif",
                "⏰ Informe tes contacts du retard potentiel"
            ],
            "general": [
                "😌 Reste calme et respire profondément",
                "📋 Fais une liste de ce que tu peux faire",
                "👥 N'hésite pas à demander de l'aide",
                "📞 Contacte quelqu'un de confiance",
                "🏠 Dirige-toi vers un lieu sûr si possible"
            ]
        }
        
        return advice_templates.get(emergency_type, advice_templates["general"])
    
    def _find_nearby_emergency_services(self, location: tuple) -> Dict[str, Any]:
        """Trouve les services d'urgence à proximité using Google Maps API"""
        if not location:
            return {}
        
        lat, lon = location
        
        # Simulation des services à proximité (remplacez par Google Places API)
        return {
            "nearest_hospital": {
                "name": "Hôpital le plus proche",
                "distance": "1.2 km",
                "phone": "01 42 34 56 78"
            },
            "nearest_police": {
                "name": "Commissariat Central", 
                "distance": "0.8 km",
                "phone": "17"
            },
            "nearest_pharmacy": {
                "name": "Pharmacie de garde",
                "distance": "0.3 km", 
                "phone": "01 23 45 67 89"
            }
        }
    
    def _get_immediate_actions(self, emergency_type: str) -> List[str]:
        """Actions immédiates selon le type d'urgence"""
        actions = {
            "medical": ["Appeler le 15", "Se mettre en position de sécurité", "Arrêter les saignements"],
            "security": ["Appeler le 17", "Se mettre à l'abri", "Alerter les proches"],
            "lost": ["Rester sur place", "Activer la géolocalisation", "Contacter les proches"],
            "technical": ["Évaluer la situation", "Chercher des alternatives", "Informer les contacts"],
            "general": ["Respirer calmement", "Évaluer la situation", "Demander de l'aide"]
        }
        return actions.get(emergency_type, actions["general"])
    
    def _get_relevant_contacts(self, emergency_type: str) -> List[str]:
        """Contacts à notifier selon le type d'urgence"""
        contacts = {
            "medical": ["Contacts d'urgence", "Médecin traitant"],
            "security": ["Police (17)", "Contacts d'urgence", "Famille"],
            "lost": ["Famille", "Amis proches"],
            "technical": ["Assistance technique", "Contacts d'urgence"],
            "general": ["Contacts d'urgence"]
        }
        return contacts.get(emergency_type, contacts["general"])

class SmartResponseSystem:
    """Système de réponse intelligent qui utilise l'IA pour les conversations"""
    
    def __init__(self, advisor: IntelligentAdvisor):
        self.advisor = advisor
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.conversation_context = []
    
    def process_emergency_response(self, user_response: str, context: str = "") -> Dict[str, Any]:
        """
        Traite une réponse d'urgence et génère des conseils intelligents
        
        Args:
            user_response: Réponse de l'utilisateur ("non", description du problème, etc.)
            context: Contexte de la situation (alerte déclenchée, etc.)
            
        Returns:
            Dict avec la réponse du système et les actions à prendre
        """
        self.conversation_context.append({
            "user_input": user_response,
            "context": context,
            "timestamp": logging.Formatter().formatTime(logging.LogRecord("", 0, "", 0, "", (), None))
        })
        
        # Si l'utilisateur dit "non", c'est une urgence
        if user_response.lower().strip() == "non":
            return {
                "type": "emergency_follow_up",
                "message": "🚨 Que se passe-t-il ? Décris-moi la situation :",
                "next_action": "wait_for_description",
                "urgency": "high"
            }
        
        # Si c'est une description de problème
        elif len(user_response) > 5 and user_response.lower() != "oui":
            analysis = self.advisor.analyze_emergency_situation(user_response)
            
            return {
                "type": "emergency_analysis",
                "analysis": analysis,
                "message": self._format_advice_message(analysis),
                "next_action": "provide_help",
                "urgency": analysis["urgency_level"]
            }
        
        # Si l'utilisateur dit "oui"
        else:
            return {
                "type": "confirmation", 
                "message": "✅ Parfait ! Tout semble aller bien. Continuez votre chemin en sécurité.",
                "next_action": "continue_monitoring",
                "urgency": "low"
            }
    
    def _format_advice_message(self, analysis: Dict[str, Any]) -> str:
        """Formate les conseils en message lisible"""
        emergency_type = analysis["emergency_type"]
        advice_list = analysis["advice"]
        immediate_actions = analysis["immediate_actions"]
        
        message = f"""
🤖 **Analyse de la situation** ({emergency_type})
📊 Niveau d'urgence: {analysis["urgency_level"]}

🚀 **Actions immédiates:**
{chr(10).join(f"   • {action}" for action in immediate_actions)}

💡 **Conseils détaillés:**
{chr(10).join(advice_list)}

📍 **Services d'urgence:**
"""
        
        for service_type, service_info in analysis["emergency_services"].items():
            message += f"   • {service_info['name']} - {service_info['distance']}\n"
        
        return message