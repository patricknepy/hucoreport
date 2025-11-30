# 🗄️ Schéma Base de Données - Huco Report

**Document Technique**  
**Base de Données** : SQLite (fichier local `data/cache.db`)  
**Date** : 29 novembre 2025

---

## 🎯 Principe Fondamental

### Base de Données = Miroir du Fichier Excel

```
📁 Fichier Excel
   ├── S45 (51 projets)
   ├── S46 (50 projets)
   ├── S47 (48 projets)
   └── S48 (51 projets)
        ↓
    IMPORT
        ↓
💾 Base de Données
   └── projects (200 lignes = 4 semaines)
```

**À chaque import** :
1. DELETE FROM projects; (tout vider)
2. INSERT toutes les semaines du fichier
3. Base = État exact du fichier Excel

**Historique** : Fichiers Excel sauvegardés, pas en base

---

## 📊 Table Unique : `projects`

### Schéma SQL Complet

```sql
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
    dispositif_expandable BOOLEAN,
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
);
```

---

## 📋 Index pour Performance

```sql
-- Index sur les colonnes fréquemment utilisées
CREATE INDEX IF NOT EXISTS idx_week_number ON projects(week_number);
CREATE INDEX IF NOT EXISTS idx_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_client_name ON projects(client_name);
CREATE INDEX IF NOT EXISTS idx_next_actor ON projects(next_actor);
CREATE INDEX IF NOT EXISTS idx_dlic ON projects(dlic);
CREATE INDEX IF NOT EXISTS idx_dli ON projects(dli);
CREATE INDEX IF NOT EXISTS idx_import_date ON projects(import_date);

-- Index composite pour requêtes dashboard
CREATE INDEX IF NOT EXISTS idx_week_status ON projects(week_number, status);
CREATE INDEX IF NOT EXISTS idx_week_client ON projects(week_number, client_name);
```

---

## 📊 Détail des Champs

### Métadonnées (3 champs)

| Champ | Type | Description | Auto |
|-------|------|-------------|------|
| `id` | INTEGER | Clé primaire unique | ✅ |
| `week_number` | INTEGER | Numéro de semaine (45, 46, 47, 48...) | ✅ |
| `import_date` | TIMESTAMP | Date/heure d'import | ✅ |

### Groupe 1 : Identification Projet (12 champs)

| Champ | Type | NULL | Contrainte | Notes |
|-------|------|------|------------|-------|
| `id_projet` | INTEGER | NON | - | Numéro du projet |
| `status` | TEXT | OUI | 4 valeurs | EN COURS, PAUSE, TERMINÉ, À VENIR |
| `bu` | TEXT | NON | - | Business Unit (obligatoire) |
| `client_name` | TEXT | NON | - | Nom du client (obligatoire) |
| `description` | TEXT | OUI | - | Description du projet |
| `project_manager` | TEXT | OUI | - | Chef de projet |
| `technical_lead` | TEXT | OUI | - | Responsable technique |
| `project_director` | TEXT | OUI | - | Direction projet |
| `project_phase` | TEXT | OUI | - | Phase (AVANT VENTES, CADRAGE, RUN...) |
| `contract_type` | TEXT | OUI | - | Type contrat (FORFAIT, REGIE...) |
| `project_code` | TEXT | OUI | - | Code projet interne |
| `days_sold` | INTEGER | OUI | - | Nombre de jours vendus |

### Groupe 2 : NPS (2 champs)

| Champ | Type | Contrainte | Description |
|-------|------|------------|-------------|
| `nps_commercial` | INTEGER | -100 à +100 | NPS Relation Client Commercial |
| `nps_project` | INTEGER | -100 à +100 | NPS Relation Client Projet |

### Groupe 3 : Pilotage (9 champs)

| Champ | Type | Valeurs possibles | Notes |
|-------|------|-------------------|-------|
| `vision_client` | TEXT | warning, bon, à améliorer, non défini, vide | Actualité/État vision client |
| `vision_internal` | TEXT | warning, bon, à améliorer, non défini, vide | Actualité/État vision interne |
| `risk_identified` | TEXT | - | Risques identifiés |
| `action_description` | TEXT | - | Description action à mener |
| `next_actor` | TEXT | - | Prochain acteur (Benjamin, Matthieu...) |
| `last_client_exchange` | DATE | - | Date dernier échange |
| `next_client_exchange` | DATE | - | Date prochain RDV |
| `dlic` | DATE | - | **Date Limite Interaction Client** |
| `dli` | DATE | - | Date Limite Interne |

### Groupe 4 : Actualités (3 champs)

