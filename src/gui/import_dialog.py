"""
Dialog de validation et simulation d'import Excel.

Affiche les résultats de validation et simulation avant l'import réel.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit, QGroupBox, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from typing import Dict, Any


class ImportDialog(QDialog):
    """Dialog affichant les résultats de validation et simulation."""
    
    def __init__(self, validation_result: Dict[str, Any], parent=None):
        """
        Initialise le dialog.
        
        Args:
            validation_result: Résultats de validate_and_simulate()
            parent: Widget parent
        """
        super().__init__(parent)
        self.validation_result = validation_result
        self.user_confirmed = False
        self.init_ui()
    
    def init_ui(self):
        """Initialise l'interface utilisateur."""
        self.setWindowTitle("Validation et Simulation d'Import")
        self.setMinimumSize(700, 600)
        
        layout = QVBoxLayout()
        
        # Titre
        title = QLabel("📊 VALIDATION ET SIMULATION D'IMPORT")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Nom du fichier
        file_label = QLabel(f"Fichier : {self.validation_result.get('file_name', 'N/A')}")
        layout.addWidget(file_label)
        
        # Zone résultats de validation
        validation_group = self._create_validation_section()
        layout.addWidget(validation_group)
        
        # Zone résultats de simulation
        if self.validation_result.get('valid', False):
            simulation_group = self._create_simulation_section()
            layout.addWidget(simulation_group)
        
        # Zone d'erreurs/warnings
        if self.validation_result.get('errors') or self.validation_result.get('warnings'):
            messages_group = self._create_messages_section()
            layout.addWidget(messages_group)
        
        # Boutons
        buttons_layout = self._create_buttons()
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
    
    def _create_validation_section(self) -> QGroupBox:
        """Crée la section validation."""
        group = QGroupBox("✓ VALIDATION DE LA STRUCTURE")
        layout = QVBoxLayout()
        
        val_result = self.validation_result.get('validation', {})
        
        if val_result.get('valid', False):
            status_label = QLabel("✅ Structure Excel VALIDE")
            status_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            status_label = QLabel("❌ Structure Excel INVALIDE")
            status_label.setStyleSheet("color: red; font-weight: bold;")
        
        layout.addWidget(status_label)
        
        # Semaines trouvées
        sheets = val_result.get('sheets_found', [])
        if sheets:
            sheets_label = QLabel(f"Onglets détectés : {', '.join(sheets)}")
            layout.addWidget(sheets_label)
        
        group.setLayout(layout)
        return group
    
    def _create_simulation_section(self) -> QGroupBox:
        """Crée la section simulation."""
        group = QGroupBox("📊 SIMULATION D'IMPORT")
        layout = QVBoxLayout()
        
        sim_result = self.validation_result.get('simulation', {})
        
        # Statistiques
        stats_layout = QVBoxLayout()
        
        total_projects = sim_result.get('total_projects', 0)
        active_projects = sim_result.get('active_projects', 0)
        weeks = sim_result.get('weeks_detected', [])
        latest_week = sim_result.get('latest_week', 'N/A')
        
        # Récupérer les indicateurs de validation
        validation = sim_result.get('validation_indicators', {})
        
        # Labels avec style - Indicateurs de validation
        title_label = QLabel(f"📊 Semaine S{latest_week} - Indicateurs de validation :")
        title_label.setStyleSheet("font-size: 11pt; font-weight: bold; margin-bottom: 10px;")
        stats_layout.addWidget(title_label)
        
        # Indicateur 1 : DLIC cette semaine
        dlic_week_label = QLabel(f"• DLIC cette semaine : {validation.get('dlic_this_week', '?')}")
        dlic_week_label.setStyleSheet("font-size: 11pt;")
        stats_layout.addWidget(dlic_week_label)
        
        # Indicateur 2 : DLIC dépassées
        dlic_overdue_label = QLabel(f"• DLIC dépassées : {validation.get('dlic_overdue', '?')}")
        dlic_overdue_label.setStyleSheet("font-size: 11pt; color: #F44336;")
        stats_layout.addWidget(dlic_overdue_label)
        
        # Indicateur 3 : Acteurs identifiés
        pct_actor = validation.get('pct_with_actor', 0)
        actifs_with_actor = validation.get('actifs_with_actor', 0)
        total_actifs = validation.get('total_actifs', 0)
        actor_label = QLabel(f"• Dossiers actifs avec acteur : {actifs_with_actor}/{total_actifs} ({pct_actor}%)")
        actor_label.setStyleSheet("font-size: 11pt; color: #4CAF50;")
        stats_layout.addWidget(actor_label)
        
        # Ligne de séparation
        stats_layout.addSpacing(10)
        
        # Info complémentaire
        active_label = QLabel(f"✅ {active_projects} projets actifs détectés (S{latest_week})")
        active_label.setStyleSheet("font-size: 10pt; color: #666;")
        stats_layout.addWidget(active_label)
        
        weeks_label = QLabel(f"📅 Semaines : {len(weeks)} ({', '.join(['S' + str(w) for w in weeks])})")
        stats_layout.addWidget(weeks_label)
        
        latest_label = QLabel(f"📍 Dernière semaine : S{latest_week}")
        stats_layout.addWidget(latest_label)
        
        layout.addLayout(stats_layout)
        
        group.setLayout(layout)
        return group
    
    def _create_messages_section(self) -> QGroupBox:
        """Crée la section erreurs/warnings."""
        group = QGroupBox("⚠️ MESSAGES")
        layout = QVBoxLayout()
        
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setMaximumHeight(150)
        
        messages = []
        
        # Erreurs
        errors = self.validation_result.get('errors', [])
        if errors:
            messages.append("❌ ERREURS :\n")
            for err in errors:
                messages.append(f"  • {err}\n")
            messages.append("\n")
        
        # Warnings
        warnings = self.validation_result.get('warnings', [])
        if warnings:
            messages.append("⚠️ AVERTISSEMENTS :\n")
            for warn in warnings[:10]:  # Limiter à 10 warnings
                messages.append(f"  • {warn}\n")
            if len(warnings) > 10:
                messages.append(f"  ... et {len(warnings) - 10} autres avertissements\n")
        
        text_edit.setPlainText(''.join(messages))
        layout.addWidget(text_edit)
        
        group.setLayout(layout)
        return group
    
    def _create_buttons(self) -> QHBoxLayout:
        """Crée les boutons d'action."""
        layout = QHBoxLayout()
        layout.addStretch()
        
        # Bouton Annuler (toujours présent)
        cancel_btn = QPushButton("🔴 Annuler l'opération")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
                color: white;
                padding: 10px 20px;
                font-weight: bold;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #D32F2F;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        layout.addWidget(cancel_btn)
        
        # Bouton Confirmer (seulement si validation OK)
        if self.validation_result.get('valid', False):
            confirm_btn = QPushButton("🟢 Confirmer l'import")
            confirm_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    padding: 10px 20px;
                    font-weight: bold;
                    border: none;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #45A049;
                }
            """)
            confirm_btn.clicked.connect(self.confirm_import)
            layout.addWidget(confirm_btn)
        
        return layout
    
    def confirm_import(self):
        """L'utilisateur confirme l'import."""
        # Récupérer les indicateurs
        sim_result = self.validation_result.get('simulation', {})
        validation = sim_result.get('validation_indicators', {})
        latest_week = sim_result.get('latest_week', 'N/A')
        
        # Demander une dernière confirmation
        reply = QMessageBox.question(
            self,
            "Confirmation d'import",
            f"📊 Confirmation d'import\n\n"
            f"Semaine : S{latest_week}\n"
            f"• DLIC cette semaine : {validation.get('dlic_this_week', '?')}\n"
            f"• DLIC dépassées : {validation.get('dlic_overdue', '?')}\n"
            f"• Acteurs identifiés : {validation.get('pct_with_actor', 0)}%\n\n"
            f"Si ces valeurs vous semblent cohérentes,\n"
            f"vous pouvez confirmer l'import.\n\n"
            f"ℹ️ La base de données sera mise à jour avec ces nouvelles données.\n\n"
            f"Confirmer ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.user_confirmed = True
            self.accept()
    
    def is_confirmed(self) -> bool:
        """Retourne True si l'utilisateur a confirmé l'import."""
        return self.user_confirmed

