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
    QSplitter
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

    def _create_compact_tile(self, title: str, value: str, color: str = "#2196F3") -> QFrame:
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
                background-color: #f5f5f5;
                border: 2px solid black;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
            }
        """)

        layout = QHBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(15, 15, 15, 15)

        self.tile_total_cdp = self._create_compact_tile("Chefs de Projet", "0", "#2196F3")
        layout.addWidget(self.tile_total_cdp)

        self.tile_avg_projects = self._create_compact_tile("Moy. projets/CDP", "0", "#4CAF50")
        layout.addWidget(self.tile_avg_projects)

        self.tile_avg_health = self._create_compact_tile("Taux santé moy.", "0%", "#FF9800")
        layout.addWidget(self.tile_avg_health)

        self.tile_cdp_warning = self._create_compact_tile("CDP avec warn.", "0", "#F44336")
        layout.addWidget(self.tile_cdp_warning)

        self.tile_total_days = self._create_compact_tile("Jours dispositif", "0", "#9C27B0")
        layout.addWidget(self.tile_total_days)

        self.tile_avg_nps_com = self._create_compact_tile("NPS Com. moy.", "N/A", "#00BCD4")
        layout.addWidget(self.tile_avg_nps_com)

        self.tile_avg_nps_proj = self._create_compact_tile("NPS Proj. moy.", "N/A", "#009688")
        layout.addWidget(self.tile_avg_nps_proj)

        layout.addStretch()

        group.setLayout(layout)
        return group

    def _create_table_section(self) -> QGroupBox:
        """Crée la section du tableau récapitulatif."""
        group = QGroupBox("STATISTIQUES PAR CHEF DE PROJET")
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
                background-color: #4CAF50;
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
                background-color: #f5f5f5;
                border: 2px solid black;
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
        self.chart_charge = self._create_bar_chart("Projets actifs par CDP", "#2196F3")
        layout.addWidget(self.chart_charge, stretch=1)

        # Graphique Santé
        self.chart_health = self._create_bar_chart("Taux de santé par CDP", "#4CAF50")
        layout.addWidget(self.chart_health, stretch=1)

        group.setLayout(layout)
        return group

    def _create_evolution_section(self) -> QGroupBox:
        """Crée la section évolution avec filtre CDP."""
        group = QGroupBox("ÉVOLUTION SUR PLUSIEURS SEMAINES")
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

        # Filtre CDP
        filter_layout = QHBoxLayout()
        filter_label = QLabel("Filtrer par Chef de Projet :")
        filter_label.setStyleSheet("font-weight: bold;")
        filter_layout.addWidget(filter_label)

        self.cdp_filter_combo = QComboBox()
        self.cdp_filter_combo.setMinimumWidth(200)
        self.cdp_filter_combo.addItem("Tous les CDP", None)
        self.cdp_filter_combo.currentIndexChanged.connect(self.on_cdp_filter_changed)
        filter_layout.addWidget(self.cdp_filter_combo)

        filter_layout.addStretch()
        main_layout.addLayout(filter_layout)

        # Graphiques d'évolution (2 lignes de 2)
        charts_layout = QGridLayout()
        charts_layout.setSpacing(15)

        # Graphique évolution projets actifs
        self.chart_evolution_projects = self._create_line_chart("Évolution des projets actifs", "#2196F3")
        charts_layout.addWidget(self.chart_evolution_projects, 0, 0)

        # Graphique évolution warnings
        self.chart_evolution_warnings = self._create_line_chart("Évolution des warnings", "#FF9800")
        charts_layout.addWidget(self.chart_evolution_warnings, 0, 1)

        # Graphique évolution taux de santé
        self.chart_evolution_health = self._create_line_chart("Évolution du taux de santé (%)", "#4CAF50")
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
        """Charge la liste des CDP dans le filtre."""
        try:
            calc = DashboardCalculator(self.db)
            cdp_names = calc.get_all_cdp_names()

            self.cdp_filter_combo.blockSignals(True)
            self.cdp_filter_combo.clear()
            self.cdp_filter_combo.addItem("Tous les CDP", None)

            for cdp in cdp_names:
                self.cdp_filter_combo.addItem(cdp, cdp)

            self.cdp_filter_combo.blockSignals(False)
        except Exception as e:
            logger.error(f"Erreur chargement filtre CDP: {e}")

    def on_week_changed(self, index: int):
        """Gère le changement de semaine."""
        if index < 0:
            return

        week = self.week_combo.itemData(index)
        if week:
            self.current_week = week
            self.refresh_data()

    def on_cdp_filter_changed(self, index: int):
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
            self._update_table(stats)
            self._update_charts(stats)
            self.refresh_evolution_charts()

        except Exception as e:
            logger.error(f"Erreur lors du rafraîchissement CDP: {e}")

    def refresh_evolution_charts(self):
        """Rafraîchit les graphiques d'évolution."""
        try:
            calc = DashboardCalculator(self.db)

            # Récupérer le CDP sélectionné
            cdp_name = self.cdp_filter_combo.currentData()

            # Récupérer les données d'évolution
            evolution = calc.get_cdp_evolution(cdp_name)

            weeks = evolution['weeks']

            # Graphique projets actifs
            self._update_line_chart(
                self.chart_evolution_projects,
                weeks,
                [{'label': 'Projets actifs', 'values': evolution['active_projects'], 'color': '#2196F3'}]
            )

            # Graphique warnings (2 courbes)
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
                [{'label': 'Taux de santé', 'values': evolution['health_rate'], 'color': '#4CAF50'}],
                '%'
            )

            # Graphique NPS (2 courbes)
            self._update_line_chart(
                self.chart_evolution_nps,
                weeks,
                [
                    {'label': 'NPS Commercial', 'values': evolution['nps_commercial'], 'color': '#00BCD4'},
                    {'label': 'NPS Projet', 'values': evolution['nps_project'], 'color': '#009688'}
                ]
            )

        except Exception as e:
            logger.error(f"Erreur lors du rafraîchissement évolution: {e}")

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
