"""
Onglet CDP (Chefs de Projet) de l'application.

Affiche les statistiques par Chef de Projet :
- Tableau récapitulatif avec tous les indicateurs (dont NPS)
- Graphiques de classement (charge, santé)
- Évolution sur plusieurs semaines avec filtre par CDP
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QGroupBox, QTableWidget, QTableWidgetItem,
    QScrollArea, QFrame, QGridLayout, QSizePolicy, QHeaderView,
    QSplitter, QListWidget, QListWidgetItem, QCheckBox, QPushButton
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from typing import List, Dict, Any

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from src.core.database import Database
from src.core.dashboard_calculator import DashboardCalculator
import logging

logger = logging.getLogger(__name__)


class CDPTab(QWidget):
    """Onglet Chefs de Projet."""

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

        # Scroll area pour le contenu
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setSpacing(15)
        content_layout.setContentsMargins(5, 5, 5, 5)

        # Section KPIs globaux
        self.kpis_section = self._create_kpis_section()
        content_layout.addWidget(self.kpis_section)

        # Section Jours Facturables en Main (graphique barres EN HAUT)
        self.facturable_section = self._create_facturable_section()
        content_layout.addWidget(self.facturable_section)

        # Section Tableau CDP
        self.table_section = self._create_table_section()
        content_layout.addWidget(self.table_section)

        # Section Graphiques classement
        self.charts_section = self._create_charts_section()
        content_layout.addWidget(self.charts_section)

        # Section Évolution (avec filtre CDP)
        self.evolution_section = self._create_evolution_section()
        content_layout.addWidget(self.evolution_section)

        content_layout.addStretch()
        content_widget.setLayout(content_layout)
        scroll.setWidget(content_widget)

        main_layout.addWidget(scroll)
        self.setLayout(main_layout)

    def _create_header(self) -> QWidget:
        """Crée l'en-tête avec titre et sélecteur de semaine."""
        widget = QWidget()
        layout = QHBoxLayout()

        title = QLabel("CHEFS DE PROJET")
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
        tile.setFixedWidth(140)
        tile.setFixedHeight(90)

        layout = QVBoxLayout(tile)
        layout.setSpacing(3)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        value_label = QLabel(value)
        value_label.setStyleSheet("font-size: 20pt; color: white; font-weight: bold;")
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
        """Crée la section des KPIs globaux."""
        group = QGroupBox("VUE D'ENSEMBLE")
        group.setStyleSheet("""
            QGroupBox {
                background-color: #f8faff;
                border: 2px solid #0166FE;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
            }
        """)

        layout = QHBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(15, 15, 15, 15)

        self.tile_total_cdp = self._create_compact_tile("Chefs de Projet", "0", "#0166FE")
        layout.addWidget(self.tile_total_cdp)

        self.tile_avg_projects = self._create_compact_tile("Moy. projets/CDP", "0", "#0A1563")
        layout.addWidget(self.tile_avg_projects)

        self.tile_avg_health = self._create_compact_tile("Taux santé moy.", "0%", "#FF9800")
        layout.addWidget(self.tile_avg_health)

        self.tile_cdp_warning = self._create_compact_tile("CDP avec warn.", "0", "#F44336")
        layout.addWidget(self.tile_cdp_warning)

        self.tile_total_days = self._create_compact_tile("Jours dispositif", "0", "#FE4502")
        layout.addWidget(self.tile_total_days)

        self.tile_avg_nps_com = self._create_compact_tile("NPS Com. moy.", "N/A", "#00BCD4")
        layout.addWidget(self.tile_avg_nps_com)

        self.tile_avg_nps_proj = self._create_compact_tile("NPS Proj. moy.", "N/A", "#009688")
        layout.addWidget(self.tile_avg_nps_proj)

        layout.addStretch()

        group.setLayout(layout)
        return group

    def _create_facturable_section(self) -> QGroupBox:
        """Crée la section Jours Facturables en Main avec 3 graphiques."""
        group = QGroupBox("PIPE - JOURS FACTURABLES EN MAIN")
        group.setStyleSheet("""
            QGroupBox {
                background-color: #f8faff;
                border: 2px solid #FE4502;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                color: #0A1563;
            }
        """)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Ligne 1 : Top Projets (vertical) + Par CDP (horizontal)
        row1_layout = QHBoxLayout()
        row1_layout.setSpacing(15)

        # Graph 1 : Top projets (barres verticales)
        self.chart_top_projects = self._create_vertical_bar_chart("Top Projets (jours fact. en main)", "#FE4502")
        row1_layout.addWidget(self.chart_top_projects, stretch=1)

        # Graph 2 : Par CDP (barres horizontales)
        self.chart_facturable_cdp = self._create_bar_chart("Par Chef de Projet", "#0166FE")
        row1_layout.addWidget(self.chart_facturable_cdp, stretch=1)

        main_layout.addLayout(row1_layout)

        # Ligne 2 : Corrélation Nb projets VS PIPE
        self.chart_correlation = self._create_dual_axis_chart(
            "Évolution : Nb Projets Actifs vs PIPE (corrélation)",
            "#0166FE", "#FE4502"
        )
        main_layout.addWidget(self.chart_correlation)

        group.setLayout(main_layout)
        return group

    def _create_vertical_bar_chart(self, title: str, color: str) -> QWidget:
        """Crée un graphique à barres verticales."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(3)
        layout.setContentsMargins(5, 3, 5, 3)

        title_label = QLabel(title)
        title_label.setStyleSheet("font-weight: bold; font-size: 10pt; color: #0A1563;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        fig = Figure(figsize=(5, 3.5), dpi=100)
        fig.patch.set_facecolor('#f8faff')
        canvas = FigureCanvas(fig)
        canvas.setMinimumHeight(220)
        canvas.setMinimumWidth(350)

        canvas.figure = fig
        canvas.chart_color = color

        layout.addWidget(canvas, stretch=1)

        return widget

    def _create_dual_axis_chart(self, title: str, color1: str, color2: str) -> QWidget:
        """Crée un graphique double axe (corrélation)."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(3)
        layout.setContentsMargins(5, 3, 5, 3)

        title_label = QLabel(title)
        title_label.setStyleSheet("font-weight: bold; font-size: 10pt; color: #0A1563;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Légende explicative
        legend_label = QLabel("↑ Si PIPE baisse alors que Nb projets monte = problème de remplissage")
        legend_label.setStyleSheet("font-size: 8pt; color: #666; font-style: italic;")
        legend_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(legend_label)

        fig = Figure(figsize=(10, 3), dpi=100)
        fig.patch.set_facecolor('#f8faff')
        canvas = FigureCanvas(fig)
        canvas.setMinimumHeight(200)

        canvas.figure = fig
        canvas.color1 = color1
        canvas.color2 = color2

        layout.addWidget(canvas, stretch=1)

        return widget

    def _create_table_section(self) -> QGroupBox:
        """Crée la section du tableau récapitulatif."""
        group = QGroupBox("STATISTIQUES PAR CHEF DE PROJET")
        group.setStyleSheet("""
            QGroupBox {
                background-color: #f8faff;
                border: 2px solid #0166FE;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)

        # Tableau avec colonnes NPS
        self.table = QTableWidget()
        self.table.setColumnCount(15)
        self.table.setHorizontalHeaderLabels([
            "Chef de Projet",
            "Actifs",
            "Total",
            "Pause",
            "Terminés",
            "À venir",
            "Warn. Client",
            "Warn. Interne",
            "Taux Santé",
            "DLIC Dép.",
            "DLIC Vides",
            "Taux DLIC",
            "NPS Com.",
            "NPS Proj.",
            "Jours Disp."
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
                padding: 4px;
            }
            QHeaderView::section {
                background-color: #0A1563;
                color: white;
                padding: 6px;
                font-weight: bold;
                font-size: 8pt;
                border: none;
            }
            QTableWidget::item:alternate {
                background-color: #f9f9f9;
            }
        """)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for i in range(1, 15):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)

        self.table.setMinimumHeight(250)
        layout.addWidget(self.table)

        group.setLayout(layout)
        return group

    def _create_charts_section(self) -> QGroupBox:
        """Crée la section des graphiques de classement."""
        group = QGroupBox("CLASSEMENTS (SEMAINE SÉLECTIONNÉE)")
        group.setStyleSheet("""
            QGroupBox {
                background-color: #f8faff;
                border: 2px solid #0166FE;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
            }
        """)

        layout = QHBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(15, 15, 15, 15)

        # Graphique Charge
        self.chart_charge = self._create_bar_chart("Projets actifs par CDP", "#0166FE")
        layout.addWidget(self.chart_charge, stretch=1)

        # Graphique Santé avec description
        health_widget = QWidget()
        health_layout = QVBoxLayout(health_widget)
        health_layout.setSpacing(2)
        health_layout.setContentsMargins(0, 0, 0, 0)

        self.chart_health = self._create_bar_chart("Taux de santé par CDP", "#0A1563")
        health_layout.addWidget(self.chart_health)

        # Description du taux de santé
        health_desc = QLabel("Taux santé = % projets actifs SANS warning (Client ou Interne)")
        health_desc.setStyleSheet("font-size: 8pt; color: #666; font-style: italic;")
        health_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        health_layout.addWidget(health_desc)

        layout.addWidget(health_widget, stretch=1)

        group.setLayout(layout)
        return group

    def _create_evolution_section(self) -> QGroupBox:
        """Crée la section évolution avec filtre CDP."""
        group = QGroupBox("ÉVOLUTION SUR PLUSIEURS SEMAINES")
        group.setStyleSheet("""
            QGroupBox {
                background-color: #f8faff;
                border: 2px solid #0166FE;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
            }
        """)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Filtre CDP multi-select
        filter_layout = QHBoxLayout()
        filter_label = QLabel("Filtrer par Chef de Projet (cocher pour comparer) :")
        filter_label.setStyleSheet("font-weight: bold;")
        filter_layout.addWidget(filter_label)

        # Liste avec checkboxes
        self.cdp_filter_list = QListWidget()
        self.cdp_filter_list.setMaximumHeight(120)
        self.cdp_filter_list.setMinimumWidth(250)
        self.cdp_filter_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ccc;
                border-radius: 5px;
                background-color: white;
            }
            QListWidget::item {
                padding: 3px;
            }
        """)
        filter_layout.addWidget(self.cdp_filter_list)

        # Boutons de sélection rapide
        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(5)

        self.btn_select_all = QPushButton("Tout")
        self.btn_select_all.setMaximumWidth(80)
        self.btn_select_all.clicked.connect(self._select_all_cdp)
        btn_layout.addWidget(self.btn_select_all)

        self.btn_clear_all = QPushButton("Aucun")
        self.btn_clear_all.setMaximumWidth(80)
        self.btn_clear_all.clicked.connect(self._clear_all_cdp)
        btn_layout.addWidget(self.btn_clear_all)

        btn_layout.addStretch()
        filter_layout.addLayout(btn_layout)

        filter_layout.addStretch()
        main_layout.addLayout(filter_layout)

        # === BLOC FACTURABLE EN HAUT ===
        facturable_label = QLabel("FACTURABLE (PIPE)")
        facturable_label.setStyleSheet("font-weight: bold; font-size: 11pt; color: #FE4502; margin-top: 10px;")
        main_layout.addWidget(facturable_label)

        fact_layout = QGridLayout()
        fact_layout.setSpacing(15)

        # Ligne 1 : Évolution PIPE + Corrélation
        self.chart_evolution_facturable = self._create_line_chart("Évolution Temps Facturable en Main (jours)", "#FE4502")
        fact_layout.addWidget(self.chart_evolution_facturable, 0, 0)

        self.chart_evolution_correlation = self._create_dual_axis_chart(
            "Corrélation Nb Projets vs PIPE",
            "#0166FE", "#FE4502"
        )
        fact_layout.addWidget(self.chart_evolution_correlation, 0, 1)

        # Ligne 2 : Jours par projet (barres verticales) pour le CDP sélectionné
        self.chart_evolution_projects_bars = self._create_vertical_bar_chart("Jours fact. par Projet (CDP sélectionné)", "#FE4502")
        fact_layout.addWidget(self.chart_evolution_projects_bars, 1, 0, 1, 2)  # Span 2 colonnes

        main_layout.addLayout(fact_layout)

        # Séparateur
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background-color: #0166FE; max-height: 2px; margin: 10px 0;")
        main_layout.addWidget(sep)

        # === BLOC AUTRES INDICATEURS EN BAS ===
        autres_label = QLabel("INDICATEURS PROJET")
        autres_label.setStyleSheet("font-weight: bold; font-size: 11pt; color: #0166FE;")
        main_layout.addWidget(autres_label)

        charts_layout = QGridLayout()
        charts_layout.setSpacing(15)

        # Graphique évolution projets actifs
        self.chart_evolution_projects = self._create_line_chart("Évolution des projets actifs", "#0166FE")
        charts_layout.addWidget(self.chart_evolution_projects, 0, 0)

        # Graphique évolution warnings
        self.chart_evolution_warnings = self._create_line_chart("Évolution des warnings", "#FF9800")
        charts_layout.addWidget(self.chart_evolution_warnings, 0, 1)

        # Graphique évolution taux de santé
        self.chart_evolution_health = self._create_line_chart("Évolution du taux de santé (%)", "#0A1563")
        charts_layout.addWidget(self.chart_evolution_health, 1, 0)

        # Graphique évolution NPS
        self.chart_evolution_nps = self._create_line_chart("Évolution NPS", "#00BCD4")
        charts_layout.addWidget(self.chart_evolution_nps, 1, 1)

        main_layout.addLayout(charts_layout)

        group.setLayout(main_layout)
        return group

    def _create_bar_chart(self, title: str, color: str) -> QWidget:
        """Crée un widget graphique à bâtons horizontal."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(3)
        layout.setContentsMargins(5, 3, 5, 3)

        title_label = QLabel(title)
        title_label.setStyleSheet("font-weight: bold; font-size: 10pt;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        fig = Figure(figsize=(5, 4), dpi=100)
        fig.patch.set_facecolor('#f5f5f5')
        canvas = FigureCanvas(fig)
        canvas.setMinimumHeight(250)
        canvas.setMinimumWidth(350)

        canvas.figure = fig
        canvas.chart_color = color

        layout.addWidget(canvas, stretch=1)

        return widget

    def _create_line_chart(self, title: str, color: str) -> QWidget:
        """Crée un widget graphique en ligne."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(3)
        layout.setContentsMargins(5, 3, 5, 3)

        title_label = QLabel(title)
        title_label.setStyleSheet("font-weight: bold; font-size: 10pt;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        fig = Figure(figsize=(5, 3), dpi=100)
        fig.patch.set_facecolor('#f5f5f5')
        canvas = FigureCanvas(fig)
        canvas.setMinimumHeight(200)
        canvas.setMinimumWidth(350)

        canvas.figure = fig
        canvas.chart_color = color

        layout.addWidget(canvas, stretch=1)

        return widget

    def _update_bar_chart(self, widget: QWidget, labels: List[str], values: List[float], suffix: str = ""):
        """Met à jour un graphique à bâtons horizontal."""
        canvas = None
        for child in widget.children():
            if isinstance(child, FigureCanvas):
                canvas = child
                break

        if not canvas:
            return

        fig = canvas.figure
        fig.clear()
        ax = fig.add_subplot(111)

        if values:
            # Limiter à 10 CDP max pour lisibilité
            display_labels = labels[:10]
            display_values = values[:10]

            bars = ax.barh(range(len(display_labels)), display_values, color=canvas.chart_color, alpha=0.7)
            ax.set_yticks(range(len(display_labels)))
            ax.set_yticklabels(display_labels, fontsize=8)
            ax.invert_yaxis()
            ax.grid(axis='x', alpha=0.3)

            for i, bar in enumerate(bars):
                width = bar.get_width()
                ax.text(width + 0.5, bar.get_y() + bar.get_height()/2.,
                       f'{display_values[i]:.0f}{suffix}',
                       ha='left', va='center', fontsize=8)
        else:
            ax.text(0.5, 0.5, 'Aucune donnée', ha='center', va='center', transform=ax.transAxes)

        fig.tight_layout()
        canvas.draw()

    def _update_line_chart(self, widget: QWidget, weeks: List[str], datasets: List[Dict], y_suffix: str = ""):
        """
        Met à jour un graphique en ligne.

        Args:
            datasets: Liste de {label, values, color}
        """
        canvas = None
        for child in widget.children():
            if isinstance(child, FigureCanvas):
                canvas = child
                break

        if not canvas:
            return

        fig = canvas.figure
        fig.clear()
        ax = fig.add_subplot(111)

        if weeks and datasets:
            for ds in datasets:
                values = ds['values']
                # Remplacer les None par 0 pour le tracé
                plot_values = [v if v is not None else 0 for v in values]
                ax.plot(range(len(weeks)), plot_values,
                       label=ds['label'],
                       color=ds['color'],
                       marker='o',
                       markersize=4,
                       linewidth=2)

            ax.set_xticks(range(len(weeks)))
            ax.set_xticklabels(weeks, rotation=45, ha='right', fontsize=8)
            ax.grid(axis='both', alpha=0.3)

            if len(datasets) > 1:
                ax.legend(loc='upper left', fontsize=8)

            # Ajouter suffixe à l'axe Y si nécessaire
            if y_suffix:
                ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.0f}{y_suffix}'))
        else:
            ax.text(0.5, 0.5, 'Aucune donnée', ha='center', va='center', transform=ax.transAxes)

        fig.tight_layout()
        canvas.draw()

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

        # Charger la liste des CDP pour le filtre
        self._load_cdp_filter()

        if weeks:
            self.week_combo.setCurrentIndex(0)
            self.current_week = weeks[0]
            self.refresh_data()

    def _load_cdp_filter(self):
        """Charge la liste des CDP dans le filtre avec checkboxes."""
        try:
            calc = DashboardCalculator(self.db)
            cdp_names = calc.get_all_cdp_names()

            self.cdp_filter_list.clear()

            for cdp in cdp_names:
                item = QListWidgetItem(cdp)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(Qt.CheckState.Unchecked)
                self.cdp_filter_list.addItem(item)

            # Connecter le signal de changement
            self.cdp_filter_list.itemChanged.connect(self.on_cdp_filter_changed)

        except Exception as e:
            logger.error(f"Erreur chargement filtre CDP: {e}")

    def _select_all_cdp(self):
        """Sélectionne tous les CDP."""
        self.cdp_filter_list.blockSignals(True)
        for i in range(self.cdp_filter_list.count()):
            self.cdp_filter_list.item(i).setCheckState(Qt.CheckState.Checked)
        self.cdp_filter_list.blockSignals(False)
        self.refresh_evolution_charts()

    def _clear_all_cdp(self):
        """Désélectionne tous les CDP."""
        self.cdp_filter_list.blockSignals(True)
        for i in range(self.cdp_filter_list.count()):
            self.cdp_filter_list.item(i).setCheckState(Qt.CheckState.Unchecked)
        self.cdp_filter_list.blockSignals(False)
        self.refresh_evolution_charts()

    def _get_selected_cdps(self) -> list:
        """Retourne la liste des CDP cochés."""
        selected = []
        for i in range(self.cdp_filter_list.count()):
            item = self.cdp_filter_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                selected.append(item.text())
        return selected

    def on_week_changed(self, index: int):
        """Gère le changement de semaine."""
        if index < 0:
            return

        week = self.week_combo.itemData(index)
        if week:
            self.current_week = week
            self.refresh_data()

    def on_cdp_filter_changed(self, item=None):
        """Gère le changement de filtre CDP."""
        self.refresh_evolution_charts()

    def refresh_data(self):
        """Rafraîchit toutes les données de l'onglet."""
        if not self.current_week:
            return

        try:
            calc = DashboardCalculator(self.db)
            stats = calc.get_cdp_statistics(self.current_week)

            self._update_kpis(stats)
            self._update_facturable_chart(calc)  # Nouveau graphique facturable
            self._update_table(stats)
            self._update_charts(stats)
            self.refresh_evolution_charts()

        except Exception as e:
            logger.error(f"Erreur lors du rafraîchissement CDP: {e}")

    def refresh_evolution_charts(self):
        """Rafraîchit les graphiques d'évolution avec support multi-CDP."""
        try:
            calc = DashboardCalculator(self.db)

            # Récupérer les CDP sélectionnés
            selected_cdps = self._get_selected_cdps()

            # Couleurs pour les différents CDP
            colors = ['#0166FE', '#0A1563', '#FF9800', '#E91E63', '#FE4502', '#00BCD4', '#FF5722', '#795548']

            if not selected_cdps:
                # Aucun CDP sélectionné = afficher le total global
                evolution = calc.get_cdp_evolution(None)
                weeks = evolution['weeks']

                # Graphique projets actifs
                self._update_line_chart(
                    self.chart_evolution_projects,
                    weeks,
                    [{'label': 'Tous', 'values': evolution['active_projects'], 'color': '#0166FE'}]
                )

                # Graphique warnings
                self._update_line_chart(
                    self.chart_evolution_warnings,
                    weeks,
                    [
                        {'label': 'Warning Client', 'values': evolution['warnings_client'], 'color': '#FF5722'},
                        {'label': 'Warning Interne', 'values': evolution['warnings_internal'], 'color': '#FF9800'}
                    ]
                )

                # Graphique taux de santé
                self._update_line_chart(
                    self.chart_evolution_health,
                    weeks,
                    [{'label': 'Tous', 'values': evolution['health_rate'], 'color': '#0A1563'}],
                    '%'
                )

                # Graphique NPS
                self._update_line_chart(
                    self.chart_evolution_nps,
                    weeks,
                    [
                        {'label': 'NPS Commercial', 'values': evolution['nps_commercial'], 'color': '#00BCD4'},
                        {'label': 'NPS Projet', 'values': evolution['nps_project'], 'color': '#009688'}
                    ]
                )

                # Graphique Temps facturable
                facturable_evolution = calc.get_facturable_evolution(None)
                self._update_line_chart(
                    self.chart_evolution_facturable,
                    facturable_evolution['weeks'],
                    [{'label': 'Total', 'values': facturable_evolution['total_facturable'], 'color': '#FE4502'}],
                    ' j'
                )

                # Graphique corrélation (global)
                correlation_data = calc.get_projects_vs_pipe_evolution(None)
                self._update_correlation_chart(self.chart_evolution_correlation, correlation_data)

                # Graphique jours par projet (tous CDP)
                top_projects = calc.get_facturable_by_project(self.current_week, limit=15, cdp_name=None)
                if top_projects:
                    labels = [f"{p['client_name']}\n({p['bu']})" for p in top_projects]
                    values = [p['days_facturable'] for p in top_projects]
                    self._update_vertical_bar_chart(self.chart_evolution_projects_bars, labels, values)

            else:
                # CDP sélectionnés = afficher une courbe par CDP
                datasets_projects = []
                datasets_health = []
                datasets_facturable = []
                weeks = None

                for i, cdp_name in enumerate(selected_cdps):
                    color = colors[i % len(colors)]
                    evolution = calc.get_cdp_evolution(cdp_name)

                    if weeks is None:
                        weeks = evolution['weeks']

                    datasets_projects.append({
                        'label': cdp_name,
                        'values': evolution['active_projects'],
                        'color': color
                    })
                    datasets_health.append({
                        'label': cdp_name,
                        'values': evolution['health_rate'],
                        'color': color
                    })

                    # Temps facturable par CDP
                    fact_evol = calc.get_facturable_evolution(cdp_name)
                    datasets_facturable.append({
                        'label': cdp_name,
                        'values': fact_evol['total_facturable'],
                        'color': color
                    })

                # Graphique projets actifs (multi-CDP)
                self._update_line_chart(self.chart_evolution_projects, weeks, datasets_projects)

                # Graphique warnings (agrégé pour tous les CDP sélectionnés)
                evolution_all = calc.get_cdp_evolution(None)
                self._update_line_chart(
                    self.chart_evolution_warnings,
                    weeks,
                    [
                        {'label': 'Warning Client', 'values': evolution_all['warnings_client'], 'color': '#FF5722'},
                        {'label': 'Warning Interne', 'values': evolution_all['warnings_internal'], 'color': '#FF9800'}
                    ]
                )

                # Graphique taux de santé (multi-CDP)
                self._update_line_chart(self.chart_evolution_health, weeks, datasets_health, '%')

                # Graphique NPS (agrégé)
                self._update_line_chart(
                    self.chart_evolution_nps,
                    weeks,
                    [
                        {'label': 'NPS Commercial', 'values': evolution_all['nps_commercial'], 'color': '#00BCD4'},
                        {'label': 'NPS Projet', 'values': evolution_all['nps_project'], 'color': '#009688'}
                    ]
                )

                # Graphique Temps facturable (multi-CDP)
                self._update_line_chart(
                    self.chart_evolution_facturable,
                    weeks,
                    datasets_facturable,
                    ' j'
                )

                # Graphique corrélation (premier CDP sélectionné)
                if selected_cdps:
                    correlation_data = calc.get_projects_vs_pipe_evolution(selected_cdps[0])
                    self._update_correlation_chart(self.chart_evolution_correlation, correlation_data)

                    # Graphique jours par projet (CDP sélectionné)
                    top_projects = calc.get_facturable_by_project(self.current_week, limit=15, cdp_name=selected_cdps[0])
                    if top_projects:
                        labels = [f"{p['client_name']}\n({p['bu']})" for p in top_projects]
                        values = [p['days_facturable'] for p in top_projects]
                        self._update_vertical_bar_chart(self.chart_evolution_projects_bars, labels, values)
                    else:
                        self._update_vertical_bar_chart(self.chart_evolution_projects_bars, [], [])

        except Exception as e:
            logger.error(f"Erreur lors du rafraîchissement évolution: {e}")

    def _update_facturable_chart(self, calc: DashboardCalculator):
        """Met à jour les 3 graphiques PIPE."""
        try:
            # Graph 1 : Top projets (barres verticales) avec BU
            top_projects = calc.get_facturable_by_project(self.current_week, limit=12)
            if top_projects:
                # Format: "Client (BU)"
                labels = [f"{p['client_name']}\n({p['bu']})" for p in top_projects]
                values = [p['days_facturable'] for p in top_projects]
                self._update_vertical_bar_chart(self.chart_top_projects, labels, values)

            # Graph 2 : Par CDP (barres horizontales)
            ranking = calc.get_facturable_by_cdp_ranking(self.current_week)
            if ranking:
                labels = [r['project_manager'] for r in ranking]
                values = [r['total_facturable'] for r in ranking]
                self._update_bar_chart(self.chart_facturable_cdp, labels, values, "j")

            # Graph 3 : Corrélation Nb projets vs PIPE
            correlation_data = calc.get_projects_vs_pipe_evolution()
            self._update_correlation_chart(self.chart_correlation, correlation_data)

        except Exception as e:
            logger.error(f"Erreur mise à jour graphiques PIPE: {e}")

    def _update_vertical_bar_chart(self, widget: QWidget, labels: list, values: list):
        """Met à jour un graphique à barres verticales. Projets à 0j en rouge."""
        canvas = None
        for child in widget.children():
            if isinstance(child, FigureCanvas):
                canvas = child
                break

        if not canvas:
            return

        fig = canvas.figure
        fig.clear()
        ax = fig.add_subplot(111)

        if values:
            x = range(len(labels))
            # Couleur : rouge si 0 jours, sinon couleur normale
            colors = ['#E53935' if v == 0 else canvas.chart_color for v in values]
            bars = ax.bar(x, values, color=colors, alpha=0.8)
            ax.set_xticks(x)
            ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=7)
            ax.grid(axis='y', alpha=0.3)

            # Afficher les valeurs sur les barres
            for bar, val in zip(bars, values):
                label_text = f'{val:.0f}j' if val > 0 else '0j !'
                label_color = '#E53935' if val == 0 else '#0A1563'
                y_pos = max(bar.get_height(), 1) + 0.5
                ax.text(bar.get_x() + bar.get_width()/2., y_pos,
                       label_text, ha='center', va='bottom', fontsize=7,
                       color=label_color, fontweight='bold' if val == 0 else 'normal')
        else:
            ax.text(0.5, 0.5, 'Aucune donnée', ha='center', va='center', transform=ax.transAxes)

        ax.set_facecolor('#f8faff')
        fig.tight_layout()
        canvas.draw()

    def _update_correlation_chart(self, widget: QWidget, data: dict):
        """Met à jour le graphique de corrélation (double axe)."""
        canvas = None
        for child in widget.children():
            if isinstance(child, FigureCanvas):
                canvas = child
                break

        if not canvas:
            return

        fig = canvas.figure
        fig.clear()
        ax1 = fig.add_subplot(111)

        weeks = data.get('weeks', [])
        nb_projects = data.get('active_projects', [])
        total_pipe = data.get('total_pipe', [])

        if weeks and nb_projects:
            x = range(len(weeks))

            # Axe 1 : Nb projets (barres bleues)
            ax1.bar(x, nb_projects, color=canvas.color1, alpha=0.6, label='Nb Projets Actifs')
            ax1.set_ylabel('Nb Projets', color=canvas.color1, fontsize=9)
            ax1.tick_params(axis='y', labelcolor=canvas.color1)
            ax1.set_xticks(x)
            ax1.set_xticklabels(weeks, rotation=45, ha='right', fontsize=8)

            # Axe 2 : PIPE (ligne orange)
            ax2 = ax1.twinx()
            ax2.plot(x, total_pipe, color=canvas.color2, marker='o', linewidth=2.5,
                    markersize=5, label='PIPE (jours)')
            ax2.set_ylabel('PIPE (jours)', color=canvas.color2, fontsize=9)
            ax2.tick_params(axis='y', labelcolor=canvas.color2)

            # Afficher les valeurs du PIPE
            for i, val in enumerate(total_pipe):
                ax2.text(i, val + max(total_pipe)*0.02, f'{val:.0f}',
                        ha='center', va='bottom', fontsize=7, color=canvas.color2, fontweight='bold')

            # Légendes combinées
            lines1, labels1 = ax1.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=8)

            ax1.grid(axis='y', alpha=0.3)
        else:
            ax1.text(0.5, 0.5, 'Aucune donnée', ha='center', va='center', transform=ax1.transAxes)

        ax1.set_facecolor('#f8faff')
        fig.tight_layout()
        canvas.draw()

    def _update_kpis(self, stats: List[Dict[str, Any]]):
        """Met à jour les KPIs globaux."""
        # Nombre de CDP
        total_cdp = len(stats)
        self.tile_total_cdp.value_label.setText(str(total_cdp))

        # Moyenne projets par CDP
        total_active = sum(s['active_projects'] for s in stats)
        avg_projects = round(total_active / total_cdp, 1) if total_cdp > 0 else 0
        self.tile_avg_projects.value_label.setText(str(avg_projects))

        # Taux santé moyen
        cdp_with_active = [s for s in stats if s['active_projects'] > 0]
        if cdp_with_active:
            avg_health = sum(s['health_rate'] for s in cdp_with_active) / len(cdp_with_active)
            self.tile_avg_health.value_label.setText(f"{avg_health:.0f}%")
        else:
            self.tile_avg_health.value_label.setText("N/A")

        # CDP avec warnings
        cdp_with_warnings = sum(1 for s in stats if s['projects_with_warning'] > 0)
        self.tile_cdp_warning.value_label.setText(str(cdp_with_warnings))

        # Total jours dispositif
        total_days = sum(s['total_days_dispositif'] for s in stats)
        self.tile_total_days.value_label.setText(str(total_days))

        # NPS Commercial moyen
        nps_com_values = [s['avg_nps_commercial'] for s in stats if s['avg_nps_commercial'] is not None]
        if nps_com_values:
            avg_nps_com = sum(nps_com_values) / len(nps_com_values)
            self.tile_avg_nps_com.value_label.setText(f"{avg_nps_com:.0f}")
        else:
            self.tile_avg_nps_com.value_label.setText("N/A")

        # NPS Projet moyen
        nps_proj_values = [s['avg_nps_project'] for s in stats if s['avg_nps_project'] is not None]
        if nps_proj_values:
            avg_nps_proj = sum(nps_proj_values) / len(nps_proj_values)
            self.tile_avg_nps_proj.value_label.setText(f"{avg_nps_proj:.0f}")
        else:
            self.tile_avg_nps_proj.value_label.setText("N/A")

    def _update_table(self, stats: List[Dict[str, Any]]):
        """Met à jour le tableau."""
        self.table.setRowCount(len(stats))

        for row, s in enumerate(stats):
            # Chef de Projet
            self.table.setItem(row, 0, QTableWidgetItem(s['project_manager']))

            # Actifs
            item = QTableWidgetItem(str(s['active_projects']))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 1, item)

            # Total
            item = QTableWidgetItem(str(s['total_projects']))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 2, item)

            # Pause
            item = QTableWidgetItem(str(s['paused_projects']))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 3, item)

            # Terminés
            item = QTableWidgetItem(str(s['completed_projects']))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 4, item)

            # À venir
            item = QTableWidgetItem(str(s['upcoming_projects']))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 5, item)

            # Warnings Client
            item = QTableWidgetItem(str(s['warnings_client']))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if s['warnings_client'] > 0:
                item.setBackground(QColor("#FFCDD2"))
            self.table.setItem(row, 6, item)

            # Warnings Interne
            item = QTableWidgetItem(str(s['warnings_internal']))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if s['warnings_internal'] > 0:
                item.setBackground(QColor("#FFE0B2"))
            self.table.setItem(row, 7, item)

            # Taux Santé
            item = QTableWidgetItem(f"{s['health_rate']:.0f}%")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if s['health_rate'] >= 80:
                item.setBackground(QColor("#C8E6C9"))
            elif s['health_rate'] >= 50:
                item.setBackground(QColor("#FFF9C4"))
            else:
                item.setBackground(QColor("#FFCDD2"))
            self.table.setItem(row, 8, item)

            # DLIC Dépassées
            item = QTableWidgetItem(str(s['dlic_overdue']))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if s['dlic_overdue'] > 0:
                item.setBackground(QColor("#FFCDD2"))
            self.table.setItem(row, 9, item)

            # DLIC Vides
            item = QTableWidgetItem(str(s['dlic_empty']))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if s['dlic_empty'] > 0:
                item.setBackground(QColor("#FFE0B2"))
            self.table.setItem(row, 10, item)

            # Taux DLIC
            item = QTableWidgetItem(f"{s['dlic_fill_rate']:.0f}%")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 11, item)

            # NPS Commercial
            nps_com = s.get('avg_nps_commercial')
            if nps_com is not None:
                item = QTableWidgetItem(f"{nps_com:.0f}")
                if nps_com >= 50:
                    item.setBackground(QColor("#C8E6C9"))
                elif nps_com >= 0:
                    item.setBackground(QColor("#FFF9C4"))
                else:
                    item.setBackground(QColor("#FFCDD2"))
            else:
                item = QTableWidgetItem("N/A")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 12, item)

            # NPS Projet
            nps_proj = s.get('avg_nps_project')
            if nps_proj is not None:
                item = QTableWidgetItem(f"{nps_proj:.0f}")
                if nps_proj >= 50:
                    item.setBackground(QColor("#C8E6C9"))
                elif nps_proj >= 0:
                    item.setBackground(QColor("#FFF9C4"))
                else:
                    item.setBackground(QColor("#FFCDD2"))
            else:
                item = QTableWidgetItem("N/A")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 13, item)

            # Jours Dispositif
            item = QTableWidgetItem(str(s['total_days_dispositif']))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 14, item)

    def _update_charts(self, stats: List[Dict[str, Any]]):
        """Met à jour les graphiques de classement."""
        # Filtrer les CDP avec des projets actifs
        active_cdps = [s for s in stats if s['active_projects'] > 0]

        # Graphique Charge (trié par nombre de projets)
        sorted_by_charge = sorted(active_cdps, key=lambda x: x['active_projects'], reverse=True)
        labels_charge = [s['project_manager'] for s in sorted_by_charge]
        values_charge = [s['active_projects'] for s in sorted_by_charge]
        self._update_bar_chart(self.chart_charge, labels_charge, values_charge)

        # Graphique Santé (trié par taux de santé)
        sorted_by_health = sorted(active_cdps, key=lambda x: x['health_rate'], reverse=True)
        labels_health = [s['project_manager'] for s in sorted_by_health]
        values_health = [s['health_rate'] for s in sorted_by_health]
        self._update_bar_chart(self.chart_health, labels_health, values_health, "%")
