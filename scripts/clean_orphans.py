#!/usr/bin/env python3
"""
Guardian - Script de nettoyage des codes orphelins
Supprime automatiquement les fichiers temporaires et inutilisés
"""

import os
import glob
import shutil
from pathlib import Path

def clean_project():
    """Nettoie le projet des fichiers orphelins"""
    
    # Répertoire racine du projet
    project_root = Path(__file__).parent.parent
    
    print("Nettoyage des codes orphelins Guardian...")
    
    # 1. Supprimer les fichiers de cache Python
    cache_dirs = list(project_root.rglob("__pycache__"))
    for cache_dir in cache_dirs:
        shutil.rmtree(cache_dir, ignore_errors=True)
        print(f"Supprimé: {cache_dir}")
    
    # 2. Supprimer les fichiers .pyc
    pyc_files = list(project_root.rglob("*.pyc"))
    for pyc_file in pyc_files:
        pyc_file.unlink(missing_ok=True)
        print(f"Supprimé: {pyc_file}")
    
    # 3. Supprimer les fichiers de log anciens
    log_files = list(project_root.rglob("*.log"))
    for log_file in log_files:
        if log_file.stat().st_size > 10 * 1024 * 1024:  # > 10MB
            log_file.unlink(missing_ok=True)
            print(f"Supprimé (trop volumineux): {log_file}")
    
    # 4. Supprimer les fichiers temporaires
    temp_patterns = ["*.tmp", "*.temp", "*~", ".DS_Store"]
    for pattern in temp_patterns:
        temp_files = list(project_root.rglob(pattern))
        for temp_file in temp_files:
            temp_file.unlink(missing_ok=True)
            print(f"Supprimé: {temp_file}")
    
    # 5. Supprimer les dossiers vides
    for root, dirs, files in os.walk(project_root, topdown=False):
        for dir_name in dirs:
            dir_path = Path(root) / dir_name
            try:
                if not any(dir_path.iterdir()):  # Dossier vide
                    dir_path.rmdir()
                    print(f"Dossier vide supprimé: {dir_path}")
            except OSError:
                pass  # Dossier non vide ou problème d'accès
    
    # 6. Lister les fichiers potentiellement orphelins
    print("\n=== Vérification des fichiers potentiellement orphelins ===")
    
    # Rechercher les fichiers Python non importés
    python_files = list(project_root.rglob("*.py"))
    all_imports = set()
    
    # Extraire tous les imports
    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Rechercher les imports
                import_lines = [line for line in content.split('\n') 
                              if line.strip().startswith(('import ', 'from '))]
                for line in import_lines:
                    all_imports.add(line.strip())
        except:
            continue
    
    print(f"Analysé {len(python_files)} fichiers Python")
    print(f"Trouvé {len(all_imports)} instructions d'import")
    
    print("\nNettoyage terminé!")

if __name__ == "__main__":
    clean_project()