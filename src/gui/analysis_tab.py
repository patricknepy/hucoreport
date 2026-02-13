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

        title_label = QLabel("Evolution des Warnings")
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
                background-color: #2196F3;
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

        # Ligne 1 : 2 graphiques côte à côte
        row1_layout = QHBoxLayout()
        row1_layout.setSpacing(10)

        # Graphique 1 : Warnings par semaine
        self.weekly_chart_group = self._create_chart_group(
            "Warnings par Semaine", ""
        )
        row1_layout.addWidget(self.weekly_chart_group)

        # Graphique 2 : Projets actifs par semaine
        self.active_chart_group = self._create_chart_group(
            "Projets Actifs par Semaine", ""
        )
        row1_layout.addWidget(self.active_chart_group)

        self.charts_layout.addLayout(row1_layout)

        # Ligne 2 : 2 graphiques côte à côte
        row2_layout = QHBoxLayout()
        row2_layout.setSpacing(10)

        # Graphique 3 : % Warnings
        self.ratio_chart_group = self._create_chart_group(
            "% Warnings / Projets Actifs", ""
        )
        row2_layout.addWidget(self.ratio_chart_group)

        # Graphique 4 : Warnings par mois
        self.monthly_chart_group = self._create_chart_group(
            "Warnings par Mois", ""
        )
        row2_layout.addWidget(self.monthly_chart_group)

        self.charts_layout.addLayout(row2_layout)

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

            # Mettre à jour les 4 graphiques
            self._update_weekly_chart(weekly_data)
            self._update_active_projects_chart(weekly_data)
            self._update_ratio_chart(weekly_data)
            self._update_monthly_chart(monthly_data)

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
            bars = ax.bar(x, active_projects, color='#4CAF50', alpha=0.8, label='Projets Actifs')

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

    def _update_weekly_chart(self, data: dict):
        """Met à jour le graphique d'évolution par semaine."""
        figure = self.weekly_chart_group.figure
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

            bars1 = ax.bar(x - width/2, warning_client, width,
                          label='Vision Client', color='#FF5722', alpha=0.8)
            bars2 = ax.bar(x + width/2, warning_internal, width,
                          label='Vision Interne', color='#FF9800', alpha=0.8)

            ax.set_xlabel('Semaine', fontsize=10)
            ax.set_ylabel('Nombre de warnings', fontsize=10)
            ax.set_title('Evolution des Warnings par Semaine', fontsize=12, fontweight='bold')
            ax.set_xticks(x)
            ax.set_xticklabels(weeks, rotation=45, ha='right')
            ax.legend(loc='upper left')
            ax.set_facecolor('#fafafa')
            ax.grid(axis='y', alpha=0.3)

            # Ajouter les valeurs sur les barres
            for bar in bars1:
                height = bar.get_height()
                if height > 0:
                    ax.annotate(f'{int(height)}',
                               xy=(bar.get_x() + bar.get_width() / 2, height),
                               xytext=(0, 3), textcoords="offset points",
                               ha='center', va='bottom', fontsize=8)

            for bar in bars2:
                height = bar.get_height()
                if height > 0:
                    ax.annotate(f'{int(height)}',
                               xy=(bar.get_x() + bar.get_width() / 2, height),
                               xytext=(0, 3), textcoords="offset points",
                               ha='center', va='bottom', fontsize=8)

        figure.tight_layout()
        self.weekly_chart_group.canvas.draw()

    def _update_monthly_chart(self, data: dict):
        """Met à jour le graphique d'évolution par mois."""
        figure = self.monthly_chart_group.figure
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

            bars1 = ax.bar(x - width/2, warning_client, width,
                          label='Vision Client', color='#E91E63', alpha=0.8)
            bars2 = ax.bar(x + width/2, warning_internal, width,
                          label='Vision Interne', color='#9C27B0', alpha=0.8)

            ax.set_xlabel('Mois', fontsize=10)
            ax.set_ylabel('Nombre de warnings', fontsize=10)
            ax.set_title('Evolution des Warnings par Mois', fontsize=12, fontweight='bold')
            ax.set_xticks(x)
            ax.set_xticklabels(months, rotation=45, ha='right')
            ax.legend(loc='upper left')
            ax.set_facecolor('#fafafa')
            ax.grid(axis='y', alpha=0.3)

            # Ajouter les valeurs sur les barres
            for bar in bars1:
                height = bar.get_height()
                if height > 0:
                    ax.annotate(f'{int(height)}',
                               xy=(bar.get_x() + bar.get_width() / 2, height),
                               xytext=(0, 3), textcoords="offset points",
                               ha='center', va='bottom', fontsize=8)

            for bar in bars2:
                height = bar.get_height()
                if height > 0:
                    ax.annotate(f'{int(height)}',
                               xy=(bar.get_x() + bar.get_width() / 2, height),
                               xytext=(0, 3), textcoords="offset points",
                               ha='center', va='bottom', fontsize=8)

        figure.tight_layout()
        self.monthly_chart_group.canvas.draw()

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
                   color='#4CAF50', linestyle='--', label='Projets actifs')
            ax2.set_ylabel('Nb projets actifs', fontsize=10, color='#4CAF50')
            ax2.set_ylim(0, 100)
            ax2.tick_params(axis='y', labelcolor='#4CAF50')

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

