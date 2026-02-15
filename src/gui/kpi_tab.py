"""
Onglet KPI - Indicateurs clés de performance.

Affiche les KPIs de santé du portefeuille client et les KPIs commerciaux.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox,
    QGridLayout, QFrame, QPushButton, QComboBox, QScrollArea,
    QFileDialog, QMessageBox, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from pathlib import Path

import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import logging

from src.core.dashboard_calculator import DashboardCalculator
from src.core.database import Database
from src.core.commercial_parser import CommercialParser
from src.core.paths import get_application_path

logger = logging.getLogger(__name__)


class KPICard(QFrame):
    """Carte KPI individuelle avec style propre."""

    def __init__(self, title: str, value: str, description: str, color: str):
        super().__init__()
        self.color = color
        self.setup_ui(title, value, description)

    def setup_ui(self, title: str, value: str, description: str):
        self.setObjectName("kpiCard")
        self.setStyleSheet(f"""
            QFrame#kpiCard {{
                background-color: white;
                border: 2px solid {self.color};
                border-radius: 10px;
            }}
        """)
        self.setMinimumSize(180, 110)
        self.setMaximumHeight(130)

        layout = QVBoxLayout(self)
        layout.setSpacing(3)
        layout.setContentsMargins(8, 8, 8, 8)

        # Titre
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet(f"""
            QLabel {{
                color: {self.color};
                font-weight: bold;
                font-size: 10px;
                background: transparent;
                border: none;
            }}
        """)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)

        # Valeur
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet(f"""
            QLabel {{
                color: {self.color};
                font-size: 26px;
                font-weight: bold;
                background: transparent;
                border: none;
            }}
        """)
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.value_label)

        # Description
        self.desc_label = QLabel(description)
        self.desc_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 9px;
                background: transparent;
                border: none;
            }
        """)
        self.desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.desc_label.setWordWrap(True)
        layout.addWidget(self.desc_label)

    def set_value(self, value: str):
        self.value_label.setText(value)


