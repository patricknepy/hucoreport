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
            "critique_vision_client": self._count_critique_client(week_number),
            "critique_vision_internal": self._count_critique_internal(week_number),
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

    def _count_critique_client(self, week: int) -> int:
        """Compte les critiques vision client (colonne P)."""
        return self.db.execute_scalar(
            """SELECT COUNT(*) FROM projects
               WHERE week_number = ?
               AND status = 'EN COURS'
               AND (LOWER(vision_client) LIKE '%critique%' OR LOWER(vision_client) LIKE '%critical%')""",
            (week,)
        ) or 0

    def _count_critique_internal(self, week: int) -> int:
        """Compte les critiques vision interne (colonne Q)."""
        return self.db.execute_scalar(
            """SELECT COUNT(*) FROM projects
               WHERE week_number = ?
               AND status = 'EN COURS'
               AND (LOWER(vision_internal) LIKE '%critique%' OR LOWER(vision_internal) LIKE '%critical%')""",
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

    def get_critiques_by_bu(self, week: int) -> List[Dict[str, Any]]:
        """
        Récupère le nombre de critiques par BU.
        Chaque critique compte séparément : un projet avec P et Q critique compte pour 2.

        Returns:
            Liste de dicts: [{bu, count}]
        """
        query = """
            SELECT
                COALESCE(bu, 'Non défini') as bu,
                COUNT(*) as count
            FROM (
                -- Critiques vision client (colonne P)
                SELECT bu
                FROM projects
                WHERE week_number = ?
                AND status = 'EN COURS'
                AND (LOWER(vision_client) LIKE '%critique%' OR LOWER(vision_client) LIKE '%critical%')

                UNION ALL

                -- Critiques vision interne (colonne Q)
                SELECT bu
                FROM projects
                WHERE week_number = ?
                AND status = 'EN COURS'
                AND (LOWER(vision_internal) LIKE '%critique%' OR LOWER(vision_internal) LIKE '%critical%')
            )
            GROUP BY bu
            ORDER BY LOWER(bu) ASC
        """

        cursor = self.db.conn.cursor()
        cursor.execute(query, (week, week))
        rows = cursor.fetchall()

        return [dict(row) for row in rows]

    def get_critiques_and_warnings_by_bu(self, week: int) -> Dict[str, List[Dict[str, Any]]]:
        """
        Récupère le nombre de critiques ET warnings par BU dans une structure combinée.

        Returns:
            Dict avec 'critiques' et 'warnings', chacun étant [{bu, count}]
        """
        return {
            'critiques': self.get_critiques_by_bu(week),
            'warnings': self.get_warnings_by_bu(week)
        }

    def get_projects_critique_client(self, week: int) -> List[Dict[str, Any]]:
        """Récupère les projets avec CRITIQUE en Vision Client."""
        query = """
            SELECT id_projet, client_name, project_manager, vision_client, vision_internal,
                   comment_vision_client, action_description, next_actor
            FROM projects
            WHERE week_number = ?
            AND status = 'EN COURS'
            AND (LOWER(vision_client) LIKE '%critique%' OR LOWER(vision_client) LIKE '%critical%')
            ORDER BY client_name
        """
        return self.db.execute_query(query, (week,))

    def get_projects_critique_internal(self, week: int) -> List[Dict[str, Any]]:
        """Récupère les projets avec CRITIQUE en Vision Interne."""
        query = """
            SELECT id_projet, client_name, project_manager, vision_client, vision_internal,
                   comment_vision_internal, action_description, next_actor
            FROM projects
            WHERE week_number = ?
            AND status = 'EN COURS'
            AND (LOWER(vision_internal) LIKE '%critique%' OR LOWER(vision_internal) LIKE '%critical%')
            ORDER BY client_name
        """
        return self.db.execute_query(query, (week,))

    def get_projects_warning_client(self, week: int) -> List[Dict[str, Any]]:
        """Récupère les projets avec WARNING en Vision Client."""
        query = """
            SELECT id_projet, client_name, project_manager, vision_client, vision_internal,
                   comment_vision_client, action_description, next_actor
            FROM projects
            WHERE week_number = ?
            AND status = 'EN COURS'
            AND (LOWER(vision_client) LIKE '%warning%')
            ORDER BY client_name
        """
        return self.db.execute_query(query, (week,))

    def get_projects_warning_internal(self, week: int) -> List[Dict[str, Any]]:
        """Récupère les projets avec WARNING en Vision Interne."""
        query = """
            SELECT id_projet, client_name, project_manager, vision_client, vision_internal,
                   comment_vision_internal, action_description, next_actor
            FROM projects
            WHERE week_number = ?
            AND status = 'EN COURS'
            AND (LOWER(vision_internal) LIKE '%warning%')
            ORDER BY client_name
        """
        return self.db.execute_query(query, (week,))

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

    def get_warnings_evolution(self) -> Dict[str, Any]:
        """
        Récupère l'évolution des warnings et critiques par semaine pour toutes les semaines disponibles.

        Returns:
            Dict avec 'weeks', 'warning_client', 'warning_internal', 'critique_client', 'critique_internal',
            'projects_with_warning' (nb de DOSSIERS en warning), 'active_projects'
        """
        from datetime import datetime

        # Récupérer toutes les semaines disponibles
        available_weeks = self.db.get_available_weeks()

        if not available_weeks:
            return {
                'weeks': [],
                'warning_client': [],
                'warning_internal': [],
                'critique_client': [],
                'critique_internal': [],
                'projects_with_warning': [],
                'total_warnings': [],
                'active_projects': []
            }

        # Tri CHRONOLOGIQUE : semaines 2025 (S39-S51) AVANT semaines 2026 (S01-S04)
        current_week = datetime.now().isocalendar()[1]

        def chronological_sort(week: int) -> int:
            # Les semaines > current_week sont de l'année précédente (ex: S39-S51 en 2025)
            # Les semaines <= current_week sont de l'année courante (ex: S01-S04 en 2026)
            if week > current_week:
                return week - 100  # S51 -> -49, S39 -> -61 (donc avant S01=1)
            else:
                return week  # S01 -> 1, S04 -> 4

        weeks = sorted(available_weeks, key=chronological_sort)
        warning_client = []
        warning_internal = []
        critique_client = []
        critique_internal = []
        projects_with_warning = []
        total_warnings = []
        active_projects = []

        for week in weeks:
            wc = self._count_warning_client(week)
            wi = self._count_warning_internal(week)
            cc = self._count_critique_client(week)
            ci = self._count_critique_internal(week)
            pw = self._count_projects_with_warning(week)  # Nb de DOSSIERS en warning
            active = self._count_active(week)

            warning_client.append(wc)
            warning_internal.append(wi)
            critique_client.append(cc)
            critique_internal.append(ci)
            projects_with_warning.append(pw)  # Compte un dossier une seule fois
            total_warnings.append(wc + wi)  # Conservé pour compatibilité
            active_projects.append(active)

        return {
            'weeks': [f"S{w}" for w in weeks],
            'week_numbers': weeks,
            'warning_client': warning_client,
            'warning_internal': warning_internal,
            'critique_client': critique_client,
            'critique_internal': critique_internal,
            'projects_with_warning': projects_with_warning,
            'total_warnings': total_warnings,
            'active_projects': active_projects
        }

    def get_warnings_by_month(self) -> Dict[str, Any]:
        """
        Agrège les warnings et critiques par mois (basé sur le numéro de semaine).
        Utilise la dernière semaine de chaque mois pour les statistiques.

        Returns:
            Dict avec 'months', 'warning_client', 'warning_internal', 'critique_client', 'critique_internal'
        """
        import datetime

        # Récupérer toutes les semaines disponibles
        available_weeks = self.db.get_available_weeks()

        if not available_weeks:
            return {
                'months': [],
                'warning_client': [],
                'warning_internal': [],
                'critique_client': [],
                'critique_internal': [],
                'total_warnings': []
            }

        # Déterminer l'année correcte pour chaque semaine
        # Les semaines > semaine_courante sont de l'année précédente (2025)
        # Les semaines <= semaine_courante sont de l'année courante (2026)
        current_year = datetime.datetime.now().year
        current_week = datetime.datetime.now().isocalendar()[1]

        weeks_by_month = {}
        for week in available_weeks:
            # Calculer la date du lundi de cette semaine avec la BONNE année
            try:
                # Déterminer l'année : S39-S51 = 2025, S01-S04 = 2026
                if week > current_week:
                    year = current_year - 1  # Année précédente (2025)
                else:
                    year = current_year  # Année courante (2026)

                # ISO week: lundi de la semaine N
                monday = datetime.datetime.strptime(f'{year}-W{week:02d}-1', '%G-W%V-%u')
                month_key = monday.strftime('%Y-%m')
                month_label = monday.strftime('%b %Y')  # "Nov 2025"

                if month_key not in weeks_by_month:
                    weeks_by_month[month_key] = {
                        'label': month_label,
                        'weeks': []
                    }
                weeks_by_month[month_key]['weeks'].append(week)
            except ValueError:
                # Si la semaine est invalide, on l'ignore
                continue

        # Pour chaque mois, prendre la dernière semaine et calculer les warnings/critiques
        months = []
        warning_client = []
        warning_internal = []
        critique_client = []
        critique_internal = []
        total_warnings = []

        for month_key in sorted(weeks_by_month.keys()):
            month_data = weeks_by_month[month_key]
            last_week = max(month_data['weeks'])

            wc = self._count_warning_client(last_week)
            wi = self._count_warning_internal(last_week)
            cc = self._count_critique_client(last_week)
            ci = self._count_critique_internal(last_week)

            months.append(month_data['label'])
            warning_client.append(wc)
            warning_internal.append(wi)
            critique_client.append(cc)
            critique_internal.append(ci)
            total_warnings.append(wc + wi)

        return {
            'months': months,
            'warning_client': warning_client,
            'warning_internal': warning_internal,
            'critique_client': critique_client,
            'critique_internal': critique_internal,
            'total_warnings': total_warnings
        }

    # ============================================================
    # MÉTHODES CDP (Chefs de Projet)
    # ============================================================

    def get_cdp_statistics(self, week: int) -> List[Dict[str, Any]]:
        """
        Récupère les statistiques complètes par Chef de Projet.

        Returns:
            Liste de dicts avec toutes les stats CDP
        """
        query = """
            SELECT
                COALESCE(project_manager, 'Non défini') as project_manager,
                COUNT(*) as total_projects,
                SUM(CASE WHEN status = 'EN COURS' THEN 1 ELSE 0 END) as active_projects,
                SUM(CASE WHEN status = 'PAUSE' THEN 1 ELSE 0 END) as paused_projects,
                SUM(CASE WHEN status = 'TERMINÉ' THEN 1 ELSE 0 END) as completed_projects,
                SUM(CASE WHEN status = 'À VENIR' THEN 1 ELSE 0 END) as upcoming_projects,
                SUM(CASE WHEN status = 'EN COURS' AND (LOWER(vision_client) LIKE '%warning%') THEN 1 ELSE 0 END) as warnings_client,
                SUM(CASE WHEN status = 'EN COURS' AND (LOWER(vision_internal) LIKE '%warning%') THEN 1 ELSE 0 END) as warnings_internal,
                SUM(CASE WHEN status = 'EN COURS' AND (LOWER(vision_client) LIKE '%warning%' OR LOWER(vision_internal) LIKE '%warning%') THEN 1 ELSE 0 END) as projects_with_warning,
                SUM(CASE WHEN status = 'EN COURS' AND dlic IS NOT NULL AND dlic < date('now') THEN 1 ELSE 0 END) as dlic_overdue,
                SUM(CASE WHEN status = 'EN COURS' AND (dlic IS NULL OR dlic = '') THEN 1 ELSE 0 END) as dlic_empty,
                SUM(CASE WHEN status = 'EN COURS' AND dlic IS NOT NULL AND dlic >= date('now') AND dlic <= date('now', '+7 days') THEN 1 ELSE 0 END) as dlic_this_week,
                AVG(CASE WHEN status = 'EN COURS' AND nps_commercial IS NOT NULL THEN nps_commercial END) as avg_nps_commercial,
                AVG(CASE WHEN status = 'EN COURS' AND nps_project IS NOT NULL THEN nps_project END) as avg_nps_project,
                SUM(CASE WHEN status = 'EN COURS' THEN COALESCE(days_dispositif_monthly, 0) ELSE 0 END) as total_days_dispositif
            FROM projects
            WHERE week_number = ?
            GROUP BY project_manager
            ORDER BY active_projects DESC, LOWER(project_manager) ASC
        """

        cursor = self.db.conn.cursor()
        cursor.execute(query, (week,))
        rows = cursor.fetchall()

        results = []
        for row in rows:
            data = dict(row)
            # Calculer le taux de santé (% projets actifs sans warning)
            active = data['active_projects'] or 0
            with_warning = data['projects_with_warning'] or 0
            if active > 0:
                data['health_rate'] = round(((active - with_warning) / active) * 100, 1)
            else:
                data['health_rate'] = 100.0

            # Calculer le taux de remplissage DLIC
            dlic_empty = data['dlic_empty'] or 0
            if active > 0:
                data['dlic_fill_rate'] = round(((active - dlic_empty) / active) * 100, 1)
            else:
                data['dlic_fill_rate'] = 100.0

            # Arrondir les NPS
            if data['avg_nps_commercial'] is not None:
                data['avg_nps_commercial'] = round(data['avg_nps_commercial'], 1)
            if data['avg_nps_project'] is not None:
                data['avg_nps_project'] = round(data['avg_nps_project'], 1)

            results.append(data)

        return results

    def get_cdp_by_bu(self, week: int) -> Dict[str, List[Dict[str, Any]]]:
        """
        Récupère la répartition des projets par BU pour chaque CDP.

        Returns:
            Dict {cdp_name: [{bu, count}]}
        """
        query = """
            SELECT
                COALESCE(project_manager, 'Non défini') as project_manager,
                COALESCE(bu, 'Non défini') as bu,
                COUNT(*) as count
            FROM projects
            WHERE week_number = ?
            AND status = 'EN COURS'
            GROUP BY project_manager, bu
            ORDER BY project_manager, bu
        """

        cursor = self.db.conn.cursor()
        cursor.execute(query, (week,))
        rows = cursor.fetchall()

        result = {}
        for row in rows:
            pm = row['project_manager']
            if pm not in result:
                result[pm] = []
            result[pm].append({
                'bu': row['bu'],
                'count': row['count']
            })

        return result

    def get_cdp_ranking_by_health(self, week: int) -> List[Dict[str, Any]]:
        """
        Classement des CDP par taux de santé du portefeuille.

        Returns:
            Liste triée par taux de santé décroissant
        """
        stats = self.get_cdp_statistics(week)
        # Filtrer uniquement les CDP avec des projets actifs
        active_cdps = [s for s in stats if s['active_projects'] > 0]
        return sorted(active_cdps, key=lambda x: x['health_rate'], reverse=True)

    def get_cdp_ranking_by_charge(self, week: int) -> List[Dict[str, Any]]:
        """
        Classement des CDP par charge de travail (nombre de projets actifs).

        Returns:
            Liste triée par nombre de projets actifs décroissant
        """
        stats = self.get_cdp_statistics(week)
        return sorted(stats, key=lambda x: x['active_projects'], reverse=True)

    # ============================================================
    # MÉTHODES WARNINGS (Synthèse des warnings)
    # ============================================================

    def get_warnings_details(self, week: int) -> List[Dict[str, Any]]:
        """
        Récupère tous les projets avec warnings et leurs détails.

        Returns:
            Liste de dicts avec infos projet + commentaires warnings
        """
        query = """
            SELECT
                id_projet,
                client_name,
                project_manager,
                bu,
                status,
                vision_client,
                vision_internal,
                action_description,
                next_actor,
                dlic,
                dli,
                strftime('%d/%m/%Y', dlic) as dlic_formatted,
                strftime('%d/%m/%Y', dli) as dli_formatted,
                CASE WHEN dlic IS NOT NULL AND dlic < date('now') THEN 1 ELSE 0 END as dlic_overdue,
                CASE WHEN dli IS NOT NULL AND dli < date('now') THEN 1 ELSE 0 END as dli_overdue
            FROM projects
            WHERE week_number = ?
            AND status = 'EN COURS'
            AND (LOWER(vision_client) LIKE '%warning%' OR LOWER(vision_internal) LIKE '%warning%')
            ORDER BY
                CASE WHEN dlic IS NOT NULL AND dlic < date('now') THEN 0 ELSE 1 END,
                dlic ASC,
                client_name ASC
        """

        cursor = self.db.conn.cursor()
        cursor.execute(query, (week,))
        rows = cursor.fetchall()

        results = []
        for row in rows:
            data = dict(row)
            # Déterminer le type de warning
            has_client = 'warning' in (data['vision_client'] or '').lower()
            has_internal = 'warning' in (data['vision_internal'] or '').lower()

            if has_client and has_internal:
                data['warning_type'] = 'Les deux'
            elif has_client:
                data['warning_type'] = 'Client'
            else:
                data['warning_type'] = 'Interne'

            results.append(data)

        return results

    def get_warnings_by_cdp(self, week: int) -> Dict[str, List[Dict[str, Any]]]:
        """
        Récupère les warnings groupés par Chef de Projet.

        Returns:
            Dict {cdp_name: [liste des projets en warning]}
        """
        warnings = self.get_warnings_details(week)

        result = {}
        for w in warnings:
            pm = w.get('project_manager') or 'Non défini'
            if pm not in result:
                result[pm] = []
            result[pm].append(w)

        return result

    def get_warnings_summary(self, week: int) -> Dict[str, Any]:
        """
        Récupère un résumé des warnings.

        Returns:
            Dict avec les compteurs
        """
        warnings = self.get_warnings_details(week)

        total = len(warnings)
        client_only = sum(1 for w in warnings if w['warning_type'] == 'Client')
        internal_only = sum(1 for w in warnings if w['warning_type'] == 'Interne')
        both = sum(1 for w in warnings if w['warning_type'] == 'Les deux')
        dlic_overdue = sum(1 for w in warnings if w['dlic_overdue'])
        no_actor = sum(1 for w in warnings if not w.get('next_actor'))

        return {
            'total_warnings': total,
            'client_only': client_only,
            'internal_only': internal_only,
            'both': both,
            'dlic_overdue': dlic_overdue,
            'no_actor': no_actor
        }

    # ============================================================
    # MÉTHODES HISTORIQUE CDP (Évolution sur plusieurs semaines)
    # ============================================================

    def get_all_cdp_names(self) -> List[str]:
        """
        Récupère la liste de tous les chefs de projet distincts.

        Returns:
            Liste des noms de CDP triés alphabétiquement
        """
        query = """
            SELECT DISTINCT COALESCE(project_manager, 'Non défini') as project_manager
            FROM projects
            WHERE project_manager IS NOT NULL AND project_manager != ''
            ORDER BY LOWER(project_manager) ASC
        """
        cursor = self.db.conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        return [row['project_manager'] for row in rows]

    def get_cdp_evolution(self, cdp_name: str = None) -> Dict[str, Any]:
        """
        Récupère l'évolution des indicateurs CDP sur toutes les semaines.

        Args:
            cdp_name: Nom du CDP (si None, agrège tous les CDP)

        Returns:
            Dict avec weeks, projets_actifs, warnings, taux_sante, nps_commercial, nps_project
        """
        from datetime import datetime

        available_weeks = self.db.get_available_weeks()

        if not available_weeks:
            return {
                'weeks': [],
                'week_numbers': [],
                'active_projects': [],
                'warnings_client': [],
                'warnings_internal': [],
                'health_rate': [],
                'nps_commercial': [],
                'nps_project': []
            }

        # Tri chronologique
        current_week = datetime.now().isocalendar()[1]

        def chronological_sort(week: int) -> int:
            if week > current_week:
                return week - 100
            else:
                return week

        weeks = sorted(available_weeks, key=chronological_sort)

        active_projects = []
        warnings_client = []
        warnings_internal = []
        health_rate = []
        nps_commercial = []
        nps_project = []

        for week in weeks:
            if cdp_name:
                # Stats pour un CDP spécifique
                stats = self._get_cdp_week_stats(week, cdp_name)
            else:
                # Stats agrégées pour tous les CDP
                stats = self._get_all_cdp_week_stats(week)

            active_projects.append(stats['active_projects'])
            warnings_client.append(stats['warnings_client'])
            warnings_internal.append(stats['warnings_internal'])
            health_rate.append(stats['health_rate'])
            nps_commercial.append(stats['nps_commercial'])
            nps_project.append(stats['nps_project'])

        return {
            'weeks': [f"S{w}" for w in weeks],
            'week_numbers': weeks,
            'active_projects': active_projects,
            'warnings_client': warnings_client,
            'warnings_internal': warnings_internal,
            'health_rate': health_rate,
            'nps_commercial': nps_commercial,
            'nps_project': nps_project
        }

    def _get_cdp_week_stats(self, week: int, cdp_name: str) -> Dict[str, Any]:
        """Récupère les stats d'un CDP pour une semaine donnée."""
        query = """
            SELECT
                COUNT(CASE WHEN status = 'EN COURS' THEN 1 END) as active_projects,
                COUNT(CASE WHEN status = 'EN COURS' AND LOWER(vision_client) LIKE '%warning%' THEN 1 END) as warnings_client,
                COUNT(CASE WHEN status = 'EN COURS' AND LOWER(vision_internal) LIKE '%warning%' THEN 1 END) as warnings_internal,
                COUNT(CASE WHEN status = 'EN COURS' AND (LOWER(vision_client) LIKE '%warning%' OR LOWER(vision_internal) LIKE '%warning%') THEN 1 END) as projects_with_warning,
                AVG(CASE WHEN status = 'EN COURS' AND nps_commercial IS NOT NULL THEN nps_commercial END) as nps_commercial,
                AVG(CASE WHEN status = 'EN COURS' AND nps_project IS NOT NULL THEN nps_project END) as nps_project
            FROM projects
            WHERE week_number = ?
            AND COALESCE(project_manager, 'Non défini') = ?
        """

        cursor = self.db.conn.cursor()
        cursor.execute(query, (week, cdp_name))
        row = cursor.fetchone()

        if not row:
            return {
                'active_projects': 0,
                'warnings_client': 0,
                'warnings_internal': 0,
                'health_rate': 100.0,
                'nps_commercial': None,
                'nps_project': None
            }

        active = row['active_projects'] or 0
        with_warning = row['projects_with_warning'] or 0

        if active > 0:
            health = round(((active - with_warning) / active) * 100, 1)
        else:
            health = 100.0

        return {
            'active_projects': active,
            'warnings_client': row['warnings_client'] or 0,
            'warnings_internal': row['warnings_internal'] or 0,
            'health_rate': health,
            'nps_commercial': round(row['nps_commercial'], 1) if row['nps_commercial'] else None,
            'nps_project': round(row['nps_project'], 1) if row['nps_project'] else None
        }

    def _get_all_cdp_week_stats(self, week: int) -> Dict[str, Any]:
        """Récupère les stats agrégées de tous les CDP pour une semaine."""
        query = """
            SELECT
                COUNT(CASE WHEN status = 'EN COURS' THEN 1 END) as active_projects,
                COUNT(CASE WHEN status = 'EN COURS' AND LOWER(vision_client) LIKE '%warning%' THEN 1 END) as warnings_client,
                COUNT(CASE WHEN status = 'EN COURS' AND LOWER(vision_internal) LIKE '%warning%' THEN 1 END) as warnings_internal,
                COUNT(CASE WHEN status = 'EN COURS' AND (LOWER(vision_client) LIKE '%warning%' OR LOWER(vision_internal) LIKE '%warning%') THEN 1 END) as projects_with_warning,
                AVG(CASE WHEN status = 'EN COURS' AND nps_commercial IS NOT NULL THEN nps_commercial END) as nps_commercial,
                AVG(CASE WHEN status = 'EN COURS' AND nps_project IS NOT NULL THEN nps_project END) as nps_project
            FROM projects
            WHERE week_number = ?
        """

        cursor = self.db.conn.cursor()
        cursor.execute(query, (week,))
        row = cursor.fetchone()

        if not row:
            return {
                'active_projects': 0,
                'warnings_client': 0,
                'warnings_internal': 0,
                'health_rate': 100.0,
                'nps_commercial': None,
                'nps_project': None
            }

        active = row['active_projects'] or 0
        with_warning = row['projects_with_warning'] or 0

        if active > 0:
            health = round(((active - with_warning) / active) * 100, 1)
        else:
            health = 100.0

        return {
            'active_projects': active,
            'warnings_client': row['warnings_client'] or 0,
            'warnings_internal': row['warnings_internal'] or 0,
            'health_rate': health,
            'nps_commercial': round(row['nps_commercial'], 1) if row['nps_commercial'] else None,
            'nps_project': round(row['nps_project'], 1) if row['nps_project'] else None
        }

    def get_cdp_evolution_comparison(self) -> Dict[str, Dict[str, List]]:
        """
        Récupère l'évolution de tous les CDP pour comparaison.

        Returns:
            Dict {cdp_name: {weeks, active_projects, health_rate, ...}}
        """
        cdp_names = self.get_all_cdp_names()
        result = {}

        for cdp in cdp_names:
            result[cdp] = self.get_cdp_evolution(cdp)

        return result

    # ============================================================
    # MÉTHODES TEMPS FACTURABLE (Matelas d'activité)
    # ============================================================

    def get_facturable_evolution(self, cdp_name: str = None) -> Dict[str, Any]:
        """
        Récupère l'évolution du temps facturable en main par semaine.

        Args:
            cdp_name: Nom du CDP (si None, agrège tous les CDP)

        Returns:
            Dict avec weeks, total_facturable (somme des jours facturable par semaine)
        """
        from datetime import datetime

        available_weeks = self.db.get_available_weeks()

        if not available_weeks:
            return {
                'weeks': [],
                'week_numbers': [],
                'total_facturable': []
            }

        # Tri chronologique
        current_week = datetime.now().isocalendar()[1]

        def chronological_sort(week: int) -> int:
            if week > current_week:
                return week - 100
            else:
                return week

        weeks = sorted(available_weeks, key=chronological_sort)
        total_facturable = []

        for week in weeks:
            if cdp_name:
                # Total pour un CDP spécifique
                result = self._get_facturable_by_cdp(week, cdp_name)
            else:
                # Total global
                result = self._get_facturable_total(week)

            total_facturable.append(result)

        return {
            'weeks': [f"S{w}" for w in weeks],
            'week_numbers': weeks,
            'total_facturable': total_facturable
        }

    def _get_facturable_total(self, week: int) -> float:
        """Récupère le total temps facturable pour une semaine (tous projets actifs)."""
        result = self.db.execute_scalar(
            """SELECT COALESCE(SUM(days_facturable_main), 0)
               FROM projects
               WHERE week_number = ?
               AND status = 'EN COURS'
               AND days_facturable_main IS NOT NULL""",
            (week,)
        )
        return round(result or 0, 1)

    def _get_facturable_by_cdp(self, week: int, cdp_name: str) -> float:
        """Récupère le total temps facturable pour un CDP et une semaine."""
        result = self.db.execute_scalar(
            """SELECT COALESCE(SUM(days_facturable_main), 0)
               FROM projects
               WHERE week_number = ?
               AND status = 'EN COURS'
               AND COALESCE(project_manager, 'Non défini') = ?
               AND days_facturable_main IS NOT NULL""",
            (week, cdp_name)
        )
        return round(result or 0, 1)

    def get_facturable_by_cdp_ranking(self, week: int) -> List[Dict[str, Any]]:
        """
        Classement des CDP par temps facturable en main.

        Returns:
            Liste triée par temps facturable décroissant
        """
        query = """
            SELECT
                COALESCE(project_manager, 'Non défini') as project_manager,
                COALESCE(SUM(days_facturable_main), 0) as total_facturable,
                COUNT(*) as active_projects
            FROM projects
            WHERE week_number = ?
            AND status = 'EN COURS'
            GROUP BY project_manager
            HAVING total_facturable > 0
            ORDER BY total_facturable DESC
        """

        cursor = self.db.conn.cursor()
        cursor.execute(query, (week,))
        rows = cursor.fetchall()

        return [{'project_manager': row['project_manager'],
                 'total_facturable': round(row['total_facturable'], 1),
                 'active_projects': row['active_projects']} for row in rows]

    def get_facturable_by_bu(self, week: int) -> List[Dict[str, Any]]:
        """
        Temps facturable par BU/Techno.

        Returns:
            Liste triée par temps facturable décroissant
        """
        query = """
            SELECT
                COALESCE(bu, 'Non défini') as bu,
                COALESCE(SUM(days_facturable_main), 0) as total_facturable,
                COUNT(*) as project_count
            FROM projects
            WHERE week_number = ?
            AND status = 'EN COURS'
            GROUP BY bu
            HAVING total_facturable > 0
            ORDER BY total_facturable DESC
        """

        cursor = self.db.conn.cursor()
        cursor.execute(query, (week,))
        rows = cursor.fetchall()

        return [{'bu': row['bu'],
                 'total_facturable': round(row['total_facturable'], 1),
                 'project_count': row['project_count']} for row in rows]

    def get_facturable_by_contract_type(self, week: int) -> List[Dict[str, Any]]:
        """
        Temps facturable par type de contrat (Build/Run/Forfait/Régie...).

        Returns:
            Liste triée par temps facturable décroissant
        """
        query = """
            SELECT
                COALESCE(contract_type, 'Non défini') as contract_type,
                COALESCE(SUM(days_facturable_main), 0) as total_facturable,
                COUNT(*) as project_count
            FROM projects
            WHERE week_number = ?
            AND status = 'EN COURS'
            GROUP BY contract_type
            HAVING total_facturable > 0
            ORDER BY total_facturable DESC
        """

        cursor = self.db.conn.cursor()
        cursor.execute(query, (week,))
        rows = cursor.fetchall()

        return [{'contract_type': row['contract_type'],
                 'total_facturable': round(row['total_facturable'], 1),
                 'project_count': row['project_count']} for row in rows]

    def get_facturable_by_client(self, week: int) -> List[Dict[str, Any]]:
        """
        Temps facturable par client.

        Returns:
            Liste triée par temps facturable décroissant (top clients)
        """
        query = """
            SELECT
                COALESCE(client_name, 'Non défini') as client_name,
                COALESCE(SUM(days_facturable_main), 0) as total_facturable,
                COUNT(*) as project_count
            FROM projects
            WHERE week_number = ?
            AND status = 'EN COURS'
            GROUP BY client_name
            HAVING total_facturable > 0
            ORDER BY total_facturable DESC
            LIMIT 20
        """

        cursor = self.db.conn.cursor()
        cursor.execute(query, (week,))
        rows = cursor.fetchall()

        return [{'client_name': row['client_name'],
                 'total_facturable': round(row['total_facturable'], 1),
                 'project_count': row['project_count']} for row in rows]

    def get_facturable_by_project(self, week: int, limit: int = 15, cdp_name: str = None) -> List[Dict[str, Any]]:
        """
        Top projets par temps facturable en main.

        Args:
            week: Numéro de semaine
            limit: Nombre max de projets
            cdp_name: Si spécifié, filtre par chef de projet

        Returns:
            Liste triée par temps facturable décroissant (top projets)
        """
        if cdp_name:
            query = """
                SELECT
                    COALESCE(client_name, 'Non défini') as client_name,
                    COALESCE(bu, 'N/A') as bu,
                    COALESCE(project_manager, 'Non défini') as project_manager,
                    COALESCE(days_facturable_main, 0) as days_facturable
                FROM projects
                WHERE week_number = ?
                AND status = 'EN COURS'
                AND COALESCE(project_manager, 'Non défini') = ?
                ORDER BY days_facturable_main DESC
                LIMIT ?
            """
            cursor = self.db.conn.cursor()
            cursor.execute(query, (week, cdp_name, limit))
        else:
            query = """
                SELECT
                    COALESCE(client_name, 'Non défini') as client_name,
                    COALESCE(bu, 'N/A') as bu,
                    COALESCE(project_manager, 'Non défini') as project_manager,
                    COALESCE(days_facturable_main, 0) as days_facturable
                FROM projects
                WHERE week_number = ?
                AND status = 'EN COURS'
                ORDER BY days_facturable_main DESC
                LIMIT ?
            """
            cursor = self.db.conn.cursor()
            cursor.execute(query, (week, limit))

        rows = cursor.fetchall()

        return [{'client_name': row['client_name'][:18],
                 'bu': row['bu'],
                 'project_manager': row['project_manager'],
                 'days_facturable': round(row['days_facturable'], 1)} for row in rows]

    def get_projects_vs_pipe_evolution(self, cdp_name: str = None) -> Dict[str, Any]:
        """
        Évolution corrélée : Nb projets actifs VS Total PIPE par semaine.

        Args:
            cdp_name: Si spécifié, filtre par chef de projet

        Returns:
            Dict avec weeks, active_projects, total_pipe (ordre chronologique S39 → S14)
        """
        weeks = self.db.get_available_weeks()
        # Inverser pour ordre chronologique (anciennes semaines à gauche)
        weeks = list(reversed(weeks))

        result = {
            'weeks': [],
            'active_projects': [],
            'total_pipe': [],
            'avg_pipe_per_project': []
        }

        for week in weeks:
            result['weeks'].append(f"S{week}")

            if cdp_name:
                # Filtré par CDP
                nb_projects = self.db.execute_scalar(
                    """SELECT COUNT(*) FROM projects
                       WHERE week_number = ? AND status = 'EN COURS'
                       AND COALESCE(project_manager, 'Non défini') = ?""",
                    (week, cdp_name)
                ) or 0

                total_pipe = self.db.execute_scalar(
                    """SELECT COALESCE(SUM(days_facturable_main), 0)
                       FROM projects WHERE week_number = ? AND status = 'EN COURS'
                       AND COALESCE(project_manager, 'Non défini') = ?""",
                    (week, cdp_name)
                ) or 0
            else:
                # Tous les projets
                nb_projects = self.db.execute_scalar(
                    "SELECT COUNT(*) FROM projects WHERE week_number = ? AND status = 'EN COURS'",
                    (week,)
                ) or 0

                total_pipe = self.db.execute_scalar(
                    """SELECT COALESCE(SUM(days_facturable_main), 0)
                       FROM projects WHERE week_number = ? AND status = 'EN COURS'""",
                    (week,)
                ) or 0

            result['active_projects'].append(nb_projects)
            result['total_pipe'].append(round(total_pipe, 1))

            # Moyenne par projet
            avg = round(total_pipe / nb_projects, 1) if nb_projects > 0 else 0
            result['avg_pipe_per_project'].append(avg)

        return result

