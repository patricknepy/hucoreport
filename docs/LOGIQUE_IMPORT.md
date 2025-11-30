# 📥 Logique d'Import - Huco Report

**Document de Spécifications Techniques**  
**Projet** : Humans Connexion - Suivi Hebdomadaire GDP  
**Date** : 29 novembre 2025

---

## 🎯 Objectif

Définir la logique complète d'import du fichier Excel vers la base de données SQLite, avec validation en deux temps :
1. **Simulation** : Validation et prévisualisation
2. **Import réel** : Écrasement complet de la base + insertion de toutes les semaines du fichier

### Tableau Récapitulatif - Types de Données (46 champs)

| Catégorie | Champ Base de Données | Type SQL |
|-----------|----------------------|----------|
| **IDENTIFICATION PROJET (12)** | | |
| | `id_projet` | INTEGER |
| | `status` | TEXT |
| | `bu` | TEXT |
| | `client_name` | TEXT |
| | `description` | TEXT |
| | `project_manager` | TEXT |
| | `technical_lead` | TEXT |
| | `project_director` | TEXT |
| | `project_phase` | TEXT |
| | `contract_type` | TEXT |
| | `project_code` | TEXT |
| | `days_sold` | INTEGER |
| **NPS (2)** | | |
| | `nps_commercial` | INTEGER |
| | `nps_project` | INTEGER |
| **PILOTAGE (9)** | | |
| | `vision_client` | TEXT |
| | `vision_internal` | TEXT |
| | `risk_identified` | TEXT |
| | `action_description` | TEXT |
| | `next_actor` | TEXT |
| | `last_client_exchange` | DATE |
| | `next_client_exchange` | DATE |
| | `dlic` | DATE |
| | `dli` | DATE |
| **ACTUALITÉS (3)** | | |
| | `news_project` | TEXT |
| | `news_commercial` | TEXT |
| | `news_technical` | TEXT |
| **PLANIFICATION (7)** | | |
| | `data_remarks` | TEXT |
| | `next_milestone_date` | DATE |
| | `next_milestone_object` | TEXT |
| | `remarks_3months` | TEXT |
| | `remarks_6months` | TEXT |
| | `remarks_1year` | TEXT |
| | `commercial_production_goal` | TEXT |
| **COMMERCIAL & PRODUCTION (5)** | | |
| | `days_dispositif_monthly` | INTEGER |
| | `dispositif_expandable` | BOOLEAN |
| | `days_forfait` | INTEGER |
| | `days_to_sign` | INTEGER |
| | `start_date` | DATE |
| **POTENTIEL COMMERCIAL (5)** | | |
| | `potential_new_projects` | BOOLEAN |
| | `potential_maintenance` | BOOLEAN |
| | `potential_hosting` | BOOLEAN |
| | `potential_infra` | BOOLEAN |
| | `potential_consulting` | BOOLEAN |
| **MÉTADONNÉES AUTO (3)** | | |
| | `id` | INTEGER (PK AUTO) |
| | `week_number` | INTEGER |
| | `import_date` | TIMESTAMP |

**TOTAL : 46 champs** (43 Excel + 3 métadonnées)

---

## 📊 Structure Fichier Excel Source

### Caractéristiques Générales

```yaml
format: .xlsx (Excel multi-feuilles)
encoding: UTF-8
feuilles: ~30 (W34, W35, ..., S39, S42, S43, S44, S45, S46, S47, S48, etc.)
```

### Onglet Cible

**Règle** : Toujours importer le **dernier onglet Sxx** (numéro de semaine le plus élevé)

**Exemples** :
- Semaine 48 → Onglet `S48`
- Semaine 49 → Onglet `S49`
- Semaine 52 → Onglet `S52`
- Semaine 1 (année suivante) → Nouveau fichier

**Algorithme de détection** :
```python
1. Lister toutes les feuilles du fichier
2. Filtrer celles qui matchent le pattern "S\d+" (S48, S49, etc.)
3. Extraire le numéro (48, 49, etc.)
4. Sélectionner le numéro maximum
5. Si aucun onglet Sxx trouvé → ERREUR BLOQUANTE
```

---

## 📋 Structure de l'Onglet Sxx

### Lignes Spéciales

