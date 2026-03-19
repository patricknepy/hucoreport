"""
Onglet Engagements de l'application Huco Report.

Affiche les engagements CDP S+1 depuis le fichier Excel Suivi_Hebdo_Projet_GDP_HUCO :
- Tableau des projets actifs tries par jours S+1
- Totaux par Chef de Projet
- Totaux par Phase (RUN, BUILD, AVANT VENTES)
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QGroupBox, QTableWidget, QTableWidgetItem,
    QScrollArea, QFrame, QHeaderView, QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
import pandas as pd
from pathlib import Path
import re
import logging
import unicodedata

logger = logging.getLogger(__name__)


def normalize_col_name(name: str) -> str:
    """Normalise un nom de colonne en supprimant les accents et espaces multiples."""
    # Normaliser unicode (NFD decompose les accents)
    normalized = unicodedata.normalize('NFD', str(name))
    # Supprimer les diacritiques (accents)
    ascii_name = ''.join(c for c in normalized if unicodedata.category(c) != 'Mn')
    # Mettre en minuscules et supprimer espaces multiples
    return ' '.join(ascii_name.lower().split())


def find_column(df, pattern: str, alternatives: list = None) -> str:
    """Trouve une colonne correspondant au pattern (insensible aux accents).

    Args:
        df: DataFrame pandas
        pattern: Pattern principal a chercher
        alternatives: Liste de patterns alternatifs a essayer si le principal echoue
    """
    patterns_to_try = [pattern] + (alternatives or [])

    for p in patterns_to_try:
        pattern_normalized = normalize_col_name(p)
        # Match exact
        for col in df.columns:
            if normalize_col_name(col) == pattern_normalized:
                return col
        # Match partiel
        for col in df.columns:
            if pattern_normalized in normalize_col_name(col):
                return col

    raise KeyError(f"Colonne '{pattern}' non trouvee (alternatives essayees: {alternatives})")


class EngagementsTab(QWidget):
    """Onglet Engagements CDP S+1."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.df_projets = None
        self.current_file = None
        self.current_sheet = None
        self.init_ui()

    def init_ui(self):
        """Initialise l'interface utilisateur."""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # En-tete
        header = self._create_header()
        main_layout.addWidget(header)

        # Scroll area pour le contenu
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setSpacing(15)
        content_layout.setContentsMargins(5, 5, 5, 5)

        # Section Totaux
        self.totals_section = self._create_totals_section()
        content_layout.addWidget(self.totals_section)

        # Section Tableau CDP
        self.cdp_section = self._create_cdp_section()
        content_layout.addWidget(self.cdp_section)

        # Section Tableau Projets
        self.projects_section = self._create_projects_section()
        content_layout.addWidget(self.projects_section)

        content_layout.addStretch()
        content_widget.setLayout(content_layout)
        scroll.setWidget(content_widget)

        main_layout.addWidget(scroll)
        self.setLayout(main_layout)

        # Charger automatiquement le dernier fichier
        self.auto_load_latest_file()

    def _create_header(self) -> QWidget:
        """Cree l'en-tete avec titre et bouton de chargement."""
        widget = QWidget()
        layout = QHBoxLayout()

        title = QLabel("ENGAGEMENTS CDP - S+1")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #1E3A5F;")
        layout.addWidget(title)

        layout.addStretch()

        # Info fichier charge
        self.file_info_label = QLabel("Aucun fichier charge")
        self.file_info_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.file_info_label)

        # Bouton charger
        load_btn = QPushButton("Charger fichier Excel")
        load_btn.setStyleSheet("""
            QPushButton {
                background-color: #E86C00;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FF8C20;
            }
        """)
        load_btn.clicked.connect(self.load_file_dialog)
        layout.addWidget(load_btn)

        # Bouton rafraichir
        refresh_btn = QPushButton("Rafraichir")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        refresh_btn.clicked.connect(self.auto_load_latest_file)
        layout.addWidget(refresh_btn)

        widget.setLayout(layout)
        return widget

    def _create_totals_section(self) -> QGroupBox:
        """Cree la section des totaux."""
        group = QGroupBox("TOTAL ENGAGEMENT S+1")
        group.setStyleSheet("""
            QGroupBox {
                background-color: #1E3A5F;
                border: none;
                border-radius: 5px;
                margin-top: 10px;
                padding: 15px;
                color: white;
                font-weight: bold;
                font-size: 12pt;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: white;
            }
        """)

        layout = QHBoxLayout()
        layout.setSpacing(20)

        # Total jours
        self.total_jours_label = QLabel("0")
        self.total_jours_label.setStyleSheet("""
            font-size: 36pt;
            font-weight: bold;
            color: #E86C00;
        """)
        self.total_jours_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        total_jours_title = QLabel("JOURS")
        total_jours_title.setStyleSheet("font-size: 10pt; color: white;")
        total_jours_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        jours_layout = QVBoxLayout()
        jours_layout.addWidget(self.total_jours_label)
        jours_layout.addWidget(total_jours_title)
        layout.addLayout(jours_layout)

        # Separateur
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setStyleSheet("background-color: #fff; max-width: 2px;")
        layout.addWidget(sep)

        # Par phase
        self.phase_labels = {}
        for phase in ["RUN", "BUILD", "AVANT VENTES"]:
            phase_layout = QVBoxLayout()

            value_label = QLabel("0")
            value_label.setStyleSheet("font-size: 20pt; font-weight: bold; color: white;")
            value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.phase_labels[phase] = value_label

            title_label = QLabel(phase)
            title_label.setStyleSheet("font-size: 9pt; color: #aaa;")
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            phase_layout.addWidget(value_label)
            phase_layout.addWidget(title_label)
            layout.addLayout(phase_layout)

        layout.addStretch()
        group.setLayout(layout)
        return group

    def _create_cdp_section(self) -> QGroupBox:
        """Cree la section tableau par CDP."""
        group = QGroupBox("PAR CHEF DE PROJET")
        group.setStyleSheet("""
            QGroupBox {
                background-color: #f5f5f5;
                border: 2px solid #1E3A5F;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
                font-weight: bold;
            }
        """)

        layout = QVBoxLayout()

        self.cdp_table = QTableWidget()
        self.cdp_table.setColumnCount(3)
        self.cdp_table.setHorizontalHeaderLabels(["Chef de Projet", "Jours S+1", "Nb Projets"])
        self.cdp_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.cdp_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.cdp_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.cdp_table.setColumnWidth(1, 100)
        self.cdp_table.setColumnWidth(2, 100)
        self.cdp_table.setAlternatingRowColors(True)
        self.cdp_table.setMaximumHeight(250)

        layout.addWidget(self.cdp_table)
        group.setLayout(layout)
        return group

    def _create_projects_section(self) -> QGroupBox:
        """Cree la section tableau des projets."""
        group = QGroupBox("LISTE DES PROJETS ACTIFS")
        group.setStyleSheet("""
            QGroupBox {
                background-color: #f5f5f5;
                border: 2px solid #6B2D7B;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
                font-weight: bold;
            }
        """)

        layout = QVBoxLayout()

        self.projects_table = QTableWidget()
        self.projects_table.setColumnCount(4)
        self.projects_table.setHorizontalHeaderLabels(["Projet", "Jours S+1", "Phase", "Chef de Projet"])
        self.projects_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.projects_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.projects_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.projects_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.projects_table.setColumnWidth(1, 100)
        self.projects_table.setColumnWidth(2, 120)
        self.projects_table.setColumnWidth(3, 180)
        self.projects_table.setAlternatingRowColors(True)
        self.projects_table.setMinimumHeight(400)

        layout.addWidget(self.projects_table)
        group.setLayout(layout)
        return group

    def auto_load_latest_file(self):
        """Charge automatiquement le dernier fichier Suivi_Hebdo dans Downloads."""
        try:
            # Chemin Downloads
            downloads_path = Path.home() / "Downloads"

            # Chercher tous les fichiers Suivi_Hebdo
            pattern = "Suivi_Hebdo_Projet_GDP_HUCO*.xlsx"
            files = list(downloads_path.glob(pattern))

            if not files:
                self.file_info_label.setText("Aucun fichier Suivi_Hebdo trouve dans Downloads")
                return

            # Trier par numero (extraire le numero entre parentheses)
            def get_file_number(f):
                match = re.search(r'\((\d+)\)', f.name)
                if match:
                    return int(match.group(1))
                return 0

            files.sort(key=get_file_number, reverse=True)
            latest_file = files[0]

            self.load_excel_file(str(latest_file))

        except Exception as e:
            logger.error(f"Erreur auto_load: {e}")
            self.file_info_label.setText(f"Erreur: {str(e)}")

    def load_file_dialog(self):
        """Ouvre un dialogue pour selectionner un fichier Excel."""
        downloads_path = str(Path.home() / "Downloads")

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Selectionner le fichier Suivi Hebdo",
            downloads_path,
            "Fichiers Excel (*.xlsx);;Tous les fichiers (*.*)"
        )

        if file_path:
            self.load_excel_file(file_path)

    def load_excel_file(self, file_path: str):
        """Charge un fichier Excel et extrait les donnees."""
        try:
            # Charger le fichier Excel
            xl = pd.ExcelFile(file_path)

            # Trouver la derniere feuille SXX
            sheet_names = xl.sheet_names
            sxx_sheets = [s for s in sheet_names if re.match(r'^S\d+$', s)]

            if not sxx_sheets:
                # Chercher les feuilles avec "S" suivi de chiffres
                sxx_sheets = [s for s in sheet_names if s.startswith('S') and any(c.isdigit() for c in s)]

            if not sxx_sheets:
                QMessageBox.warning(self, "Erreur", "Aucune feuille SXX trouvee dans le fichier")
                return

            # Prendre la derniere feuille SXX dans l'ordre du fichier
            # (les feuilles recentes sont ajoutees a la fin)
            # On garde l'ordre original de sheet_names
            ordered_sxx = [s for s in sheet_names if s in sxx_sheets]
            latest_sheet = ordered_sxx[-1]

            # Charger la feuille
            df = pd.read_excel(file_path, sheet_name=latest_sheet, header=2)
            df.columns = df.columns.str.strip()

            # Trouver les noms de colonnes (insensible aux accents)
            col_statut = find_column(df, 'Statut Projet')
            col_projet = find_column(df, 'Projet Client')
            col_facturable = find_column(df, 'Facturable prevu S+1', [
                'Temps facturable en main',
                'Facturable en main',
                'facturable S+1'
            ])
            col_phase = find_column(df, 'Phase du projet')
            col_cdp = find_column(df, 'Chef de projet')

            # Filtrer projets actifs
            df_actif = df[df[col_statut] == 'Actif'].copy()
            df_actif[col_facturable] = pd.to_numeric(
                df_actif[col_facturable], errors='coerce'
            ).fillna(0)

            # Preparer les donnees avec noms de colonnes standardises
            self.df_projets = df_actif[[col_projet, col_facturable, col_phase, col_cdp]].copy()
            self.df_projets.columns = ['Projet Client', 'Jours S+1', 'Phase du projet', 'Chef de projet']
            self.df_projets = self.df_projets.sort_values('Jours S+1', ascending=False)
            self.df_projets['Projet Client'] = self.df_projets['Projet Client'].str.replace('\n', ' ')
            self.df_projets['Phase du projet'] = self.df_projets['Phase du projet'].fillna('N/A')

            self.current_file = file_path
            self.current_sheet = latest_sheet

            # Mettre a jour l'affichage
            self.update_display()

            # Mettre a jour le label
            file_name = Path(file_path).name
            self.file_info_label.setText(f"{file_name} - Feuille {latest_sheet}")
            self.file_info_label.setStyleSheet("color: #4CAF50; font-weight: bold;")

        except Exception as e:
            logger.error(f"Erreur load_excel: {e}")
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement:\n{str(e)}")

    def update_display(self):
        """Met a jour l'affichage avec les donnees chargees."""
        if self.df_projets is None:
            return

        df = self.df_projets

        # Total
        total = df['Jours S+1'].sum()
        self.total_jours_label.setText(f"{total:.0f}")

        # Par phase
        phase_totals = df.groupby('Phase du projet')['Jours S+1'].sum()
        for phase, label in self.phase_labels.items():
            val = phase_totals.get(phase, 0)
            label.setText(f"{val:.1f}")

        # Tableau CDP
        cdp_recap = df.groupby('Chef de projet').agg({
            'Jours S+1': 'sum',
            'Projet Client': 'count'
        }).rename(columns={'Projet Client': 'Nb Projets'})
        cdp_recap = cdp_recap.sort_values('Jours S+1', ascending=False)

        self.cdp_table.setRowCount(len(cdp_recap))
        for i, (cdp, row) in enumerate(cdp_recap.iterrows()):
            self.cdp_table.setItem(i, 0, QTableWidgetItem(str(cdp)))

            jours_item = QTableWidgetItem(f"{row['Jours S+1']:.1f}")
            jours_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if row['Jours S+1'] > 0:
                jours_item.setForeground(QColor("#E86C00"))
                jours_item.setFont(QFont("", -1, QFont.Weight.Bold))
            self.cdp_table.setItem(i, 1, jours_item)

            nb_item = QTableWidgetItem(str(int(row['Nb Projets'])))
            nb_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.cdp_table.setItem(i, 2, nb_item)

        # Tableau projets
        self.projects_table.setRowCount(len(df))
        for i, (_, row) in enumerate(df.iterrows()):
            self.projects_table.setItem(i, 0, QTableWidgetItem(str(row['Projet Client'])[:50]))

            jours_item = QTableWidgetItem(f"{row['Jours S+1']:.1f}" if row['Jours S+1'] > 0 else "-")
            jours_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if row['Jours S+1'] > 0:
                jours_item.setForeground(QColor("#E86C00"))
                jours_item.setFont(QFont("", -1, QFont.Weight.Bold))
            self.projects_table.setItem(i, 1, jours_item)

            phase_item = QTableWidgetItem(str(row['Phase du projet']))
            phase_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.projects_table.setItem(i, 2, phase_item)

            self.projects_table.setItem(i, 3, QTableWidgetItem(str(row['Chef de projet'])))
