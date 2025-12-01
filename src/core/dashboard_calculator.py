"""
Calculs des indicateurs pour le dashboard.

Ce module calcule tous les KPIs et statistiques affichés sur le dashboard.
"""

from typing import Dict, List, Any
import logging

from .database import Database

logger = logging.getLogger(__name__)


class DashboardCalculator:
    """Calculateur d'indicateurs pour le dashboard."""
    
    def __init__(self, db: Database = None):
        """
        Initialise le calculateur.
        
        Args:
            db: Instance de Database (si None, en crée une nouvelle)
        """
        self.db = db if db else Database()
    
    def get_all_indicators(self, week_number: int) -> Dict[str, Any]:
        """
        Calcule tous les indicateurs pour une semaine donnée.
        
        Args:
            week_number: Numéro de semaine (ex: 48)
            
        Returns:
            Dictionnaire avec tous les indicateurs
        """
        logger.info(f"Calcul des indicateurs pour S{week_number}")
        
        indicators = {
            "week": week_number,
            "total_projects": self._count_total(week_number),
            "active_projects": self._count_active(week_number),
            "dispositif_monthly": self._sum_dispositif_monthly(week_number),
            "dispositif_expandable": self._count_dispositif_expandable(week_number),
            "warning_vision_client": self._count_warning_client(week_number),
            "warning_vision_internal": self._count_warning_internal(week_number),
            "pct_projects_with_warning": self._calculate_pct_projects_with_warning(week_number),
            "dlic_this_week": self._count_dlic_this_week(week_number),
            "dli_this_week": self._count_dli_this_week(week_number),
            "dlic_overdue": self._count_dlic_overdue(week_number),
            "dli_overdue": self._count_dli_overdue(week_number),
            "dlic_empty": self._count_dlic_empty(week_number),
            "rdv_client_this_week": self._get_rdv_client(week_number)
        }
        
        logger.info(f"Indicateurs calcules : {indicators['total_projects']} projets, {indicators['active_projects']} actifs")
        
        return indicators
    
    def _count_total(self, week: int) -> int:
        """Compte le nombre total de projets."""
        return self.db.execute_scalar(
            "SELECT COUNT(*) FROM projects WHERE week_number = ?",
            (week,)
        ) or 0
    
    def _count_active(self, week: int) -> int:
        """Compte les projets actifs (EN COURS)."""
        return self.db.execute_scalar(
            "SELECT COUNT(*) FROM projects WHERE week_number = ? AND status = 'EN COURS'",
            (week,)
        ) or 0
    
    def _sum_dispositif_monthly(self, week: int) -> int:
        """Somme des jours dispositif mensuel (projets actifs uniquement)."""
        return self.db.execute_scalar(
            """SELECT COALESCE(SUM(days_dispositif_monthly), 0) 
               FROM projects 
               WHERE week_number = ? 
               AND status = 'EN COURS'
               AND days_dispositif_monthly IS NOT NULL""",
            (week,)
        ) or 0
    
    def _count_dispositif_expandable(self, week: int) -> int:
        """Compte les projets actifs avec dispositif augmentable (oui/oui+)."""
        return self.db.execute_scalar(
            """SELECT COUNT(*) 
               FROM projects 
               WHERE week_number = ? 
               AND status = 'EN COURS'
               AND (LOWER(dispositif_expandable) LIKE '%oui%')""",
            (week,)
        ) or 0
    
    def _count_warning_client(self, week: int) -> int:
        """Compte les warnings vision client (colonne P)."""
        return self.db.execute_scalar(
            """SELECT COUNT(*) FROM projects 
               WHERE week_number = ? 
               AND status = 'EN COURS'
               AND (LOWER(vision_client) LIKE '%warning%' OR vision_client LIKE '%WARNING%')""",
            (week,)
        ) or 0
    
    def _count_warning_internal(self, week: int) -> int:
        """Compte les warnings vision interne (colonne Q)."""
        return self.db.execute_scalar(
            """SELECT COUNT(*) FROM projects 
               WHERE week_number = ? 
               AND status = 'EN COURS'
               AND (LOWER(vision_internal) LIKE '%warning%' OR vision_internal LIKE '%WARNING%')""",
            (week,)
        ) or 0
    
    def _count_projects_with_warning(self, week: int) -> int:
        """
        Compte les projets actifs avec au moins un warning (P ou Q ou les deux).
        Un projet avec P et Q compte pour 1 (pas 2).
        """
        return self.db.execute_scalar(
            """SELECT COUNT(DISTINCT id_projet) FROM projects 
               WHERE week_number = ? 
               AND status = 'EN COURS'
               AND (LOWER(vision_client) LIKE '%warning%' 
                    OR LOWER(vision_internal) LIKE '%warning%'
                    OR vision_client LIKE '%WARNING%'
                    OR vision_internal LIKE '%WARNING%')""",
            (week,)
        ) or 0
    
    def _calculate_pct_projects_with_warning(self, week: int) -> float:
        """
        Calcule le pourcentage de projets actifs avec au moins un warning.
        
        Returns:
            Pourcentage arrondi à 1 décimale (ex: 23.5)
        """
        total_active = self._count_active(week)
        if total_active == 0:
            return 0.0
        
        projects_with_warning = self._count_projects_with_warning(week)
        pct = (projects_with_warning / total_active) * 100
        return round(pct, 1)
    
    def _count_dlic_this_week(self, week: int) -> int:
        """
        Compte les DLIC à traiter : cette semaine + dépassées.
        Un projet ne compte qu'une fois (pas de double comptage).
        """
        return self.db.execute_scalar(
            """SELECT COUNT(DISTINCT id_projet) FROM projects
               WHERE week_number = ?
               AND status = 'EN COURS'
               AND dlic IS NOT NULL
               AND (
                   -- DLIC dépassées
                   dlic < date('now')
                   OR
                   -- DLIC cette semaine (jusqu'à dimanche)
                   (dlic >= date('now') AND dlic BETWEEN date('now', 'weekday 0', '-6 days') AND date('now', 'weekday 0'))
               )""",
            (week,)
        ) or 0
    
    def _count_dli_this_week(self, week: int) -> int:
        """
        Compte les DLI à traiter : cette semaine + dépassées.
        Un projet ne compte qu'une fois (pas de double comptage).
        """
        return self.db.execute_scalar(
            """SELECT COUNT(DISTINCT id_projet) FROM projects
               WHERE week_number = ?
               AND status = 'EN COURS'
               AND dli IS NOT NULL
               AND (
                   -- DLI dépassées
                   dli < date('now')
                   OR
                   -- DLI cette semaine (jusqu'à dimanche)
                   (dli >= date('now') AND dli BETWEEN date('now', 'weekday 0', '-6 days') AND date('now', 'weekday 0'))
               )""",
            (week,)
        ) or 0
    
    def _count_dlic_overdue(self, week: int) -> int:
        """Compte les DLIC dépassées."""
        return self.db.execute_scalar(
            """SELECT COUNT(*) FROM projects
               WHERE week_number = ?
               AND status = 'EN COURS'
               AND dlic IS NOT NULL
               AND dlic < date('now')""",
            (week,)
        ) or 0
    
    def _count_dli_overdue(self, week: int) -> int:
        """Compte les DLI dépassées."""
        return self.db.execute_scalar(
            """SELECT COUNT(*) FROM projects
               WHERE week_number = ?
               AND status = 'EN COURS'
               AND dli IS NOT NULL
               AND dli < date('now')""",
            (week,)
        ) or 0
    
    def _count_dlic_empty(self, week: int) -> int:
        """Compte les DLIC vides (projets actifs uniquement)."""
        return self.db.execute_scalar(
            """SELECT COUNT(*) FROM projects
               WHERE week_number = ?
               AND status = 'EN COURS'
               AND (dlic IS NULL OR dlic = '')""",
            (week,)
        ) or 0
    
    def _get_rdv_client(self, week: int) -> List[Dict[str, Any]]:
        """
        Récupère la liste des RDV client de cette semaine.
        
        Returns:
            Liste de dicts: [{id_projet, client_name, next_client_exchange, date_formattee}]
        """
        query = """
            SELECT 
                id_projet,
                client_name,
                next_client_exchange,
                strftime('%d/%m/%Y', next_client_exchange) as date_formattee
            FROM projects
            WHERE week_number = ?
            AND next_client_exchange IS NOT NULL
            AND next_client_exchange BETWEEN date('now', 'weekday 0', '-6 days')
                                         AND date('now', 'weekday 0')
            ORDER BY next_client_exchange ASC
        """
        
        cursor = self.db.conn.cursor()
        cursor.execute(query, (week,))
        rows = cursor.fetchall()
        
        return [dict(row) for row in rows]
    
    def get_project_details(self, id_projet: int, week_number: int) -> Dict[str, Any]:
        """
        Récupère les détails complets d'un projet.
        
        Args:
            id_projet: ID du projet
            week_number: Numéro de semaine
            
        Returns:
            Dictionnaire avec toutes les infos du projet
        """
        query = "SELECT * FROM projects WHERE id_projet = ? AND week_number = ?"
        
        cursor = self.db.conn.cursor()
        cursor.execute(query, (id_projet, week_number))
        row = cursor.fetchone()
        
        return dict(row) if row else None
    
    def get_projects_by_manager(self, week: int) -> List[Dict[str, Any]]:
        """
        Récupère le nombre de projets actifs par chef de projet.
        
        Returns:
            Liste de dicts: [{project_manager, count}] triés alphabétiquement
        """
        query = """
            SELECT 
                COALESCE(project_manager, 'Non défini') as project_manager,
                COUNT(*) as count
            FROM projects
            WHERE week_number = ?
            AND status = 'EN COURS'
            GROUP BY project_manager
            ORDER BY LOWER(project_manager) ASC
        """
        
        cursor = self.db.conn.cursor()
        cursor.execute(query, (week,))
        rows = cursor.fetchall()
        
        return [dict(row) for row in rows]
    
    def get_active_projects_by_bu(self, week: int) -> List[Dict[str, Any]]:
        """
        Récupère le nombre de projets actifs par BU.
        
        Returns:
            Liste de dicts: [{bu, count}]
        """
        query = """
            SELECT 
                COALESCE(bu, 'Non défini') as bu,
                COUNT(*) as count
            FROM projects
            WHERE week_number = ?
            AND status = 'EN COURS'
            GROUP BY bu
            ORDER BY LOWER(bu) ASC
        """
        
        cursor = self.db.conn.cursor()
        cursor.execute(query, (week,))
        rows = cursor.fetchall()
        
        return [dict(row) for row in rows]
    
    def get_warnings_by_bu(self, week: int) -> List[Dict[str, Any]]:
        """
        Récupère le nombre de warnings par BU.
        Chaque warning compte séparément : un projet avec P et Q compte pour 2 warnings.
        
        Returns:
            Liste de dicts: [{bu, count}]
        """
        # Utiliser UNION ALL pour compter chaque warning séparément
        query = """
            SELECT 
                COALESCE(bu, 'Non défini') as bu,
                COUNT(*) as count
            FROM (
                -- Warnings vision client (colonne P)
                SELECT bu
                FROM projects
                WHERE week_number = ?
                AND status = 'EN COURS'
                AND (LOWER(vision_client) LIKE '%warning%' OR vision_client LIKE '%WARNING%')
                
                UNION ALL
                
                -- Warnings vision interne (colonne Q)
                SELECT bu
                FROM projects
                WHERE week_number = ?
                AND status = 'EN COURS'
                AND (LOWER(vision_internal) LIKE '%warning%' OR vision_internal LIKE '%WARNING%')
            )
            GROUP BY bu
            ORDER BY LOWER(bu) ASC
        """
        
        cursor = self.db.conn.cursor()
        cursor.execute(query, (week, week))
        rows = cursor.fetchall()
        
        return [dict(row) for row in rows]
    
    def get_actions_by_actor(self, week: int) -> Dict[str, Any]:
        """
        Récupère le nombre d'actions par acteur (projets avec warning).
        
        Returns:
            Dict avec 'with_actor' et 'empty' (sans acteur)
        """
        # Actions avec acteur défini
        query_with_actor = """
            SELECT 
                next_actor,
                COUNT(*) as count
            FROM projects
            WHERE week_number = ?
            AND status = 'EN COURS'
            AND (LOWER(vision_client) LIKE '%warning%' OR LOWER(vision_internal) LIKE '%warning%')
            AND next_actor IS NOT NULL
            AND next_actor != ''
            GROUP BY next_actor
            ORDER BY LOWER(next_actor) ASC
        """
        
        cursor = self.db.conn.cursor()
        cursor.execute(query_with_actor, (week,))
        with_actor = [dict(row) for row in cursor.fetchall()]
        
        # Actions sans acteur (vides)
        query_empty = """
            SELECT COUNT(*) as count
            FROM projects
            WHERE week_number = ?
            AND status = 'EN COURS'
            AND (LOWER(vision_client) LIKE '%warning%' OR LOWER(vision_internal) LIKE '%warning%')
            AND (next_actor IS NULL OR next_actor = '')
        """
        
        cursor.execute(query_empty, (week,))
        empty_count = cursor.fetchone()[0]
        
        return {
            'with_actor': with_actor,
            'empty': empty_count
        }
    
    def get_actions_by_actor_with_clients(self, week: int) -> Dict[str, Any]:
        """
        Récupère les actions par acteur avec les noms des clients (projets avec warning).
        Format pour affichage style calendrier.
        
        Returns:
            Dict avec 'by_actor' (dict acteur -> liste de clients) et 'empty' (liste de clients sans acteur)
        """
        # Actions avec acteur défini - avec noms des clients
        query_with_actor = """
            SELECT 
                next_actor,
                client_name,
                id_projet
            FROM projects
            WHERE week_number = ?
            AND status = 'EN COURS'
            AND (LOWER(vision_client) LIKE '%warning%' OR LOWER(vision_internal) LIKE '%warning%')
            AND next_actor IS NOT NULL
            AND next_actor != ''
            ORDER BY LOWER(next_actor) ASC, client_name ASC
        """
        
        cursor = self.db.conn.cursor()
        cursor.execute(query_with_actor, (week,))
        rows = cursor.fetchall()
        
        # Organiser par acteur
        by_actor = {}
        for row in rows:
            actor = row['next_actor']
            client_name = row['client_name']
            if actor not in by_actor:
                by_actor[actor] = []
            by_actor[actor].append({
                'client_name': client_name,
                'id_projet': row['id_projet']
            })
        
        # Actions sans acteur (vides)
        query_empty = """
            SELECT client_name, id_projet
            FROM projects
            WHERE week_number = ?
            AND status = 'EN COURS'
            AND (LOWER(vision_client) LIKE '%warning%' OR LOWER(vision_internal) LIKE '%warning%')
            AND (next_actor IS NULL OR next_actor = '')
            ORDER BY client_name ASC
        """
        
        cursor.execute(query_empty, (week,))
        empty_rows = cursor.fetchall()
        empty_clients = [{'client_name': row['client_name'], 'id_projet': row['id_projet']} 
                        for row in empty_rows]
        
        return {
            'by_actor': by_actor,
            'empty': empty_clients
        }

