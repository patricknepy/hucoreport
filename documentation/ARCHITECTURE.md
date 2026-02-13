# Architecture Technique - Huco Report

## Vue d'ensemble

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           INTERFACE (PyQt6)                                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐│
│  │Dashboard │ │   KPIs   │ │ Analyse  │ │Exploitat.│ │ Rapports │ │  Auto  ││
│  │   Tab    │ │   Tab    │ │   Tab    │ │   Tab    │ │   Tab    │ │  Tab   ││
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘ └────────┘│
└─────────────────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    LOGIQUE MÉTIER                            │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐         │
│  │   Excel      │ │  Dashboard   │ │   Database   │         │
│  │  Importer    │ │  Calculator  │ │   Manager    │         │
│  └──────────────┘ └──────────────┘ └──────────────┘         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    DONNÉES                                   │
│  ┌──────────────┐                 ┌──────────────┐          │
│  │  Fichier     │ ───import────▶  │   SQLite     │          │
│  │   Excel      │                 │   (cache.db) │          │
│  └──────────────┘                 └──────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

---

## Modules principaux

### 1. src/core/database.py

**Rôle** : Gestion de la base de données SQLite

**Classe principale** : `Database`

**Méthodes clés** :
```python
class Database:
    def __init__(db_path)          # Connexion à la base
    def _create_tables()           # Création du schéma
    def clear_all()                # Vide la base (avant import)
    def insert_project(data)       # Insère un projet
    def insert_projects_batch(list)# Insertion en lot
    def get_available_weeks()      # Liste des semaines (tri 6 mois glissants)
    def execute_scalar(query)      # Requête retournant une valeur
    def count_total_projects(week) # Total projets pour une semaine
    def count_active_projects(week)# Projets actifs pour une semaine
```

**Tri des semaines (6 mois glissants)** :
```python
def get_available_weeks(self):
    current_week = datetime.now().isocalendar()[1]

    def week_distance(week):
        if week <= current_week:
            return current_week - week
        else:
            return current_week + (52 - week)

    return sorted(weeks, key=week_distance)
```

---

### 2. src/core/excel_parser.py

**Rôle** : Lecture et parsing des fichiers Excel

**Classe principale** : `ExcelParser`

**Méthodes clés** :
```python
class ExcelParser:
    def load_file(path)            # Charge le fichier Excel
    def get_available_weeks()      # Semaines détectées (pattern S\d+)
    def parse_sheet(week_number)   # Parse un onglet de semaine
    def parse_all_weeks()          # Parse toutes les semaines
    def simulate(excel_path)       # Simulation avant import
```

**Gestion des formats S02/S2** :
```python
# Accepte S2, S02, S002
possible_names = [
    f"S{week_number}",        # S2
    f"S{week_number:02d}",    # S02
    f"S{week_number:03d}"     # S002
]
```

**Conversion des données** :
- Dates : JJ/MM/AAAA, AAAA-MM-JJ, "2025-11", "Novembre 2025"
- Booléens : "X", "x" → True
- Statuts : "Actif" → "EN COURS", "Pause" → "PAUSE"

---

### 3. src/core/commercial_parser.py

**Rôle** : Parser du fichier input.xlsx (données commerciales)

**Classe principale** : `CommercialParser`

**Méthodes clés** :
```python
class CommercialParser:
    def load_file(path)           # Charge le fichier input.xlsx
    def parse_sheet(sheet_name)   # Parse l'onglet HUMAN'S
    def calculate_kpis()          # Calcule tous les KPIs commerciaux
    def get_offer_type(offre)     # Catégorise en REGIE ou BUILD
    def get_pipeline_weight(status) # Pondération par statut (0.2 à 1.0)
```

**Pondérations du pipeline** :
```python
PIPELINE_WEIGHTS = {
    'signed': 1.0,    # 100% - Contrat signé
    'agreed': 0.8,    # 80% - Accord verbal
    'likely': 0.5,    # 50% - Probable
    'specul': 0.2,    # 20% - Spéculatif
}
```

---

### 4. src/core/dashboard_calculator.py

**Rôle** : Calcul des indicateurs KPI

**Classe principale** : `DashboardCalculator`

