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
        """Initialise l'interface de l'onglet Analyse."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Titre
        title_label = QLabel("Evolution des Warnings")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #333;")
        main_layout.addWidget(title_label)

        # Description
        desc_label = QLabel(
            "Suivi de l'évolution des warnings Vision Client (le client râle) "
            "et Vision Interne (le chef de projet s'inquiète) au fil des semaines."
        )
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #666; font-size: 12px; margin-bottom: 10px;")
        main_layout.addWidget(desc_label)

        # Bouton de rafraîchissement
        refresh_btn = QPushButton("Actualiser les graphiques")
        refresh_btn.setMaximumWidth(200)
        refresh_btn.clicked.connect(self.refresh_charts)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        main_layout.addWidget(refresh_btn)

        # Zone scrollable pour les graphiques
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        scroll_content = QWidget()
        self.charts_layout = QVBoxLayout(scroll_content)
        self.charts_layout.setSpacing(20)

        # Graphique 1 : Evolution par semaine
        self.weekly_chart_group = self._create_chart_group(
            "Evolution des Warnings par Semaine",
            "Nombre de warnings Vision Client et Vision Interne pour chaque semaine importée."
        )
        self.charts_layout.addWidget(self.weekly_chart_group)

        # Graphique 2 : Evolution par mois
        self.monthly_chart_group = self._create_chart_group(
            "Evolution des Warnings par Mois",
            "Agrégation mensuelle basée sur la dernière semaine de chaque mois."
        )
        self.charts_layout.addWidget(self.monthly_chart_group)

        # Graphique 3 : Ratio warnings / projets actifs
        self.ratio_chart_group = self._create_chart_group(
            "Ratio Warnings / Projets Actifs",
            "Pourcentage de projets en warning par rapport au total de projets actifs."
        )
        self.charts_layout.addWidget(self.ratio_chart_group)

        self.charts_layout.addStretch()

        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area, stretch=1)

    def _create_chart_group(self, title: str, description: str) -> QGroupBox:
        """Crée un groupe avec un graphique matplotlib."""
        group = QGroupBox(title)
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 1px solid #ddd;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: #fafafa;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px;
                color: #333;
            }
        """)

        layout = QVBoxLayout(group)
        layout.setContentsMargins(15, 20, 15, 15)

        # Description
        desc = QLabel(description)
        desc.setStyleSheet("color: #666; font-size: 11px; font-weight: normal;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Canvas matplotlib
        figure = Figure(figsize=(10, 4), dpi=100)
        figure.patch.set_facecolor('#fafafa')
        canvas = FigureCanvas(figure)
        canvas.setMinimumHeight(300)
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

            # Mettre à jour le graphique par semaine
            self._update_weekly_chart(weekly_data)

            # Mettre à jour le graphique par mois
            self._update_monthly_chart(monthly_data)

            # Mettre à jour le graphique ratio
            self._update_ratio_chart(weekly_data)

        except Exception as e:
            logger.error(f"Erreur lors de l'actualisation des graphiques: {e}")

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
        """Met à jour le graphique du ratio warnings / projets actifs."""
        figure = self.ratio_chart_group.figure
        figure.clear()

        ax = figure.add_subplot(111)

        weeks = data.get('weeks', [])
        total_warnings = data.get('total_warnings', [])
        active_projects = data.get('active_projects', [])

        if not weeks:
            ax.text(0.5, 0.5, 'Aucune donnée disponible\nImportez un fichier Excel',
                   ha='center', va='center', fontsize=14, color='#999',
                   transform=ax.transAxes)
            ax.set_facecolor('#fafafa')
            ax.axis('off')
        else:
            # Calculer le pourcentage
            ratios = []
            for tw, ap in zip(total_warnings, active_projects):
                if ap > 0:
                    ratios.append(round((tw / ap) * 100, 1))
                else:
                    ratios.append(0)

            ax.plot(weeks, ratios, marker='o', linewidth=2, markersize=8,
                   color='#F44336', label='% projets en warning')
            ax.fill_between(weeks, ratios, alpha=0.2, color='#F44336')

            ax.set_xlabel('Semaine', fontsize=10)
            ax.set_ylabel('% de projets en warning', fontsize=10)
            ax.set_title('Ratio Warnings / Projets Actifs', fontsize=12, fontweight='bold')
            ax.set_xticklabels(weeks, rotation=45, ha='right')
            ax.legend(loc='upper left')
            ax.set_facecolor('#fafafa')
            ax.grid(alpha=0.3)

            # Ajouter les valeurs sur les points
            for i, (x, y) in enumerate(zip(weeks, ratios)):
                ax.annotate(f'{y}%',
                           xy=(i, y),
                           xytext=(0, 8), textcoords="offset points",
                           ha='center', va='bottom', fontsize=9, fontweight='bold')

        figure.tight_layout()
        self.ratio_chart_group.canvas.draw()

