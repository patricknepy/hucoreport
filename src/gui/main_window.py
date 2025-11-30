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
from PyQt6.QtGui import QAction, QFont
import sys
from pathlib import Path

from src.config.settings import APP_NAME, APP_VERSION, COMPANY_NAME
from src.gui.dashboard_tab import DashboardTab
from src.gui.import_dialog import ImportDialog
from src.core.excel_importer import ExcelImporter


def get_application_path():
    """Retourne le chemin de base de l'application (compatible .exe)."""
    if getattr(sys, 'frozen', False):
        # Mode .exe (PyInstaller)
        return Path(sys.executable).parent
    else:
        # Mode développement
        return Path(__file__).parent.parent


class MainWindow(QMainWindow):
    """Fenêtre principale de l'application"""
    
    def __init__(self):
        super().__init__()
        self.importer = ExcelImporter()
        self.dashboard_tab = None
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
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # En-tête avec titre et logo
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Zone d'import de fichier
        import_section = self.create_import_section()
        main_layout.addWidget(import_section)
        
        # Onglets principaux
        tabs = self.create_tabs()
        main_layout.addWidget(tabs, stretch=1)
        
        # Barre de menu
        self.create_menu_bar()
        
        # Barre de statut
        self.create_status_bar()
        
        # Appliquer le style moderne
        self.apply_stylesheet()
        
    def create_header(self):
        """Crée l'en-tête de l'application"""
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(20, 10, 20, 10)
        
        # Logo
        from PyQt6.QtGui import QPixmap
        logo_label = QLabel()
        app_path = get_application_path()
        logo_path = app_path / "img" / "cropped-logo-groupe-huco.webp"
        pixmap = QPixmap(str(logo_path))
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
        header_layout.addWidget(logo_label)
        
        # Titres
        titles_layout = QVBoxLayout()
        
        # Titre principal
        title_label = QLabel(f"{APP_NAME}")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #2196F3;")
        
        # Sous-titre
        subtitle_label = QLabel(f"Outil de Gestion de Rapports de Performance - {COMPANY_NAME}")
        subtitle_font = QFont()
        subtitle_font.setPointSize(9)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setStyleSheet("color: #666;")
        
        titles_layout.addWidget(title_label)
        titles_layout.addWidget(subtitle_label)
        
        header_layout.addLayout(titles_layout)
        header_layout.addStretch()
        
        return header_widget
    
    def create_import_section(self):
        """Crée la section d'import de fichiers Excel"""
        import_widget = QWidget()
        import_widget.setStyleSheet("""
            QWidget {
                background-color: #fafafa;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
        """)
        import_layout = QHBoxLayout(import_widget)
        import_layout.setContentsMargins(15, 10, 15, 10)
        
        # Label
        label = QLabel("📁 Importer un fichier Excel")
        label.setStyleSheet("color: #666; font-size: 11pt;")
        import_layout.addWidget(label)
        
        import_layout.addStretch()
        
        # Bouton d'import compact
        import_button = QPushButton("Choisir un fichier")
        import_button.setMinimumHeight(35)
        import_button.setMaximumWidth(200)
        import_button.setCursor(Qt.CursorShape.PointingHandCursor)
        import_button.clicked.connect(self.import_excel_file)
        import_layout.addWidget(import_button)
        
        return import_widget
    
    def create_tabs(self):
        """Crée les onglets principaux de l'application"""
        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.TabPosition.North)
        
        # Onglet 1 : Dashboard
        dashboard_tab = self.create_dashboard_tab()
        tabs.addTab(dashboard_tab, "📊 Dashboard")
        
        # Onglet 2 : Analyse
        analysis_tab = self.create_analysis_tab()
        tabs.addTab(analysis_tab, "📈 Analyse")
        
        # Onglet 3 : Rapports
        reports_tab = self.create_reports_tab()
        tabs.addTab(reports_tab, "📄 Rapports")
        
        # Onglet 4 : Automatisation
        automation_tab = self.create_automation_tab()
        tabs.addTab(automation_tab, "⚙️ Automatisation")
        
        return tabs
    
    def create_dashboard_tab(self):
        """Crée l'onglet Dashboard"""
        self.dashboard_tab = DashboardTab()
        return self.dashboard_tab
    
    def create_analysis_tab(self):
        """Crée l'onglet Analyse"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        label = QLabel("Analyse - Tableaux croisés dynamiques et filtres")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 16px; color: #666; padding: 50px;")
        
        layout.addStretch()
        layout.addWidget(label)
        layout.addStretch()
        
        return widget
    
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
                        f"✅ Import terminé avec succès !\n\n"
                        f"• Fichier sauvegardé : {import_result['file_saved_as']}\n"
                        f"• Projets importés : {import_result['projects_imported']}\n"
                        f"• Semaines : {', '.join(['S' + str(w) for w in import_result['weeks_imported']])}\n\n"
                        f"Le dashboard a été mis à jour."
                    )
                    
                    # Rafraîchir le dashboard
                    if self.dashboard_tab:
                        self.dashboard_tab.load_available_weeks()
                else:
                    # Erreur d'import
                    error_msg = '\n'.join(import_result['errors'])
                    QMessageBox.critical(
                        self,
                        "Erreur d'import",
                        f"❌ L'import a échoué :\n\n{error_msg}"
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

