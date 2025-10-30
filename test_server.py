#!/usr/bin/env python3
"""
Serveur de test Guardian avec toutes les routes nécessaires
"""

from flask import Flask, render_template
import os

# Configuration du serveur Flask
app = Flask(__name__, template_folder='web/templates', static_folder='web/static')

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
def guardian_agent():
    """Page agent Guardian"""
    return render_template('guardian_agent.html')

@app.route('/guardian-setup')
def guardian_setup():
    """Page setup Guardian"""
    return render_template('guardian_setup.html')

@app.errorhandler(404)
def not_found(error):
    """Gestionnaire d'erreur 404"""
    return f"""
    <h1>🚨 Erreur 404 - Page non trouvée</h1>
    <p>La page demandée n'existe pas.</p>
    <p><a href="/">← Retour à l'accueil</a></p>
    <hr>
    <p>URL demandée: {error.description}</p>
    """, 404

if __name__ == '__main__':
    print("🛡️ Serveur de test Guardian")
    print("=" * 40)
    print("🌐 Pages disponibles:")
    print("  • http://localhost:5002/         (Accueil)")
    print("  • http://localhost:5002/demo     (Démo complète)")
    print("  • http://localhost:5002/conversation (Conversation)")
    print("  • http://localhost:5002/debug    (Debug)")
    print("  • http://localhost:5002/voice-test (Test vocal)")
    print("=" * 40)
    
    app.run(host='0.0.0.0', port=5002, debug=True)