**Méthodes clés** :
```python
class DashboardCalculator:
    def get_all_indicators(week)   # Tous les KPI d'une semaine

    # Comptages
    def _count_total(week)
    def _count_active(week)
    def _count_warning_client(week)
    def _count_warning_internal(week)
    def _count_projects_with_warning(week)
    def _calculate_pct_projects_with_warning(week)

    # Deadlines
    def _count_dlic_this_week(week)
    def _count_dlic_overdue(week)
    def _count_dlic_empty(week)

    # Graphiques
    def get_active_projects_by_bu(week)
    def get_projects_by_manager(week)
    def get_warnings_by_bu(week)
    def get_actions_by_actor(week)

    # Évolution (pour onglet Analyse)
    def get_warnings_evolution()
    def get_warnings_by_month()
```

---

### 4. src/gui/dashboard_tab.py

**Rôle** : Interface du tableau de bord principal

**Sections** :
1. **Header** : Titre + sélecteur de semaine (dropdown)
2. **Actions & Deadlines** : Tuiles KPI compactes
3. **Vue Globale** : Chiffres + graphiques (par BU, par CP)
4. **Actualité Client** : Warnings + graphique + calendrier actions
5. **RDV Client** : Calendrier hebdomadaire

**Événements** :
```python
def load_available_weeks()    # Au démarrage, charge les semaines
def on_week_changed(index)    # Quand l'utilisateur change de semaine
def refresh_dashboard()       # Met à jour tous les KPI et graphiques
```

---

### 6. src/gui/kpi_tab.py

**Rôle** : Onglet KPIs avec indicateurs de santé et commerciaux

**Sections** :
1. **Santé du Portefeuille** : Taux projets sains, Alerte anticipée, Projets à risque, Tendance
2. **Performance Commerciale** : Taux Régie/Build, Pipeline pondéré, Taux réalisation, TJM, Compteurs

**Événements** :
```python
def load_weeks()              # Charge les semaines disponibles
def refresh_kpis()            # Met à jour les KPIs portefeuille
def load_commercial_file()    # Charge input.xlsx
def refresh_commercial_kpis() # Met à jour les KPIs commerciaux
```

---

### 7. src/gui/exploitation_tab.py (NOUVEAU - Janvier 2026)

**Rôle** : Tableau éditable pour modification directe des données

**Classe principale** : `ExploitationTab`

**Colonnes éditables** (13 au total) :
| Champ | Label | Éditable | Type |
|-------|-------|----------|------|
| id_projet | ID | Non | - |
| client_name | Client | Oui | Texte |
| bu | BU | Oui | Texte |
| status | Statut | Oui | Combo (EN COURS, PAUSE, TERMINÉ, À VENIR) |
| project_manager | Chef Projet | Oui | Texte |
| vision_client | Vision Client | Oui | Combo (OK, WARNING, CRITIQUE) |
| vision_internal | Vision Interne | Oui | Combo (OK, WARNING, CRITIQUE) |
| next_actor | Acteur | Oui | Texte |
| action_description | Action | Oui | Texte |
| dlic | DLIC | Oui | Date |
| nps_commercial | NPS Com. | Oui | Entier |
| nps_project | NPS Projet | Oui | Entier |
| description | Description | Oui | Texte |

**Méthodes clés** :
```python
class ExploitationTab:
    def load_weeks()           # Charge les semaines disponibles
    def load_data()            # Charge les projets de la semaine
    def on_cell_changed()      # Détecte les modifications
    def filter_table()         # Filtre par recherche texte
    def save_changes()         # Sauvegarde en base de données
    def add_new_project()      # Ajoute un nouveau projet
```

**Fonctionnalités** :
- Coloration conditionnelle (warnings en rouge/orange, statuts colorés)
- Surlignage jaune des cellules modifiées
- Confirmation avant perte de modifications
- Recherche dynamique multi-colonnes

---

### 8. src/gui/analysis_tab.py

**Rôle** : Graphiques d'évolution des warnings

**Graphiques** :
1. Évolution par semaine (barres Vision Client vs Vision Interne)
2. Évolution par mois (agrégation mensuelle)
3. Ratio warnings / projets actifs (courbe %)

---

## Base de données

### Schéma de la table `projects`

