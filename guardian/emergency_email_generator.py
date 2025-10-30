"""
Générateur d'emails visuels d'urgence pour Guardian
Crée des emails HTML avec cartes, géolocalisation et informations d'urgence
"""

import logging
import requests
import base64
from typing import Tuple, Dict, Any, Optional
from datetime import datetime
import html

class EmergencyEmailGenerator:
    """
    Générateur d'emails visuels d'urgence avec cartes et géolocalisation
    """
    
    def __init__(self, api_keys_config: Dict[str, Any] = None):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.api_keys = api_keys_config or {}
        
        # Configuration des APIs
        self.google_maps_api_key = self.api_keys.get('google_cloud', {}).get('services', {}).get('maps_api_key')
        self.what3words_api_key = self.api_keys.get('transport_apis', {}).get('what3words_api_key')
        
        self.logger.info("Générateur d'emails d'urgence initialisé")
    
    def generate_emergency_email_html(self, 
                                    location: Tuple[float, float],
                                    emergency_type: str,
                                    urgency_level: str,
                                    situation_details: str,
                                    person_name: str = "Utilisateur Guardian",
                                    additional_info: Dict[str, Any] = None) -> str:
        """
        Génère un email HTML complet pour une urgence
        
        Args:
            location: (latitude, longitude)
            emergency_type: Type d'urgence (chute, immobilité, etc.)
            urgency_level: Niveau d'urgence (critique, élevée, modérée)
            situation_details: Détails de la situation
            person_name: Nom de la personne en urgence
            additional_info: Informations supplémentaires (vitesse chute, etc.)
            
        Returns:
            HTML complet de l'email d'urgence
        """
        
        lat, lon = location
        timestamp = datetime.now().strftime("%d/%m/%Y à %H:%M:%S")
        
        # Obtenir What3Words
        what3words = self._get_what3words_address(location)
        
        # Générer l'URL de la carte
        map_url = self._generate_map_url(location)
        map_image_url = self._generate_static_map_url(location)
        
        # Déterminer le style selon l'urgence
        urgency_style = self._get_urgency_style(urgency_level)
        
        # Obtenir l'adresse approximative
        address = self._get_reverse_geocoding(location)
        
        # Template HTML
        html_content = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚨 ALERTE URGENCE - Guardian</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            line-height: 1.6;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: {urgency_style['bg_color']};
            color: white;
            padding: 20px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
        }}
        .urgency-badge {{
            background: {urgency_style['badge_color']};
            padding: 8px 16px;
            border-radius: 20px;
            display: inline-block;
            margin-top: 10px;
            font-weight: bold;
            font-size: 14px;
        }}
        .content {{
            padding: 20px;
        }}
        .emergency-info {{
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 8px;
            padding: 15px;
            margin: 15px 0;
        }}
        .location-section {{
            background: #e7f3ff;
            border: 1px solid #b3d9ff;
            border-radius: 8px;
            padding: 15px;
            margin: 15px 0;
        }}
        .map-container {{
            text-align: center;
            margin: 20px 0;
        }}
        .map-image {{
            max-width: 100%;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .coordinates {{
            font-family: monospace;
            background: #f8f9fa;
            padding: 10px;
            border-radius: 4px;
            margin: 10px 0;
        }}
        .what3words {{
            background: #e74c3c;
            color: white;
            padding: 12px;
            border-radius: 8px;
            text-align: center;
            margin: 15px 0;
            font-size: 18px;
            font-weight: bold;
        }}
        .action-buttons {{
            text-align: center;
            margin: 20px 0;
        }}
        .btn {{
            display: inline-block;
            padding: 12px 24px;
            margin: 5px;
            border-radius: 6px;
            text-decoration: none;
            font-weight: bold;
            color: white;
        }}
        .btn-maps {{
            background: #4285f4;
        }}
        .btn-call {{
            background: #34a853;
        }}
        .btn-emergency {{
            background: #ea4335;
        }}
        .additional-info {{
            background: #f8f9fa;
            border-left: 4px solid {urgency_style['accent_color']};
            padding: 15px;
            margin: 15px 0;
        }}
        .footer {{
            background: #2c3e50;
            color: white;
            padding: 15px;
            text-align: center;
            font-size: 12px;
        }}
        .timestamp {{
            color: #666;
            font-size: 12px;
            text-align: center;
            margin: 10px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- En-tête d'urgence -->
        <div class="header">
            <h1>🚨 ALERTE D'URGENCE</h1>
            <p><strong>{person_name}</strong> a besoin d'aide immédiatement</p>
            <div class="urgency-badge">
                {urgency_style['icon']} URGENCE {urgency_level.upper()}
            </div>
        </div>
        
        <!-- Informations sur l'urgence -->
        <div class="content">
            <div class="emergency-info">
                <h3>📋 Détails de la situation</h3>
                <p><strong>Type d'urgence:</strong> {emergency_type}</p>
                <p><strong>Description:</strong> {html.escape(situation_details)}</p>
                <div class="timestamp">
                    🕒 Alerte déclenchée le {timestamp}
                </div>
            </div>
            
            <!-- Informations supplémentaires -->
            {self._generate_additional_info_section(additional_info)}
            
            <!-- Section localisation -->
            <div class="location-section">
                <h3>📍 Localisation précise</h3>
                
                <div class="what3words">
                    <strong>What3Words:</strong> {what3words}
                </div>
                
                <p><strong>Adresse approximative:</strong><br>{address}</p>
                
                <div class="coordinates">
                    <strong>Coordonnées GPS:</strong><br>
                    Latitude: {lat:.6f}<br>
                    Longitude: {lon:.6f}
                </div>
            </div>
            
            <!-- Carte -->
            <div class="map-container">
                <h3>🗺️ Localisation sur carte</h3>
                <img src="{map_image_url}" alt="Carte de localisation" class="map-image">
            </div>
            
            <!-- Boutons d'action -->
            <div class="action-buttons">
                <a href="{map_url}" class="btn btn-maps" target="_blank">
                    📍 Ouvrir dans Google Maps
                </a>
                <a href="tel:15" class="btn btn-emergency">
                    🚑 Appeler SAMU (15)
                </a>
                <a href="tel:112" class="btn btn-call">
                    📞 Urgences EU (112)
                </a>
            </div>
            
            <!-- Instructions -->
            <div class="emergency-info">
                <h3>⚡ Actions recommandées</h3>
                <ul>
                    <li><strong>Contactez immédiatement les secours</strong> si nécessaire (15, 18, 112)</li>
                    <li><strong>Rendez-vous sur place</strong> ou envoyez quelqu'un de confiance</li>
                    <li><strong>Gardez votre téléphone allumé</strong> pour les mises à jour</li>
                    <li><strong>Utilisez What3Words</strong> pour une localisation ultra-précise</li>
                </ul>
            </div>
        </div>
        
        <!-- Pied de page -->
        <div class="footer">
            <p>🛡️ <strong>Guardian</strong> - Système de sécurité personnelle</p>
            <p>Email généré automatiquement • Ne pas répondre à cette adresse</p>
        </div>
    </div>
</body>
</html>"""
        
        return html_content
    
    def _get_urgency_style(self, urgency_level: str) -> Dict[str, str]:
        """Retourne les styles CSS selon le niveau d'urgence"""
        
        styles = {
            'critique': {
                'bg_color': 'linear-gradient(135deg, #e74c3c, #c0392b)',
                'badge_color': '#c0392b',
                'accent_color': '#e74c3c',
                'icon': '🆘'
            },
            'élevée': {
                'bg_color': 'linear-gradient(135deg, #f39c12, #e67e22)',
                'badge_color': '#e67e22',
                'accent_color': '#f39c12',
                'icon': '⚠️'
            },
            'modérée': {
                'bg_color': 'linear-gradient(135deg, #f1c40f, #f39c12)',
                'badge_color': '#e67e22',
                'accent_color': '#f1c40f',
                'icon': '⚡'
            },
            'faible': {
                'bg_color': 'linear-gradient(135deg, #3498db, #2980b9)',
                'badge_color': '#2980b9',
                'accent_color': '#3498db',
                'icon': 'ℹ️'
            }
        }
        
        return styles.get(urgency_level.lower(), styles['modérée'])
    
    def _generate_additional_info_section(self, additional_info: Dict[str, Any] = None) -> str:
        """Génère la section des informations supplémentaires"""
        
        if not additional_info:
            return ""
            
        html_section = '<div class="additional-info"><h3>📊 Informations techniques</h3><ul>'
        
        # Informations de chute
        if 'fall_type' in additional_info:
            html_section += f'<li><strong>Type de chute:</strong> {additional_info["fall_type"]}</li>'
        
        if 'previous_speed' in additional_info:
            html_section += f'<li><strong>Vitesse avant incident:</strong> {additional_info["previous_speed"]:.1f} km/h</li>'
            
        if 'acceleration' in additional_info:
            html_section += f'<li><strong>Décélération mesurée:</strong> {additional_info["acceleration"]:.1f} m/s²</li>'
            
        if 'severity' in additional_info:
            html_section += f'<li><strong>Sévérité évaluée:</strong> {additional_info["severity"]}</li>'
            
        # Informations de position
        if 'time_since_fall' in additional_info:
            html_section += f'<li><strong>Temps depuis incident:</strong> {additional_info["time_since_fall"]:.0f} secondes</li>'
            
        if 'movement_since_fall' in additional_info:
            html_section += f'<li><strong>Mouvement détecté:</strong> {additional_info["movement_since_fall"]:.1f} mètres</li>'
        
        html_section += '</ul></div>'
        
        return html_section
    
    def _get_what3words_address(self, location: Tuple[float, float]) -> str:
        """
        Obtient l'adresse What3Words pour une localisation
        """
        
        if not self.what3words_api_key or self.what3words_api_key.startswith('YOUR_'):
            # Mode simulation
            return f"simulation.exemple.mots"
        
        try:
            lat, lon = location
            
            url = "https://api.what3words.com/v3/convert-to-3wa"
            params = {
                'coordinates': f"{lat},{lon}",
                'key': self.what3words_api_key,
                'language': 'fr'
            }
            
            response = requests.get(url, params=params, timeout=5)
            data = response.json()
            
            if 'words' in data:
                return data['words']
            else:
                self.logger.warning(f"Erreur What3Words: {data}")
                return f"erreur.localisation.indisponible"
                
        except Exception as e:
            self.logger.error(f"Erreur What3Words API: {e}")
            return f"api.erreur.temporaire"
    
    def _generate_map_url(self, location: Tuple[float, float]) -> str:
        """Génère l'URL Google Maps pour ouvrir la localisation"""
        
        lat, lon = location
        return f"https://maps.google.com/?q={lat},{lon}&ll={lat},{lon}&z=16"
    
    def _generate_static_map_url(self, location: Tuple[float, float]) -> str:
        """
        Génère l'URL de la carte statique Google Maps
        """
        
        lat, lon = location
        
        # Si pas d'API key, utiliser une carte OpenStreetMap
        if not self.google_maps_api_key or self.google_maps_api_key.startswith('YOUR_'):
            return f"https://www.openstreetmap.org/export/embed.html?bbox={lon-0.01}%2C{lat-0.01}%2C{lon+0.01}%2C{lat+0.01}&layer=mapnik&marker={lat}%2C{lon}"
        
        # URL Google Static Maps avec marqueur d'urgence
        base_url = "https://maps.googleapis.com/maps/api/staticmap"
        params = {
            'center': f"{lat},{lon}",
            'zoom': '16',
            'size': '600x400',
            'markers': f"color:red|size:large|label:🚨|{lat},{lon}",
            'maptype': 'roadmap',
            'key': self.google_maps_api_key
        }
        
        param_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{base_url}?{param_string}"
    
    def _get_reverse_geocoding(self, location: Tuple[float, float]) -> str:
        """
        Obtient l'adresse approximative via reverse geocoding
        """
        
        if not self.google_maps_api_key or self.google_maps_api_key.startswith('YOUR_'):
            # Mode simulation
            lat, lon = location
            return f"Adresse approximative simulée près de {lat:.4f}, {lon:.4f}"
        
        try:
            lat, lon = location
            
            url = "https://maps.googleapis.com/maps/api/geocode/json"
            params = {
                'latlng': f"{lat},{lon}",
                'key': self.google_maps_api_key,
                'language': 'fr'
            }
            
            response = requests.get(url, params=params, timeout=5)
            data = response.json()
            
            if data.get('status') == 'OK' and data.get('results'):
                return data['results'][0]['formatted_address']
            else:
                return f"Adresse non disponible ({lat:.4f}, {lon:.4f})"
                
        except Exception as e:
            self.logger.error(f"Erreur reverse geocoding: {e}")
            return f"Adresse temporairement indisponible"
    
    def generate_test_email(self) -> str:
        """Génère un email de test pour prévisualisation"""
        
        test_location = (48.8566, 2.3522)  # Paris, Place du Châtelet
        
        test_additional_info = {
            'fall_type': 'chute_velo',
            'previous_speed': 18.5,
            'acceleration': -9.2,
            'severity': 'grave'
        }
        
        return self.generate_emergency_email_html(
            location=test_location,
            emergency_type="🚴 Chute à vélo détectée",
            urgency_level="critique",
            situation_details="Chute à vélo potentiellement grave détectée par les capteurs. La personne ne répond pas depuis 30 secondes.",
            person_name="Test Guardian",
            additional_info=test_additional_info
        )