| Champ | Type | Description |
|-------|------|-------------|
| `news_project` | TEXT | Actualités projet |
| `news_commercial` | TEXT | Actualités commerciales |
| `news_technical` | TEXT | Actualités techniques |

### Groupe 5 : Planification & Remarques (7 champs)

| Champ | Type | Description |
|-------|------|-------------|
| `data_remarks` | TEXT | Remarques pour DATA |
| `next_milestone_date` | DATE | Date prochain jalon |
| `next_milestone_object` | TEXT | Objet du jalon |
| `remarks_3months` | TEXT | Remarques à 3 mois |
| `remarks_6months` | TEXT | Remarques à 6 mois |
| `remarks_1year` | TEXT | Remarques à 1 an |
| `commercial_production_goal` | TEXT | Objectif suivi com/prod |

### Groupe 6 : Commercial & Production (5 champs)

| Champ | Type | Description |
|-------|------|-------------|
| `days_dispositif_monthly` | INTEGER | Nb jours dispositif mensuel |
| `dispositif_expandable` | TEXT | Dispositif augmentable (oui, oui+, non) |
| `days_forfait` | INTEGER | Nb jours au forfait |
| `days_to_sign` | INTEGER | Nb jours à signer |
| `start_date` | DATE | Date de démarrage |

### Groupe 7 : Potentiel Commercial Avenir (5 champs)

| Champ | Type | Description |
|-------|------|-------------|
| `potential_new_projects` | BOOLEAN | Potentiel nouveaux projets |
| `potential_maintenance` | BOOLEAN | Potentiel maintenance |
| `potential_hosting` | BOOLEAN | Potentiel hébergement |
| `potential_infra` | BOOLEAN | Potentiel infrastructure |
| `potential_consulting` | BOOLEAN | Potentiel conseil |

---

## 🔄 Workflow Base de Données

### 1. Création de la Base (au premier lancement)

```python
import sqlite3
from pathlib import Path

# Créer le dossier data si inexistant
Path("data").mkdir(exist_ok=True)

# Connexion (crée le fichier si inexistant)
conn = sqlite3.connect('data/cache.db')
cursor = conn.cursor()

# Créer la table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS projects (
        -- [Schéma complet ci-dessus]
    )
''')

# Créer les index
cursor.execute('CREATE INDEX IF NOT EXISTS idx_week_number ...')
# ... autres index

conn.commit()
conn.close()
```

### 2. Import (écrasement complet)

```python
import sqlite3
import pandas as pd

def import_excel_to_db(excel_file: str):
    """Importe le fichier Excel en écrasant la base"""
    
    # 1. Lire toutes les semaines du fichier
    all_weeks = []  # Liste de (week_number, dataframe)
    
    wb = openpyxl.load_workbook(excel_file)
    for sheet_name in wb.sheetnames:
        if sheet_name.startswith('S') and sheet_name[1:].isdigit():
            week_num = int(sheet_name[1:])
            df = read_sheet(wb[sheet_name])  # Fonction custom
            all_weeks.append((week_num, df))
    
    # 2. Connexion base de données
    conn = sqlite3.connect('data/cache.db')
    cursor = conn.cursor()
    
    try:
        # 3. TRANSACTION : Tout ou rien
        cursor.execute('BEGIN TRANSACTION')
        
        # 4. VIDER LA BASE
        cursor.execute('DELETE FROM projects')
        
        # 5. INSÉRER TOUTES LES SEMAINES
        for week_num, df in all_weeks:
            for _, row in df.iterrows():
                cursor.execute('''
                    INSERT INTO projects (
                        week_number, id_projet, client_name, bu, ...
                    ) VALUES (?, ?, ?, ?, ...)
                ''', (week_num, row['id_projet'], row['client_name'], ...))
        
        # 6. COMMIT
        cursor.execute('COMMIT')
        print(f"✅ Import réussi : {len(all_weeks)} semaines importées")
        
    except Exception as e:
        # ROLLBACK en cas d'erreur
        cursor.execute('ROLLBACK')
        print(f"❌ Erreur import : {e}")
        raise
    
    finally:
        conn.close()
```

### 3. Requêtes Dashboard

