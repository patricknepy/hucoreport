"""
Fenêtre principale de l'application Huco Report
Interface moderne et professionnelle pour la gestion de rapports de performance
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTabWidget, QFileDialog,
    QMessageBox, QStatusBar, QMenuBar, QMenu, QProgressDialog
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QFont, QIcon
import sys
from pathlib import Path

from src.config.settings import APP_NAME, APP_VERSION, COMPANY_NAME
from src.gui.dashboard_tab import DashboardTab
from src.gui.analysis_tab import AnalysisTab
from src.gui.kpi_tab import KPITab
from src.gui.exploitation_tab import ExploitationTab
from src.gui.cdp_tab import CDPTab
from src.gui.warnings_tab import WarningsTab
from src.gui.import_dialog import ImportDialog
from src.core.excel_importer import ExcelImporter


def get_application_path():
    """Retourne le chemin de base de l'application (compatible .exe)."""
    if getattr(sys, 'frozen', False):
        # Mode .exe (PyInstaller)
        return Path(sys.executable).parent.resolve()
    else:
        # Mode développement
        return Path(__file__).parent.parent.resolve()


class MainWindow(QMainWindow):
    """Fenêtre principale de l'application"""

    def __init__(self):
        super().__init__()
        self.importer = ExcelImporter()
        self.dashboard_tab = None
        self.kpi_tab = None
        self.analysis_tab = None
        self.exploitation_tab = None
        self.cdp_tab = None
        self.warnings_tab = None
        self.init_ui()
        self.showMaximized()  # Plein écran au démarrage

    def init_ui(self):
        """Initialise l'interface utilisateur"""

        # Configuration de la fenêtre
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION} - {COMPANY_NAME}")
        self.setMinimumSize(1200, 800)

        # Création du widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal (COMPACT)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(4)
        main_layout.setContentsMargins(4, 4, 4, 4)

        # En-tête compact avec titre et logo
        header = self.create_header()
        main_layout.addWidget(header)

        # Onglets principaux (import via menu Fichier)
        tabs = self.create_tabs()
        main_layout.addWidget(tabs, stretch=1)

        # Barre de menu
        self.create_menu_bar()

        # Barre de statut
        self.create_status_bar()

        # Appliquer le style moderne
        self.apply_stylesheet()

    def create_header(self):
        """Crée l'en-tête compact de l'application"""
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(10, 2, 10, 2)

        # Logo (taille réduite)
        from PyQt6.QtGui import QPixmap

        logo_label = QLabel()
        logo_size = 40  # Réduit de 70 à 40
        app_path = get_application_path()
        logo_path = Path(__file__).parent.parent.parent / "img" / "cropped-logo-groupe-huco.webp"

        if logo_path.exists():
            pixmap = QPixmap(str(logo_path.resolve()))
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(logo_size, logo_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                logo_label.setPixmap(scaled_pixmap)
        else:
            alt_path = app_path / "img" / "cropped-logo-groupe-huco.webp"
            if alt_path.exists():
                pixmap = QPixmap(str(alt_path.resolve()))
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(logo_size, logo_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    logo_label.setPixmap(scaled_pixmap)

        header_layout.addWidget(logo_label)

        # Titre compact (une seule ligne)
        title_label = QLabel(f"{APP_NAME} - {COMPANY_NAME}")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #2196F3; margin-left: 10px;")

        header_layout.addWidget(title_label)
        header_layout.addStretch()

        return header_widget

    def create_import_section(self):
        """Crée la section d'import de fichiers Excel"""
        import_widget = QWidget()
        import_widget.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
        """)
        import_layout = QHBoxLayout(import_widget)
        import_layout.setContentsMargins(20, 15, 20, 15)

        # Bouton principal d'import avec icône
        import_button = QPushButton("Importer un fichier Excel")
        import_button.setMinimumHeight(45)
        import_button.setMinimumWidth(300)
        import_button.setCursor(Qt.CursorShape.PointingHandCursor)
        import_button.clicked.connect(self.import_excel_file)

        # Style du bouton principal (bien visible)
        import_button.setStyleSheet("""
            QPushButton {
                background-color: #FFC107;
                color: #333;
                border: 2px solid #FFA000;
                border-radius: 5px;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: bold;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #FFD54F;
                border: 2px solid #FFC107;
            }
            QPushButton:pressed {
                background-color: #FFA000;
                border: 2px solid #FF8F00;
            }
        """)

        import_layout.addWidget(import_button)
        import_layout.addStretch()

        return import_widget

    def create_tabs(self):
        """Crée les onglets principaux de l'application"""
        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.TabPosition.North)

        # Onglet 1 : Dashboard
        dashboard_tab = self.create_dashboard_tab()
        tabs.addTab(dashboard_tab, "Dashboard")

        # Onglet 2 : KPIs
        kpi_tab = self.create_kpi_tab()
        tabs.addTab(kpi_tab, "KPIs")

        # Onglet 3 : Analyse
        analysis_tab = self.create_analysis_tab()
        tabs.addTab(analysis_tab, "Analyse")

        # Onglet 4 : Exploitation
        exploitation_tab = self.create_exploitation_tab()
        tabs.addTab(exploitation_tab, "Exploitation")

        # Onglet 5 : CDP (Chefs de Projet)
        cdp_tab = self.create_cdp_tab()
        tabs.addTab(cdp_tab, "CDP")

        # Onglet 6 : Warnings
        warnings_tab = self.create_warnings_tab()
        tabs.addTab(warnings_tab, "Warnings")

        # Onglet 7 : Rapports
        reports_tab = self.create_reports_tab()
        tabs.addTab(reports_tab, "Rapports")

        # Onglet 8 : Automatisation
        automation_tab = self.create_automation_tab()
        tabs.addTab(automation_tab, "Automatisation")

        return tabs

    def create_dashboard_tab(self):
        """Crée l'onglet Dashboard"""
        self.dashboard_tab = DashboardTab()
        return self.dashboard_tab

    def create_kpi_tab(self):
        """Crée l'onglet KPIs"""
        self.kpi_tab = KPITab()
        return self.kpi_tab

    def create_analysis_tab(self):
        """Crée l'onglet Analyse avec les graphiques d'évolution des warnings"""
        self.analysis_tab = AnalysisTab()
        return self.analysis_tab

    def create_exploitation_tab(self):
        """Crée l'onglet Exploitation avec le tableau éditable"""
        self.exploitation_tab = ExploitationTab()
        return self.exploitation_tab

    def create_cdp_tab(self):
        """Crée l'onglet CDP (Chefs de Projet)"""
        self.cdp_tab = CDPTab()
        return self.cdp_tab

    def create_warnings_tab(self):
        """Crée l'onglet Warnings (synthèse des warnings)"""
        self.warnings_tab = WarningsTab()
        return self.warnings_tab

    def create_reports_tab(self):
        """Crée l'onglet Rapports"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        label = QLabel("Rapports - Génération et envoi de rapports")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 16px; color: #666; padding: 50px;")

        # Bouton de génération de rapport
        generate_button = QPushButton("Générer un rapport")
        generate_button.setMinimumHeight(40)
        generate_button.setMaximumWidth(200)
        generate_button.clicked.connect(self.generate_report)

        layout.addStretch()
        layout.addWidget(label)
        layout.addWidget(generate_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()

        return widget

    def create_automation_tab(self):
        """Crée l'onglet Automatisation"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        label = QLabel("Automatisation - Planification et monitoring des deadlines")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 16px; color: #666; padding: 50px;")

        layout.addStretch()
        layout.addWidget(label)
        layout.addStretch()

        return widget

    def create_menu_bar(self):
        """Crée la barre de menu"""
        menubar = self.menuBar()

        # Menu Fichier
        file_menu = menubar.addMenu("Fichier")

        import_action = QAction("Importer Excel...", self)
        import_action.setShortcut("Ctrl+O")
        import_action.triggered.connect(self.import_excel_file)
        file_menu.addAction(import_action)

        file_menu.addSeparator()

        quit_action = QAction("Quitter", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # Menu Outils
        tools_menu = menubar.addMenu("Outils")

        settings_action = QAction("Paramètres...", self)
        settings_action.triggered.connect(self.open_settings)
        tools_menu.addAction(settings_action)

        # Menu Aide
        help_menu = menubar.addMenu("Aide")

        about_action = QAction("À propos", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_status_bar(self):
        """Crée la barre de statut"""
        self.statusBar().showMessage("Prêt - En attente d'un fichier Excel")

    def apply_stylesheet(self):
        """Applique le style CSS à l'application"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QTabWidget::pane {
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #f0f0f0;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background-color: #4CAF50;
                color: white;
            }
            QTabBar::tab:hover {
                background-color: #e0e0e0;
            }
            QGroupBox {
                background-color: #f5f5f5;
                border: none;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)

    # Méthodes d'action

    def import_excel_file(self):
        """Ouvre le dialogue d'import de fichier Excel"""
        app_path = get_application_path()
        import_dir = str(app_path / "import") if (app_path / "import").exists() else str(app_path)

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Sélectionner un fichier Excel",
            import_dir,
            "Fichiers Excel (*.xlsx *.xls);;Tous les fichiers (*.*)"
        )

        if not file_path:
            return

        try:
            # Afficher progression
            progress = QProgressDialog("Validation et simulation en cours...", None, 0, 0, self)
            progress.setWindowTitle("Import en cours")
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.show()

            # ÉTAPE 1+2 : Validation + Simulation
            result = self.importer.validate_and_simulate(file_path)

            progress.close()

            # ÉTAPE 3 : Afficher dialog de validation/simulation
            dialog = ImportDialog(result, self)

            if dialog.exec() and dialog.is_confirmed():
                # L'utilisateur a confirmé l'import
                progress = QProgressDialog("Import des données en cours...", None, 0, 0, self)
                progress.setWindowTitle("Import en cours")
                progress.setWindowModality(Qt.WindowModality.WindowModal)
                progress.show()

                # Import réel
                import_result = self.importer.execute_import(file_path)

                progress.close()

                if import_result['success']:
                    # Succès !
                    self.statusBar().showMessage(
                        f"Import réussi : {import_result['projects_imported']} projets importés"
                    )

                    QMessageBox.information(
                        self,
                        "Import réussi",
                        f"Import terminé avec succès !\n\n"
                        f"* Fichier sauvegardé : {import_result['file_saved_as']}\n"
                        f"* Projets importés : {import_result['projects_imported']}\n"
                        f"* Semaines : {', '.join(['S' + str(w) for w in import_result['weeks_imported']])}\n\n"
                        f"Le dashboard a été mis à jour."
                    )

                    # Rafraîchir tous les onglets
                    if self.dashboard_tab:
                        self.dashboard_tab.load_available_weeks()
                    if self.analysis_tab:
                        self.analysis_tab.refresh_charts()
                    if self.exploitation_tab:
                        self.exploitation_tab.load_weeks()
                    if self.cdp_tab:
                        self.cdp_tab.load_available_weeks()
                    if self.warnings_tab:
                        self.warnings_tab.load_available_weeks()
                else:
                    # Erreur d'import
                    error_msg = '\n'.join(import_result['errors'])
                    QMessageBox.critical(
                        self,
                        "Erreur d'import",
                        f"L'import a échoué :\n\n{error_msg}"
                    )
            else:
                # L'utilisateur a annulé
                self.statusBar().showMessage("Import annulé")

        except Exception as e:
            QMessageBox.critical(
                self,
                "Erreur",
                f"Une erreur est survenue :\n\n{str(e)}"
            )
            self.statusBar().showMessage("Erreur lors de l'import")

    def generate_report(self):
        """Génère un rapport"""
        QMessageBox.information(
            self,
            "Génération de rapport",
            "Fonctionnalité de génération de rapport en cours de développement..."
        )

    def open_settings(self):
        """Ouvre les paramètres"""
        QMessageBox.information(
            self,
            "Paramètres",
            "Interface de paramètres en cours de développement..."
        )

    def show_about(self):
        """Affiche la boîte de dialogue À propos"""
        QMessageBox.about(
            self,
            f"À propos de {APP_NAME}",
            f"<h2>{APP_NAME}</h2>"
            f"<p>Version {APP_VERSION}</p>"
            f"<p><b>{COMPANY_NAME}</b></p>"
            f"<p>Outil professionnel de gestion de rapports de performance</p>"
            f"<p>Développé avec Python et PyQt6</p>"
            f"<hr>"
            f"<p style='font-size: 10px;'>© 2025 {COMPANY_NAME}. Tous droits réservés.</p>"
        )