```
Ligne 1  : Catégories de haut niveau (RISQUE PROJET, etc.)
Ligne 2  : Totaux / Formules (=SUBTOTAL, etc.) - IGNORÉE
Ligne 3  : EN-TÊTES (Number, BU, Client, ...) ← MAPPING DES COLONNES
Ligne 4+ : DONNÉES PROJETS
```

### Plage de Données

**Spécifications attendues** :

```yaml
ligne_entetes: 3
premiere_ligne_data: 4
derniere_ligne_data: ~54 (variable, détection automatique)
nombre_projets_attendu: 40 à 60 (plage normale)
```

**Détection de fin** :
```
STOP l'import quand :
- Colonne C (BU) est vide ET
- Colonne D (Client) est vide
```

---

## 🔑 Champs Obligatoires

### Règle de Validation Primaire

**3 colonnes OBLIGATOIRES** pour qu'une ligne soit considérée comme projet valide :

```yaml
A (id_projet):  NON VIDE, TYPE: INTEGER
C (bu):         NON VIDE, TYPE: TEXT
D (client_name): NON VIDE, TYPE: TEXT
```

**Si un seul de ces champs est vide** → La ligne est **IGNORÉE** (pas une erreur, juste fin des projets)

---

## 📊 Mapping Colonnes Excel → Base de Données

### Colonnes Importées (43 colonnes)

#### Groupe 1 : Identification Projet (12 colonnes)

| Excel | Nom Excel | Base de Données | Type | Obligatoire | Notes |
|-------|-----------|-----------------|------|-------------|-------|
| A | Number | `id_projet` | INTEGER | ✅ OUI | Peut contenir formules (=A4+1) |
| B | Statut Projet | `status` | TEXT | Non | Valeurs autorisées ci-dessous |
| C | BU | `bu` | TEXT | ✅ OUI | Business Unit |
| D | Client | `client_name` | TEXT | ✅ OUI | Nom du client |
| E | Description projet | `description` | TEXT | Non | |
| F | Priorité Entreprise | - | - | ❌ IGNORÉ | |
| G | Chef de projet | `project_manager` | TEXT | Non | |
| H | Resp. Technique | `technical_lead` | TEXT | Non | |
| I | Direction Projet | `project_director` | TEXT | Non | |
| J | Phase du projet | `project_phase` | TEXT | Non | |
| K | Type de contrat | `contract_type` | TEXT | Non | |
| L | Code projet | `project_code` | TEXT | Non | |
| M | Nombre de jours vendus | `days_sold` | INTEGER | Non | |

**Valeurs autorisées pour `status`** :
- `EN COURS`
- `PAUSE`
- `TERMINÉ`
- `À VENIR`

#### Groupe 2 : NPS (2 colonnes)

| Excel | Nom Excel | Base de Données | Type | Contrainte |
|-------|-----------|-----------------|------|------------|
| N | Relation Client Commer. | `nps_commercial` | INTEGER | -100 ≤ N ≤ 100 |
| O | Relation Client Projet | `nps_project` | INTEGER | -100 ≤ O ≤ 100 |

**Échelle NPS** : -100 (détracteurs) à +100 (promoteurs)

#### Groupe 3 : Pilotage (9 colonnes)

| Excel | Nom Excel | Base de Données | Type | Valeurs | Notes |
|-------|-----------|-----------------|------|---------|-------|
| P | Vision Client | `vision_client` | TEXT | warning, bon, à améliorer, non défini, vide | Actualité client |
| Q | Vision Interne | `vision_internal` | TEXT | warning, bon, à améliorer, non défini, vide | Actualité interne |
| R | Risque identifié | `risk_identified` | TEXT | - | |
| S | Action ? | `action_description` | TEXT | - | Descriptif action |
| T | Acteur | `next_actor` | TEXT | - | Prochain acteur |
| U | Date dernier échange client | `last_client_exchange` | DATE | - | |
| V | Date prochain échange client | `next_client_exchange` | DATE | - | |
| W | DLIC | `dlic` | DATE | - | **Date Limite Interaction Client** |
| X | DLI Date Limite Interne | `dli` | DATE | - | Date Limite Interne |

#### Groupe 4 : Actualités (3 colonnes)

| Excel | Nom Excel | Base de Données | Type |
|-------|-----------|-----------------|------|
| Y | Actualité Projet | `news_project` | TEXT |
| Z | Actualité Commerciale | `news_commercial` | TEXT |
| AA | Actualité Technique | `news_technical` | TEXT |