```sql
CREATE TABLE projects (
    -- MÉTADONNÉES
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    week_number INTEGER NOT NULL,
    import_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- IDENTIFICATION (12 champs)
    id_projet INTEGER NOT NULL,
    status TEXT,
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

    -- NPS (2 champs)
    nps_commercial INTEGER,
    nps_project INTEGER,

    -- PILOTAGE (9 champs)
    vision_client TEXT,
    vision_internal TEXT,
    risk_identified TEXT,
    action_description TEXT,
    next_actor TEXT,
    last_client_exchange DATE,
    next_client_exchange DATE,
    dlic DATE,
    dli DATE,

    -- ACTUALITÉS (3 champs)
    news_project TEXT,
    news_commercial TEXT,
    news_technical TEXT,

    -- PLANIFICATION (7 champs)
    data_remarks TEXT,
    next_milestone_date DATE,
    next_milestone_object TEXT,
    remarks_3months TEXT,
    remarks_6months TEXT,
    remarks_1year TEXT,
    commercial_production_goal TEXT,

    -- COMMERCIAL (5 champs)
    days_dispositif_monthly INTEGER,
    dispositif_expandable TEXT,
    days_forfait INTEGER,
    days_to_sign INTEGER,
    start_date DATE,

    -- POTENTIEL (5 champs)
    potential_new_projects BOOLEAN,
    potential_maintenance BOOLEAN,
    potential_hosting BOOLEAN,
    potential_infra BOOLEAN,
    potential_consulting BOOLEAN,

    UNIQUE(id_projet, week_number)
);
```

### Index

```sql
CREATE INDEX idx_week_number ON projects(week_number);
CREATE INDEX idx_status ON projects(status);
CREATE INDEX idx_client_name ON projects(client_name);
CREATE INDEX idx_next_actor ON projects(next_actor);
CREATE INDEX idx_dlic ON projects(dlic);
CREATE INDEX idx_dli ON projects(dli);
```

---

## Flux de données

### Import Excel

```
1. Utilisateur clique "Importer"
       │
       ▼
2. QFileDialog → Sélection fichier
       │
       ▼
3. ExcelImporter.validate_and_simulate()
       │
       ├── ExcelValidator.validate_structure()
       │       └── Vérifie colonnes obligatoires
       │
       └── ExcelParser.simulate()
               └── Parse et calcule indicateurs
       │
       ▼
4. ImportDialog → Affiche résultats simulation
       │
       ▼
5. Si confirmé → ExcelImporter.execute_import()
       │
       ├── Database.clear_all()  (vide la base)
       │
       └── Database.insert_projects_batch()
       │
       ▼
6. Dashboard.refresh() → Mise à jour affichage
```

### Changement de semaine

```
1. Utilisateur change le dropdown
       │
       ▼
2. on_week_changed(index)
       │
       ▼
3. DashboardCalculator.get_all_indicators(week)
       │
       ▼
4. Mise à jour des tuiles KPI
       │
       ▼
5. Mise à jour des graphiques (matplotlib)
```

---

## Configuration

### config/excel_schema.json

```json
{
  "sheet_pattern": "^S\\d+$",
  "header_row": 3,
  "data_start_row": 4,
  "data_end_row": 999,  // OBSOLETE - le parser utilise ws.max_row
  "columns": {
    "A": {"name": "id_projet", "type": "integer", "required": true},
    "B": {"name": "status", "type": "status"},
    "C": {"name": "bu", "type": "string", "required": true},
    "D": {"name": "client_name", "type": "string", "required": true},
    ...
  }
}
```

**IMPORTANT (v0.6.7)** :
- `data_end_row` n'est plus utilise - le parser lit jusqu'a `ws.max_row`
- L'ID projet est genere avec `row_idx + (week * 1000)` car la colonne Number peut avoir des doublons
- Les colonnes sont detectees dynamiquement par mots-cles dans l'en-tete
```

### src/config/settings.py

```python
APP_NAME = "Huco Report"
APP_VERSION = "0.6.6"
COMPANY_NAME = "Humans Connexion"
```

---

## Déploiement

### Mode développement

```bash
# Activer l'environnement virtuel
./venv_new/Scripts/activate

# Lancer l'application
python main.py
```

### Build .exe (PyInstaller)

```bash
# Exécuter le script de build
./BUILD.bat
```

Résultat : `dist/HucoReport/HucoReport.exe`

Le .exe inclut :
- Python embarqué
- Toutes les dépendances
- Fichiers de configuration
- Images et logo
