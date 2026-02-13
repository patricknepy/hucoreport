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

        # ========== Section 1 : Santé du Portefeuille ==========
        sante_group = QGroupBox("1. Santé du Portefeuille")
        sante_group.setStyleSheet("""
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

        sante_layout = QHBoxLayout(sante_group)
        sante_layout.setSpacing(15)
        sante_layout.setContentsMargins(15, 25, 15, 15)

        # KPI Cards - Santé
        self.kpi_sains = KPICard(
            "Taux Projets Sains",
            "0%",
            "Sans warning",
            "#4CAF50"
        )
        sante_layout.addWidget(self.kpi_sains)

        self.kpi_anticipe = KPICard(
            "Alerte Anticipée",
            "0%",
            "Warning Interne seul",
            "#2196F3"
        )
        sante_layout.addWidget(self.kpi_anticipe)

        self.kpi_risque = KPICard(
            "Projets à Risque",
            "0",
            "Double warning",
            "#f44336"
        )
        sante_layout.addWidget(self.kpi_risque)

        self.kpi_tendance = KPICard(
            "Tendance",
            "-",
            "vs semaine préc.",
            "#FF9800"
        )
        sante_layout.addWidget(self.kpi_tendance)

        sante_layout.addStretch()

        main_layout.addWidget(sante_group)

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

            # Calculs
            total_actifs = self.calculator._count_active(week)
            warning_client = self.calculator._count_warning_client(week)
            warning_internal = self.calculator._count_warning_internal(week)
            projects_with_warning = self.calculator._count_projects_with_warning(week)

            # 1. Taux de projets sains
            if total_actifs > 0:
                taux_sains = ((total_actifs - projects_with_warning) / total_actifs) * 100
            else:
                taux_sains = 0
            self.kpi_sains.set_value(f"{taux_sains:.1f}%")

            # 2. Taux d'alerte anticipée
            warning_interne_seul = self._count_warning_internal_only(week)
            if projects_with_warning > 0:
                taux_anticipe = (warning_interne_seul / projects_with_warning) * 100
            else:
                taux_anticipe = 0
            self.kpi_anticipe.set_value(f"{taux_anticipe:.1f}%")

            # 3. Projets à risque
            projets_risque = self._count_double_warning(week)
            self.kpi_risque.set_value(str(projets_risque))

            # 4. Tendance warnings
            tendance = self._calculate_tendance(week)
            self.kpi_tendance.set_value(tendance)

            # Détails
            details = f"""
<b>Semaine S{week:02d}</b><br><br>
<b>Projets actifs :</b> {total_actifs}<br>
<b>Projets sains :</b> {total_actifs - projects_with_warning} ({taux_sains:.1f}%)<br>
<b>Projets avec warning :</b> {projects_with_warning}<br>
&nbsp;&nbsp;- Warning Client uniquement : {warning_client - projets_risque}<br>
&nbsp;&nbsp;- Warning Interne uniquement : {warning_interne_seul}<br>
&nbsp;&nbsp;- Double warning : {projets_risque}
"""
            self.details_label.setText(details)

        except Exception as e:
            logger.error(f"Erreur calcul KPIs: {e}")
            import traceback
            traceback.print_exc()

    def _count_warning_internal_only(self, week: int) -> int:
        """Compte les projets avec warning interne SANS warning client."""
        return self.db.execute_scalar(
            """SELECT COUNT(DISTINCT id_projet) FROM projects
               WHERE week_number = ?
               AND status = 'EN COURS'
               AND (LOWER(vision_internal) LIKE '%warning%')
               AND (vision_client IS NULL OR LOWER(vision_client) NOT LIKE '%warning%')""",
            (week,)
        ) or 0

    def _count_double_warning(self, week: int) -> int:
        """Compte les projets avec warning client ET interne."""
        return self.db.execute_scalar(
            """SELECT COUNT(DISTINCT id_projet) FROM projects
               WHERE week_number = ?
               AND status = 'EN COURS'
               AND (LOWER(vision_client) LIKE '%warning%')
               AND (LOWER(vision_internal) LIKE '%warning%')""",
            (week,)
        ) or 0

    def _calculate_tendance(self, week: int) -> str:
        """Calcule la tendance des warnings vs semaine précédente."""
        available_weeks = self.db.get_available_weeks()

        if len(available_weeks) < 2:
            return "-"

        try:
            current_idx = available_weeks.index(week)
            if current_idx >= len(available_weeks) - 1:
                return "-"

            prev_week = available_weeks[current_idx + 1]

            current_warnings = self.calculator._count_projects_with_warning(week)
            prev_warnings = self.calculator._count_projects_with_warning(prev_week)

            diff = current_warnings - prev_warnings

            if diff > 0:
                return f"+{diff}"
            elif diff < 0:
                return str(diff)
            else:
                return "="

        except (ValueError, IndexError):
            return "-"

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
