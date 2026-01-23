"""
Onglet Dashboard principal de l'application.

Affiche les indicateurs clés de performance pour la semaine sélectionnée.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QGroupBox, QListWidget, QMessageBox,
    QScrollArea, QFrame, QGridLayout, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QDate
from PyQt6.QtGui import QFont
from typing import List, Dict, Any
from datetime import datetime, timedelta, date
from calendar import day_name
import locale

# Configuration locale pour les noms de jours en français
try:
    locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'French_France.1252')
    except:
        pass  # Si locale français non disponible, on utilisera l'anglais

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from src.core.database import Database
from src.core.dashboard_calculator import DashboardCalculator
import logging

logger = logging.getLogger(__name__)


class DashboardTab(QWidget):
    """Onglet Dashboard."""

    project_clicked = pyqtSignal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = Database()
        self.current_week = None
        self.init_ui()
        self.load_available_weeks()

    def init_ui(self):
        """Initialise l'interface utilisateur."""
        main_layout = QVBoxLayout()

        # En-tête
        header = self._create_header()
        main_layout.addWidget(header)

        # Scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setSpacing(8)
        content_layout.setContentsMargins(5, 5, 5, 5)

        # DEADLINES EN PREMIER (tuiles horizontales)
        self.deadlines_group = self._create_deadlines_section()
        content_layout.addWidget(self.deadlines_group)

        # VUE GLOBALE (3 colonnes)
        self.vue_globale_group = self._create_vue_globale()
        content_layout.addWidget(self.vue_globale_group)

        # ACTUALITÉ CLIENT (3 colonnes)
        self.actualite_group = self._create_actualite_client()
        content_layout.addWidget(self.actualite_group)

        # RDV Client
        self.rdv_group = self._create_rdv_section()
        content_layout.addWidget(self.rdv_group)

        content_layout.addStretch()
        content_widget.setLayout(content_layout)
        scroll.setWidget(content_widget)

        main_layout.addWidget(scroll)
        self.setLayout(main_layout)

    def _create_header(self) -> QWidget:
        widget = QWidget()
        layout = QHBoxLayout()

        title = QLabel("DASHBOARD")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        layout.addStretch()

        week_label = QLabel("Afficher la semaine :")
        layout.addWidget(week_label)

        self.week_combo = QComboBox()
        self.week_combo.setMinimumWidth(150)
        self.week_combo.currentIndexChanged.connect(self.on_week_changed)
        layout.addWidget(self.week_combo)

        widget.setLayout(layout)
        return widget

    def _create_kpi_tile(self, title: str, value: str, color: str = "#2196F3", icon: str = "") -> QFrame:
        """Crée une tuile KPI stylisée (fond gris, sans bordure)."""
        tile = QFrame()
        tile.setFrameShape(QFrame.Shape.StyledPanel)
        tile.setStyleSheet(f"""
            QFrame {{
                background-color: #f5f5f5;
                border: none;
                border-radius: 5px;
            }}
        """)

        tile.setFixedWidth(200)
        tile.setFixedHeight(200)

        layout = QVBoxLayout(tile)
        layout.setSpacing(5)
        layout.setContentsMargins(8, 8, 8, 8)

        # Icône + Titre
        title_label = QLabel(f"{icon} {title}")
        title_label.setStyleSheet(f"font-size: 14pt; color: #333; font-weight: bold;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setWordWrap(True)
        title_label.setMinimumHeight(40)
        title_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout.addWidget(title_label)

        # Valeur
        value_label = QLabel(value)
        value_label.setStyleSheet(f"font-size: 36pt; color: {color}; font-weight: bold;")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout.addWidget(value_label)

        tile.value_label = value_label

        return tile

    def _create_compact_tile(self, title: str, value: str, color: str = "#2196F3") -> QFrame:
        """Crée une tuile compacte carrée (fond coloré, sans bordure)."""
        tile = QFrame()
        tile.setFrameShape(QFrame.Shape.StyledPanel)
        tile.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border: none;
                border-radius: 5px;
            }}
        """)
        tile.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        tile.setFixedWidth(160)
        tile.setFixedHeight(160)

        layout = QVBoxLayout(tile)
        layout.setSpacing(5)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Valeur (blanc sur fond coloré)
        value_label = QLabel(value)
        value_label.setStyleSheet("font-size: 32pt; color: white; font-weight: bold;")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setWordWrap(False)
        value_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout.addWidget(value_label)

        # Titre (blanc sur fond coloré)
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 10pt; color: white; font-weight: bold;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setWordWrap(True)
        title_label.setMinimumHeight(50)
        title_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(title_label)

        tile.value_label = value_label

        return tile

    def _create_vue_globale(self) -> QGroupBox:
        """Vue Globale : Chiffres à gauche | Ligne orange | Graphiques à droite."""
        group = QGroupBox("VUE GLOBALE")
        group.setStyleSheet("""
            QGroupBox {
                background-color: #f5f5f5;
                border: 2px solid black;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
            }
        """)
        main_layout = QHBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 8, 10, 8)

        # GAUCHE : Tuiles KPI (2x2 grid)
        left_layout = QGridLayout()
        left_layout.setSpacing(8)
        left_layout.setContentsMargins(5, 5, 5, 5)

        self.total_tile = self._create_kpi_tile("Total projets", "51", "#2196F3", "")
        left_layout.addWidget(self.total_tile, 0, 0)

        self.active_tile = self._create_kpi_tile("Projets actifs", "47", "#4CAF50", "")
        left_layout.addWidget(self.active_tile, 0, 1)

        self.dispositif_tile = self._create_kpi_tile("Dispositif mensuel", "245 j", "#FF9800", "")
        left_layout.addWidget(self.dispositif_tile, 1, 0)

        self.expandable_tile = self._create_kpi_tile("Augmentables", "13", "#9C27B0", "")
        left_layout.addWidget(self.expandable_tile, 1, 1)

        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        main_layout.addWidget(left_widget)

        # Ligne verticale orange de séparation
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setLineWidth(3)
        separator.setStyleSheet("background-color: #FFA500; max-width: 3px;")
        main_layout.addWidget(separator)

        # Graphiques à droite (2 colonnes)
        right_layout = QHBoxLayout()
        right_layout.setSpacing(15)
        right_layout.setContentsMargins(10, 5, 10, 5)

        # Graphique Projets actifs par BU
        self.chart_bu = self._create_bar_chart("Projets actifs par BU")
        right_layout.addWidget(self.chart_bu)

        # Graphique Projets par Chef de projet
        self.chart_manager = self._create_bar_chart("Projets par Chef de projet")
        right_layout.addWidget(self.chart_manager)

        right_layout.addStretch()
        main_layout.addLayout(right_layout, 2)

        group.setLayout(main_layout)
        return group

    def _create_actualite_client(self) -> QGroupBox:
        """Actualité Client : Chiffres à gauche | Ligne orange | Graphiques à droite."""
        group = QGroupBox("ACTUALITE CLIENT")
        group.setStyleSheet("""
            QGroupBox {
                background-color: #f5f5f5;
                border: 2px solid black;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
            }
        """)
        main_layout = QHBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # GAUCHE : Tuiles KPI
        left_layout = QVBoxLayout()
        left_layout.setSpacing(10)
        left_layout.setContentsMargins(5, 5, 5, 5)

        self.warning_client_tile = self._create_kpi_tile("Warning Vision Client", "3", "#FF9800", "")
        left_layout.addWidget(self.warning_client_tile)

        self.warning_internal_tile = self._create_kpi_tile("Warning Vision Interne", "9", "#FF5722", "")
        left_layout.addWidget(self.warning_internal_tile)

        left_layout.addStretch()
        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        main_layout.addWidget(left_widget)

        # Ligne verticale orange de séparation
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setLineWidth(3)
        separator.setStyleSheet("background-color: #FFA500; max-width: 3px;")
        main_layout.addWidget(separator)

        # Graphiques et calendrier à droite
        right_layout = QHBoxLayout()
        right_layout.setSpacing(10)

        # Graphique Warnings par BU
        self.chart_warnings_bu = self._create_bar_chart("Warnings par BU", color='#FF9800')
        right_layout.addWidget(self.chart_warnings_bu)

        # Actions par acteur (style calendrier)
        self.actions_calendar = self._create_actions_calendar()
        right_layout.addWidget(self.actions_calendar, 2)

        main_layout.addLayout(right_layout, 2)

        group.setLayout(main_layout)
        return group

    def _create_bar_chart(self, title: str, color: str = '#2196F3') -> QWidget:
        """Crée un widget contenant un graphique à bâtons matplotlib."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(3)
        layout.setContentsMargins(5, 3, 5, 3)

        # Titre
        title_label = QLabel(title)
        title_label.setStyleSheet("font-weight: bold; font-size: 10pt;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Figure matplotlib
        fig = Figure(figsize=(2.8, 2.2), dpi=80)
        fig.patch.set_facecolor('#ffffff')
        canvas = FigureCanvas(fig)
        canvas.setFixedHeight(180)
        canvas.setFixedWidth(250)

        widget.setFixedWidth(260)
        widget.setFixedHeight(200)

        canvas.figure = fig
        canvas.chart_color = color

        layout.addWidget(canvas)

        return widget

    def _update_bar_chart(self, widget: QWidget, data: List[Dict[str, Any]], label_key: str, value_key: str):
        """Met à jour un graphique à bâtons."""
        canvas = None
        for child in widget.children():
            if isinstance(child, FigureCanvas):
                canvas = child
                break

        if not canvas:
            return

        if not data:
            labels = []
            values = []
        else:
            labels = [str(item[label_key]) for item in data]
            values = [item[value_key] for item in data]

        fig = canvas.figure
        fig.clear()
        ax = fig.add_subplot(111)

        if values:
            bars = ax.bar(range(len(labels)), values, color=canvas.chart_color, alpha=0.7)
            ax.set_xticks(range(len(labels)))
            ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=8)
            ax.set_ylabel('Nombre', fontsize=9)
            ax.tick_params(axis='both', labelsize=8)
            ax.grid(axis='y', alpha=0.3)

            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}',
                       ha='center', va='bottom', fontsize=8)
        else:
            ax.text(0.5, 0.5, 'Aucune donnée', ha='center', va='center', transform=ax.transAxes)

        fig.tight_layout()
        canvas.draw()

    def _create_deadlines_section(self) -> QGroupBox:
        """Section Deadlines avec tuiles horizontales épurées."""
        group = QGroupBox("ACTIONS & DEADLINES CETTE SEMAINE")
        group.setStyleSheet("""
            QGroupBox {
                background-color: #f5f5f5;
                border: 2px solid black;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
            }
        """)
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)

        tiles_layout = QHBoxLayout()
        tiles_layout.setSpacing(8)
        tiles_layout.setContentsMargins(5, 5, 5, 5)

        # 6 tuiles compactes en ligne
        self.pct_warning_tile = self._create_compact_tile("% Dossiers\nen warning", "0%", "#E91E63")
        tiles_layout.addWidget(self.pct_warning_tile, alignment=Qt.AlignmentFlag.AlignLeft)

        self.dlic_week_tile = self._create_compact_tile("DLIC à traiter\n(semaine en cours)", "0", "#2196F3")
        tiles_layout.addWidget(self.dlic_week_tile, alignment=Qt.AlignmentFlag.AlignLeft)

        self.dli_week_tile = self._create_compact_tile("DLI à traiter\n(semaine en cours)", "0", "#03A9F4")
        tiles_layout.addWidget(self.dli_week_tile, alignment=Qt.AlignmentFlag.AlignLeft)

        self.dlic_overdue_tile = self._create_compact_tile("DLIC dépassées", "0", "#F44336")
        tiles_layout.addWidget(self.dlic_overdue_tile, alignment=Qt.AlignmentFlag.AlignLeft)

        self.dli_overdue_tile = self._create_compact_tile("DLI dépassées", "0", "#E53935")
        tiles_layout.addWidget(self.dli_overdue_tile, alignment=Qt.AlignmentFlag.AlignLeft)

        self.dlic_empty_tile = self._create_compact_tile("DLIC vides\n(projets actifs)", "0", "#FF9800")
        tiles_layout.addWidget(self.dlic_empty_tile, alignment=Qt.AlignmentFlag.AlignLeft)

        tiles_layout.addStretch()
        main_layout.addLayout(tiles_layout)

        group.setLayout(main_layout)
        return group

    def _create_rdv_section(self) -> QGroupBox:
        group = QGroupBox("RENDEZ-VOUS CLIENT CETTE SEMAINE")
        group.setStyleSheet("""
            QGroupBox {
                background-color: #f5f5f5;
                border: 2px solid black;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
            }
        """)
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)

        self.rdv_count_label = QLabel("0 rendez-vous programmés")
        self.rdv_count_label.setStyleSheet("font-weight: bold; font-size: 11pt; padding: 5px;")
        layout.addWidget(self.rdv_count_label)

        # Calendrier hebdomadaire
        self.calendar_widget = QWidget()
        self.calendar_layout = QHBoxLayout(self.calendar_widget)
        self.calendar_layout.setSpacing(5)
        layout.addWidget(self.calendar_widget)

        self.calendar_columns = []

        group.setLayout(layout)
        return group

    def _create_calendar_day_column(self, day_name: str, date_str: str) -> QFrame:
        """Crée une colonne pour un jour du calendrier."""
        column = QFrame()
        column.setFrameShape(QFrame.Shape.StyledPanel)
        column.setStyleSheet("""
            QFrame {
                background-color: #f9f9f9;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
        """)
        column.setMinimumWidth(120)
        column.setMinimumHeight(200)

        layout = QVBoxLayout(column)
        layout.setSpacing(3)
        layout.setContentsMargins(5, 5, 5, 5)

        # En-tête : Jour
        day_label = QLabel(day_name)
        day_label.setStyleSheet("font-weight: bold; font-size: 10pt; color: #2196F3;")
        day_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(day_label)

        # En-tête : Date
        date_label = QLabel(date_str)
        date_label.setStyleSheet("font-size: 9pt; color: #666;")
        date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(date_label)

        # Séparateur
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #ddd;")
        layout.addWidget(separator)

        # Zone pour les RDV
        rdv_container = QWidget()
        rdv_container.setVisible(True)
        rdv_layout = QVBoxLayout(rdv_container)
        rdv_layout.setSpacing(3)
        rdv_layout.setContentsMargins(5, 5, 5, 5)
        rdv_layout.addStretch()

        layout.addWidget(rdv_container)
        layout.setStretchFactor(rdv_container, 1)

        column.rdv_layout = rdv_layout
        column.rdv_data = []

        return column

    def _create_actions_calendar(self) -> QWidget:
        """Crée une visualisation style calendrier pour les actions par acteur."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)

        # Titre
        title_label = QLabel("Actions par acteur")
        title_label.setStyleSheet("font-weight: bold; font-size: 10pt;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Scroll area pour le calendrier
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        # Widget contenant les colonnes d'acteurs
        calendar_widget = QWidget()
        self.actions_calendar_layout = QHBoxLayout(calendar_widget)
        self.actions_calendar_layout.setSpacing(10)
        self.actions_calendar_layout.setContentsMargins(5, 5, 5, 5)

        scroll.setWidget(calendar_widget)
        layout.addWidget(scroll)

        self.actions_columns = []

        return widget

    def _create_actor_column(self, actor_name: str) -> QFrame:
        """Crée une colonne pour un acteur (style calendrier)."""
        column = QFrame()
        column.setFrameShape(QFrame.Shape.StyledPanel)
        column.setStyleSheet("""
            QFrame {
                background-color: #fff3cd;
                border: 2px solid #ffc107;
                border-radius: 5px;
            }
        """)
        column.setMinimumWidth(150)
        column.setMaximumWidth(200)

        layout = QVBoxLayout(column)
        layout.setSpacing(5)
        layout.setContentsMargins(10, 10, 10, 10)

        # En-tête : Nom de l'acteur
        actor_label = QLabel(actor_name)
        actor_label.setStyleSheet("font-weight: bold; font-size: 11pt; color: #856404;")
        actor_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        actor_label.setWordWrap(True)
        layout.addWidget(actor_label)

        # Séparateur
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #ffc107; max-height: 2px;")
        layout.addWidget(separator)

        # Zone pour les clients
        clients_container = QWidget()
        clients_layout = QVBoxLayout(clients_container)
        clients_layout.setSpacing(5)
        clients_layout.setContentsMargins(0, 0, 0, 0)
        clients_layout.addStretch()

        layout.addWidget(clients_container)

        column.clients_layout = clients_layout
        column.clients_data = []

        return column

    def load_available_weeks(self, select_latest: bool = True):
        """
        Charge les semaines disponibles dans le dropdown.

        Args:
            select_latest: Si True, sélectionne automatiquement la dernière semaine (la plus récente)
        """
        weeks = self.db.get_available_weeks()

        self.week_combo.blockSignals(True)
        self.week_combo.clear()

        if not weeks:
            self.week_combo.addItem("Aucune donnée")
            self.week_combo.setEnabled(False)
            self.week_combo.blockSignals(False)
            return

        self.week_combo.setEnabled(True)

        # Les semaines sont triées avec logique 6 mois glissants (plus récente en premier)
        for week in weeks:
            # Afficher avec padding : S02, S03, S48, etc.
            self.week_combo.addItem(f"S{week:02d} (Semaine {week})", week)

        self.week_combo.blockSignals(False)

        # Sélectionner la première (= la plus récente car trié DESC)
        if weeks and select_latest:
            self.week_combo.setCurrentIndex(0)
            self.current_week = weeks[0]
            self.refresh_dashboard()

    def on_week_changed(self, index: int):
        if index < 0:
            return

        week = self.week_combo.itemData(index)
        if week:
            self.current_week = week
            self.refresh_dashboard()

    def refresh_dashboard(self):
        if not self.current_week:
            return

        try:
            calc = DashboardCalculator(self.db)
            indicators = calc.get_all_indicators(self.current_week)

            # Vue Globale - Tuiles KPI
            self.total_tile.value_label.setText(str(indicators['total_projects']))
            self.active_tile.value_label.setText(str(indicators['active_projects']))
            self.dispositif_tile.value_label.setText(f"{indicators['dispositif_monthly']} j")
            self.expandable_tile.value_label.setText(str(indicators['dispositif_expandable']))

            # Vue Globale - Graphique Projets actifs par BU
            bu_data = calc.get_active_projects_by_bu(self.current_week)
            self._update_bar_chart(self.chart_bu, bu_data, 'bu', 'count')

            # Vue Globale - Graphique Projets par Chef de projet
            managers = calc.get_projects_by_manager(self.current_week)
            self._update_bar_chart(self.chart_manager, managers, 'project_manager', 'count')

            # Actualité Client - Tuiles KPI
            self.warning_client_tile.value_label.setText(str(indicators['warning_vision_client']))
            self.warning_internal_tile.value_label.setText(str(indicators['warning_vision_internal']))

            # Actualité Client - Graphique Warnings par BU
            warnings_bu = calc.get_warnings_by_bu(self.current_week)
            self._update_bar_chart(self.chart_warnings_bu, warnings_bu, 'bu', 'count')

            # Actualité Client - Actions par acteur (calendrier)
            actions_data = calc.get_actions_by_actor_with_clients(self.current_week)
            self._update_actions_calendar(actions_data)

            # Deadlines - Tuiles compactes
            self.pct_warning_tile.value_label.setText(f"{indicators.get('pct_projects_with_warning', 0)}%")
            self.dlic_week_tile.value_label.setText(str(indicators['dlic_this_week']))
            self.dli_week_tile.value_label.setText(str(indicators['dli_this_week']))
            self.dlic_overdue_tile.value_label.setText(str(indicators['dlic_overdue']))
            self.dli_overdue_tile.value_label.setText(str(indicators['dli_overdue']))
            self.dlic_empty_tile.value_label.setText(str(indicators['dlic_empty']))

            # RDV Client - Calendrier
            rdv_list = indicators['rdv_client_this_week']
            self.rdv_count_label.setText(f"{len(rdv_list)} rendez-vous programmés")

            self._update_calendar(rdv_list)

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la mise à jour du dashboard : {str(e)}")

    def _update_calendar(self, rdv_list: List[Dict[str, Any]]):
        """Met à jour le calendrier avec les RDV de la semaine."""
        # Nettoyer l'ancien calendrier
        while self.calendar_layout.count():
            item = self.calendar_layout.takeAt(0)
            if item.widget():
                widget = item.widget()
                widget.setParent(None)
                widget.deleteLater()

        self.calendar_columns = []

        # Déterminer les dates de la semaine actuelle
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        days_since_monday = today.weekday()
        monday = today - timedelta(days=days_since_monday)

        # Noms des jours en français
        day_names_fr = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']

        # Créer les 7 colonnes
        for i in range(7):
            day_date = monday + timedelta(days=i)
            day_name = day_names_fr[i]
            date_str = day_date.strftime('%d/%m')

            # Créer la colonne
            column = self._create_calendar_day_column(day_name, date_str)
            self.calendar_layout.addWidget(column)
            self.calendar_columns.append(column)

            # Filtrer les RDV pour ce jour
            day_rdv = [rdv for rdv in rdv_list if self._rdv_is_on_date(rdv, day_date)]

            # Retirer le stretch initial s'il existe
            if column.rdv_layout.count() > 0:
                last_item = column.rdv_layout.itemAt(column.rdv_layout.count() - 1)
                if last_item and last_item.spacerItem():
                    column.rdv_layout.removeItem(last_item)

            # Ajouter les RDV à la colonne
            for rdv in day_rdv:
                rdv_label = QLabel(rdv['client_name'])
                rdv_label.setStyleSheet("""
                    background-color: #E3F2FD;
                    border-left: 3px solid #2196F3;
                    padding: 8px;
                    margin: 3px 0;
                    font-size: 9pt;
                    font-weight: normal;
                    border-radius: 3px;
                    color: #1976D2;
                """)
                rdv_label.setMinimumHeight(30)
                rdv_label.setWordWrap(True)
                rdv_label.setCursor(Qt.CursorShape.PointingHandCursor)
                rdv_label.setToolTip(f"Double-cliquez pour voir la fiche projet")
                rdv_label.setVisible(True)

                rdv_label.setProperty('id_projet', rdv['id_projet'])
                rdv_label.mouseDoubleClickEvent = lambda event, proj_id=rdv['id_projet']: self.on_rdv_label_clicked(proj_id)

                column.rdv_layout.addWidget(rdv_label)

            column.rdv_layout.addStretch()

        self.calendar_widget.update()
        self.calendar_widget.repaint()

    def _rdv_is_on_date(self, rdv: Dict[str, Any], target_date: datetime) -> bool:
        """Vérifie si un RDV est à la date cible."""
        try:
            rdv_date_value = rdv.get('next_client_exchange')
            if rdv_date_value is None:
                return False

            if isinstance(rdv_date_value, date) and not isinstance(rdv_date_value, datetime):
                rdv_date_obj = datetime.combine(rdv_date_value, datetime.min.time())
            elif isinstance(rdv_date_value, datetime):
                rdv_date_obj = rdv_date_value
            elif isinstance(rdv_date_value, str):
                for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%Y-%m-%d %H:%M:%S']:
                    try:
                        rdv_date_obj = datetime.strptime(rdv_date_value, fmt)
                        break
                    except ValueError:
                        continue
                else:
                    return False
            else:
                return False

            return rdv_date_obj.date() == target_date.date()

        except Exception as e:
            logger.error(f"Erreur lors de la vérification de date RDV: {e}")
            return False

    def on_rdv_label_clicked(self, id_projet: int):
        """Gère le double-clic sur un RDV."""
        if id_projet and self.current_week:
            QMessageBox.information(self, "Fiche Projet", f"Fiche projet #{id_projet}\n\n(À développer)")
            self.project_clicked.emit(id_projet, self.current_week)

    def _update_actions_calendar(self, actions_data: Dict[str, Any]):
        """Met à jour le calendrier d'actions par acteur avec les clients en warning."""
        # Nettoyer l'ancien calendrier
        while self.actions_calendar_layout.count():
            item = self.actions_calendar_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.actions_columns = []

        by_actor = actions_data.get('by_actor', {})

        for actor_name in sorted(by_actor.keys(), key=str.lower):
            clients = by_actor[actor_name]

            column = self._create_actor_column(actor_name)
            self.actions_columns.append(column)
            self.actions_calendar_layout.addWidget(column)

            for client_info in clients:
                client_label = QLabel(client_info['client_name'])
                client_label.setStyleSheet("""
                    background-color: #fff;
                    border-left: 3px solid #ffc107;
                    padding: 6px;
                    margin: 3px 0;
                    font-size: 9pt;
                    border-radius: 3px;
                """)
                client_label.setWordWrap(True)
                client_label.setCursor(Qt.CursorShape.PointingHandCursor)
                client_label.setToolTip(f"Projet #{client_info['id_projet']}")

                client_label.setProperty('id_projet', client_info['id_projet'])

                if column.clients_layout.count() > 0:
                    last_item = column.clients_layout.itemAt(column.clients_layout.count() - 1)
                    if last_item.spacerItem():
                        column.clients_layout.removeItem(last_item)

                column.clients_layout.addWidget(client_label)
                column.clients_layout.addStretch()

        # Ajouter une colonne "VIDE" (rouge) s'il y a des clients sans acteur
        empty_clients = actions_data.get('empty', [])
        if empty_clients:
            column = QFrame()
            column.setFrameShape(QFrame.Shape.StyledPanel)
            column.setStyleSheet("""
                QFrame {
                    background-color: #f8d7da;
                    border: 2px solid #dc3545;
                    border-radius: 5px;
                }
            """)
            column.setMinimumWidth(150)
            column.setMaximumWidth(200)

            layout = QVBoxLayout(column)
            layout.setSpacing(5)
            layout.setContentsMargins(10, 10, 10, 10)

            actor_label = QLabel("VIDE")
            actor_label.setStyleSheet("font-weight: bold; font-size: 11pt; color: #721c24;")
            actor_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            actor_label.setWordWrap(True)
            layout.addWidget(actor_label)

            separator = QFrame()
            separator.setFrameShape(QFrame.Shape.HLine)
            separator.setStyleSheet("background-color: #dc3545; max-height: 2px;")
            layout.addWidget(separator)

            clients_container = QWidget()
            clients_layout = QVBoxLayout(clients_container)
            clients_layout.setSpacing(5)
            clients_layout.setContentsMargins(0, 0, 0, 0)
            clients_layout.addStretch()

            layout.addWidget(clients_container)

            column.clients_layout = clients_layout
            column.clients_data = []

            self.actions_columns.append(column)
            self.actions_calendar_layout.addWidget(column)

            for client_info in empty_clients:
                client_label = QLabel(client_info['client_name'])
                client_label.setStyleSheet("""
                    background-color: #fff;
                    border-left: 3px solid #dc3545;
                    padding: 6px;
                    margin: 3px 0;
                    font-size: 9pt;
                    border-radius: 3px;
                """)
                client_label.setWordWrap(True)
                client_label.setCursor(Qt.CursorShape.PointingHandCursor)
                client_label.setToolTip(f"Projet #{client_info['id_projet']} - Aucun acteur assigné")

                client_label.setProperty('id_projet', client_info['id_projet'])

                if column.clients_layout.count() > 0:
                    last_item = column.clients_layout.itemAt(column.clients_layout.count() - 1)
                    if last_item.spacerItem():
                        column.clients_layout.removeItem(last_item)

                column.clients_layout.addWidget(client_label)
                column.clients_layout.addStretch()

        self.actions_calendar_layout.addStretch()