**❌ AB à AI : IGNORÉS** (calculés dans les rapports)

#### Groupe 5 : Planification & Remarques (7 colonnes)

| Excel | Nom Excel | Base de Données | Type |
|-------|-----------|-----------------|------|
| AJ | Remarques pour DATA | `data_remarks` | TEXT |
| AK | Date prochain jalon | `next_milestone_date` | DATE |
| AL | Objet prochain jalon | `next_milestone_object` | TEXT |
| AM | REMARQUES 3 mois | `remarks_3months` | TEXT |
| AN | REMARQUES 6 mois | `remarks_6months` | TEXT |
| AO | REMARQUES 1 an | `remarks_1year` | TEXT |
| AQ | Objectif suivi commercial et production | `commercial_production_goal` | TEXT |

#### Groupe 6 : Commercial & Production (5 colonnes)

| Excel | Nom Excel | Base de Données | Type |
|-------|-----------|-----------------|------|
| AR | NB jours Dispositif mensuel | `days_dispositif_monthly` | INTEGER |
| AS | Dispositif augmentable | `dispositif_expandable` | BOOLEAN |
| AT | NB jours Au forfait | `days_forfait` | INTEGER |
| AU | NB jours À signer | `days_to_sign` | INTEGER |
| AV | Date Démarrage | `start_date` | DATE |

#### Groupe 7 : Potentiel Commercial Avenir (5 colonnes)

| Excel | Nom Excel | Base de Données | Type | Notes |
|-------|-----------|-----------------|------|-------|
| AW | Potentiel nouveaux projets | `potential_new_projects` | BOOLEAN | X = True |
| AX | Potentiel maintenance | `potential_maintenance` | BOOLEAN | X = True |
| AY | Potentiel hébergement | `potential_hosting` | BOOLEAN | X = True |
| AZ | Potentiel infra | `potential_infra` | BOOLEAN | X = True |
| BA | Potentiel conseil | `potential_consulting` | BOOLEAN | X = True |

---

## 🔄 Conversions de Types

### Dates

**Formats Excel acceptés** :
- Format date Excel (nombre de jours depuis 1900)
- Texte : `DD/MM/YYYY`, `YYYY-MM-DD`
- Vide → `NULL`

**Conversion** :
```python
if isinstance(value, datetime):
    return value.strftime('%Y-%m-%d')
elif isinstance(value, str):
    return parse_date(value)  # Essayer plusieurs formats
else:
    return None
```

### Booléens

**Valeurs TRUE** :
- `"X"`, `"x"`, `"OUI"`, `"Oui"`, `"TRUE"`, `"1"`, `1`

**Valeurs FALSE** :
- `""` (vide), `None`, `"NON"`, `"Non"`, `"FALSE"`, `"0"`, `0`

**Conversion** :
```python
def convert_to_bool(value):
    if value in ['X', 'x', 'OUI', 'Oui', 'TRUE', '1', 1, True]:
        return True
    return False
```

### Nombres (INTEGER)

**Sources** :
- Nombres Excel directs
- **Formules Excel** (ex: `=A4+1`) → Évaluées automatiquement par openpyxl
- Textes numériques (ex: `"42"`)

**Conversion** :
```python
def convert_to_int(value):
    if value is None or value == "":
        return None
    try:
        return int(float(value))  # Gérer les .0
    except:
        return None
```

---

## ✅ Règles de Validation

### Niveau 1 : Validation Structure (BLOQUANT)

❌ **Import REFUSÉ si** :

1. **Aucun onglet Sxx trouvé**
2. **Ligne 3 ne contient pas les en-têtes clés** : `Number`, `BU`, `Client`
3. **Moins de 30 projets détectés** (seuil minimum de cohérence)
4. **Plus de 100 projets détectés** (seuil maximum de cohérence)

### Niveau 2 : Validation Données (BLOQUANT)

❌ **Import REFUSÉ si** :

1. **Doublons `id_projet`** dans le fichier
2. **Plus de 20% des projets ont champs obligatoires vides** (A, C, D)
3. **Types de données incompatibles** :
   - Texte dans colonne INTEGER
   - Date invalide (ex: "abc")
