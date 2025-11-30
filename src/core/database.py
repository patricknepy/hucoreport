"""
Gestion de la base de données SQLite pour Huco Report.

Ce module gère :
- Création et connexion à la base de données
- Création des tables et index
- Opérations CRUD sur les projets
- Requêtes pour le dashboard et les rapports
"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime
import logging
import sys
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_application_path():
    """Retourne le chemin de base de l'application (compatible .exe)."""
    if getattr(sys, 'frozen', False):
        # Mode .exe (PyInstaller)
        return Path(sys.executable).parent
    else:
        # Mode développement
        return Path(__file__).parent.parent.parent


class Database:
    """Gestionnaire de base de données SQLite pour Huco Report."""
    
    def __init__(self, db_path: str = "data/cache.db"):
        """
        Initialise la connexion à la base de données.
        
        Args:
            db_path: Chemin vers le fichier de base de données
        """
        # Utiliser un chemin absolu basé sur l'emplacement de l'exe
        app_path = get_application_path()
        self.db_path = app_path / db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn: Optional[sqlite3.Connection] = None
        self._connect()
        self._create_tables()
    
    def _connect(self):
        """Établit la connexion à la base de données."""
        try:
            self.conn = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
            )
            self.conn.row_factory = sqlite3.Row
            logger.info(f"Connexion a la base : {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Erreur connexion base : {e}")
            raise
    
    def _create_tables(self):
        """Crée les tables et index si elles n'existent pas."""
        cursor = self.conn.cursor()
        
        try:
            # Table projects
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS projects (
                    -- MÉTADONNÉES AUTO-GÉNÉRÉES
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    week_number INTEGER NOT NULL,
                    import_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    
                    -- GROUPE 1 : IDENTIFICATION PROJET (12 champs)
                    id_projet INTEGER NOT NULL,
                    status TEXT CHECK(status IN ('EN COURS', 'PAUSE', 'TERMINÉ', 'À VENIR', '')),
                    bu TEXT NOT NULL,
                    client_name TEXT NOT NULL,
                    description TEXT,
                    project_manager TEXT,
                    technical_lead TEXT,
                    project_director TEXT,
                    project_phase TEXT,
                    contract_type TEXT,
                    project_code TEXT,
                    days_sold INTEGER,
                    
                    -- GROUPE 2 : NPS (2 champs)
                    nps_commercial INTEGER CHECK(nps_commercial BETWEEN -100 AND 100 OR nps_commercial IS NULL),
                    nps_project INTEGER CHECK(nps_project BETWEEN -100 AND 100 OR nps_project IS NULL),
                    
                    -- GROUPE 3 : PILOTAGE (9 champs)
                    vision_client TEXT,
                    vision_internal TEXT,
                    risk_identified TEXT,
                    action_description TEXT,
                    next_actor TEXT,
                    last_client_exchange DATE,
                    next_client_exchange DATE,
                    dlic DATE,
                    dli DATE,
                    
                    -- GROUPE 4 : ACTUALITÉS (3 champs)
                    news_project TEXT,
                    news_commercial TEXT,
                    news_technical TEXT,
                    
                    -- GROUPE 5 : PLANIFICATION & REMARQUES (7 champs)
                    data_remarks TEXT,
                    next_milestone_date DATE,
                    next_milestone_object TEXT,
                    remarks_3months TEXT,
                    remarks_6months TEXT,
                    remarks_1year TEXT,
                    commercial_production_goal TEXT,
                    
                    -- GROUPE 6 : COMMERCIAL & PRODUCTION (5 champs)
                    days_dispositif_monthly INTEGER,
                    dispositif_expandable TEXT,
                    days_forfait INTEGER,
                    days_to_sign INTEGER,
                    start_date DATE,
                    
                    -- GROUPE 7 : POTENTIEL COMMERCIAL AVENIR (5 champs)
                    potential_new_projects BOOLEAN DEFAULT 0,
                    potential_maintenance BOOLEAN DEFAULT 0,
                    potential_hosting BOOLEAN DEFAULT 0,
                    potential_infra BOOLEAN DEFAULT 0,
                    potential_consulting BOOLEAN DEFAULT 0,
                    
                    -- CONTRAINTES
                    UNIQUE(id_projet, week_number)
                )
            ''')
            
            # Index pour performance
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_week_number ON projects(week_number)",
                "CREATE INDEX IF NOT EXISTS idx_status ON projects(status)",
                "CREATE INDEX IF NOT EXISTS idx_client_name ON projects(client_name)",
                "CREATE INDEX IF NOT EXISTS idx_next_actor ON projects(next_actor)",
                "CREATE INDEX IF NOT EXISTS idx_dlic ON projects(dlic)",
                "CREATE INDEX IF NOT EXISTS idx_dli ON projects(dli)",
                "CREATE INDEX IF NOT EXISTS idx_import_date ON projects(import_date)",
                "CREATE INDEX IF NOT EXISTS idx_week_status ON projects(week_number, status)",
                "CREATE INDEX IF NOT EXISTS idx_week_client ON projects(week_number, client_name)"
            ]
            
            for index_sql in indexes:
                cursor.execute(index_sql)
            
            self.conn.commit()
            logger.info("Tables et index crees/verifies")
            
        except sqlite3.Error as e:
            logger.error(f"Erreur creation tables : {e}")
            raise
    
    def clear_all(self):
        """Vide complètement la table projects (utilisé avant chaque import)."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM projects")
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='projects'")
            self.conn.commit()
            logger.info("Base de donnees videe")
        except sqlite3.Error as e:
            logger.error(f"Erreur vidage base : {e}")
            raise
    
    def insert_project(self, project_data: Dict[str, Any]):
        """
        Insère un projet dans la base de données.
        
        Args:
            project_data: Dictionnaire contenant les données du projet
        """
        try:
            cursor = self.conn.cursor()
            
            columns = ', '.join(project_data.keys())
            placeholders = ', '.join(['?' for _ in project_data])
            values = tuple(project_data.values())
            
            query = f"INSERT INTO projects ({columns}) VALUES ({placeholders})"
            cursor.execute(query, values)
            
        except sqlite3.Error as e:
            logger.error(f"Erreur insertion projet : {e}")
            raise
    
    def insert_projects_batch(self, projects: List[Dict[str, Any]]):
        """
        Insère plusieurs projets en une seule transaction.
        
        Args:
            projects: Liste de dictionnaires de projets
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("BEGIN TRANSACTION")
            
            for project in projects:
                self.insert_project(project)
            
            cursor.execute("COMMIT")
            logger.info(f"{len(projects)} projets inseres")
            
        except sqlite3.Error as e:
            cursor.execute("ROLLBACK")
            logger.error(f"Erreur insertion batch : {e}")
            raise
    
    def get_available_weeks(self) -> List[int]:
        """Récupère la liste des semaines disponibles en base."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT DISTINCT week_number FROM projects ORDER BY week_number DESC"
            )
            rows = cursor.fetchall()
            return [row[0] for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Erreur recuperation semaines : {e}")
            raise
    
    def execute_scalar(self, query: str, params: Tuple = ()) -> Any:
        """Exécute une requête qui retourne une seule valeur."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            result = cursor.fetchone()
            return result[0] if result else None
        except sqlite3.Error as e:
            logger.error(f"Erreur execution scalar : {e}")
            raise
    
    def count_total_projects(self, week_number: int) -> int:
        """Compte le nombre total de projets pour une semaine."""
        return self.execute_scalar(
            "SELECT COUNT(*) FROM projects WHERE week_number = ?",
            (week_number,)
        ) or 0
    
    def count_active_projects(self, week_number: int) -> int:
        """Compte le nombre de projets actifs pour une semaine."""
        return self.execute_scalar(
            "SELECT COUNT(*) FROM projects WHERE week_number = ? AND status = 'EN COURS'",
            (week_number,)
        ) or 0
    
    def close(self):
        """Ferme la connexion à la base de données."""
        if self.conn:
            self.conn.close()
            logger.info("Connexion base fermee")