class KPITab(QWidget):
    """Onglet KPI avec indicateurs de santé du portefeuille et commerciaux."""

    def __init__(self):
        super().__init__()
        self.db = Database()
        self.calculator = DashboardCalculator(self.db)
        self.commercial_parser = CommercialParser()
        self.commercial_data = None
        self.current_week = None
        self.init_ui()
        self.load_weeks()
        self.auto_load_commercial()

    def init_ui(self):
        """Initialise l'interface de l'onglet KPI."""
        # Layout principal avec scroll
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        content_widget = QWidget()
        main_layout = QVBoxLayout(content_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Header avec titre et sélecteur de semaine
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)

        title_label = QLabel("KPIs - Tableau de Bord")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #1a237e; background: transparent;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Sélecteur de semaine
        week_label = QLabel("Semaine :")
        week_label.setStyleSheet("background: transparent;")
        header_layout.addWidget(week_label)

        self.week_combo = QComboBox()
        self.week_combo.setMinimumWidth(100)
        self.week_combo.currentIndexChanged.connect(self.on_week_changed)
        header_layout.addWidget(self.week_combo)

        # Bouton actualiser
        refresh_btn = QPushButton("Actualiser")
        refresh_btn.clicked.connect(self.refresh_all)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a237e;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #303f9f;
            }
        """)
        header_layout.addWidget(refresh_btn)

        main_layout.addWidget(header_widget)

        # ========== Section 1 : Taux de Maîtrise ==========
        maitrise_group = QGroupBox("1. Taux de Maîtrise du Portefeuille")
        maitrise_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                border: 2px solid #4CAF50;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 8px;
                background-color: #f8f9fa;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                color: #2E7D32;
            }
        """)

        maitrise_main = QVBoxLayout(maitrise_group)
        maitrise_main.setSpacing(10)
        maitrise_main.setContentsMargins(15, 25, 15, 15)

        # Ligne 1 : KPI Cards
        row1_layout = QHBoxLayout()
        row1_layout.setSpacing(15)

        self.kpi_maitrise = KPICard(
            "Taux de Maîtrise",
            "0%",
            "Projets sans warning",
            "#4CAF50"
        )
        row1_layout.addWidget(self.kpi_maitrise)

        self.kpi_critique_client = KPICard(
            "Critique Client",
            "0%",
            "Vision Client",
            "#7030A0"
        )
        row1_layout.addWidget(self.kpi_critique_client)

        self.kpi_critique_interne = KPICard(
            "Critique Interne",
            "0%",
            "Vision Interne",
            "#9B59B6"
        )
        row1_layout.addWidget(self.kpi_critique_interne)

        self.kpi_warning_total = KPICard(
            "Projets en Warning",
            "0",
            "Client ou Interne",
            "#E67E00"
        )
        row1_layout.addWidget(self.kpi_warning_total)

        row1_layout.addStretch()
        maitrise_main.addLayout(row1_layout)

        # Ligne 2 : Graphique évolution du taux de maîtrise
        self.chart_evolution = self._create_chart_widget("Evolution du Taux de Maîtrise par Semaine")
        maitrise_main.addWidget(self.chart_evolution)

        main_layout.addWidget(maitrise_group)

        # ========== Section 2 : Répartition par Chef de Projet ==========
        repartition_group = QGroupBox("2. Répartition par Chef de Projet")
        repartition_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                border: 2px solid #1a237e;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 8px;
                background-color: #f8f9fa;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                color: #1a237e;
            }
        """)

        repartition_layout = QHBoxLayout(repartition_group)
        repartition_layout.setSpacing(15)
        repartition_layout.setContentsMargins(15, 25, 15, 15)

        # Graphique Warnings par CDP
        self.chart_warnings_cdp = self._create_chart_widget("Warnings par Chef de Projet")
        repartition_layout.addWidget(self.chart_warnings_cdp)

        # Graphique Critiques par CDP
        self.chart_critiques_cdp = self._create_chart_widget("Critiques par Chef de Projet")
        repartition_layout.addWidget(self.chart_critiques_cdp)

        main_layout.addWidget(repartition_group)

        # ========== Section 2 : KPIs Commerciaux ==========
        commercial_group = QGroupBox("2. Performance Commerciale (input.xlsx)")
        commercial_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                border: 2px solid #FF9800;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 8px;
                background-color: #fffde7;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                color: #E65100;
            }
        """)

        commercial_main = QVBoxLayout(commercial_group)
        commercial_main.setSpacing(10)
        commercial_main.setContentsMargins(15, 25, 15, 15)

        # Ligne 1 : Bouton + KPIs principaux
        row1_layout = QHBoxLayout()
        row1_layout.setSpacing(15)

        load_commercial_btn = QPushButton("Charger input.xlsx")
        load_commercial_btn.clicked.connect(self.load_commercial_file)
        load_commercial_btn.setMinimumHeight(40)
        load_commercial_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        row1_layout.addWidget(load_commercial_btn)

        self.kpi_taux_regie = KPICard("Taux Régie", "-%", "vs Build", "#FF9800")
        row1_layout.addWidget(self.kpi_taux_regie)

        self.kpi_pipeline = KPICard("Pipeline Pondéré", "-€", "CA pondéré", "#4CAF50")
        row1_layout.addWidget(self.kpi_pipeline)

        self.kpi_taux_real = KPICard("Réalisation", "-%", "Réalisé/Prévu", "#2196F3")
        row1_layout.addWidget(self.kpi_taux_real)

        row1_layout.addStretch()
        commercial_main.addLayout(row1_layout)

        # Ligne 2 : KPIs secondaires
        row2_layout = QHBoxLayout()
        row2_layout.setSpacing(15)

        self.kpi_tjm = KPICard("TJM Moyen", "-€", "Taux journalier", "#9C27B0")
        row2_layout.addWidget(self.kpi_tjm)

        self.kpi_signed = KPICard("Signés", "0", "100%", "#4CAF50")
        row2_layout.addWidget(self.kpi_signed)

        self.kpi_agreed = KPICard("Agreed", "0", "80%", "#8BC34A")
        row2_layout.addWidget(self.kpi_agreed)

        self.kpi_likely = KPICard("Likely", "0", "50%", "#FFC107")
        row2_layout.addWidget(self.kpi_likely)

        row2_layout.addStretch()
        commercial_main.addLayout(row2_layout)

        main_layout.addWidget(commercial_group)

        # ========== Section Détails ==========
        details_group = QGroupBox("Détails")
        details_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 12px;
                border: 1px solid #ddd;
                border-radius: 5px;
                margin-top: 12px;
                padding-top: 8px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)

        details_layout = QVBoxLayout(details_group)
        self.details_label = QLabel("Sélectionnez une semaine pour voir les détails.")
        self.details_label.setWordWrap(True)
        self.details_label.setStyleSheet("padding: 10px; color: #666; background: transparent;")
        self.details_label.setTextFormat(Qt.TextFormat.RichText)
        details_layout.addWidget(self.details_label)

        main_layout.addWidget(details_group)
        main_layout.addStretch()

        scroll.setWidget(content_widget)
        outer_layout.addWidget(scroll)

    def _create_chart_widget(self, title: str) -> QWidget:
        """Crée un widget avec un graphique matplotlib."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(3)
        layout.setContentsMargins(5, 3, 5, 3)

        # Titre
        title_label = QLabel(title)
        title_label.setStyleSheet("font-weight: bold; font-size: 10pt; background: transparent;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Figure matplotlib
        fig = Figure(figsize=(5, 3), dpi=100)
        fig.patch.set_facecolor('#f8f9fa')
        canvas = FigureCanvas(fig)
        canvas.setMinimumHeight(200)

        widget.figure = fig
        widget.canvas = canvas

        layout.addWidget(canvas, stretch=1)

        return widget

    def load_weeks(self):
        """Charge les semaines disponibles."""
        weeks = self.db.get_available_weeks()
        self.week_combo.clear()

        if weeks:
            for week in weeks:
                self.week_combo.addItem(f"S{week:02d}", week)

            self.current_week = weeks[0]
            self.refresh_kpis()

    def on_week_changed(self, index):
        """Quand l'utilisateur change de semaine."""
        if index >= 0:
            self.current_week = self.week_combo.itemData(index)
            self.refresh_kpis()

    def refresh_all(self):
        """Actualise tous les KPIs."""
        self.refresh_kpis()
        if self.commercial_data:
            self.refresh_commercial_kpis()

    def refresh_kpis(self):
        """Actualise les KPIs santé portefeuille."""
        if self.current_week is None:
            return

        logger.info(f"Calcul KPIs pour S{self.current_week}")

        try:
            week = self.current_week

            # Calculs de base
            total_actifs = self.calculator._count_active(week)
            projects_with_warning = self.calculator._count_projects_with_warning(week)
            critique_client = self.calculator._count_critique_client(week)
            critique_internal = self.calculator._count_critique_internal(week)

            # 1. Taux de maîtrise (% sans warning)
            if total_actifs > 0:
                taux_maitrise = ((total_actifs - projects_with_warning) / total_actifs) * 100
            else:
                taux_maitrise = 100
            self.kpi_maitrise.set_value(f"{taux_maitrise:.1f}%")

            # 2. Taux critique client
            if total_actifs > 0:
                taux_critique_client = (critique_client / total_actifs) * 100
            else:
                taux_critique_client = 0
            self.kpi_critique_client.set_value(f"{taux_critique_client:.1f}%")

            # 3. Taux critique interne
            if total_actifs > 0:
                taux_critique_interne = (critique_internal / total_actifs) * 100
            else:
                taux_critique_interne = 0
            self.kpi_critique_interne.set_value(f"{taux_critique_interne:.1f}%")

            # 4. Total projets en warning
            self.kpi_warning_total.set_value(str(projects_with_warning))

            # Mise à jour des graphiques
            self._update_evolution_chart()
            self._update_warnings_by_cdp_chart(week)
            self._update_critiques_by_cdp_chart(week)

            # Détails
            details = f"""
<b>Semaine S{week:02d}</b><br><br>
<b>Projets actifs :</b> {total_actifs}<br>
<b>Taux de maîtrise :</b> {taux_maitrise:.1f}% ({total_actifs - projects_with_warning} projets sains)<br>
<b>Projets en warning :</b> {projects_with_warning}<br>
<b>Critiques Client :</b> {critique_client} ({taux_critique_client:.1f}%)<br>
<b>Critiques Interne :</b> {critique_internal} ({taux_critique_interne:.1f}%)
"""
            self.details_label.setText(details)

        except Exception as e:
            logger.error(f"Erreur calcul KPIs: {e}")
            import traceback
            traceback.print_exc()

    def _update_evolution_chart(self):
        """Met à jour le graphique d'évolution du taux de maîtrise."""
        import numpy as np
        from datetime import datetime

        fig = self.chart_evolution.figure
        fig.clear()
        ax = fig.add_subplot(111)

        # Récupérer toutes les semaines
        available_weeks = self.db.get_available_weeks()

        if not available_weeks:
            ax.text(0.5, 0.5, 'Aucune donnée', ha='center', va='center', fontsize=12)
            ax.axis('off')
            self.chart_evolution.canvas.draw()
            return

        # Tri chronologique
        current_week = datetime.now().isocalendar()[1]

        def chronological_sort(week: int) -> int:
            if week > current_week:
                return week - 100
            return week

        weeks = sorted(available_weeks, key=chronological_sort)

        # Calculer le taux de maîtrise pour chaque semaine
        taux_maitrise = []
        for w in weeks:
            total = self.calculator._count_active(w)
            with_warning = self.calculator._count_projects_with_warning(w)
            if total > 0:
                taux = ((total - with_warning) / total) * 100
            else:
                taux = 100
            taux_maitrise.append(taux)

        x = np.arange(len(weeks))
        week_labels = [f"S{w}" for w in weeks]

        # Barres avec couleur selon le taux
        colors = ['#4CAF50' if t >= 80 else '#FFC107' if t >= 60 else '#f44336' for t in taux_maitrise]
        bars = ax.bar(x, taux_maitrise, color=colors, alpha=0.8)

        # Ligne de tendance
        ax.plot(x, taux_maitrise, color='#2E7D32', linewidth=2, marker='o', markersize=5)

        ax.set_xlabel('Semaine', fontsize=9)
        ax.set_ylabel('Taux de maîtrise (%)', fontsize=9)
        ax.set_xticks(x)
        ax.set_xticklabels(week_labels, rotation=45, ha='right', fontsize=8)
        ax.set_ylim(0, 105)
        ax.axhline(y=80, color='#4CAF50', linestyle='--', alpha=0.5, label='Objectif 80%')
        ax.grid(axis='y', alpha=0.3)
        ax.set_facecolor('#f8f9fa')

        # Valeurs sur les barres
        for bar, val in zip(bars, taux_maitrise):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                   f'{val:.0f}%', ha='center', va='bottom', fontsize=7, fontweight='bold')

        fig.tight_layout()
        self.chart_evolution.canvas.draw()

    def _update_warnings_by_cdp_chart(self, week: int):
        """Met à jour le graphique des warnings par chef de projet."""
        import numpy as np

        fig = self.chart_warnings_cdp.figure
        fig.clear()
        ax = fig.add_subplot(111)

        # Requête pour compter les warnings par CDP
        query = """
            SELECT
                COALESCE(project_manager, 'Non défini') as cdp,
                SUM(CASE WHEN LOWER(vision_client) LIKE '%warning%' THEN 1 ELSE 0 END) as warning_client,
                SUM(CASE WHEN LOWER(vision_internal) LIKE '%warning%' THEN 1 ELSE 0 END) as warning_interne
            FROM projects
            WHERE week_number = ?
            AND status = 'EN COURS'
            GROUP BY project_manager
            HAVING warning_client > 0 OR warning_interne > 0
            ORDER BY (warning_client + warning_interne) DESC
            LIMIT 10
        """
        cursor = self.db.conn.cursor()
        cursor.execute(query, (week,))
        rows = cursor.fetchall()

        if not rows:
            ax.text(0.5, 0.5, 'Aucun warning', ha='center', va='center', fontsize=12)
            ax.axis('off')
            self.chart_warnings_cdp.canvas.draw()
            return

        cdps = [row['cdp'][:15] for row in rows]  # Tronquer les noms
        warning_client = [row['warning_client'] for row in rows]
        warning_interne = [row['warning_interne'] for row in rows]

        x = np.arange(len(cdps))
        width = 0.35

        bars1 = ax.bar(x - width/2, warning_client, width, label='Client', color='#FFC000', alpha=0.9)
        bars2 = ax.bar(x + width/2, warning_interne, width, label='Interne', color='#FF9800', alpha=0.9)

        ax.set_ylabel('Nb warnings', fontsize=9)
        ax.set_xticks(x)
        ax.set_xticklabels(cdps, rotation=45, ha='right', fontsize=7)
        ax.legend(fontsize=8)
        ax.grid(axis='y', alpha=0.3)
        ax.set_facecolor('#f8f9fa')

        fig.tight_layout()
        self.chart_warnings_cdp.canvas.draw()

    def _update_critiques_by_cdp_chart(self, week: int):
        """Met à jour le graphique des critiques par chef de projet."""
        import numpy as np

        fig = self.chart_critiques_cdp.figure
        fig.clear()
        ax = fig.add_subplot(111)

        # Requête pour compter les critiques par CDP
        query = """
            SELECT
                COALESCE(project_manager, 'Non défini') as cdp,
                SUM(CASE WHEN LOWER(vision_client) LIKE '%critique%' OR LOWER(vision_client) LIKE '%critical%' THEN 1 ELSE 0 END) as critique_client,
                SUM(CASE WHEN LOWER(vision_internal) LIKE '%critique%' OR LOWER(vision_internal) LIKE '%critical%' THEN 1 ELSE 0 END) as critique_interne
            FROM projects
            WHERE week_number = ?
            AND status = 'EN COURS'
            GROUP BY project_manager
            HAVING critique_client > 0 OR critique_interne > 0
            ORDER BY (critique_client + critique_interne) DESC
            LIMIT 10
        """
        cursor = self.db.conn.cursor()
        cursor.execute(query, (week,))
        rows = cursor.fetchall()

        if not rows:
            ax.text(0.5, 0.5, 'Aucun critique', ha='center', va='center', fontsize=12)
            ax.axis('off')
            self.chart_critiques_cdp.canvas.draw()
            return

        cdps = [row['cdp'][:15] for row in rows]  # Tronquer les noms
        critique_client = [row['critique_client'] for row in rows]
        critique_interne = [row['critique_interne'] for row in rows]

        x = np.arange(len(cdps))
        width = 0.35

        bars1 = ax.bar(x - width/2, critique_client, width, label='Client', color='#7030A0', alpha=0.9)
        bars2 = ax.bar(x + width/2, critique_interne, width, label='Interne', color='#9B59B6', alpha=0.9)

        ax.set_ylabel('Nb critiques', fontsize=9)
        ax.set_xticks(x)
        ax.set_xticklabels(cdps, rotation=45, ha='right', fontsize=7)
        ax.legend(fontsize=8)
        ax.grid(axis='y', alpha=0.3)
        ax.set_facecolor('#f8f9fa')

        fig.tight_layout()
        self.chart_critiques_cdp.canvas.draw()

    def auto_load_commercial(self):
        """Charge automatiquement input.xlsx s'il existe."""
        app_path = get_application_path()
        possible_paths = [
            app_path / "import" / "input.xlsx",
            app_path / "input.xlsx",
            Path("C:/Huco_Report 2/import/input.xlsx"),
            Path("C:/Huco_Report 2/input.xlsx"),
        ]

        for path in possible_paths:
            if path.exists():
                logger.info(f"Auto-chargement fichier commercial: {path}")
                self._load_commercial_from_path(str(path))
                return

        logger.info("Aucun fichier input.xlsx trouvé")

    def load_commercial_file(self):
        """Ouvre un dialogue pour charger le fichier commercial."""
        app_path = get_application_path()
        import_dir = str(app_path / "import") if (app_path / "import").exists() else str(app_path)

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Sélectionner le fichier commercial (input.xlsx)",
            import_dir,
            "Fichiers Excel (*.xlsx *.xls);;Tous les fichiers (*.*)"
        )

        if file_path:
            self._load_commercial_from_path(file_path)

    def _load_commercial_from_path(self, file_path: str):
        """Charge et parse le fichier commercial."""
        try:
            if self.commercial_parser.load_file(file_path):
                self.commercial_parser.parse_sheet()
                self.commercial_data = self.commercial_parser.calculate_kpis()
                self.refresh_commercial_kpis()
                logger.info(f"Fichier commercial chargé: {self.commercial_data['total_projets']} projets")
        except Exception as e:
            logger.error(f"Erreur chargement fichier commercial: {e}")
            QMessageBox.warning(
                self,
                "Erreur",
                f"Impossible de charger le fichier commercial:\n{str(e)}"
            )

    def refresh_commercial_kpis(self):
        """Met à jour l'affichage des KPIs commerciaux."""
        if not self.commercial_data:
            return

        data = self.commercial_data

        # Taux Régie
        self.kpi_taux_regie.set_value(f"{data['taux_regie']}%")

        # Pipeline pondéré
        pipeline = data['pipeline_pondere']
        if pipeline >= 1000000:
            pipeline_str = f"{pipeline/1000000:.1f}M€"
        elif pipeline >= 1000:
            pipeline_str = f"{pipeline/1000:.0f}K€"
        else:
            pipeline_str = f"{pipeline:.0f}€"
        self.kpi_pipeline.set_value(pipeline_str)

        # Taux réalisation
        self.kpi_taux_real.set_value(f"{data['taux_realisation']}%")

        # TJM moyen
        self.kpi_tjm.set_value(f"{data['tjm_moyen']}€")

        # Compteurs par statut
        self.kpi_signed.set_value(str(data['nb_projets_signed']))
        self.kpi_agreed.set_value(str(data['nb_projets_agreed']))
        self.kpi_likely.set_value(str(data['nb_projets_likely']))

        # Ajouter détails commerciaux
        current_details = self.details_label.text()
        if "<hr>" not in current_details:
            commercial_details = f"""
<br><hr><br>
<b>Données Commerciales</b><br><br>
<b>Total projets :</b> {data['total_projets']}<br>
<b>Pipeline total :</b> {data['pipeline_total']:,.0f}€<br>
<b>Pipeline pondéré :</b> {data['pipeline_pondere']:,.0f}€<br>
<b>Répartition :</b> {data['taux_regie']:.1f}% Régie / {data['taux_build']:.1f}% Build<br>
<br>
<b>Par statut :</b><br>
&nbsp;&nbsp;- Signed : {data['nb_projets_signed']}<br>
&nbsp;&nbsp;- Agreed : {data['nb_projets_agreed']}<br>
&nbsp;&nbsp;- Likely : {data['nb_projets_likely']}<br>
&nbsp;&nbsp;- Specul : {data['nb_projets_specul']}
"""
            self.details_label.setText(current_details + commercial_details)
