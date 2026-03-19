"""
Huco Report - Outil de Gestion de Rapports de Performance
Humans Connexion - 2025

Point d'entrée principal de l'application
"""

import sys
import traceback
import logging
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

def get_application_path():
    """Retourne le chemin de base de l'application (compatible .exe)."""
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent.resolve()
    else:
        return Path(__file__).parent.resolve()

# Configuration du logging AVANT tout import
app_path = get_application_path()

# En mode développement, utiliser le dossier logs/ du projet
# En mode .exe, on utilisera AppData (via get_data_directory plus tard si nécessaire)
log_dir = app_path / "logs"

log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / "error.log"

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
    ]
)
logger = logging.getLogger(__name__)

def exception_handler(exc_type, exc_value, exc_traceback):
    """Gestionnaire global des exceptions non capturées."""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    logger.critical(f"Exception non capturée:\n{error_msg}")
    
    # Afficher un message d'erreur visible à l'utilisateur
    try:
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("Erreur - Huco Report")
        msg.setText("Une erreur critique est survenue.")
        msg.setInformativeText(
            f"L'application n'a pas pu démarrer.\n\n"
            f"Veuillez consulter le fichier de log :\n{log_file}\n\n"
            f"Erreur : {str(exc_value)}"
        )
        msg.exec()
    except:
        pass

# Installer le gestionnaire d'exceptions
sys.excepthook = exception_handler

from src.gui.main_window import MainWindow


def main():
    """Lance l'application Huco Report"""
    try:
        logger.info("=" * 60)
        logger.info("DEMARRAGE HUCO REPORT")
        logger.info("=" * 60)
        logger.info(f"Chemin application: {app_path}")
        logger.info(f"Fichier log: {log_file}")
        
        # Configuration de l'application
        app = QApplication(sys.argv)
        app.setApplicationName("Huco Report")
        app.setOrganizationName("Humans Connexion")
        app.setOrganizationDomain("humansconnexion.com")
        
        logger.info("Application Qt créée")

        # Active le High DPI scaling pour les écrans modernes
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )

        # Style global pour les scrollbars (plus larges et visibles)
        app.setStyleSheet("""
            QScrollBar:vertical {
                background-color: #f0f0f0;
                width: 16px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #888;
                min-height: 30px;
                border-radius: 7px;
                margin: 2px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #666;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar:horizontal {
                background-color: #f0f0f0;
                height: 16px;
                margin: 0px;
            }
            QScrollBar::handle:horizontal {
                background-color: #888;
                min-width: 30px;
                border-radius: 7px;
                margin: 2px;
            }
            QScrollBar::handle:horizontal:hover {
                background-color: #666;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
        """)

        logger.info("Création de la fenêtre principale...")
        # Création et affichage de la fenêtre principale
        window = MainWindow()
        logger.info("Fenêtre principale créée")
        
        window.show()
        logger.info("Fenêtre affichée - Lancement de la boucle d'événements")
        
        # Lancement de la boucle d'événements
        sys.exit(app.exec())
        
    except Exception as e:
        logger.critical(f"Erreur fatale au démarrage: {e}", exc_info=True)
        error_msg = QMessageBox()
        error_msg.setIcon(QMessageBox.Icon.Critical)
        error_msg.setWindowTitle("Erreur Fatale")
        error_msg.setText(f"L'application n'a pas pu démarrer.\n\nErreur: {str(e)}\n\nVoir le log: {log_file}")
        error_msg.exec()
        sys.exit(1)


if __name__ == "__main__":
    main()