4. **Valeurs hors limites** :
   - NPS Commercial/Projet < -100 ou > 100
   - Vision Client/Interne : valeurs autres que (warning, bon, à améliorer, non défini, vide)

### Niveau 3 : Validation Métier (AVERTISSEMENT)

⚠️ **Import AUTORISÉ avec AVERTISSEMENTS** :

1. **Dates DLIC/DLI dépassées** (< date du jour)
2. **Statut invalide** (ni EN COURS, ni PAUSE, ni TERMINÉ, ni À VENIR)
3. **Champs recommandés vides** :
   - `project_manager` vide
   - `next_actor` vide
   - `dlic` vide

---

## 🧪 Simulation d'Import

### Processus de Simulation

```
1. Ouvrir le fichier Excel (lecture seule)
2. Détecter l'onglet Sxx
3. Valider la structure (ligne 3 = en-têtes)
4. Scanner les données (ligne 4 → fin)
5. Appliquer toutes les règles de validation
6. Générer rapport de simulation
7. NE PAS toucher à la base de données
```

### Rapport de Simulation

**Structure JSON** :

```json
{
  "valid": true,
  "onglet_detecte": "S48",
  "week_number": 48,
  "projets_detectes": 51,
  "projets_valides": 51,
  "projets_ignores": 0,
  "ligne_debut": 4,
  "ligne_fin": 54,
  "erreurs_bloquantes": [],
  "avertissements": [
    {
      "type": "DATE_PASSEE",
      "ligne": 12,
      "projet": "HEMAC",
      "champ": "dlic",
      "valeur": "2025-11-15",
      "message": "DLIC dépassée de 14 jours"
    }
  ],
  "preview": [
    {"id_projet": 1, "client": "Proarchives", "bu": "BU DEV SPE"},
    {"id_projet": 2, "client": "MIDI2I", "bu": "BU DEV SPE"},
    {"id_projet": 3, "client": "HEMAC", "bu": "BU ERP / CRM / BI"}
  ],
  "statistiques": {
    "par_statut": {
      "EN COURS": 35,
      "PAUSE": 10,
      "TERMINÉ": 4,
      "À VENIR": 2
    },
    "par_bu": {
      "BU DEV SPE": 15,
      "BU ERP / CRM / BI": 20,
      "BU WEB / E-COM": 16
    },
    "nps_moyen_client": 42,
    "nps_moyen_interne": 38
  }
}
```

### Interface Utilisateur - Rapport de Simulation

```
╔═══════════════════════════════════════════════════════════════╗
║  🔍 SIMULATION IMPORT - Résultats                             ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  📁 Fichier : Suivi_Hebdo_Projet_GDP_HUCO (5).xlsx           ║
║  📊 Onglet  : S48 (Semaine 48)                               ║
║                                                               ║
║  ✅ VALIDATION RÉUSSIE                                        ║
║                                                               ║
║  📈 Projets détectés : 51                                     ║
║     - Valides        : 51                                     ║
║     - Ignorés        : 0                                      ║
║     - Plage lignes   : 4 à 54                                ║
║                                                               ║
║  📊 Répartition :                                             ║
║     - EN COURS  : 35 (69%)                                    ║
║     - PAUSE     : 10 (20%)                                    ║
║     - TERMINÉ   : 4  (8%)                                     ║
║     - À VENIR   : 2  (3%)                                     ║
║                                                               ║
║  ⚠️  3 AVERTISSEMENTS (non bloquants) :                       ║
║     - 3 dates DLIC dépassées                                  ║
║                                                               ║
║  📋 Aperçu (5 premiers projets) :                             ║
║     1  | Proarchives          | BU DEV SPE                    ║
║     2  | MIDI2I               | BU DEV SPE                    ║
║     3  | HEMAC                | BU ERP / CRM / BI             ║
║     4  | Be ys / quantum...   | BU ERP / CRM / BI             ║
║     5  | Allora               | BU ERP / CRM / BI             ║
║                                                               ║
║  ⏱️  Durée simulation : 1.2s                                  ║
║                                                               ║
╠═══════════════════════════════════════════════════════════════╣
║  [✅ Valider et Importer]     [❌ Annuler]                    ║
╚═══════════════════════════════════════════════════════════════╝
```

### Cas d'Erreur Bloquante

