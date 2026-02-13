# Dictionnaire de Données - Huco Report

## Table `projects`

Cette table stocke tous les projets importés depuis le fichier Excel.
Chaque ligne = un projet pour une semaine donnée.

---

## Colonnes de métadonnées

| Colonne | Type | Description |
|---------|------|-------------|
| `id` | INTEGER | Identifiant auto-incrémenté (clé primaire) |
| `week_number` | INTEGER | Numéro de semaine (1-53) |
| `import_date` | TIMESTAMP | Date et heure de l'import |

---

## Groupe 1 : Identification du projet

| Colonne | Colonne Excel | Type | Obligatoire | Description |
|---------|---------------|------|-------------|-------------|
| `id_projet` | A | INTEGER | Oui | Numéro unique du projet |
| `status` | B | TEXT | Non | Statut : EN COURS, PAUSE, TERMINÉ, À VENIR |
| `bu` | C | TEXT | Oui | Business Unit |
| `client_name` | D | TEXT | Oui | Nom du client |
| `description` | E | TEXT | Non | Description du projet |
| `project_manager` | F | TEXT | Non | Chef de projet |
| `technical_lead` | G | TEXT | Non | Dév Principal (anciennement Lead technique) |
| `project_director` | H | TEXT | Non | Directeur de projet |
| `project_phase` | I | TEXT | Non | Phase du projet |
| `contract_type` | J | TEXT | Non | Type de contrat |
| `project_code` | K | TEXT | Non | Code projet |
| `days_sold` | L | INTEGER | Non | Nombre de jours vendus |

---

## Groupe 2 : NPS (Net Promoter Score)

| Colonne | Colonne Excel | Type | Contrainte | Description |
|---------|---------------|------|------------|-------------|
| `nps_commercial` | N | INTEGER | -100 à +100 | NPS côté commercial |
| `nps_project` | O | INTEGER | -100 à +100 | NPS côté projet |

---

## Groupe 3 : Pilotage

| Colonne | Colonne Excel | Type | Description |
|---------|---------------|------|-------------|
| `vision_client` | N | TEXT | Vision client : "bon", "WARNING !", etc. |
| `vision_internal` | O | TEXT | Vision interne : "bon", "WARNING !", etc. |
| `comment_vision_client` | P | TEXT | Commentaire vision client (nouveau) |
| `comment_vision_internal` | Q | TEXT | Commentaire vision interne (nouveau) |
| `risk_identified` | - | TEXT | Risques identifiés |
| `action_description` | R | TEXT | Description de l'action en cours |
| `next_actor` | S | TEXT | Prochain acteur (qui doit agir) |
| `last_client_exchange` | T | DATE | Dernier échange client |
| `next_client_exchange` | U | DATE | Prochain échange client prévu |
| `dlic` | W | DATE | Date Limite Interne Client |
| `dli` | X | DATE | Date Limite Interne |
| `upsell` | AA | TEXT | Potentiel Upsell (nouveau) |
| `crosssell` | AB | TEXT | Potentiel Cross-sell (nouveau) |

---

## Groupe 4 : Actualités

| Colonne | Colonne Excel | Type | Description |
|---------|---------------|------|-------------|
| `news_project` | Y | TEXT | Actualité projet |
| `news_commercial` | Z | TEXT | Actualité commerciale |
| `news_technical` | AA | TEXT | Actualité technique |

---

## Groupe 5 : Planification & Remarques

| Colonne | Colonne Excel | Type | Description |
|---------|---------------|------|-------------|
| `data_remarks` | AB | TEXT | Remarques sur les données |
| `next_milestone_date` | AC | DATE | Date du prochain jalon |
| `next_milestone_object` | AD | TEXT | Objet du prochain jalon |
| `remarks_3months` | AE | TEXT | Remarques à 3 mois |
| `remarks_6months` | AF | TEXT | Remarques à 6 mois |
| `remarks_1year` | AG | TEXT | Remarques à 1 an |
| `commercial_production_goal` | AH | TEXT | Objectif commercial/production |

---

## Groupe 6 : Commercial & Production

