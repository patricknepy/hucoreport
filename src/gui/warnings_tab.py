"""
Onglet Warnings de l'application.

Affiche une synthèse de tous les projets en warning avec :
- Nom du client
- Chef de projet
- Type de warning (Client/Interne/Les deux)
- Commentaire vision interne
- Action
- Prochain acteur
- DLIC et DLI
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QGroupBox, QTableWidget, QTableWidgetItem,
    QScrollArea, QFrame, QHeaderView, QTextEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from typing import List, Dict, Any

from src.core.database import Database
from src.core.dashboard_calculator import DashboardCalculator
import logging

logger = logging.getLogger(__name__)


class WarningsTab(QWidget):
    """Onglet synthèse des Warnings."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = Database()
        self.current_week = None
        self.init_ui()
        self.load_available_weeks()

    def init_ui(self):
        """Initialise l'interface utilisateur."""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # En-tête
        header = self._create_header()
        main_layout.addWidget(header)

        # Section KPIs
        self.kpis_section = self._create_kpis_section()
        main_layout.addWidget(self.kpis_section)

        # Section Tableau
        self.table_section = self._create_table_section()
        main_layout.addWidget(self.table_section, stretch=1)

        self.setLayout(main_layout)

    def _create_header(self) -> QWidget:
        """Crée l'en-tête avec titre et sélecteur de semaine."""
        widget = QWidget()
        layout = QHBoxLayout()

        title = QLabel("SYNTHESE DES WARNINGS")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        layout.addStretch()

        week_label = QLabel("Semaine :")
        layout.addWidget(week_label)

        self.week_combo = QComboBox()
        self.week_combo.setMinimumWidth(150)
        self.week_combo.currentIndexChanged.connect(self.on_week_changed)
        layout.addWidget(self.week_combo)

        widget.setLayout(layout)
        return widget

    def _create_compact_tile(self, title: str, value: str, color: str = "#0166FE") -> QFrame:
        """Crée une tuile compacte."""
        tile = QFrame()
        tile.setFrameShape(QFrame.Shape.StyledPanel)
        tile.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border: none;
                border-radius: 5px;
            }}
        """)
        tile.setFixedWidth(150)
        tile.setFixedHeight(90)

        layout = QVBoxLayout(tile)
        layout.setSpacing(3)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        value_label = QLabel(value)
        value_label.setStyleSheet("font-size: 22pt; color: white; font-weight: bold;")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(value_label)

        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 8pt; color: white; font-weight: bold;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setWordWrap(True)
        layout.addWidget(title_label)

        tile.value_label = value_label

        return tile

    def _create_kpis_section(self) -> QGroupBox:
        """Crée la section des KPIs."""
        group = QGroupBox("RESUME")
        group.setStyleSheet("""
            QGroupBox {
                background-color: #f8faff;
                border: 2px solid black;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
            }
        """)

        layout = QHBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        self.tile_total = self._create_compact_tile("Total Warnings", "0", "#F44336")
        layout.addWidget(self.tile_total)

        self.tile_client = self._create_compact_tile("Warning Client", "0", "#FF9800")
        layout.addWidget(self.tile_client)

        self.tile_internal = self._create_compact_tile("Warning Interne", "0", "#FF5722")
        layout.addWidget(self.tile_internal)

        self.tile_both = self._create_compact_tile("Les deux", "0", "#FE4502")
        layout.addWidget(self.tile_both)

        self.tile_dlic_overdue = self._create_compact_tile("DLIC Dépassées", "0", "#D32F2F")
        layout.addWidget(self.tile_dlic_overdue)

        self.tile_no_actor = self._create_compact_tile("Sans acteur", "0", "#795548")
        layout.addWidget(self.tile_no_actor)

        layout.addStretch()

        group.setLayout(layout)
        return group

    def _create_table_section(self) -> QGroupBox:
        """Crée la section du tableau."""
        group = QGroupBox("DETAILS DES WARNINGS")
        group.setStyleSheet("""
            QGroupBox {
                background-color: #f8faff;
                border: 2px solid black;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)

        # Tableau
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "Client",
            "Chef Projet",
            "BU",
            "Type",
            "Vision Client",
            "Vision Interne",
            "Action",
            "Acteur",
            "DLIC",
            "DLI"
        ])

        # Style du tableau
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                gridline-color: #ddd;
                font-size: 9pt;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #F44336;
                color: white;
                padding: 8px;
                font-weight: bold;
                border: none;
            }
            QTableWidget::item:alternate {
                background-color: #f9f9f9;
            }
        """)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Client
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Chef Projet
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # BU
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Type
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)  # Vision Client
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)  # Vision Interne
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)  # Action
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)  # Acteur
        header.setSectionResizeMode(8, QHeaderView.ResizeMode.ResizeToContents)  # DLIC
        header.setSectionResizeMode(9, QHeaderView.ResizeMode.ResizeToContents)  # DLI

        self.table.setWordWrap(True)
        self.table.verticalHeader().setDefaultSectionSize(60)

        layout.addWidget(self.table)

        group.setLayout(layout)
        return group

    def load_available_weeks(self):
        """Charge les semaines disponibles."""
        weeks = self.db.get_available_weeks()

        self.week_combo.blockSignals(True)
        self.week_combo.clear()

        if not weeks:
            self.week_combo.addItem("Aucune donnée")
            self.week_combo.setEnabled(False)
            self.week_combo.blockSignals(False)
            return

        self.week_combo.setEnabled(True)

        for week in weeks:
            self.week_combo.addItem(f"S{week:02d}", week)

        self.week_combo.blockSignals(False)

        if weeks:
            self.week_combo.setCurrentIndex(0)
            self.current_week = weeks[0]
            self.refresh_data()

    def on_week_changed(self, index: int):
        """Gère le changement de semaine."""
        if index < 0:
            return

        week = self.week_combo.itemData(index)
        if week:
            self.current_week = week
            self.refresh_data()

    def refresh_data(self):
        """Rafraîchit toutes les données de l'onglet."""
        if not self.current_week:
            return

        try:
            calc = DashboardCalculator(self.db)

            # Récupérer le résumé
            summary = calc.get_warnings_summary(self.current_week)
            self._update_kpis(summary)

            # Récupérer les détails
            warnings = calc.get_warnings_details(self.current_week)
            self._update_table(warnings)

        except Exception as e:
            logger.error(f"Erreur lors du rafraîchissement Warnings: {e}")

    def _update_kpis(self, summary: Dict[str, Any]):
        """Met à jour les KPIs."""
        self.tile_total.value_label.setText(str(summary['total_warnings']))
        self.tile_client.value_label.setText(str(summary['client_only']))
        self.tile_internal.value_label.setText(str(summary['internal_only']))
        self.tile_both.value_label.setText(str(summary['both']))
        self.tile_dlic_overdue.value_label.setText(str(summary['dlic_overdue']))
        self.tile_no_actor.value_label.setText(str(summary['no_actor']))

    def _update_table(self, warnings: List[Dict[str, Any]]):
        """Met à jour le tableau."""
        self.table.setRowCount(len(warnings))

        for row, w in enumerate(warnings):
            # Client
            item = QTableWidgetItem(w.get('client_name', ''))
            item.setToolTip(f"Projet #{w.get('id_projet', '')}")
            self.table.setItem(row, 0, item)

            # Chef Projet
            item = QTableWidgetItem(w.get('project_manager', '') or '')
            self.table.setItem(row, 1, item)

            # BU
            item = QTableWidgetItem(w.get('bu', '') or '')
            self.table.setItem(row, 2, item)

            # Type de warning
            warning_type = w.get('warning_type', '')
            item = QTableWidgetItem(warning_type)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if warning_type == 'Client':
                item.setBackground(QColor("#FFCDD2"))
            elif warning_type == 'Interne':
                item.setBackground(QColor("#FFE0B2"))
            else:  # Les deux
                item.setBackground(QColor("#E1BEE7"))
            self.table.setItem(row, 3, item)

            # Vision Client
            vision_client = w.get('vision_client', '') or ''
            item = QTableWidgetItem(vision_client)
            item.setToolTip(vision_client)
            self.table.setItem(row, 4, item)

            # Vision Interne
            vision_internal = w.get('vision_internal', '') or ''
            item = QTableWidgetItem(vision_internal)
            item.setToolTip(vision_internal)
            self.table.setItem(row, 5, item)

            # Action
            action = w.get('action_description', '') or ''
            item = QTableWidgetItem(action)
            item.setToolTip(action)
            self.table.setItem(row, 6, item)

            # Acteur
            actor = w.get('next_actor', '') or ''
            item = QTableWidgetItem(actor)
            if not actor:
                item.setBackground(QColor("#FFCDD2"))
                item.setText("VIDE")
            self.table.setItem(row, 7, item)

            # DLIC
            dlic = w.get('dlic_formatted', '') or ''
            item = QTableWidgetItem(dlic)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if w.get('dlic_overdue'):
                item.setBackground(QColor("#FFCDD2"))
                item.setForeground(QColor("#D32F2F"))
            self.table.setItem(row, 8, item)

            # DLI
            dli = w.get('dli_formatted', '') or ''
            item = QTableWidgetItem(dli)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if w.get('dli_overdue'):
                item.setBackground(QColor("#FFE0B2"))
            self.table.setItem(row, 9, item)

        # Ajuster la hauteur des lignes en fonction du contenu
        self.table.resizeRowsToContents()