```
╔═══════════════════════════════════════════════════════════════╗
║  ❌ SIMULATION IMPORT - ÉCHEC                                 ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  📁 Fichier : Suivi_Hebdo_Projet_GDP_HUCO_OLD.xlsx           ║
║                                                               ║
║  ❌ ERREURS BLOQUANTES (3) :                                  ║
║                                                               ║
║  1. [STRUCTURE] Aucun onglet Sxx trouvé                       ║
║     → Fichier incompatible ou corrompu                        ║
║                                                               ║
║  2. [DONNÉES] 5 doublons détectés :                           ║
║     - Projet ID 12 : présent 2 fois (lignes 15, 28)          ║
║     - Projet ID 23 : présent 2 fois (lignes 26, 41)          ║
║     → Corriger le fichier Excel avant import                  ║
║                                                               ║
║  3. [COHÉRENCE] Seulement 18 projets détectés                 ║
║     → Minimum attendu : 30 projets                            ║
║     → Vérifier l'intégrité du fichier                         ║
║                                                               ║
║  ⚠️  Import impossible. Corriger les erreurs ci-dessus.      ║
║                                                               ║
╠═══════════════════════════════════════════════════════════════╣
║  [🔄 Réessayer avec autre fichier]     [❌ Fermer]            ║
╚═══════════════════════════════════════════════════════════════╝
```

---

## 📥 Import Réel

### Philosophie : Base de Données = Miroir du Fichier Excel

⚠️ **PRINCIPE FONDAMENTAL** : La base de données est **entièrement écrasée** à chaque import.

**Pourquoi ?**
- Base = État actuel du dernier fichier Excel importé
- Pas d'historique en base (historique = fichiers Excel sauvegardés)
- Simplicité et fiabilité maximales

**Historique via Fichiers Excel** :
```
import/
├── Suivi_Hebdo_20251129_1532.xlsx  ← Import aujourd'hui
├── Suivi_Hebdo_20251015_0930.xlsx  ← Import il y a 1 mois
└── Suivi_Hebdo_20250915_1145.xlsx  ← Import il y a 2 mois

Besoin de voir l'état d'il y a 1 mois ?
→ Réimporter le fichier du 15/10
→ Base écrasée = État du 15/10
```

---

### Processus d'Import

**Exécuté UNIQUEMENT si simulation OK** :

```python
1. Renommer et sauvegarder fichier Excel :
   → import/Suivi_Hebdo_AAAAMMJJ_HHMM.xlsx
   
2. Créer transaction SQL (BEGIN)

3. VIDER COMPLÈTEMENT LA BASE :
   DELETE FROM projects;  -- Tout effacer !
   
4. Pour chaque SEMAINE du fichier (S45, S46, S47, S48...) :
   Pour chaque projet de la semaine :
     a. Convertir types
     b. Insérer dans table projects avec week_number
     c. Logger l'insertion

5. Si erreur → ROLLBACK complet (base reste vide)
6. Si succès → COMMIT
7. Générer rapport d'import
```

### Transaction Atomique

```sql
BEGIN TRANSACTION;

-- 1. TOUT VIDER
DELETE FROM projects;

-- 2. IMPORTER TOUTES LES SEMAINES DU FICHIER
-- Semaine 45
INSERT INTO projects (id_projet, client_name, bu, week_number, ...) 
VALUES (1, 'Proarchives', 'BU DEV SPE', 45, ...);
-- ... autres projets S45

-- Semaine 46
INSERT INTO projects (id_projet, client_name, bu, week_number, ...) 
VALUES (1, 'Proarchives', 'BU DEV SPE', 46, ...);
-- ... autres projets S46

-- Semaine 47
-- ...

-- Semaine 48
INSERT INTO projects (id_projet, client_name, bu, week_number, ...) 
VALUES (1, 'Proarchives', 'BU DEV SPE', 48, ...);
-- ... autres projets S48

COMMIT;  -- Ou ROLLBACK si erreur
```

### Gestion des Réimports

**Stratégie** : Écrasement complet sans confirmation

```
À chaque import :
1. Sauvegarder fichier avec date/heure
2. VIDER base complètement (DELETE FROM projects)
3. Réinsérer TOUTES les semaines du nouveau fichier
4. Dashboard affiche les données du dernier import
```

