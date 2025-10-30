"""
GUARDIAN VERTEX AI - SERVICE CLOUD
API REST pour déploiement sur Vertex AI avec Google Cloud Functions
Optimisé pour haute disponibilité et faible latence
"""

import os
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify, Response
from google.cloud import aiplatform
from google.cloud import logging as cloud_logging
import yaml

# Configuration du logging cloud
cloud_logging.Client().setup_logging()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class GuardianVertexAI:
    """Version cloud-native de Guardian pour Vertex AI"""
    
    def __init__(self):
        self.project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        self.region = os.getenv('GOOGLE_CLOUD_REGION', 'europe-west1')
        self.model_endpoint = None
        self.initialize_vertex_ai()
    
    def initialize_vertex_ai(self):
        """Initialise Vertex AI"""
        try:
            aiplatform.init(
                project=self.project_id,
                location=self.region
            )
            logger.info(f"Vertex AI initialisé - Projet: {self.project_id}, Région: {self.region}")
        except Exception as e:
            logger.error(f"Erreur initialisation Vertex AI: {e}")
    
    def analyze_emergency(self, situation_text: str, user_info: dict) -> dict:
        """Analyse une situation d'urgence avec l'IA"""
        try:
            # Prompt optimisé pour Vertex AI
            prompt = self._create_emergency_prompt(situation_text, user_info)
            
            # Appel au modèle Gemini sur Vertex AI
            response = self._call_gemini_model(prompt)
            
            # Parse de la réponse
            analysis = self._parse_emergency_response(response)
            
            logger.info(f"Analyse d'urgence: niveau {analysis.get('urgency_level', 0)}/10")
            return analysis
            
        except Exception as e:
            logger.error(f"Erreur analyse d'urgence: {e}")
            return self._get_fallback_response()
    
    def _create_emergency_prompt(self, situation: str, user_info: dict) -> str:
        """Crée le prompt optimisé pour urgences"""
        user_name = user_info.get('name', 'Utilisateur')
        location = user_info.get('location', 'Position inconnue')
        
        return f"""Tu es Guardian, assistant IA d'urgence. Analyse RAPIDEMENT cette situation.

URGENCE RAPPORTÉE: "{situation}"
PERSONNE: {user_name}
LIEU: {location}
HEURE: {datetime.now().strftime('%H:%M')}

RÉPONSE REQUISE (format JSON):
{{
  "urgency_level": [1-10],
  "emergency_type": "medical|security|navigation|other",
  "immediate_actions": ["action1", "action2", "action3"],
  "alert_contacts": true/false,
  "message": "Message court et rassurant"
}}

CRITÈRES ALERTE CONTACTS:
- Niveau ≥ 7/10
- Danger physique immédiat
- Personne suivie/menacée
- Accident/blessure
- Situation médicale grave

Réponds UNIQUEMENT en JSON valide."""
    
    def _call_gemini_model(self, prompt: str) -> str:
        """Appelle le modèle Gemini sur Vertex AI"""
        try:
            # Ici on utiliserait l'endpoint Vertex AI déployé
            # Pour le prototype, on utilise l'API REST Gemini
            from google.cloud import aiplatform_v1
            
            # Configuration temporaire - à remplacer par endpoint déployé
            model_name = "gemini-1.5-flash-latest"
            
            # Simulation d'appel - à remplacer par vrai endpoint
            response = {
                "urgency_level": 8,
                "emergency_type": "security", 
                "immediate_actions": ["Restez calme", "Cherchez lieu sûr", "Appelez police"],
                "alert_contacts": True,
                "message": "Je suis là pour vous aider. Suivez ces instructions."
            }
            
            return json.dumps(response)
            
        except Exception as e:
            logger.error(f"Erreur modèle Gemini: {e}")
            raise
    
    def _parse_emergency_response(self, response_text: str) -> dict:
        """Parse la réponse JSON du modèle"""
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            logger.error("Réponse IA non-JSON valide")
            return self._get_fallback_response()
    
    def _get_fallback_response(self) -> dict:
        """Réponse de secours si l'IA échoue"""
        return {
            "urgency_level": 5,
            "emergency_type": "other",
            "immediate_actions": ["Restez calme", "Décrivez votre situation", "Appelez le 112 si danger"],
            "alert_contacts": False,
            "message": "System temporairement indisponible. En urgence, appelez le 17 ou 112."
        }

# Instance globale Guardian
guardian = GuardianVertexAI()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check pour monitoring"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Guardian Vertex AI",
        "version": "1.0.0"
    })

@app.route('/emergency', methods=['POST'])
def handle_emergency():
    """Endpoint principal pour traiter les urgences"""
    try:
        # Validation de la requête
        if not request.is_json:
            return jsonify({"error": "Content-Type doit être application/json"}), 400
        
        data = request.get_json()
        
        # Validation des champs requis
        required_fields = ['situation', 'user_info']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Champ requis manquant: {field}"}), 400
        
        # Traitement de l'urgence
        start_time = datetime.now()
        
        analysis = guardian.analyze_emergency(
            data['situation'], 
            data['user_info']
        )
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Ajout de métadonnées
        analysis['metadata'] = {
            "processing_time_ms": round(processing_time * 1000),
            "timestamp": start_time.isoformat(),
            "region": guardian.region,
            "model": "gemini-vertex-ai"
        }
        
        # Log pour monitoring
        logger.info(f"Urgence traitée en {processing_time:.3f}s - Niveau: {analysis.get('urgency_level')}")
        
        return jsonify(analysis), 200
        
    except Exception as e:
        logger.error(f"Erreur traitement urgence: {e}")
        return jsonify({
            "error": "Erreur interne du service",
            "details": str(e)
        }), 500

@app.route('/voice-emergency', methods=['POST'])
def handle_voice_emergency():
    """Endpoint pour urgences vocales (à implémenter)"""
    return jsonify({
        "message": "Endpoint vocal en développement",
        "use": "/emergency pour urgences texte"
    }), 501

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint non trouvé"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Erreur interne du serveur"}), 500

# Point d'entrée pour Google Cloud Functions
def guardian_vertex_ai(request):
    """Entry point pour Cloud Functions"""
    with app.test_request_context(path=request.path, method=request.method, 
                                  data=request.data, headers=request.headers):
        try:
            response = app.dispatch_request()
            return response
        except Exception as e:
            logger.error(f"Erreur Cloud Function: {e}")
            return jsonify({"error": "Service temporairement indisponible"}), 500

if __name__ == '__main__':
    # Mode développement local
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)