"""
Huco Report - Outil de Gestion de Rapports de Performance
Humans Connexion - 2025

Point d'entrée principal de l'application
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

from src.gui.main_window import MainWindow


def main():
    """Lance l'application Huco Report"""
    
    # Configuration de l'application
    app = QApplication(sys.argv)
    app.setApplicationName("Huco Report")
    app.setOrganizationName("Humans Connexion")
    app.setOrganizationDomain("humansconnexion.com")
    
    # Active le High DPI scaling pour les écrans modernes
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    # Création et affichage de la fenêtre principale
    window = MainWindow()
    window.show()
    
    # Lancement de la boucle d'événements
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