**Pas de question "Remplacer ?"** → Import = toujours écrasement total

---

### Sauvegarde Automatique des Fichiers

**Format de nommage** :
```
Suivi_Hebdo_AAAAMMJJ_HHMM.xlsx
```

**Exemples** :
- `Suivi_Hebdo_20251129_1532.xlsx` (29 nov 2025 à 15h32)
- `Suivi_Hebdo_20251206_0915.xlsx` (6 déc 2025 à 9h15)

**Avantages** :
- Traçabilité complète
- Historique accessible
- Rollback possible (réimporter ancien fichier)

---

## 📊 Métadonnées Auto-Générées

### Champs Ajoutés Automatiquement

```sql
id              INTEGER PRIMARY KEY AUTOINCREMENT  -- Clé primaire auto
week_number     INTEGER NOT NULL                   -- Extrait du nom onglet (48)
import_date     TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Date/heure de l'import
```

**Exemple** :
```
Onglet "S48" → week_number = 48
Import le 29/11/2025 15:32 → import_date = '2025-11-29 15:32:00'

TOUS les projets importés en même temps = même import_date
```

---

## 📊 Dashboard - Sélection de Semaine

### Navigation entre Semaines

**Interface Dashboard** :
```
┌────────────────────────────────────────────┐
│ 📊 DASHBOARD                               │
│                                            │
│ Afficher la semaine : [S48 ▼]  ← Dropdown │
│                       S48 (Semaine 48)     │
│                       S47 (Semaine 47)     │
│                       S46 (Semaine 46)     │
│                       S45 (Semaine 45)     │
│                                            │
│ Total projets : 51                         │
│ EN COURS : 35 | PAUSE : 10 | TERMINÉ : 6  │
└────────────────────────────────────────────┘
```

**Fonctionnement** :
1. **Par défaut** : Semaine la plus récente (S48)
2. **Dropdown** : Liste toutes les semaines présentes en base
3. **Changement** : Rafraîchit tout le dashboard instantanément
4. **Requêtes SQL** : Filtrées par `WHERE week_number = 48`

**Requête SQL exemple** :
```sql
-- Projets de la semaine sélectionnée
SELECT * FROM projects WHERE week_number = 48;

-- Statistiques par statut
SELECT status, COUNT(*) 
FROM projects 
WHERE week_number = 48 
GROUP BY status;
```

---

## 🔍 Logs d'Import

### Structure des Logs

```
logs/import_YYYYMMDD_HHMMSS.log
```

**Contenu** :
```
2025-11-29 15:32:00 - INFO - Début simulation import
2025-11-29 15:32:00 - INFO - Fichier : Suivi_Hebdo_Projet_GDP_HUCO (5).xlsx
2025-11-29 15:32:01 - INFO - Onglet détecté : S48
2025-11-29 15:32:01 - INFO - 51 projets valides détectés
2025-11-29 15:32:02 - WARN - Projet ID 12 : DLIC dépassée (2025-11-15)
2025-11-29 15:32:02 - INFO - Simulation OK
2025-11-29 15:32:05 - INFO - Import réel démarré
2025-11-29 15:32:06 - INFO - 51 projets insérés avec succès
2025-11-29 15:32:06 - INFO - Import terminé (durée: 6.2s)
```

---

## 🎯 Résumé - Checklist Validation

### ✅ Validation Obligatoire (Bloquante)

- [ ] Onglet Sxx trouvé
- [ ] Ligne 3 contient en-têtes clés (Number, BU, Client)
- [ ] 30 ≤ Nombre projets ≤ 100
- [ ] Pas de doublons id_projet
- [ ] Champs obligatoires présents (A, C, D)
- [ ] Types de données valides
- [ ] Contraintes respectées (NPS -100/+100, Vision client/interne valides)

### ⚠️ Validation Recommandée (Avertissements)

- [ ] Dates cohérentes (DLIC/DLI futures)
- [ ] Statuts valides
- [ ] Champs clés remplis (project_manager, next_actor)

### 📥 Import Réel

- [ ] Transaction SQL
- [ ] Rollback si erreur
- [ ] Logging complet
- [ ] Rapport final

---

<p align="center">
  <strong>Document de référence pour l'import Huco Report</strong><br>
  <em>Validation rigoureuse, traçabilité complète</em>
</p>

