"""
Orchestration complète de l'import Excel.

Ce module coordonne :
1. Validation de la structure Excel
2. Simulation de l'import avec statistiques
3. Import réel dans la base de données
4. Sauvegarde du fichier Excel avec date/heure
"""

from pathlib import Path
from typing import Dict, Any
from datetime import datetime
import shutil
import logging
import sys

from .excel_validator import ExcelValidator
from .excel_parser import ExcelParser
from .database import Database

logger = logging.getLogger(__name__)


def get_application_path():
    """Retourne le chemin de base de l'application (compatible .exe)."""
    if getattr(sys, 'frozen', False):
        # Mode .exe (PyInstaller)
        return Path(sys.executable).parent
    else:
        # Mode développement
        return Path(__file__).parent.parent.parent


class ExcelImporter:
    """Gestionnaire complet de l'import Excel."""
    
    def __init__(
        self,
        schema_path: str = "config/excel_schema.json",
        db_path: str = "data/cache.db"
    ):
        """
        Initialise l'importeur.
        
        Args:
            schema_path: Chemin vers le schéma de référence
            db_path: Chemin vers la base de données
        """
        self.validator = ExcelValidator(schema_path)
        self.parser = ExcelParser(schema_path)
        self.db = Database(db_path)
    
    def validate_and_simulate(self, excel_path: str) -> Dict[str, Any]:
        """
        Étape 1+2 : Valide la structure PUIS simule l'import.
        
        Args:
            excel_path: Chemin vers le fichier Excel
            
        Returns:
            Dictionnaire avec résultats complets
        """
        result = {
            "step": "validation_and_simulation",
            "valid": True,
            "file_path": str(Path(excel_path)),
            "file_name": Path(excel_path).name,
            "validation": {},
            "simulation": {},
            "errors": [],
            "warnings": []
        }
        
        logger.info("=" * 60)
        logger.info("ETAPE 1 : VALIDATION DE LA STRUCTURE")
        logger.info("=" * 60)
        
        # 1. VALIDATION
        validation_result = self.validator.validate_structure(excel_path)
        result['validation'] = validation_result
        
        if not validation_result['valid']:
            result['valid'] = False
            result['errors'].extend(validation_result['errors'])
            result['warnings'].extend(validation_result['warnings'])
            logger.error("Validation ECHOUEE - Import impossible")
            return result
        
        logger.info("Validation REUSSIE")
        result['warnings'].extend(validation_result['warnings'])
        
        # 2. SIMULATION
        logger.info("=" * 60)
        logger.info("ETAPE 2 : SIMULATION DE L'IMPORT")
        logger.info("=" * 60)
        
        simulation_result = self.parser.simulate_import(excel_path)
        result['simulation'] = simulation_result
        
        if not simulation_result['valid']:
            result['valid'] = False
            result['errors'].extend(simulation_result['errors'])
            result['warnings'].extend(simulation_result['warnings'])
            logger.error("Simulation ECHOUEE - Import impossible")
            return result
        
        logger.info("Simulation REUSSIE")
        result['warnings'].extend(simulation_result['warnings'])
        
        # 3. RÉCAPITULATIF
        logger.info("=" * 60)
        logger.info("RECAPITULATIF")
        logger.info("=" * 60)
        logger.info(f"Fichier : {result['file_name']}")
        logger.info(f"Semaines detectees : {simulation_result['weeks_detected']}")
        logger.info(f"Derniere semaine : S{simulation_result['latest_week']}")
        logger.info(f"Total projets : {simulation_result['total_projects']}")
        logger.info(f"Projets actifs (S{simulation_result['latest_week']}) : {simulation_result['active_projects']}")
        logger.info(f"Erreurs : {len(result['errors'])}")
        logger.info(f"Warnings : {len(result['warnings'])}")
        logger.info("=" * 60)
        
        return result
    
    def execute_import(self, excel_path: str) -> Dict[str, Any]:
        """
        Étape 3 : Import RÉEL dans la base de données.
        
        Cette fonction doit être appelée APRÈS validate_and_simulate().
        
        Args:
            excel_path: Chemin vers le fichier Excel
            
        Returns:
            Dictionnaire avec résultats de l'import
        """
        result = {
            "step": "import",
            "success": True,
            "file_saved_as": None,
            "projects_imported": 0,
            "weeks_imported": [],
            "errors": [],
            "warnings": []
        }
        
        logger.info("=" * 60)
        logger.info("ETAPE 3 : IMPORT REEL EN BASE DE DONNEES")
        logger.info("=" * 60)
        
        try:
            # 1. Sauvegarder le fichier Excel avec date/heure
            logger.info("Sauvegarde du fichier Excel...")
            saved_file = self._save_excel_file(excel_path)
            result['file_saved_as'] = str(saved_file)
            logger.info(f"Fichier sauvegarde : {saved_file.name}")
            
            # 2. Récupérer les données parsées
            parsed_data = self.parser.get_parsed_data()
            
            if not parsed_data:
                raise ValueError("Aucune donnee parsee. Appelez validate_and_simulate() d'abord.")
            
            # 3. VIDER LA BASE DE DONNÉES
            logger.info("Vidage complet de la base de donnees...")
            self.db.clear_all()
            logger.info("Base videe")
            
            # 4. INSÉRER TOUTES LES DONNÉES
            logger.info("Insertion des projets...")
            
            for week, projects in parsed_data.items():
                logger.info(f"  - Semaine {week} : {len(projects)} projets")
                self.db.insert_projects_batch(projects)
                result['weeks_imported'].append(week)
                result['projects_imported'] += len(projects)
            
            logger.info(f"Import termine : {result['projects_imported']} projets sur {len(result['weeks_imported'])} semaines")
            logger.info("=" * 60)
            
        except Exception as e:
            result['success'] = False
            result['errors'].append(f"Erreur lors de l'import : {str(e)}")
            logger.error(f"ECHEC DE L'IMPORT : {e}")
            logger.exception(e)
        
        return result
    
    def _save_excel_file(self, excel_path: str) -> Path:
        """
        Sauvegarde le fichier Excel avec date/heure.
        
        Args:
            excel_path: Chemin vers le fichier Excel
            
        Returns:
            Path vers le fichier sauvegardé
        """
        source = Path(excel_path)
        app_path = get_application_path()
        import_dir = app_path / "import"
        import_dir.mkdir(exist_ok=True)
        
        # Générer nom avec date/heure : Suivi_Hebdo_AAAAMMJJ_HHMM.xlsx
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        new_name = f"Suivi_Hebdo_{timestamp}.xlsx"
        destination = import_dir / new_name
        
        # Copier le fichier
        shutil.copy2(source, destination)
        
        return destination
    
    def full_import_workflow(self, excel_path: str) -> Dict[str, Any]:
        """
        Workflow complet : Validation + Simulation + Import.
        
        Cette fonction réalise les 3 étapes d'un coup.
        
        Args:
            excel_path: Chemin vers le fichier Excel
            
        Returns:
            Dictionnaire avec tous les résultats
        """
        result = {
            "workflow": "complete",
            "success": False,
            "validation_simulation": {},
            "import": {},
            "errors": [],
            "warnings": []
        }
        
        # Étapes 1+2 : Validation + Simulation
        val_sim_result = self.validate_and_simulate(excel_path)
        result['validation_simulation'] = val_sim_result
        
        if not val_sim_result['valid']:
            result['errors'] = val_sim_result['errors']
            result['warnings'] = val_sim_result['warnings']
            return result
        
        # Étape 3 : Import réel
        import_result = self.execute_import(excel_path)
        result['import'] = import_result
        
        if not import_result['success']:
            result['errors'].extend(import_result['errors'])
            result['warnings'].extend(import_result['warnings'])
            return result
        
        # Succès complet
        result['success'] = True
        result['warnings'].extend(val_sim_result['warnings'])
        result['warnings'].extend(import_result['warnings'])
        
        return result
    
    def close(self):
        """Ferme les connexions."""
        self.parser.close()
        self.db.close()
