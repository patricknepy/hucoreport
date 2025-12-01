"""
Lecture et parsing du fichier Excel.

Ce module lit les données du fichier Excel, les valide et prépare
la simulation d'import.
"""

import openpyxl
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, date, timedelta
import re
import logging
import json
import sys

from .paths import get_application_path

logger = logging.getLogger(__name__)


class ExcelParser:
    """Parser de fichier Excel Suivi Hebdo Projet."""
    
    def __init__(self, schema_path: str = "config/excel_schema.json"):
        """
        Initialise le parser avec le schéma.
        
        Args:
            schema_path: Chemin vers le fichier JSON du schéma
        """
        # Utiliser un chemin absolu basé sur l'emplacement de l'exe
        app_path = get_application_path()
        self.schema_path = app_path / schema_path
        self.schema = self._load_schema()
        self.workbook = None
        self.file_path = None
    
    def _load_schema(self) -> Dict:
        """Charge le schéma JSON."""
        with open(self.schema_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_file(self, excel_path: str):
        """
        Charge le fichier Excel.
        
        Args:
            excel_path: Chemin vers le fichier Excel
        """
        self.file_path = Path(excel_path)
        self.workbook = openpyxl.load_workbook(excel_path, data_only=True)
        logger.info(f"📂 Fichier chargé : {self.file_path.name}")
    
    def get_available_weeks(self) -> List[int]:
        """
        Retourne la liste des semaines disponibles dans le fichier.
        
        Returns:
            Liste de numéros de semaines (ex: [45, 46, 47, 48])
        """
        if not self.workbook:
            return []
        
        sheet_pattern = re.compile(self.schema['sheet_pattern'])
        weeks = []
        
        for sheet_name in self.workbook.sheetnames:
            if sheet_pattern.match(sheet_name):
                week_num = int(sheet_name[1:])  # S48 → 48
                weeks.append(week_num)
        
        return sorted(weeks)
    
    def _convert_to_boolean(self, value: Any) -> bool:
        """
        Convertit une valeur Excel en booléen.
        
        Args:
            value: Valeur Excel (X, x, vide, etc.)
            
        Returns:
            True si X/x, False sinon
        """
        if value is None or value == '':
            return False
        
        if isinstance(value, str):
            return value.strip().upper() == 'X'
        
        return bool(value)
    
    def _convert_to_date(self, value: Any) -> Optional[str]:
        """
        Convertit une valeur Excel en date ISO (YYYY-MM-DD).
        
        Gère plusieurs formats :
        - Date complète : JJ/MM/AAAA, AAAA-MM-JJ
        - Mois seul : 2025-11, Novembre 2025 → dernier jour du mois
        - Semaine : S48, semaine 48 → dernier jour (dimanche)
        
        Args:
            value: Valeur Excel (datetime, str, etc.)
            
        Returns:
            Date au format ISO ou None
        """
        if value is None or value == '':
            return None
        
        # Si déjà un objet datetime
        if isinstance(value, datetime):
            return value.date().isoformat()
        
        if isinstance(value, date):
            return value.isoformat()
        
        # Si string, essayer de parser
        if isinstance(value, str):
            value_clean = value.strip()
            
            # 1. Formats de date complète
            for fmt in ['%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y', '%d/%m/%y']:
                try:
                    dt = datetime.strptime(value_clean, fmt)
                    return dt.date().isoformat()
                except ValueError:
                    continue
            
            # 2. Format MOIS seul : "2025-11" ou "11/2025"
            # → Retourner le dernier jour du mois
            for fmt in ['%Y-%m', '%m/%Y']:
                try:
                    dt = datetime.strptime(value_clean, fmt)
                    # Calculer le dernier jour du mois
                    if dt.month == 12:
                        last_day = date(dt.year, 12, 31)
                    else:
                        last_day = date(dt.year, dt.month + 1, 1) - timedelta(days=1)
                    return last_day.isoformat()
                except ValueError:
                    continue
            
            # 3. Format SEMAINE : "S48", "semaine 48", "sem 48"
            # → Retourner le dimanche de cette semaine
            week_match = re.match(r'^[Ss]?(?:emaine\s*)?(\d{1,2})$', value_clean)
            if week_match:
                week_num = int(week_match.group(1))
                # Calculer le dimanche de cette semaine
                # (On suppose l'année en cours)
                current_year = datetime.now().year
                
                # Premier jour de l'année
                jan_1 = date(current_year, 1, 1)
                
                # Trouver le premier lundi de l'année
                days_to_monday = (7 - jan_1.weekday()) % 7
                if days_to_monday == 0 and jan_1.weekday() != 0:
                    days_to_monday = 7
                first_monday = jan_1 + timedelta(days=days_to_monday)
                
                # Calculer le dimanche de la semaine N
                target_week_start = first_monday + timedelta(weeks=week_num - 1)
                sunday = target_week_start + timedelta(days=6)
                
                return sunday.isoformat()
            
            # 4. Mois en texte : "Novembre 2025", "Nov 2025"
            mois_fr = {
                'janvier': 1, 'jan': 1,
                'février': 2, 'fev': 2, 'fevrier': 2,
                'mars': 3, 'mar': 3,
                'avril': 4, 'avr': 4,
                'mai': 5,
                'juin': 6,
                'juillet': 7, 'juil': 7,
                'août': 8, 'aout': 8,
                'septembre': 9, 'sep': 9, 'sept': 9,
                'octobre': 10, 'oct': 10,
                'novembre': 11, 'nov': 11,
                'décembre': 12, 'dec': 12, 'decembre': 12
            }
            
            for mois_nom, mois_num in mois_fr.items():
                pattern = rf'{mois_nom}\s*(\d{{4}})'
                match = re.search(pattern, value_clean.lower())
                if match:
                    year = int(match.group(1))
                    # Dernier jour du mois
                    if mois_num == 12:
                        last_day = date(year, 12, 31)
                    else:
                        last_day = date(year, mois_num + 1, 1) - timedelta(days=1)
                    return last_day.isoformat()
        
        logger.warning(f"⚠️ Impossible de convertir en date : {value}")
        return None
    
    def _convert_to_integer(self, value: Any) -> Optional[int]:
        """
        Convertit une valeur Excel en entier.
        
        Args:
            value: Valeur Excel
            
        Returns:
            Entier ou None
        """
        if value is None or value == '':
            return None
        
        try:
            # Si c'est un float, arrondir
            if isinstance(value, float):
                return int(round(value))
            
            # Si c'est un str, vérifier d'abord les erreurs Excel
            if isinstance(value, str):
                value_stripped = value.strip()
                if value_stripped == '':
                    return None
                # Détecter les erreurs Excel (#VALUE!, #REF!, #N/A, etc.)
                if value_stripped.startswith('#') and ('!' in value_stripped or value_stripped == '#N/A'):
                    logger.warning(f"⚠️ Erreur Excel détectée : {value_stripped}. La cellule contient une formule invalide. Veuillez corriger le fichier Excel.")
                    return None
                return int(float(value_stripped))
            
            return int(value)
        except (ValueError, TypeError):
            logger.warning(f"⚠️ Impossible de convertir en entier : {value}")
            return None
    
    def _convert_to_text(self, value: Any) -> Optional[str]:
        """
        Convertit une valeur Excel en texte.
        
        Args:
            value: Valeur Excel
            
        Returns:
            Texte ou None
        """
        if value is None or value == '':
            return None
        
        return str(value).strip()
    
    def _normalize_status(self, value: Any) -> Optional[str]:
        """
        Normalise les statuts de projet.
        
        Mapping:
        - "Actif" → "EN COURS"
        - "Pause" → "PAUSE"
        - "Non Actif" → "TERMINÉ"
        - "À Venir" → "À VENIR"
        
        Args:
            value: Valeur Excel du statut
            
        Returns:
            Statut normalisé
        """
        if value is None or value == '':
            return None
        
        status_mapping = {
            'actif': 'EN COURS',
            'pause': 'PAUSE',
            'non actif': 'TERMINÉ',
            'à venir': 'À VENIR',
            'terminé': 'TERMINÉ',
            'en cours': 'EN COURS'
        }
        
        normalized = str(value).strip().lower()
        return status_mapping.get(normalized, str(value).strip())
    
    def _convert_value(self, value: Any, expected_type: str) -> Any:
        """
        Convertit une valeur selon le type attendu.
        
        Args:
            value: Valeur Excel
            expected_type: Type attendu (INTEGER, DATE, TEXT, BOOLEAN)
            
        Returns:
            Valeur convertie
        """
        if expected_type == 'INTEGER':
            return self._convert_to_integer(value)
        elif expected_type == 'DATE':
            return self._convert_to_date(value)
        elif expected_type == 'BOOLEAN':
            return self._convert_to_boolean(value)
        elif expected_type == 'TEXT':
            return self._convert_to_text(value)
        else:
            return value
    
    def parse_sheet(self, week_number: int) -> List[Dict[str, Any]]:
        """
        Parse un onglet de semaine et extrait les projets.
        
        Args:
            week_number: Numéro de semaine (ex: 48)
            
        Returns:
            Liste de dictionnaires représentant les projets
        """
        if not self.workbook:
            raise ValueError("Aucun fichier chargé. Appelez load_file() d'abord.")
        
        sheet_name = f"S{week_number}"
        
        if sheet_name not in self.workbook.sheetnames:
            raise ValueError(f"Onglet {sheet_name} introuvable")
        
        ws = self.workbook[sheet_name]
        projects = []
        
        header_row = self.schema['header_row']
        data_start = self.schema['data_start_row']
        data_end = self.schema['data_end_row']
        
        # Créer le mapping colonne → db_field
        column_mapping = {}
        for col_letter, col_schema in self.schema['columns'].items():
            if col_schema.get('db_field') and not col_schema.get('ignored', False):
                column_mapping[col_letter] = {
                    'db_field': col_schema['db_field'],
                    'type': col_schema.get('type', 'TEXT')
                }
        
        # Lire les lignes de données
        for row_idx in range(data_start, data_end + 1):
            project = {'week_number': week_number}
            
            # Lire chaque colonne
            for col_letter, col_info in column_mapping.items():
                col_idx = openpyxl.utils.column_index_from_string(col_letter)
                cell_value = ws.cell(row=row_idx, column=col_idx).value
                
                db_field = col_info['db_field']
                expected_type = col_info['type']
                
                # Normaliser statut (colonne B)
                if db_field == 'status':
                    converted_value = self._normalize_status(cell_value)
                else:
                    # Convertir la valeur
                    converted_value = self._convert_value(cell_value, expected_type)
                
                project[db_field] = converted_value
            
            # Vérifier APRÈS conversion que les champs obligatoires sont valides
            id_projet = project.get('id_projet')
            bu = project.get('bu')
            client_name = project.get('client_name')
            
            # Si un des 3 champs obligatoires est None ou vide, on ignore la ligne
            # (On vérifie après conversion car la conversion peut transformer des valeurs)
            if id_projet is None:
                continue
            if bu is None or (isinstance(bu, str) and not bu.strip()):
                continue
            if client_name is None or (isinstance(client_name, str) and not client_name.strip()):
                continue
            
            projects.append(project)
        
        logger.info(f"📊 Onglet {sheet_name} : {len(projects)} projets parsés")
        return projects
    
    def parse_all_weeks(self) -> Dict[int, List[Dict[str, Any]]]:
        """
        Parse toutes les semaines disponibles.
        
        Returns:
            Dict {week_number: [projects]}
        """
        all_data = {}
        weeks = self.get_available_weeks()
        
        for week in weeks:
            projects = self.parse_sheet(week)
            all_data[week] = projects
        
        total_projects = sum(len(projects) for projects in all_data.values())
        logger.info(f"📊 Total : {total_projects} projets sur {len(weeks)} semaines")
        
        return all_data
    
    def simulate_import(self, excel_path: str) -> Dict[str, Any]:
        """
        Simule l'import complet du fichier Excel.
        
        Cette fonction :
        1. Charge le fichier
        2. Parse toutes les semaines
        3. Calcule des statistiques
        4. Valide les données
        
        Args:
            excel_path: Chemin vers le fichier Excel
            
        Returns:
            Dictionnaire avec résultats de simulation
        """
        result = {
            "valid": True,
            "file_name": Path(excel_path).name,
            "file_path": str(Path(excel_path)),
            "weeks_detected": [],
            "total_projects": 0,
            "active_projects": 0,
            "projects_by_week": {},
            "errors": [],
            "warnings": []
        }
        
        try:
            # 1. Charger le fichier
            self.load_file(excel_path)
            
            # 2. Détecter les semaines
            weeks = self.get_available_weeks()
            result['weeks_detected'] = weeks
            result['latest_week'] = max(weeks) if weeks else None
            
            if not weeks:
                result['valid'] = False
                result['errors'].append("❌ Aucune semaine détectée dans le fichier")
                return result
            
            # 3. Parser toutes les semaines
            all_data = self.parse_all_weeks()
            
            # 4. Calculer statistiques
            for week, projects in all_data.items():
                result['projects_by_week'][week] = len(projects)
                result['total_projects'] += len(projects)
                
                # Compter projets actifs (dernière semaine uniquement)
                if week == result['latest_week']:
                    active_count = sum(1 for p in projects if p.get('status') == 'EN COURS')
                    result['active_projects'] = active_count
            
            # 5. Calculer indicateurs de validation (dernière semaine uniquement)
            latest_projects = all_data[result['latest_week']]
            
            # Compter DLIC cette semaine et dépassées
            from datetime import datetime, timedelta
            today = datetime.now().date()
            week_start = today - timedelta(days=today.weekday())  # Lundi
            week_end = week_start + timedelta(days=6)  # Dimanche
            
            dlic_this_week = 0
            dlic_overdue = 0
            actifs_with_actor = 0
            total_actifs = 0
            
            for project in latest_projects:
                status = project.get('status')
                dlic = project.get('dlic')
                next_actor = project.get('next_actor')
                vision_client = str(project.get('vision_client', '')).upper()
                vision_internal = str(project.get('vision_internal', '')).upper()
                
                # Compter projets actifs
                if status == 'EN COURS':
                    total_actifs += 1
                    
                    # Acteur identifié (sur TOUS les actifs)
                    if next_actor and next_actor.strip():
                        actifs_with_actor += 1
                    
                    # DLIC cette semaine
                    if dlic:
                        try:
                            from datetime import date
                            if isinstance(dlic, str):
                                dlic_date = date.fromisoformat(dlic)
                            else:
                                dlic_date = dlic
                            
                            # DLIC dans la semaine
                            if week_start <= dlic_date <= week_end:
                                dlic_this_week += 1
                            
                            # DLIC dépassée
                            if dlic_date < today:
                                dlic_overdue += 1
                        except:
                            pass
                    
            # Calculer pourcentage (actifs avec acteur / total actifs)
            pct_with_actor = round((actifs_with_actor / total_actifs * 100) if total_actifs > 0 else 0, 1)
            
            # Stocker dans result
            result['validation_indicators'] = {
                'dlic_this_week': dlic_this_week,
                'dlic_overdue': dlic_overdue,
                'actifs_with_actor': actifs_with_actor,
                'total_actifs': total_actifs,
                'pct_with_actor': pct_with_actor
            }
            
            # 6. Stocker les données pour import ultérieur
            self.parsed_data = all_data
            
            logger.info(f"✅ Simulation terminée : {result['total_projects']} projets, {len(weeks)} semaines")
            
        except Exception as e:
            result['valid'] = False
            result['errors'].append(f"❌ Erreur lors de la simulation : {str(e)}")
            logger.exception(e)
        
        return result
    
    def get_parsed_data(self) -> Optional[Dict[int, List[Dict[str, Any]]]]:
        """
        Retourne les données parsées (après simulate_import).
        
        Returns:
            Dict {week_number: [projects]} ou None
        """
        return getattr(self, 'parsed_data', None)
    
    def close(self):
        """Ferme le fichier Excel."""
        if self.workbook:
            self.workbook.close()
            self.workbook = None
            logger.info("📂 Fichier Excel fermé")

