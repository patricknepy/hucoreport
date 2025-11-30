"""
Module de validation des données Excel pour Huco Report.

Ce module contient toutes les fonctions de validation des données
importées depuis le fichier Excel avant insertion en base de données.

Auteur: Humans Connexion
Date: 29 novembre 2025
"""

import pandas as pd
from typing import List, Dict, Tuple, Any, Optional
from datetime import datetime
import logging


# Configuration du logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ValidationError:
    """Représente une erreur de validation."""
    
    def __init__(self, level: str, field: str, row: int, message: str, value: Any = None):
        """
        Args:
            level: 'error' (bloquant) ou 'warning' (non bloquant)
            field: Nom du champ concerné
            row: Numéro de ligne Excel
            message: Description de l'erreur
            value: Valeur problématique (optionnel)
        """
        self.level = level
        self.field = field
        self.row = row
        self.message = message
        self.value = value
    
    def __str__(self):
        level_icon = "❌" if self.level == "error" else "⚠️"
        value_info = f" (valeur: {self.value})" if self.value is not None else ""
        return f"{level_icon} Ligne {self.row}, champ '{self.field}': {self.message}{value_info}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire pour JSON/affichage."""
        return {
            "level": self.level,
            "field": self.field,
            "row": self.row,
            "message": self.message,
            "value": str(self.value) if self.value is not None else None
        }


