#!/usr/bin/env python3
"""
🧹 Guardian - Script de Nettoyage et Maintenance
Nettoie les fichiers temporaires, logs anciens et optimise le système
"""

import os
import sys
import shutil
import glob
from datetime import datetime, timedelta
import logging

def setup_logging():
    """Configuration du logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/maintenance.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def clean_logs(days_to_keep=7):
    """Nettoie les anciens fichiers de logs"""
    logger = logging.getLogger(__name__)
    logs_dir = "logs"
    
    if not os.path.exists(logs_dir):
        logger.info(f"📁 Création du dossier {logs_dir}")
        os.makedirs(logs_dir)
        return
    
    cutoff_date = datetime.now() - timedelta(days=days_to_keep)
    cleaned_count = 0
    
    for log_file in glob.glob(f"{logs_dir}/*.log*"):
        try:
            file_time = datetime.fromtimestamp(os.path.getmtime(log_file))
            if file_time < cutoff_date:
                os.remove(log_file)
                cleaned_count += 1
                logger.info(f"🗑️ Supprimé: {log_file}")
        except Exception as e:
            logger.warning(f"⚠️ Erreur lors de la suppression de {log_file}: {e}")
    
    logger.info(f"✅ Nettoyage logs terminé: {cleaned_count} fichiers supprimés")

def clean_temp_files():
    """Supprime les fichiers temporaires"""
    logger = logging.getLogger(__name__)
    temp_patterns = [
        "*.pyc",
        "**/__pycache__",
        "*.tmp",
        ".DS_Store",
        "*.swp",
        "*.swo"
    ]
    
    cleaned_count = 0
    for pattern in temp_patterns:
        for temp_file in glob.glob(pattern, recursive=True):
            try:
                if os.path.isdir(temp_file):
                    shutil.rmtree(temp_file)
                else:
                    os.remove(temp_file)
                cleaned_count += 1
                logger.info(f"🗑️ Supprimé: {temp_file}")
            except Exception as e:
                logger.warning(f"⚠️ Erreur lors de la suppression de {temp_file}: {e}")
    
    logger.info(f"✅ Nettoyage fichiers temporaires: {cleaned_count} éléments supprimés")

def optimize_project_structure():
    """Vérifie et optimise la structure du projet"""
    logger = logging.getLogger(__name__)
    
    required_dirs = [
        "config", "guardian", "web/templates", "models", 
        "scripts", "tests", "demos", "docs", "logs"
    ]
    
    for directory in required_dirs:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            logger.info(f"📁 Créé: {directory}/")
    
    logger.info("✅ Structure du projet vérifiée")

def check_dependencies():
    """Vérifie les dépendances critiques"""
    logger = logging.getLogger(__name__)
    
    critical_modules = [
        "yaml", "flask", "vosk", "google.generativeai", 
        "pygame", "requests", "werkzeug"
    ]
    
    missing_modules = []
    for module in critical_modules:
        try:
            __import__(module)
            logger.info(f"✅ {module}")
        except ImportError:
            missing_modules.append(module)
            logger.error(f"❌ {module} - MANQUANT")
    
    if missing_modules:
        logger.error(f"🚨 Modules manquants: {', '.join(missing_modules)}")
        logger.info("💡 Exécutez: pip install -r requirements.txt")
    else:
        logger.info("✅ Toutes les dépendances sont installées")

def update_cache_buster():
    """Met à jour le cache-buster dans les templates"""
    logger = logging.getLogger(__name__)
    
    cache_buster = f"v{datetime.now().strftime('%Y-%m-%d-%H-%M')}-CLEAN"
    template_files = glob.glob("web/templates/*.html")
    
    for template_file in template_files:
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Remplacer le cache-buster existant
            import re
            pattern = r'<meta name="cache-buster" content="[^"]*">'
            replacement = f'<meta name="cache-buster" content="{cache_buster}">'
            
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                with open(template_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"🔄 Cache-buster mis à jour: {template_file}")
            
        except Exception as e:
            logger.warning(f"⚠️ Erreur cache-buster {template_file}: {e}")

def main():
    """Fonction principale de nettoyage"""
    logger = setup_logging()
    
    logger.info("🧹 === DÉBUT NETTOYAGE GUARDIAN ===")
    logger.info(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Étapes de nettoyage
        clean_temp_files()
        clean_logs(days_to_keep=7)
        optimize_project_structure()
        check_dependencies()
        update_cache_buster()
        
        logger.info("✅ === NETTOYAGE TERMINÉ AVEC SUCCÈS ===")
        
    except Exception as e:
        logger.error(f"❌ Erreur during cleanup: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())