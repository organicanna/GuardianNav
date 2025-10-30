"""
Configuration loader for Guardian
"""
import os
import yaml
from pathlib import Path
from typing import Dict, Any

class Config:
    """Gestionnaire de configuration pour Guardian"""
    
    def __init__(self, config_file: str = None, profile: str = "default"):
        """
        Initialise la configuration
        
        Args:
            config_file: Chemin vers le fichier de config (optionnel)
            profile: Profil de configuration à utiliser (default, test, etc.)
        """
        self.profile = profile
        self.project_root = Path(__file__).parent.parent
        
        if config_file is None:
            config_file = self.project_root / "config.yaml"
        
        self.config_data = self._load_config(config_file)
    
    def _load_config(self, config_file: Path) -> Dict[str, Any]:
        """Charge le fichier de configuration YAML"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                return data.get(self.profile, data.get("default", {}))
        except FileNotFoundError:
            print(f"Fichier de config non trouvé: {config_file}")
            return self._get_default_config()
        except Exception as e:
            print(f"Erreur lors du chargement de la config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Configuration par défaut en cas d'erreur"""
        return {
            "static_agent": {
                "distance_threshold": 10,
                "time_threshold": 300
            },
            "voice_agent": {
                "keywords": ["aide", "stop", "urgence", "secours", "oui", "non"],
                "model_path": "vosk-model-small-fr-0.22",
                "samplerate": 16000
            },
            "wrong_path_agent": {
                "deviation_threshold": 50
            },
            "logging": {
                "level": "INFO",
                "filename": "guardiannav.log"
            }
        }
    
    def get(self, key: str, default=None):
        """Récupère une valeur de configuration"""
        keys = key.split('.')
        value = self.config_data
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_model_path(self) -> str:
        """Retourne le chemin absolu vers le modèle Vosk"""
        relative_path = self.get("voice_agent.model_path")
        if relative_path:
            return str(self.project_root / relative_path)
        return None
    
    def get_static_agent_config(self) -> Dict[str, Any]:
        """Retourne la configuration pour l'agent statique"""
        return self.get("static_agent", {})
    
    def get_voice_agent_config(self) -> Dict[str, Any]:
        """Retourne la configuration pour l'agent vocal"""
        config = self.get("voice_agent", {})
        # Remplace le chemin relatif par le chemin absolu
        if "model_path" in config:
            config["model_path"] = self.get_model_path()
        return config
    
    def get_wrong_path_agent_config(self) -> Dict[str, Any]:
        """Retourne la configuration pour l'agent de déviation"""
        return self.get("wrong_path_agent", {})