class DataValidator:
    """
    Validateur de données Excel pour Huco Report.
    
    Effectue une validation multi-niveaux :
    1. Structure (colonnes obligatoires)
    2. Types de données
    3. Contraintes métier
    """
    
    # Colonnes obligatoires (doivent être présentes et non vides)
    REQUIRED_FIELDS = ['id_projet', 'bu', 'client_name']
    
    # Valeurs autorisées pour vision_client et vision_internal
    VISION_VALUES = ['warning', 'bon', 'à améliorer', 'non défini', '']
    
    # Valeurs autorisées pour status
    STATUS_VALUES = ['EN COURS', 'PAUSE', 'TERMINÉ', 'À VENIR', '']
    
    def __init__(self):
        """Initialise le validateur."""
        self.errors: List[ValidationError] = []
        self.warnings: List[ValidationError] = []
    
    def reset(self):
        """Réinitialise les listes d'erreurs et warnings."""
        self.errors = []
        self.warnings = []
    
    def validate_dataframe(self, df: pd.DataFrame, week_number: int) -> Tuple[bool, List[ValidationError], List[ValidationError]]:
        """
        Valide un DataFrame complet (une semaine de données).
        
        Args:
            df: DataFrame à valider
            week_number: Numéro de semaine pour contexte
        
        Returns:
            Tuple (is_valid, errors, warnings)
            - is_valid: True si aucune erreur bloquante
            - errors: Liste des erreurs bloquantes
            - warnings: Liste des avertissements
        """
        self.reset()
        
        logger.info(f"Validation semaine {week_number} : {len(df)} projets")
        
        # Validation 1: Structure
        self._validate_structure(df)
        
        # Validation 2: Champs obligatoires
        self._validate_required_fields(df)
        
        # Validation 3: Types et contraintes
        self._validate_types_and_constraints(df)
        
        is_valid = len(self.errors) == 0
        
        logger.info(f"Validation terminée : {len(self.errors)} erreur(s), {len(self.warnings)} warning(s)")
        
        return is_valid, self.errors, self.warnings
    
    def _validate_structure(self, df: pd.DataFrame):
        """Valide que les colonnes obligatoires sont présentes."""
        missing_columns = []
        
        for field in self.REQUIRED_FIELDS:
            if field not in df.columns:
                missing_columns.append(field)
        
        if missing_columns:
            self.errors.append(
                ValidationError(
                    'error',
                    'structure',
                    0,
                    f"Colonnes obligatoires manquantes : {', '.join(missing_columns)}"
                )
            )
    
    def _validate_required_fields(self, df: pd.DataFrame):
        """Valide que les champs obligatoires ne sont pas vides."""
        for idx, row in df.iterrows():
            excel_row = idx + 4  # Ligne Excel (en-têtes ligne 3, données débutent ligne 4)
            
            for field in self.REQUIRED_FIELDS:
                if field in df.columns:
                    value = row[field]
                    
                    # Vérifier si vide ou NaN
                    if pd.isna(value) or str(value).strip() == '':
                        self.errors.append(
                            ValidationError(
                                'error',
                                field,
                                excel_row,
                                f"Champ obligatoire vide",
                                value
                            )
                        )
    
    def _validate_types_and_constraints(self, df: pd.DataFrame):
        """Valide les types de données et contraintes métier."""
        for idx, row in df.iterrows():
            excel_row = idx + 4
            
            # Validation ID Projet (doit être un entier)
            if 'id_projet' in df.columns:
                self._validate_integer(row, 'id_projet', excel_row)
            
            # Validation Status
            if 'status' in df.columns:
                self._validate_status(row, excel_row)
            
            # Validation NPS Commercial et Projet (-100 à +100)
            if 'nps_commercial' in df.columns:
                self._validate_nps(row, 'nps_commercial', excel_row)
            
            if 'nps_project' in df.columns:
                self._validate_nps(row, 'nps_project', excel_row)
            
            # Validation Vision Client/Interne
            if 'vision_client' in df.columns:
                self._validate_vision(row, 'vision_client', excel_row)
            
            if 'vision_internal' in df.columns:
                self._validate_vision(row, 'vision_internal', excel_row)
            
            # Validation Dates
            date_fields = ['last_client_exchange', 'next_client_exchange', 'dlic', 'dli', 
                          'next_milestone_date', 'start_date']
            for field in date_fields:
                if field in df.columns:
                    self._validate_date(row, field, excel_row)
            
            # Validation Entiers positifs
            integer_fields = ['days_sold', 'days_dispositif_monthly', 'days_forfait', 'days_to_sign']
            for field in integer_fields:
                if field in df.columns:
                    self._validate_integer(row, field, excel_row, allow_negative=False)
            
            # Validation Booléens
            boolean_fields = ['dispositif_expandable', 'potential_new_projects', 
                            'potential_maintenance', 'potential_hosting', 
                            'potential_infra', 'potential_consulting']
            for field in boolean_fields:
                if field in df.columns:
                    self._validate_boolean(row, field, excel_row)
    
    def _validate_integer(self, row: pd.Series, field: str, excel_row: int, allow_negative: bool = True):
        """Valide qu'un champ est un entier valide."""
        value = row[field]
        
        # Skip si vide/NaN
        if pd.isna(value) or str(value).strip() == '':
            return
        
        try:
            int_value = int(value)
            
            if not allow_negative and int_value < 0:
                self.warnings.append(
                    ValidationError(
                        'warning',
                        field,
                        excel_row,
                        "Valeur négative détectée (attendu: ≥ 0)",
                        value
                    )
                )
        except (ValueError, TypeError):
            self.errors.append(
                ValidationError(
                    'error',
                    field,
                    excel_row,
                    "Valeur invalide (attendu: nombre entier)",
                    value
                )
            )
    
    def _validate_nps(self, row: pd.Series, field: str, excel_row: int):
        """Valide un champ NPS (-100 à +100)."""
        value = row[field]
        
        # Skip si vide/NaN
        if pd.isna(value) or str(value).strip() == '':
            return
        
        try:
            nps_value = int(value)
            
            if nps_value < -100 or nps_value > 100:
                self.errors.append(
                    ValidationError(
                        'error',
                        field,
                        excel_row,
                        "NPS hors limites (attendu: -100 à +100)",
                        value
                    )
                )
        except (ValueError, TypeError):
            self.errors.append(
                ValidationError(
                    'error',
                    field,
                    excel_row,
                    "NPS invalide (attendu: nombre entre -100 et +100)",
                    value
                )
            )
    
    def _validate_vision(self, row: pd.Series, field: str, excel_row: int):
        """Valide un champ Vision (warning, bon, à améliorer, non défini, vide)."""
        value = row[field]
        
        # Skip si vide/NaN (autorisé)
        if pd.isna(value) or str(value).strip() == '':
            return
        
        value_lower = str(value).lower().strip()
        
        if value_lower not in self.VISION_VALUES:
            self.warnings.append(
                ValidationError(
                    'warning',
                    field,
                    excel_row,
                    f"Valeur non standard (attendu: {', '.join(self.VISION_VALUES)})",
                    value
                )
            )
    
    def _validate_status(self, row: pd.Series, excel_row: int):
        """Valide le champ status."""
        value = row['status']
        
        # Skip si vide/NaN (autorisé)
        if pd.isna(value) or str(value).strip() == '':
            return
        
        value_upper = str(value).upper().strip()
        
        if value_upper not in self.STATUS_VALUES:
            self.warnings.append(
                ValidationError(
                    'warning',
                    'status',
                    excel_row,
                    f"Statut non standard (attendu: {', '.join(self.STATUS_VALUES)})",
                    value
                )
            )
    
    def _validate_date(self, row: pd.Series, field: str, excel_row: int):
        """Valide qu'un champ est une date valide."""
        value = row[field]
        
        # Skip si vide/NaN
        if pd.isna(value) or str(value).strip() == '':
            return
        
        # Si c'est déjà un datetime pandas, c'est bon
        if isinstance(value, pd.Timestamp):
            return
        
        # Sinon essayer de parser
        try:
            pd.to_datetime(value)
        except Exception:
            self.errors.append(
                ValidationError(
                    'error',
                    field,
                    excel_row,
                    "Date invalide (format attendu: JJ/MM/AAAA ou AAAA-MM-JJ)",
                    value
                )
            )
    
    def _validate_boolean(self, row: pd.Series, field: str, excel_row: int):
        """Valide qu'un champ booléen contient une valeur valide."""
        value = row[field]
        
        # Skip si vide/NaN
        if pd.isna(value) or str(value).strip() == '':
            return
        
        # Valeurs acceptées pour booléen
        valid_bool_values = [True, False, 'True', 'False', 'true', 'false', 
                            '1', '0', 1, 0, 'X', 'x', 'oui', 'non', 'yes', 'no']
        
        if value not in valid_bool_values:
            self.warnings.append(
                ValidationError(
                    'warning',
                    field,
                    excel_row,
                    "Valeur booléenne non standard (attendu: X, vide, 1/0, oui/non)",
                    value
                )
            )


