"""
Onglet Analyse - Graphiques d'évolution des warnings et analyses.

Affiche l'évolution des warnings Vision Client et Vision Interne par semaine et par mois.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox,
    QScrollArea, QFrame, QPushButton
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import logging

from src.core.dashboard_calculator import DashboardCalculator
from src.core.database import Database

logger = logging.getLogger(__name__)


class AnalysisTab(QWidget):
    """Onglet Analyse avec graphiques d'évolution des warnings."""

    def __init__(self):
        super().__init__()
        self.db = Database()
        self.calculator = DashboardCalculator(self.db)
        self.init_ui()
        self.refresh_charts()

    def init_ui(self):
        """Initialise l'interface de l'onglet Analyse (COMPACT)."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(5, 5, 5, 5)

        # En-tête compact : titre + bouton sur une ligne
        header_layout = QHBoxLayout()

        title_label = QLabel("Evolution Critiques & Warnings")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #333;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        refresh_btn = QPushButton("Actualiser")
        refresh_btn.setMaximumWidth(100)
        refresh_btn.clicked.connect(self.refresh_charts)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #0166FE;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        header_layout.addWidget(refresh_btn)

        main_layout.addLayout(header_layout)

        # Zone scrollable pour les graphiques
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        scroll_content = QWidget()
        self.charts_layout = QVBoxLayout(scroll_content)
        self.charts_layout.setSpacing(10)

        # Ligne 1 : WARNINGS (Vision Client + Vision Interne) par semaine et par mois
        row1_layout = QHBoxLayout()
        row1_layout.setSpacing(10)

        self.warnings_weekly_group = self._create_chart_group(
            "WARNINGS - Evolution par Semaine", ""
        )
        row1_layout.addWidget(self.warnings_weekly_group)

        self.warnings_monthly_group = self._create_chart_group(
            "WARNINGS - Evolution par Mois", ""
        )
        row1_layout.addWidget(self.warnings_monthly_group)

        self.charts_layout.addLayout(row1_layout)

        # Ligne 2 : CRITIQUES (Vision Client + Vision Interne) par semaine et par mois
        row2_layout = QHBoxLayout()
        row2_layout.setSpacing(10)

        self.critiques_weekly_group = self._create_chart_group(
            "CRITIQUES - Evolution par Semaine", ""
        )
        row2_layout.addWidget(self.critiques_weekly_group)

        self.critiques_monthly_group = self._create_chart_group(
            "CRITIQUES - Evolution par Mois", ""
        )
        row2_layout.addWidget(self.critiques_monthly_group)

        self.charts_layout.addLayout(row2_layout)

        # Ligne 3 : Projets actifs et % Warning
        row3_layout = QHBoxLayout()
        row3_layout.setSpacing(10)

        self.active_chart_group = self._create_chart_group(
            "Projets Actifs par Semaine", ""
        )
        row3_layout.addWidget(self.active_chart_group)

        self.ratio_chart_group = self._create_chart_group(
            "% Warnings / Projets Actifs", ""
        )
        row3_layout.addWidget(self.ratio_chart_group)

        self.charts_layout.addLayout(row3_layout)

        self.charts_layout.addStretch()

        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area, stretch=1)

    def _create_chart_group(self, title: str, description: str) -> QGroupBox:
        """Crée un groupe avec un graphique matplotlib (taille doublée)."""
        group = QGroupBox(title)
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 11px;
                border: 1px solid #ddd;
                border-radius: 5px;
                margin-top: 5px;
                padding-top: 10px;
                background-color: #fafafa;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #333;
            }
        """)

        layout = QVBoxLayout(group)
        layout.setContentsMargins(5, 15, 5, 5)
        layout.setSpacing(2)

        # Canvas matplotlib (taille doublée)
        figure = Figure(figsize=(6, 4), dpi=100)
        figure.patch.set_facecolor('#fafafa')
        canvas = FigureCanvas(figure)
        canvas.setMinimumHeight(350)
        layout.addWidget(canvas)

        # Stocker les références
        group.figure = figure
        group.canvas = canvas

        return group

    def refresh_charts(self):
        """Actualise tous les graphiques avec les données actuelles."""
        logger.info("Actualisation des graphiques d'analyse")

        try:
            # Récupérer les données
            weekly_data = self.calculator.get_warnings_evolution()
            monthly_data = self.calculator.get_warnings_by_month()

            # Mettre à jour les 6 graphiques
            self._update_warnings_weekly(weekly_data)
            self._update_warnings_monthly(monthly_data)
            self._update_critiques_weekly(weekly_data)
            self._update_critiques_monthly(monthly_data)
            self._update_active_projects_chart(weekly_data)
            self._update_ratio_chart(weekly_data)

        except Exception as e:
            logger.error(f"Erreur lors de l'actualisation des graphiques: {e}")

    def _update_active_projects_chart(self, data: dict):
        """Met à jour le graphique des projets actifs par semaine."""
        figure = self.active_chart_group.figure
        figure.clear()

        ax = figure.add_subplot(111)

        weeks = data.get('weeks', [])
        active_projects = data.get('active_projects', [])

        if not weeks:
            ax.text(0.5, 0.5, 'Aucune donnée',
                   ha='center', va='center', fontsize=14, color='#999',
                   transform=ax.transAxes)
            ax.set_facecolor('#fafafa')
            ax.axis('off')
        else:
            import numpy as np
            x = np.arange(len(weeks))

            # Barres pour projets actifs
            bars = ax.bar(x, active_projects, color='#0A1563', alpha=0.8, label='Projets Actifs')

            # Ligne de tendance
            ax.plot(x, active_projects, color='#2E7D32', linewidth=2, marker='o', markersize=6)

            ax.set_xlabel('Semaine', fontsize=10)
            ax.set_ylabel('Nombre de projets', fontsize=10)
            ax.set_title('Projets Actifs par Semaine', fontsize=12, fontweight='bold')
            ax.set_xticks(x)
            ax.set_xticklabels(weeks, rotation=45, ha='right')
            ax.set_ylim(0, 100)  # Échelle fixe 0-100
            ax.set_facecolor('#fafafa')
            ax.grid(axis='y', alpha=0.3)

            # Valeurs sur les barres
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax.annotate(f'{int(height)}',
                               xy=(bar.get_x() + bar.get_width() / 2, height),
                               xytext=(0, 3), textcoords="offset points",
                               ha='center', va='bottom', fontsize=9, fontweight='bold')

        figure.tight_layout()
        self.active_chart_group.canvas.draw()

    def _update_warnings_weekly(self, data: dict):
        """Met à jour le graphique WARNINGS par semaine (Vision Client + Vision Interne)."""
        figure = self.warnings_weekly_group.figure
        figure.clear()

        ax = figure.add_subplot(111)

        weeks = data.get('weeks', [])
        warning_client = data.get('warning_client', [])
        warning_internal = data.get('warning_internal', [])

        if not weeks:
            ax.text(0.5, 0.5, 'Aucune donnée disponible\nImportez un fichier Excel',
                   ha='center', va='center', fontsize=14, color='#999',
                   transform=ax.transAxes)
            ax.set_facecolor('#fafafa')
            ax.axis('off')
        else:
            import numpy as np
            x = np.arange(len(weeks))
            width = 0.35

            # Warning Client en orange (#FFC000), Warning Interne en orange foncé (#FF9800)
            bars_client = ax.bar(x - width/2, warning_client, width,
                                label='Vision Client', color='#FFC000', alpha=0.9)
            bars_internal = ax.bar(x + width/2, warning_internal, width,
                                  label='Vision Interne', color='#FF9800', alpha=0.9)

            ax.set_xlabel('Semaine', fontsize=10)
            ax.set_ylabel('Nombre', fontsize=10)
            ax.set_title('WARNINGS - Evolution par Semaine', fontsize=12, fontweight='bold', color='#E67E00')
            ax.set_xticks(x)
            ax.set_xticklabels(weeks, rotation=45, ha='right')
            ax.legend(loc='upper left', fontsize=9)
            ax.set_facecolor('#fafafa')
            ax.grid(axis='y', alpha=0.3)

            # Valeurs sur les barres
            for bars in [bars_client, bars_internal]:
                for bar in bars:
                    height = bar.get_height()
                    if height > 0:
                        ax.annotate(f'{int(height)}',
                                   xy=(bar.get_x() + bar.get_width() / 2, height),
                                   xytext=(0, 2), textcoords="offset points",
                                   ha='center', va='bottom', fontsize=8, fontweight='bold')

        figure.tight_layout()
        self.warnings_weekly_group.canvas.draw()

    def _update_warnings_monthly(self, data: dict):
        """Met à jour le graphique WARNINGS par mois (Vision Client + Vision Interne)."""
        figure = self.warnings_monthly_group.figure
        figure.clear()

        ax = figure.add_subplot(111)

        months = data.get('months', [])
        warning_client = data.get('warning_client', [])
        warning_internal = data.get('warning_internal', [])

        if not months:
            ax.text(0.5, 0.5, 'Aucune donnée disponible\nImportez un fichier Excel',
                   ha='center', va='center', fontsize=14, color='#999',
                   transform=ax.transAxes)
            ax.set_facecolor('#fafafa')
            ax.axis('off')
        else:
            import numpy as np
            x = np.arange(len(months))
            width = 0.35

            # Warning Client en orange (#FFC000), Warning Interne en orange foncé (#FF9800)
            bars_client = ax.bar(x - width/2, warning_client, width,
                                label='Vision Client', color='#FFC000', alpha=0.9)
            bars_internal = ax.bar(x + width/2, warning_internal, width,
                                  label='Vision Interne', color='#FF9800', alpha=0.9)

            ax.set_xlabel('Mois', fontsize=10)
            ax.set_ylabel('Nombre', fontsize=10)
            ax.set_title('WARNINGS - Evolution par Mois', fontsize=12, fontweight='bold', color='#E67E00')
            ax.set_xticks(x)
            ax.set_xticklabels(months, rotation=45, ha='right')
            ax.legend(loc='upper left', fontsize=9)
            ax.set_facecolor('#fafafa')
            ax.grid(axis='y', alpha=0.3)

            # Valeurs sur les barres
            for bars in [bars_client, bars_internal]:
                for bar in bars:
                    height = bar.get_height()
                    if height > 0:
                        ax.annotate(f'{int(height)}',
                                   xy=(bar.get_x() + bar.get_width() / 2, height),
                                   xytext=(0, 2), textcoords="offset points",
                                   ha='center', va='bottom', fontsize=8, fontweight='bold')

        figure.tight_layout()
        self.warnings_monthly_group.canvas.draw()

    def _update_critiques_weekly(self, data: dict):
        """Met à jour le graphique CRITIQUES par semaine (Vision Client + Vision Interne)."""
        figure = self.critiques_weekly_group.figure
        figure.clear()

        ax = figure.add_subplot(111)

        weeks = data.get('weeks', [])
        critique_client = data.get('critique_client', [])
        critique_internal = data.get('critique_internal', [])

        if not weeks:
            ax.text(0.5, 0.5, 'Aucune donnée disponible\nImportez un fichier Excel',
                   ha='center', va='center', fontsize=14, color='#999',
                   transform=ax.transAxes)
            ax.set_facecolor('#fafafa')
            ax.axis('off')
        else:
            import numpy as np
            x = np.arange(len(weeks))
            width = 0.35

            # Critique Client en violet foncé (#7030A0), Critique Interne en violet clair (#9B59B6)
            bars_client = ax.bar(x - width/2, critique_client, width,
                                label='Vision Client', color='#7030A0', alpha=0.9)
            bars_internal = ax.bar(x + width/2, critique_internal, width,
                                  label='Vision Interne', color='#9B59B6', alpha=0.9)

            ax.set_xlabel('Semaine', fontsize=10)
            ax.set_ylabel('Nombre', fontsize=10)
            ax.set_title('CRITIQUES - Evolution par Semaine', fontsize=12, fontweight='bold', color='#7030A0')
            ax.set_xticks(x)
            ax.set_xticklabels(weeks, rotation=45, ha='right')
            ax.legend(loc='upper left', fontsize=9)
            ax.set_facecolor('#fafafa')
            ax.grid(axis='y', alpha=0.3)

            # Valeurs sur les barres
            for bars in [bars_client, bars_internal]:
                for bar in bars:
                    height = bar.get_height()
                    if height > 0:
                        ax.annotate(f'{int(height)}',
                                   xy=(bar.get_x() + bar.get_width() / 2, height),
                                   xytext=(0, 2), textcoords="offset points",
                                   ha='center', va='bottom', fontsize=8, fontweight='bold')

        figure.tight_layout()
        self.critiques_weekly_group.canvas.draw()

    def _update_critiques_monthly(self, data: dict):
        """Met à jour le graphique CRITIQUES par mois (Vision Client + Vision Interne)."""
        figure = self.critiques_monthly_group.figure
        figure.clear()

        ax = figure.add_subplot(111)

        months = data.get('months', [])
        critique_client = data.get('critique_client', [])
        critique_internal = data.get('critique_internal', [])

        if not months:
            ax.text(0.5, 0.5, 'Aucune donnée disponible\nImportez un fichier Excel',
                   ha='center', va='center', fontsize=14, color='#999',
                   transform=ax.transAxes)
            ax.set_facecolor('#fafafa')
            ax.axis('off')
        else:
            import numpy as np
            x = np.arange(len(months))
            width = 0.35

            # Critique Client en violet foncé (#7030A0), Critique Interne en violet clair (#9B59B6)
            bars_client = ax.bar(x - width/2, critique_client, width,
                                label='Vision Client', color='#7030A0', alpha=0.9)
            bars_internal = ax.bar(x + width/2, critique_internal, width,
                                  label='Vision Interne', color='#9B59B6', alpha=0.9)

            ax.set_xlabel('Mois', fontsize=10)
            ax.set_ylabel('Nombre', fontsize=10)
            ax.set_title('CRITIQUES - Evolution par Mois', fontsize=12, fontweight='bold', color='#7030A0')
            ax.set_xticks(x)
            ax.set_xticklabels(months, rotation=45, ha='right')
            ax.legend(loc='upper left', fontsize=9)
            ax.set_facecolor('#fafafa')
            ax.grid(axis='y', alpha=0.3)

            # Valeurs sur les barres
            for bars in [bars_client, bars_internal]:
                for bar in bars:
                    height = bar.get_height()
                    if height > 0:
                        ax.annotate(f'{int(height)}',
                                   xy=(bar.get_x() + bar.get_width() / 2, height),
                                   xytext=(0, 2), textcoords="offset points",
                                   ha='center', va='bottom', fontsize=8, fontweight='bold')

        figure.tight_layout()
        self.critiques_monthly_group.canvas.draw()

    def _update_ratio_chart(self, data: dict):
        """Met à jour le graphique du ratio dossiers en warning / projets actifs."""
        figure = self.ratio_chart_group.figure
        figure.clear()

        ax1 = figure.add_subplot(111)

        weeks = data.get('weeks', [])
        projects_with_warning = data.get('projects_with_warning', [])  # Nb de DOSSIERS en warning
        active_projects = data.get('active_projects', [])

        if not weeks:
            ax1.text(0.5, 0.5, 'Aucune donnée',
                   ha='center', va='center', fontsize=14, color='#999',
                   transform=ax1.transAxes)
            ax1.set_facecolor('#fafafa')
            ax1.axis('off')
        else:
            import numpy as np
            x = np.arange(len(weeks))

            # Calculer le % de dossiers en warning
            ratios = []
            for pw, ap in zip(projects_with_warning, active_projects):
                if ap > 0:
                    ratios.append(round((pw / ap) * 100, 1))
                else:
                    ratios.append(0)

            # Axe 1 : % de dossiers en warning (rouge)
            line1, = ax1.plot(x, ratios, marker='o', linewidth=2, markersize=8,
                   color='#F44336', label='% dossiers en warning')
            ax1.fill_between(x, ratios, alpha=0.2, color='#F44336')
            ax1.set_ylabel('% de dossiers en warning', fontsize=10, color='#F44336')
            ax1.set_ylim(0, 100)
            ax1.tick_params(axis='y', labelcolor='#F44336')

            # Axe 2 : Nombre de projets actifs (vert)
            ax2 = ax1.twinx()
            line2, = ax2.plot(x, active_projects, marker='s', linewidth=2, markersize=6,
                   color='#0A1563', linestyle='--', label='Projets actifs')
            ax2.set_ylabel('Nb projets actifs', fontsize=10, color='#0A1563')
            ax2.set_ylim(0, 100)
            ax2.tick_params(axis='y', labelcolor='#0A1563')

            ax1.set_xlabel('Semaine', fontsize=10)
            ax1.set_title('% Dossiers en Warning vs Projets Actifs', fontsize=11, fontweight='bold')
            ax1.set_xticks(x)
            ax1.set_xticklabels(weeks, rotation=45, ha='right')
            ax1.set_facecolor('#fafafa')
            ax1.grid(alpha=0.3)

            # Légende combinée
            ax1.legend([line1, line2], ['% en warning', 'Projets actifs'], loc='upper right', fontsize=8)

            # Valeurs sur les points (% warning)
            for i, y in enumerate(ratios):
                ax1.annotate(f'{y}%',
                           xy=(i, y),
                           xytext=(0, 8), textcoords="offset points",
                           ha='center', va='bottom', fontsize=8, fontweight='bold', color='#F44336')

        figure.tight_layout()
        self.ratio_chart_group.canvas.draw()

