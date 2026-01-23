# Documentation Métier - Huco Report

## Objectif Principal

**Huco Report** est un tableau de bord pour les **Directeurs de Projet** de Humans Connexion (Groupe HUCO).

L'objectif est de permettre au directeur de projet de **voir en un coup d'œil** :
- Les **projets actifs** en cours
- Le nombre de projets par **Business Unit** (BU)
- Le nombre de projets par **Chef de projet**
- Les **warnings** (alertes) sur les projets
- Les **deadlines** à venir (DLIC, DLI)

## Règles Métier Fondamentales

### 1. Projets Actifs

> **Il est IMPOSSIBLE d'avoir une semaine avec 0 projet actif.**

Si le dashboard affiche 0 projet actif, c'est un bug de données, pas une réalité métier.

Les statuts de projet sont :
- **Actif** → "EN COURS" (normalisé)
- **Pause** → "PAUSE"
- **Non Actif** → "TERMINÉ"
- **À Venir** → "À VENIR"

### 2. Warnings (Alertes)

Deux types de warnings :
- **Vision Client** : "Le client râle" - problème visible côté client
- **Vision Interne** : "Le chef de projet s'inquiète" - problème interne non encore visible du client

Les valeurs possibles :
- `warning` ou `WARNING` → Alerte
- `bon` ou `BON` → Tout va bien
- `à améliorer` → Point d'attention
- Vide → Non défini

### 3. Deadlines

- **DLIC** (Date Limite Interaction Client) : Date à laquelle le client attend une réponse/livraison
- **DLI** (Date Limite Interne) : Date interne pour anticiper la DLIC

### 4. Acteurs

Chaque projet actif devrait avoir un **acteur identifié** (la personne responsable de la prochaine action).

## Structure du Fichier Excel Source

Le fichier Excel "Suivi Hebdo Projet GDP HUCO" contient :
- Un onglet par semaine (S01, S02, ... S52)
- Ligne 3 : En-têtes de colonnes
- Lignes 4-54 : Données des projets

### Colonnes Critiques (PEUVENT CHANGER DE POSITION)

| Champ | Description | Exemples de noms d'en-tête |
|-------|-------------|---------------------------|
| ID Projet | Numéro unique | Number, 0 |
| Statut | État du projet | Statut Projet |
| BU | Business Unit | BU |
| Client | Nom du client | Client |
| Chef de projet | Responsable | Chef de projet |
| Vision Client | Warning client | Vision Client |
| Vision Interne | Warning interne | Vision Interne |
| Acteur | Prochain responsable | Acteur |
| DLIC | Deadline client | DLIC |
| DLI | Deadline interne | DLI Date Limite Interne |

**IMPORTANT** : Les colonnes peuvent être à des positions différentes selon les semaines !

Exemple observé :
- S02, S03, S42-S51 : Vision Client en colonne **P**
- S04 : Vision Client en colonne **N**

Le parser doit détecter les colonnes par leur **nom d'en-tête**, pas par leur position.

## KPIs du Dashboard

### Panneau Principal (Semaine sélectionnée)

1. **Projets actifs** : Nombre total de projets avec statut "EN COURS"
2. **Warnings Vision Client** : Nombre de projets avec vision_client contenant "warning"
3. **Warnings Vision Interne** : Nombre de projets avec vision_internal contenant "warning"
4. **DLIC cette semaine** : Deadlines client tombant dans la semaine en cours
5. **DLIC dépassées** : Deadlines client déjà passées (retard)
6. **% Acteurs identifiés** : Projets actifs ayant un acteur renseigné

### Tableaux de Répartition

1. **Par Business Unit** : Nombre de projets actifs par BU
2. **Par Chef de projet** : Nombre de projets actifs par chef de projet

### Onglet Analyse

Graphiques d'évolution sur les 6 derniers mois :
- Évolution des warnings par semaine
- Évolution des warnings par mois
- Ratio warnings / projets actifs

## Tri des Semaines (6 mois glissants)

Les semaines sont triées de la plus récente à la plus ancienne, avec gestion du passage d'année.

Exemple (si on est en S04 de 2026) :
```
S04, S03, S02, S01, S52, S51, S50, S49, S48, S47...
```

Ceci permet d'avoir toujours les données les plus récentes en premier, même au début d'une nouvelle année.

## Import de Données

### Processus

1. **Validation** : Vérification de la structure du fichier Excel
2. **Simulation** : Affichage des KPIs de validation avant import
3. **Confirmation** : L'utilisateur valide les données
4. **Import** : Sauvegarde en base de données SQLite

### Indicateurs de Validation

Avant l'import, le système affiche :
- DLIC cette semaine
- DLIC dépassées
- % de projets avec acteur identifié

Si ces valeurs semblent incohérentes, l'utilisateur peut annuler l'import.

## Gestion des Erreurs de Données

### Colonnes manquantes

Si une colonne critique n'est pas trouvée (ex: Vision Client), le système :
1. Log un warning
2. Continue l'import avec la valeur NULL
3. Affiche 0 dans le dashboard pour ce KPI

### Données incohérentes

Si le dashboard affiche des valeurs impossibles (0 projets actifs, 0% warnings alors qu'il y en a), vérifier :
1. Que le fichier Excel a bien été réimporté après les corrections
2. Que les colonnes sont bien détectées (voir les logs)
3. Vider le cache (`data/cache.db`) et réimporter