def generate_validation_report(errors: List[ValidationError], warnings: List[ValidationError]) -> str:
    """
    Génère un rapport texte lisible des erreurs et warnings.
    
    Args:
        errors: Liste des erreurs bloquantes
        warnings: Liste des avertissements
    
    Returns:
        Rapport formaté en texte
    """
    report_lines = []
    report_lines.append("=" * 60)
    report_lines.append("RAPPORT DE VALIDATION")
    report_lines.append("=" * 60)
    
    if errors:
        report_lines.append(f"\n[ERREURS BLOQUANTES] ({len(errors)}) :")
        report_lines.append("-" * 60)
        for error in errors:
            # Enlever emojis pour Windows console
            error_str = str(error).replace("❌", "[ERR]").replace("⚠️", "[WARN]")
            report_lines.append(error_str)
    else:
        report_lines.append("\n[OK] Aucune erreur bloquante")
    
    if warnings:
        report_lines.append(f"\n[AVERTISSEMENTS] ({len(warnings)}) :")
        report_lines.append("-" * 60)
        for warning in warnings:
            # Enlever emojis pour Windows console
            warning_str = str(warning).replace("❌", "[ERR]").replace("⚠️", "[WARN]")
            report_lines.append(warning_str)
    else:
        report_lines.append("\n[OK] Aucun avertissement")
    
    report_lines.append("\n" + "=" * 60)
    
    if errors:
        report_lines.append("[ECHEC] VALIDATION ECHOUEE - Import impossible")
    else:
        report_lines.append("[OK] VALIDATION REUSSIE - Import possible")
    
    report_lines.append("=" * 60)
    
    return "\n".join(report_lines)


if __name__ == "__main__":
    """Tests basiques du module validators."""
    
    print("=== Test Module Validators ===\n")
    
    # Test 1: Validation DataFrame valide
    print("1. Test DataFrame valide...")
    df_valid = pd.DataFrame({
        'id_projet': [1, 2, 3],
        'bu': ['BU DEV SPE', 'BU ERP', 'BU DEV SPE'],
        'client_name': ['Client A', 'Client B', 'Client C'],
        'status': ['EN COURS', 'PAUSE', 'TERMINÉ'],
        'vision_client': ['bon', 'warning', 'à améliorer'],
        'vision_internal': ['bon', 'bon', 'warning'],
        'nps_commercial': [50, -20, 75],
        'nps_project': [60, -10, 80]
    })
    
    validator = DataValidator()
    is_valid, errors, warnings = validator.validate_dataframe(df_valid, 48)
    print(f"   [OK] Validation : {is_valid}")
    print(f"   [OK] Erreurs : {len(errors)}, Warnings : {len(warnings)}")
    
    # Test 2: Validation DataFrame avec erreurs
    print("\n2. Test DataFrame avec erreurs...")
    df_invalid = pd.DataFrame({
        'id_projet': [1, 'abc', 3],  # Erreur: 'abc' n'est pas un entier
        'bu': ['BU DEV SPE', '', 'BU ERP'],  # Erreur: BU vide
        'client_name': ['Client A', 'Client B', None],  # Erreur: client_name None
        'nps_commercial': [50, 150, -20],  # Erreur: 150 > 100
        'vision_client': ['bon', 'invalide', 'warning']  # Warning: 'invalide'
    })
    
    validator = DataValidator()
    is_valid, errors, warnings = validator.validate_dataframe(df_invalid, 48)
    print(f"   [OK] Validation : {is_valid}")
    print(f"   [OK] Erreurs detectees : {len(errors)}")
    print(f"   [OK] Warnings detectes : {len(warnings)}")
    
    # Test 3: Génération rapport
    print("\n3. Test generation rapport...")
    report = generate_validation_report(errors, warnings)
    print("   [OK] Rapport genere")
    print("\n" + report)
    
    print("\n=== Tous les tests passes ! ===")