| Colonne | Colonne Excel | Type | Description |
|---------|---------------|------|-------------|
| `days_dispositif_monthly` | AI | INTEGER | Jours dispositif mensuels |
| `dispositif_expandable` | AS | TEXT | Dispositif augmentable : "oui", "oui+", "non" |
| `days_forfait` | AJ | INTEGER | Jours forfait |
| `days_to_sign` | AK | INTEGER | Jours à signer |
| `start_date` | AL | DATE | Date de début |

---

## Groupe 7 : Potentiel commercial

| Colonne | Colonne Excel | Type | Description |
|---------|---------------|------|-------------|
| `potential_new_projects` | AM | BOOLEAN | Potentiel nouveaux projets |
| `potential_maintenance` | AN | BOOLEAN | Potentiel maintenance |
| `potential_hosting` | AO | BOOLEAN | Potentiel hébergement |
| `potential_infra` | AP | BOOLEAN | Potentiel infrastructure |
| `potential_consulting` | AQ | BOOLEAN | Potentiel consulting |

---

## Valeurs spéciales

### Statuts (colonne `status`)

| Valeur Excel | Valeur normalisée |
|--------------|-------------------|
| Actif, actif, ACTIF | EN COURS |
| Pause, pause, En pause | PAUSE |
| Non Actif, Terminé, Fini | TERMINÉ |
| À venir, A venir | À VENIR |
| (vide) | (vide) |

### Warnings (colonnes `vision_client`, `vision_internal`)

| Valeur Excel | Signification |
|--------------|---------------|
| WARNING ! | Alerte |
| warning | Alerte |
| bon | Pas d'alerte |
| (vide) | Non renseigné |

La détection utilise : `LIKE '%warning%'` (insensible à la casse)

### Dispositif augmentable (colonne `dispositif_expandable`)

| Valeur | Signification |
|--------|---------------|
| oui | Peut être augmenté |
| oui+ | Peut être significativement augmenté |
| non | Ne peut pas être augmenté |

Le comptage utilise : `LIKE '%oui%'`

### Booléens (potentiels)

| Valeur Excel | Valeur base |
|--------------|-------------|
| X, x | 1 (True) |
| (vide), autres | 0 (False) |

---

## Contraintes

### Clé unique

```sql
UNIQUE(id_projet, week_number)
```

Un projet ne peut apparaître qu'une seule fois par semaine.

### Champs obligatoires

Pour qu'une ligne soit importée, elle doit avoir :
- `id_projet` (colonne A) non vide
- `bu` (colonne C) non vide
- `client_name` (colonne D) non vide

---

## Index

| Index | Colonnes | Utilisation |
|-------|----------|-------------|
| `idx_week_number` | week_number | Filtrage par semaine |
| `idx_status` | status | Filtrage par statut |
| `idx_client_name` | client_name | Recherche par client |
| `idx_next_actor` | next_actor | Groupement par acteur |
| `idx_dlic` | dlic | Filtrage deadlines |
| `idx_dli` | dli | Filtrage deadlines |
| `idx_import_date` | import_date | Tri par date d'import |
| `idx_week_status` | week_number, status | Comptage projets actifs |
| `idx_week_client` | week_number, client_name | Recherche client par semaine |

---

## Requêtes courantes

### Compter les projets actifs

```sql
SELECT COUNT(*) FROM projects
WHERE week_number = 4 AND status = 'EN COURS'
```

### Compter les warnings Vision Client

```sql
SELECT COUNT(*) FROM projects
WHERE week_number = 4
AND status = 'EN COURS'
AND LOWER(vision_client) LIKE '%warning%'
```

### Projets avec DLIC dépassée

```sql
SELECT * FROM projects
WHERE week_number = 4
AND status = 'EN COURS'
AND dlic < date('now')
```

### Actions par acteur (warnings uniquement)

```sql
SELECT next_actor, COUNT(*) as count
FROM projects
WHERE week_number = 4
AND status = 'EN COURS'
AND (LOWER(vision_client) LIKE '%warning%'
     OR LOWER(vision_internal) LIKE '%warning%')
GROUP BY next_actor
```
