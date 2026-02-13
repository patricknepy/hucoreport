# Documentation Metier - Huco Report

## Objectif Principal

**Huco Report** est un tableau de bord pour les **Directeurs de Projet** de Humans Connexion (Groupe HUCO).

L'objectif est de permettre au directeur de projet de **voir en un coup d'oeil** :
- Les **projets actifs** en cours
- Le nombre de projets par **Business Unit** (BU)
- Le nombre de projets par **Chef de projet**
- Les **warnings** (alertes) sur les projets
- Les **deadlines** a venir (DLIC, DLI)

---

## Fiches KPI - Indicateurs Cles

### 1. PROJETS ACTIFS

| Champ | Valeur |
|-------|--------|
| **Label** | Projets Actifs |
| **Description** | Nombre total de projets avec statut "EN COURS" |
| **Calcul** | `COUNT(*) WHERE status = 'EN COURS'` |
| **Source Excel** | Colonne B (Statut Projet) = "Actif" |
| **Regle metier** | Un projet actif doit TOUJOURS avoir un chef de projet et un acteur identifies |
| **Alerte** | Si 0 projet actif = BUG (impossible en realite) |

---

### 2. WARNINGS VISION CLIENT

| Champ | Valeur |
|-------|--------|
| **Label** | Warnings Vision Client |
| **Description** | "Le client rale" - Probleme visible cote client |
| **Calcul** | `COUNT(*) WHERE vision_client LIKE '%warning%' AND status = 'EN COURS'` |
| **Source Excel** | Colonne variable (detectee par en-tete "Vision Client") |
| **Valeurs possibles** | WARNING, BON, A AMELIORER, NON DEFINI, vide |
| **Couleur** | Rouge (#FF5722) |

---

### 3. WARNINGS VISION INTERNE

| Champ | Valeur |
|-------|--------|
| **Label** | Warnings Vision Interne |
| **Description** | "Le chef de projet s'inquiete" - Probleme interne non visible du client |
| **Calcul** | `COUNT(*) WHERE vision_internal LIKE '%warning%' AND status = 'EN COURS'` |
| **Source Excel** | Colonne variable (detectee par en-tete "Vision Interne") |
| **Valeurs possibles** | WARNING, BON, A AMELIORER, NON DEFINI, vide |
| **Couleur** | Orange (#FF9800) |

---

### 4. % DOSSIERS EN WARNING

| Champ | Valeur |
|-------|--------|
| **Label** | % Dossiers en Warning |
| **Description** | Pourcentage de projets actifs ayant au moins un warning |
| **Calcul** | `(Nb dossiers avec warning / Nb projets actifs) * 100` |
| **Regle metier** | Un dossier avec 2 warnings (Client + Interne) compte pour 1 seul dossier |
| **Echelle** | 0% a 100% |
| **Seuils** | Vert < 20%, Orange 20-40%, Rouge > 40% |

---

### 5. DLIC (Date Limite Interaction Client)

| Champ | Valeur |
|-------|--------|
| **Label** | DLIC |
| **Description** | Date a laquelle le client attend une reponse/livraison |
| **Source Excel** | Colonne variable (detectee par en-tete "DLIC") |
| **Sous-indicateurs** | |
| - DLIC cette semaine | Deadlines tombant dans la semaine en cours |
| - DLIC depassees | Deadlines deja passees (retard) |
| - DLIC vides | Projets actifs sans DLIC definie |
| **Couleur alerte** | Rouge pour depassees |

---

### 6. DLI (Date Limite Interne)

| Champ | Valeur |
|-------|--------|
| **Label** | DLI |
| **Description** | Date interne pour anticiper la DLIC |
| **Source Excel** | Colonne variable (detectee par en-tete "DLI") |
| **Regle metier** | DLI doit etre AVANT la DLIC pour permettre l'anticipation |

---

### 7. ACTEUR (Prochain Acteur)

| Champ | Valeur |
|-------|--------|
| **Label** | Acteur |
| **Description** | Personne responsable de la prochaine action |
| **Source Excel** | Colonne variable (detectee par en-tete "Acteur") |
| **Indicateur derive** | % projets avec acteur identifie |
| **Regle metier** | Chaque projet actif DOIT avoir un acteur |

---

### 8. CHEF DE PROJET

| Champ | Valeur |
|-------|--------|
| **Label** | Chef de projet |
| **Description** | Responsable du projet |
| **Source Excel** | Colonne G (Chef de projet) |
| **Graphique** | Repartition des projets actifs par chef de projet |
| **Regle metier** | Un chef de projet ne peut pas avoir 0 projet actif affiche |

---

### 9. BUSINESS UNIT (BU)

| Champ | Valeur |
|-------|--------|
| **Label** | BU |
| **Description** | Unite metier (BU DEV SPE, BU ERP/CRM/BI, BU WEB/E-COM) |
| **Source Excel** | Colonne C (BU) |
| **Graphique** | Repartition des projets actifs par BU |

---

## Structure du Fichier Excel Source

### Format General
- **Nom du fichier** : Suivi Hebdo Projet GDP HUCO (ou nouveau.xlsx)
- **Un onglet par semaine** : S01, S02, ... S52 (ou S1, S2...)
- **Ligne 3** : En-tetes de colonnes
- **Lignes 4 a max_row** : Donnees des projets (SANS limite fixe)
- **ATTENTION** : Certains onglets ont PLUSIEURS SECTIONS avec numerotation qui redemarre a 1

### Colonnes Critiques (Positions Variables)

| Champ DB | En-tetes possibles | Type |
|----------|-------------------|------|
| id_projet | Number, 0 | INTEGER |
| status | Statut Projet | TEXT |
| bu | BU | TEXT |
| client_name | Client | TEXT |
| project_manager | Chef de projet | TEXT |
| vision_client | Vision Client | TEXT |
| vision_internal | Vision Interne | TEXT |
| next_actor | Acteur | TEXT |
| dlic | DLIC | DATE |
| dli | DLI Date Limite Interne | DATE |

**IMPORTANT** : Les colonnes peuvent etre a des positions differentes selon les semaines. Le parser detecte les colonnes par leur **nom d'en-tete**, pas par leur position.

### Cas Particuliers

1. **Erreur #VALUE!** dans la colonne Number
   - Certaines semaines (S48, S50, S51) ont des erreurs de formule
   - Le parser genere automatiquement un ID unique

2. **Colonnes manquantes**
   - Si une colonne critique n'est pas trouvee, le parser log un warning
   - La valeur sera NULL en base de donnees

---

## Tri des Semaines (6 mois glissants)

Les semaines sont triees de la plus recente a la plus ancienne, avec gestion du passage d'annee.

**Exemple** (si on est en S04 de 2026) :
```
S04, S03, S02, S01, S52, S51, S50, S49, S48, S47...
```

**Algorithme** :
```python
def week_distance(week, current_week):
    if week <= current_week:
        return current_week - week  # Meme annee
    else:
        return current_week + (52 - week)  # Annee precedente
```

---

## Regles Metier Fondamentales

### Impossibilites (indiquent un bug si observees)
1. **0 projet actif** pour une semaine donnee
2. **0 projet par chef de projet** (si le chef de projet existe)
3. **100% de warnings** sur une longue periode

### Coherences attendues
1. Nombre de projets actifs stable (+/- 10%) d'une semaine a l'autre
2. % warnings generalement entre 10% et 40%
3. Chaque projet actif a un acteur identifie

---

## Graphiques de l'Onglet Analyse

### 1. Warnings par Semaine
- **Type** : Barres groupees
- **Donnees** : Warning Client (rouge) + Warning Interne (orange)
- **Echelle Y** : Nombre de projets

### 2. Projets Actifs par Semaine
- **Type** : Barres + ligne de tendance
- **Donnees** : Nombre de projets actifs
- **Echelle Y** : 0 a 100

### 3. % Dossiers en Warning
- **Type** : Ligne (axe 1) + Ligne projets actifs (axe 2)
- **Donnees** : % de dossiers avec au moins 1 warning
- **Echelle Y1** : 0% a 100%
- **Echelle Y2** : 0 a 100 (projets actifs)

### 4. Warnings par Mois
- **Type** : Barres groupees
- **Donnees** : Agregation mensuelle des warnings
- **Echelle Y** : Nombre de projets

---

## Import de Donnees

### Processus en 3 etapes
1. **Validation** : Verification de la structure du fichier Excel
2. **Simulation** : Affichage des KPIs de validation avant import
3. **Import** : Sauvegarde en base de donnees SQLite

### Indicateurs de Validation (avant import)
- DLIC cette semaine : X
- DLIC depassees : Y
- % projets avec acteur : Z%

Si ces valeurs semblent incoherentes, l'utilisateur peut annuler l'import.

---

## Historique des Modifications

| Date | Version | Modifications |
|------|---------|--------------|
| 2026-01-23 | 1.0 | Version initiale |
| 2026-01-23 | 1.1 | Detection dynamique des colonnes |
| 2026-01-23 | 1.2 | Correction ID #VALUE!, graphiques ameliores |
| 2026-01-26 | 1.3 | Suppression limite ligne 54, lecture jusqu'a max_row |
| 2026-01-26 | 1.4 | ID unique base sur row_idx (colonnes Number peuvent avoir doublons) |
| 2026-01-26 | 1.5 | Correction comptage "Non Actif" qui matchait "Actif" |
| 2026-02-06 | 1.6 | Ajout onglets CDP et Warnings |

---

## Onglet CDP (Chefs de Projet)

### Objectif
Visualiser les performances et la charge de travail de chaque Chef de Projet (CDP).

### KPIs Globaux

| KPI | Description | Calcul |
|-----|-------------|--------|
| **Nombre de CDP** | Nombre total de chefs de projet distincts | `COUNT(DISTINCT project_manager)` |
| **Moy. projets/CDP** | Charge moyenne par CDP | `Total projets actifs / Nombre CDP` |
| **Taux sante moyen** | Moyenne des taux de sante | `AVG(% projets sans warning par CDP)` |
| **CDP avec warnings** | Nombre de CDP ayant au moins 1 projet en warning | `COUNT(CDP avec projects_with_warning > 0)` |
| **Jours dispositif** | Total des jours dispositif mensuels | `SUM(days_dispositif_monthly)` |
| **NPS Com. moy.** | NPS Commercial moyen tous CDP | `AVG(nps_commercial)` |
| **NPS Proj. moy.** | NPS Projet moyen tous CDP | `AVG(nps_project)` |

### Statistiques par CDP (Tableau)

| Colonne | Description |
|---------|-------------|
| **Chef de Projet** | Nom du CDP |
| **Actifs** | Nombre de projets "EN COURS" |
| **Total** | Nombre total de projets (tous statuts) |
| **Pause** | Nombre de projets en pause |
| **Termines** | Nombre de projets termines |
| **A venir** | Nombre de projets a venir |
| **Warn. Client** | Nombre de projets avec warning vision client |
| **Warn. Interne** | Nombre de projets avec warning vision interne |
| **Taux Sante** | % de projets actifs SANS warning |
| **DLIC Dep.** | Nombre de DLIC depassees |
| **DLIC Vides** | Nombre de projets actifs sans DLIC |
| **Taux DLIC** | % de projets actifs avec DLIC renseignee |
| **NPS Com.** | NPS Commercial moyen (colore vert >= 50, jaune >= 0, rouge < 0) |
| **NPS Proj.** | NPS Projet moyen (meme logique couleur) |
| **Jours Disp.** | Total jours dispositif mensuels |

### Formule du Taux de Sante

```
Taux Sante = ((Projets actifs - Projets avec warning) / Projets actifs) * 100
```

**Seuils de couleur** :
- Vert : >= 80%
- Jaune : >= 50% et < 80%
- Rouge : < 50%

### Graphiques de Classement (Semaine selectionnee)

1. **Projets actifs par CDP** : Classement horizontal des CDP par nombre de projets actifs
2. **Taux de sante par CDP** : Classement horizontal des CDP par taux de sante

### Section Evolution (Multi-semaines)

**Filtre CDP** : Permet de selectionner un CDP specifique ou "Tous les CDP" pour voir l'evolution agregee.

**4 graphiques en courbes** :

| Graphique | Description | Couleurs |
|-----------|-------------|----------|
| **Evolution projets actifs** | Nombre de projets actifs par semaine | Bleu |
| **Evolution warnings** | Warnings client + interne par semaine | Rouge (client) + Orange (interne) |
| **Evolution taux de sante** | % projets sans warning par semaine | Vert |
| **Evolution NPS** | NPS Commercial + Projet par semaine | Cyan (com.) + Teal (proj.) |

**Cas d'usage** :
- Voir la charge d'un CDP sur les dernieres semaines
- Detecter une degradation du taux de sante
- Suivre l'evolution de la satisfaction client (NPS)
- Comparer les tendances entre CDP

---

## Onglet Warnings (Synthese)

### Objectif
Afficher une vue consolidee de tous les projets en warning avec les details necessaires pour agir.

### KPIs Resume

| KPI | Description | Couleur |
|-----|-------------|---------|
| **Total Warnings** | Nombre total de projets avec au moins 1 warning | Rouge |
| **Warning Client** | Projets avec uniquement un warning vision client | Orange |
| **Warning Interne** | Projets avec uniquement un warning vision interne | Orange fonce |
| **Les deux** | Projets avec warning client ET interne | Violet |
| **DLIC Depassees** | Projets en warning avec DLIC depassee | Rouge fonce |
| **Sans acteur** | Projets en warning sans acteur identifie | Marron |

### Tableau des Details

| Colonne | Description |
|---------|-------------|
| **Client** | Nom du client |
| **Chef Projet** | Chef de projet responsable |
| **BU** | Business Unit |
| **Type** | Type de warning (Client / Interne / Les deux) |
| **Vision Client** | Commentaire de la vision client |
| **Vision Interne** | Commentaire de la vision interne |
| **Action** | Description de l'action a mener |
| **Acteur** | Personne responsable de l'action |
| **DLIC** | Date limite interaction client |
| **DLI** | Date limite interne |

### Tri par defaut

Les warnings sont tries par :
1. DLIC depassees en premier (urgence)
2. Puis par date DLIC croissante
3. Puis par nom client

### Regles de mise en forme

- **Type warning** : Fond colore selon le type (rose = client, orange = interne, violet = les deux)
- **Acteur vide** : Fond rouge avec texte "VIDE"
- **DLIC depassee** : Fond rouge avec texte rouge
- **DLI depassee** : Fond orange
