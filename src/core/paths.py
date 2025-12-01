"""
Gestion centralisée des chemins de l'application.

Ce module fournit des fonctions pour obtenir les chemins de l'application,
en gérant les problèmes de permissions et en utilisant AppData pour les données.
"""

import sys
import os
from pathlib import Path


def get_application_path() -> Path:
    """
    Retourne le chemin de base de l'application (compatible .exe).
    
    En mode .exe : retourne le dossier contenant l'exécutable
    En mode développement : retourne la racine du projet
    """
    if getattr(sys, 'frozen', False):
        # Mode .exe (PyInstaller) : chemin du dossier contenant l'exe
        return Path(sys.executable).parent.resolve()
    else:
        # Mode développement : racine du projet (3 niveaux au-dessus de ce fichier)
        return Path(__file__).parent.parent.parent.resolve()


def get_data_directory() -> Path:
    """
    Retourne le dossier pour stocker les données (base de données, logs, etc.).
    
    En mode .exe : utilise AppData/Local/HucoReport pour éviter les problèmes de permissions
    En mode développement : utilise le dossier data/ dans le projet
    """
    if getattr(sys, 'frozen', False):
        # Mode .exe : utiliser AppData pour éviter les problèmes de permissions
        appdata = os.getenv('LOCALAPPDATA')
        if appdata:
            data_dir = Path(appdata) / "HucoReport"
        else:
            # Fallback si LOCALAPPDATA n'existe pas (rare)
            data_dir = Path.home() / ".HucoReport"
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir.resolve()
    else:
        # Mode développement : dossier data/ dans le projet
        return get_application_path() / "data"