```python
def get_dashboard_data(week_number: int):
    """Récupère les données pour le dashboard d'une semaine"""
    
    conn = sqlite3.connect('data/cache.db')
    
    # Statistiques par statut
    stats_status = pd.read_sql_query('''
        SELECT status, COUNT(*) as count
        FROM projects
        WHERE week_number = ?
        GROUP BY status
    ''', conn, params=[week_number])
    
    # Projets par BU
    stats_bu = pd.read_sql_query('''
        SELECT bu, COUNT(*) as count
        FROM projects
        WHERE week_number = ?
        GROUP BY bu
    ''', conn, params=[week_number])
    
    # DLIC urgentes
    dlic_urgent = pd.read_sql_query('''
        SELECT client_name, dlic, next_actor
        FROM projects
        WHERE week_number = ?
          AND dlic IS NOT NULL
          AND dlic <= date('now', '+7 days')
        ORDER BY dlic ASC
    ''', conn, params=[week_number])
    
    conn.close()
    
    return {
        'stats_status': stats_status,
        'stats_bu': stats_bu,
        'dlic_urgent': dlic_urgent
    }
```

### 4. Liste des Semaines Disponibles

```python
def get_available_weeks():
    """Retourne la liste des semaines en base"""
    
    conn = sqlite3.connect('data/cache.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT DISTINCT week_number
        FROM projects
        ORDER BY week_number DESC
    ''')
    
    weeks = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    return weeks  # Ex: [48, 47, 46, 45]
```

---

## 📈 Exemples de Requêtes SQL

### Dashboard Global

```sql
-- Total projets semaine 48
SELECT COUNT(*) FROM projects WHERE week_number = 48;

-- Par statut
SELECT status, COUNT(*) as nb, 
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM projects WHERE week_number = 48), 1) as pct
FROM projects 
WHERE week_number = 48 
GROUP BY status;

-- NPS moyen
SELECT 
    AVG(nps_client) as nps_client_moyen,
    AVG(nps_internal) as nps_interne_moyen
FROM projects 
WHERE week_number = 48 
  AND nps_client IS NOT NULL;
```

### Rapports par Acteur

```sql
-- Projets où Matthieu est attendu
SELECT 
    id_projet,
    client_name,
    status,
    dlic,
    next_client_exchange
FROM projects
WHERE week_number = 48
  AND next_actor = 'Matthieu'
  AND status != 'TERMINÉ'
ORDER BY dlic ASC;
```

### Alertes DLIC

```sql
-- DLIC dans moins de 3 jours
SELECT 
    client_name,
    next_actor,
    dlic,
    julianday(dlic) - julianday('now') as jours_restants
FROM projects
WHERE week_number = 48
  AND dlic IS NOT NULL
  AND julianday(dlic) - julianday('now') BETWEEN 0 AND 3
ORDER BY dlic ASC;

-- DLIC dépassées
SELECT 
    client_name,
    next_actor,
    dlic,
    julianday('now') - julianday(dlic) as jours_retard
FROM projects
WHERE week_number = 48
  AND dlic IS NOT NULL
  AND dlic < date('now')
ORDER BY dlic ASC;
```

---

## 🛠️ Maintenance

### Vider la Base

```sql
-- Supprimer toutes les données
DELETE FROM projects;

-- Réinitialiser l'auto-increment
DELETE FROM sqlite_sequence WHERE name='projects';

-- Vérification
SELECT COUNT(*) FROM projects;  -- Doit retourner 0
```

### Optimiser la Base

```sql
-- Analyser les index
ANALYZE;

-- Nettoyer l'espace
VACUUM;

-- Vérifier l'intégrité
PRAGMA integrity_check;
```

### Taille de la Base

```bash
# Windows PowerShell
ls data/cache.db | Select-Object Length

# Taille attendue : ~500 KB à 2 MB selon nombre de projets
```

---

## 📊 Schéma Visuel

```
┌─────────────────────────────────────────────┐
│           TABLE: projects                   │
├─────────────────────────────────────────────┤
│ 🔑 id (PK AUTO)                             │
│ 📅 week_number → Index                      │
│ ⏰ import_date                               │
│                                             │
│ 📊 IDENTIFICATION (12 champs)               │
│    - id_projet, status, bu, client_name... │
│                                             │
│ 👥 RELATION CLIENT (2 champs)               │
│    - relation_commercial, relation_project  │
│                                             │
│ 🎯 PILOTAGE (9 champs)                      │
│    - nps, dlic, next_actor...               │
│                                             │
│ 📝 ACTUALITÉS (3 champs)                    │
│ 📅 PLANIFICATION (7 champs)                 │
│ 💼 COMMERCIAL (5 champs)                    │
│ 🚀 POTENTIEL (5 champs)                     │
│                                             │
│ TOTAL : 46 champs                           │
└─────────────────────────────────────────────┘
```

---

<p align="center">
  <strong>Schéma SQL pour Huco Report - Humans Connexion</strong><br>
  <em>Simple, robuste et performant</em>
</p>

