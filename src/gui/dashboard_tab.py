"""
Onglet Dashboard principal de l'application.

Affiche les indicateurs clés de performance pour la semaine sélectionnée.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QGroupBox, QListWidget, QMessageBox,
    QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from typing import List, Dict, Any

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from src.core.database import Database
from src.core.dashboard_calculator import DashboardCalculator


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
        
        # VUE GLOBALE (3 colonnes)
        self.vue_globale_group = self._create_vue_globale()
        content_layout.addWidget(self.vue_globale_group)
        
        # ACTUALITÉ CLIENT (3 colonnes)
        self.actualite_group = self._create_actualite_client()
        content_layout.addWidget(self.actualite_group)
        
        # Actions & Deadlines
        self.deadlines_group = self._create_deadlines_section()
        content_layout.addWidget(self.deadlines_group)
        
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
        
        title = QLabel("📊 DASHBOARD")
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
    
    def _create_vue_globale(self) -> QGroupBox:
        """Vue Globale : 3 colonnes (Stats | Projets actifs par BU | Projets par CDP)."""
        group = QGroupBox("📈 VUE GLOBALE")
        main_layout = QHBoxLayout()
        
        # GAUCHE : Stats
        left_layout = QVBoxLayout()
        
        self.total_label = QLabel("Total projets : 0")
        self.total_label.setStyleSheet("font-size: 14pt; font-weight: bold; color: #2196F3; padding: 10px;")
        left_layout.addWidget(self.total_label)
        
        self.active_label = QLabel("Projets actifs : 0")
        self.active_label.setStyleSheet("font-size: 14pt; font-weight: bold; color: #4CAF50; padding: 10px;")
        left_layout.addWidget(self.active_label)
        
        self.dispositif_monthly_label = QLabel("Dispositif mensuel : 0 jours")
        self.dispositif_monthly_label.setStyleSheet("font-size: 12pt; color: #666; padding: 10px;")
        left_layout.addWidget(self.dispositif_monthly_label)
        
        self.dispositif_expandable_label = QLabel("Dispositifs augmentables : 0")
        self.dispositif_expandable_label.setStyleSheet("font-size: 12pt; color: #666; padding: 10px;")
        left_layout.addWidget(self.dispositif_expandable_label)
        
        left_layout.addStretch()
        main_layout.addLayout(left_layout, 1)
        
        # MILIEU : Graphique Projets actifs par BU
        self.chart_bu = self._create_bar_chart("Projets actifs par BU")
        main_layout.addWidget(self.chart_bu, 1)
        
        # DROITE : Graphique Projets par Chef de projet
        self.chart_manager = self._create_bar_chart("Projets par Chef de projet")
        main_layout.addWidget(self.chart_manager, 1)
        
        group.setLayout(main_layout)
        return group
    
    def _create_actualite_client(self) -> QGroupBox:
        """Actualité Client : 3 colonnes (Stats | Warnings par BU | Actions par acteur)."""
        group = QGroupBox("⚠️ ACTUALITÉ CLIENT")
        main_layout = QHBoxLayout()
        
        # GAUCHE : Stats
        left_layout = QVBoxLayout()
        
        self.warning_client_label = QLabel("Warning Vision Client (P) : 0")
        self.warning_client_label.setStyleSheet("font-size: 13pt; font-weight: bold; color: #FF9800; padding: 10px;")
        left_layout.addWidget(self.warning_client_label)
        
        self.warning_internal_label = QLabel("Warning Vision Interne (Q) : 0")
        self.warning_internal_label.setStyleSheet("font-size: 13pt; font-weight: bold; color: #FF9800; padding: 10px;")
        left_layout.addWidget(self.warning_internal_label)
        
        left_layout.addStretch()
        main_layout.addLayout(left_layout, 1)
        
        # MILIEU : Graphique Warnings par BU
        self.chart_warnings_bu = self._create_bar_chart("Warnings par BU", color='#FF9800')
        main_layout.addWidget(self.chart_warnings_bu, 1)
        
        # DROITE : Graphique Actions par acteur
        self.chart_actions = self._create_bar_chart("Actions par acteur", color='#FF9800')
        main_layout.addWidget(self.chart_actions, 1)
        
        group.setLayout(main_layout)
        return group
    
    def _create_bar_chart(self, title: str, color: str = '#2196F3') -> QWidget:
        """Crée un widget contenant un graphique à bâtons matplotlib."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Titre
        title_label = QLabel(title)
        title_label.setStyleSheet("font-weight: bold; font-size: 10pt;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Figure matplotlib
        fig = Figure(figsize=(4, 3), dpi=80)
        canvas = FigureCanvas(fig)
        canvas.setMinimumHeight(200)
        
        # Stocker la figure et le canvas pour mise à jour
        canvas.figure = fig
        canvas.chart_color = color
        
        layout.addWidget(canvas)
        
        return widget
    
    def _update_bar_chart(self, widget: QWidget, data: List[Dict[str, Any]], label_key: str, value_key: str):
        """Met à jour un graphique à bâtons."""
        # Trouver le canvas
        canvas = None
        for child in widget.children():
            if isinstance(child, FigureCanvas):
                canvas = child
                break
        
        if not canvas:
            return
        
        # Extraire les données
        if not data:
            labels = []
            values = []
        else:
            labels = [str(item[label_key]) for item in data]
            values = [item[value_key] for item in data]
        
        # Effacer et redessiner
        fig = canvas.figure
        fig.clear()
        ax = fig.add_subplot(111)
        
        if values:
            bars = ax.bar(range(len(labels)), values, color=canvas.chart_color, alpha=0.7)
            ax.set_xticks(range(len(labels)))
            ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=8)
            ax.set_ylabel('Nombre', fontsize=9)
            ax.grid(axis='y', alpha=0.3)
            
            # Afficher les valeurs sur les barres
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
        group = QGroupBox("📅 ACTIONS & DEADLINES CETTE SEMAINE")
        layout = QVBoxLayout()
        
        self.dlic_week_label = QLabel("• DLIC à traiter (non dépassée) : 0")
        layout.addWidget(self.dlic_week_label)
        
        self.dli_week_label = QLabel("• DLI à traiter (non dépassée) : 0")
        layout.addWidget(self.dli_week_label)
        
        self.dlic_overdue_label = QLabel("• DLIC dépassées : 0")
        self.dlic_overdue_label.setStyleSheet("color: #F44336; font-weight: bold;")
        layout.addWidget(self.dlic_overdue_label)
        
        self.dli_overdue_label = QLabel("• DLI dépassées : 0")
        self.dli_overdue_label.setStyleSheet("color: #F44336; font-weight: bold;")
        layout.addWidget(self.dli_overdue_label)
        
        self.dlic_empty_label = QLabel("• DLIC vides (projets actifs) : 0")
        self.dlic_empty_label.setStyleSheet("color: #FF9800;")
        layout.addWidget(self.dlic_empty_label)
        
        group.setLayout(layout)
        return group
    
    def _create_rdv_section(self) -> QGroupBox:
        group = QGroupBox("🤝 RENDEZ-VOUS CLIENT CETTE SEMAINE")
        layout = QVBoxLayout()
        
        self.rdv_count_label = QLabel("0 rendez-vous programmés")
        self.rdv_count_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.rdv_count_label)
        
        self.rdv_list = QListWidget()
        self.rdv_list.itemDoubleClicked.connect(self.on_rdv_clicked)
        layout.addWidget(self.rdv_list)
        
        group.setLayout(layout)
        return group
    
    def load_available_weeks(self):
        weeks = self.db.get_available_weeks()
        
        self.week_combo.clear()
        
        if not weeks:
            self.week_combo.addItem("Aucune donnée")
            self.week_combo.setEnabled(False)
            return
        
        self.week_combo.setEnabled(True)
        
        for week in weeks:
            self.week_combo.addItem(f"S{week} (Semaine {week})", week)
        
        if weeks:
            self.week_combo.setCurrentIndex(0)
    
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
            
            # Vue Globale - Stats
            self.total_label.setText(f"Total projets : {indicators['total_projects']}")
            self.active_label.setText(f"Projets actifs : {indicators['active_projects']}")
            self.dispositif_monthly_label.setText(f"Dispositif mensuel : {indicators['dispositif_monthly']} jours")
            self.dispositif_expandable_label.setText(f"Dispositifs augmentables : {indicators['dispositif_expandable']}")
            
            # Vue Globale - Graphique Projets actifs par BU
            bu_data = calc.get_active_projects_by_bu(self.current_week)
            self._update_bar_chart(self.chart_bu, bu_data, 'bu', 'count')
            
            # Vue Globale - Graphique Projets par Chef de projet
            managers = calc.get_projects_by_manager(self.current_week)
            self._update_bar_chart(self.chart_manager, managers, 'project_manager', 'count')
            
            # Actualité Client - Stats
            self.warning_client_label.setText(f"Warning Vision Client (P) : {indicators['warning_vision_client']}")
            self.warning_internal_label.setText(f"Warning Vision Interne (Q) : {indicators['warning_vision_internal']}")
            
            # Actualité Client - Graphique Warnings par BU
            warnings_bu = calc.get_warnings_by_bu(self.current_week)
            self._update_bar_chart(self.chart_warnings_bu, warnings_bu, 'bu', 'count')
            
            # Actualité Client - Graphique Actions par acteur
            actions = calc.get_actions_by_actor(self.current_week)
            actions_data = actions['with_actor']
            
            # Ajouter "VIDE" en rouge si nécessaire
            if actions['empty'] > 0:
                actions_data.append({'next_actor': '⚠️ VIDE', 'count': actions['empty']})
            
            self._update_bar_chart(self.chart_actions, actions_data, 'next_actor', 'count')
            
            # Deadlines
            self.dlic_week_label.setText(f"• DLIC à traiter (non dépassée) : {indicators['dlic_this_week']}")
            self.dli_week_label.setText(f"• DLI à traiter (non dépassée) : {indicators['dli_this_week']}")
            self.dlic_overdue_label.setText(f"• DLIC dépassées : {indicators['dlic_overdue']} 🔴")
            self.dli_overdue_label.setText(f"• DLI dépassées : {indicators['dli_overdue']} 🔴")
            self.dlic_empty_label.setText(f"• DLIC vides (projets actifs) : {indicators['dlic_empty']} ⚠️")
            
            # RDV Client
            rdv_list = indicators['rdv_client_this_week']
            self.rdv_count_label.setText(f"{len(rdv_list)} rendez-vous programmés")
            
            self.rdv_list.clear()
            for rdv in rdv_list:
                item_text = f"{rdv['date_formattee']} - {rdv['client_name']}"
                self.rdv_list.addItem(item_text)
                item = self.rdv_list.item(self.rdv_list.count() - 1)
                item.setData(Qt.ItemDataRole.UserRole, rdv['id_projet'])
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur : {str(e)}")
    
    def on_rdv_clicked(self, item):
        id_projet = item.data(Qt.ItemDataRole.UserRole)
        
        if id_projet and self.current_week:
            QMessageBox.information(self, "Fiche Projet", f"Fiche projet #{id_projet}\n\n(À développer)")
            self.project_clicked.emit(id_projet, self.current_week)
