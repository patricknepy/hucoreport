"""
Configuration globale de l'application Huco Report
"""

import os
from pathlib import Path

# Chemins de base
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
TEMPLATES_DIR = DATA_DIR / "templates"
CACHE_DIR = DATA_DIR / "cache"
LOGS_DIR = BASE_DIR / "logs"

# Création des dossiers si nécessaire
for directory in [DATA_DIR, TEMPLATES_DIR, CACHE_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Configuration de l'application
APP_NAME = "Huco Report"
APP_VERSION = "1.0.0"
COMPANY_NAME = "Humans Connexion"

# Configuration de la base de données locale
DATABASE_PATH = DATA_DIR / "cache.db"

# Configuration des rapports
REPORT_FORMATS = ["PDF", "Excel", "HTML"]
DEFAULT_REPORT_FORMAT = "PDF"

# Configuration email (à configurer par l'utilisateur)
EMAIL_CONFIG = {
    "smtp_server": "",
    "smtp_port": 587,
    "use_tls": True,
    "username": "",
    "password": "",
    "from_address": "",
}

# Configuration du scheduler
SCHEDULE_CHECK_INTERVAL = 60  # secondes

# Règles d'identification Excel par défaut
EXCEL_RULES = {
    "deadline_column": "C",
    "status_column": "D",
    "responsible_column": "E",
    "priority_column": "F",
}

# Interface utilisateur
WINDOW_MIN_WIDTH = 1200
WINDOW_MIN_HEIGHT = 800
THEME = "default"  # default, dark, light

