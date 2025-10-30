#!/usr/bin/env python3
"""
Lanceur Guardian Web simplifié - Sans APIs externes
Version de test qui évite les problèmes de configuration API
"""

import os
import sys

# Configuration des chemins
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Imports Flask essentiels
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Création de l'application Flask
app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = 'guardian_test_key_2024'
socketio = SocketIO(app, cors_allowed_origins="*")

# Routes principales
@app.route('/')
def home():
    """Page d'accueil avec formulaire utilisateur"""
    return render_template('home.html')

@app.route('/demo')
def demo():
    """Page démo principale avec conversation et carte"""
    return render_template('demo.html')

@app.route('/conversation')
def conversation():
    """Page conversation seule"""
    return render_template('conversation.html')

@app.route('/debug')
def debug():
    """Page de debug"""
    return render_template('debug.html')

@app.route('/voice-test')
def voice_test():
    """Page de test vocal"""
    return render_template('voice_test.html')

@app.route('/map')
def map_page():
    """Page carte interactive"""
    return render_template('map.html')

@app.route('/emergency')
def emergency():
    """Page d'urgence"""
    return render_template('emergency.html')

@app.route('/guardian-agent')
def guardian_agent_page():
    """Page agent Guardian"""
    return render_template('guardian_agent.html')

@app.route('/guardian-setup')
def guardian_setup():
    """Page setup Guardian"""
    return render_template('guardian_setup.html')

# API simplifiées (mock) pour éviter les erreurs
@app.route('/api/guardian/analyze', methods=['POST'])
def guardian_analyze_mock():
    """API Guardian simulée pour les tests"""
    try:
        data = request.json
        situation = data.get('situation', '')
        user_info = data.get('user_info', {})
        
        # Réponse simulée
        mock_response = {
            'urgency_level': 5,
            'advice': [f"✅ Message reçu: {situation}"],
            'recommendations': ["Ceci est un mode test"],
            'response': f"🤖 Guardian (Mode Test): J'ai bien reçu votre message '{situation}'. En mode test, toutes les fonctions sont simulées.",
            'email_sent': False,
            'status': 'success',
            'guardian_active': True,
            'message': 'Mode test - Guardian simulé',
            'location': data.get('location', ''),
            'timestamp': data.get('timestamp', 'N/A')
        }
        
        return jsonify(mock_response)
        
    except Exception as e:
        logger.error(f"Erreur API Guardian mock: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Erreur mode test: {str(e)}'
        }), 500

@app.route('/api/vosk/status')
def vosk_status_mock():
    """Status Vosk simulé"""
    return jsonify({'available': False, 'message': 'Mode test - Vosk simulé'})

@app.route('/api/vosk/listen', methods=['POST'])
def vosk_listen_mock():
    """Écoute Vosk simulée"""
    return jsonify({'text': 'Test vocal simulé', 'status': 'success'})

@app.errorhandler(404)
def not_found(error):
    """Gestionnaire d'erreur 404 personnalisé"""
    return render_template('404.html') if os.path.exists('templates/404.html') else f"""
    <div style="text-align: center; margin-top: 2rem; color: #666;">
        <h1>🚨 Erreur 404 - Page non trouvée</h1>
        <p>La page demandée n'existe pas.</p>
        <p><a href="/" style="color: #4285f4;">← Retour à l'accueil</a></p>
    </div>
    """, 404

if __name__ == '__main__':
    print("🛡️ Guardian Web - Mode Test")
    print("=" * 50)
    print("🌐 Interface disponible sur: http://localhost:5003")
    print("⚠️  Mode test - APIs simulées")
    print("📱 Pour arrêter: Ctrl+C")
    print("=" * 50)
    
    socketio.run(app, 
                debug=True, 
                host='0.0.0.0', 
                port=5003, 
                allow_unsafe_werkzeug=True)