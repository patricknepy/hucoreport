# Guide Utilisateur - Huco Report

## Démarrage

### Lancer l'application

1. Double-cliquez sur `HucoReport.exe` (ou `LANCER.bat` en développement)
2. L'application s'ouvre en plein écran
3. Si des données existent en base, elles s'affichent automatiquement

### Premier lancement

Au premier lancement :
- La fenêtre peut mettre quelques secondes à apparaître (création du cache de polices)
- Le message "Aucune donnée" s'affiche si aucun fichier n'a encore été importé

---

## Import d'un fichier Excel

### Étape 1 : Ouvrir le fichier

1. Cliquez sur le bouton jaune **"Importer un fichier Excel"**
2. Naviguez vers votre fichier de suivi GDP
3. Sélectionnez le fichier `.xlsx`

### Étape 2 : Validation et simulation

Une fenêtre de simulation s'affiche avec :

- **Structure Excel** : Validation des colonnes et onglets
- **Indicateurs de la dernière semaine** :
  - DLIC cette semaine
  - DLIC dépassées
  - % Dossiers actifs avec acteur

### Étape 3 : Confirmer l'import

- Si les indicateurs semblent cohérents → Cliquez **"Confirmer l'import"**
- Si quelque chose semble anormal → Cliquez **"Annuler"**

### Après l'import

- Le dashboard se met à jour automatiquement
- La dernière semaine est sélectionnée
- Les graphiques affichent les nouvelles données

---

## Le Dashboard

### En-tête

- **Sélecteur de semaine** : Dropdown pour changer de semaine
  - Format : S04, S03, S02, S01, S52, S51...
  - La plus récente est en haut

### Section "Actions & Deadlines"

| Tuile | Description |
|-------|-------------|
| **% Dossiers en warning** | Pourcentage de projets actifs avec au moins un warning |
| **DLIC à traiter** | DLIC de la semaine en cours + dépassées |
| **DLI à traiter** | DLI de la semaine en cours + dépassées |
| **DLIC dépassées** | DLIC antérieures à aujourd'hui |
| **DLI dépassées** | DLI antérieures à aujourd'hui |
| **DLIC vides** | Projets actifs sans DLIC définie |

### Section "Vue Globale"

**Tuiles KPI** :
- Total projets
- Projets actifs
- Dispositif mensuel (total jours)
- Augmentables (dispositifs pouvant être étendus)

**Graphiques** :
- Projets actifs par BU
- Projets par Chef de projet

### Section "Actualité Client"

**Tuiles KPI** :
- Warning Vision Client (le client râle)
- Warning Vision Interne (le CP s'inquiète)

**Graphiques** :
- Warnings par BU
- Actions par acteur (qui doit agir)

### Section "RDV Client"

Calendrier hebdomadaire affichant :
- Les rendez-vous clients programmés
- Organisés par jour (Lundi → Dimanche)

---

## L'onglet KPIs

### Santé du Portefeuille

Cette section affiche les indicateurs de santé globale :
- **Taux projets sains** : Pourcentage de projets sans warning
- **Alerte anticipée** : Projets avec risques identifiés
- **Projets à risque** : Projets en warning critique
- **Tendance** : Évolution par rapport à la semaine précédente

### Performance Commerciale

Pour afficher les KPIs commerciaux :
1. Cliquez sur **"Charger fichier commercial"**
2. Sélectionnez le fichier `input.xlsx`
3. Les indicateurs s'affichent :
   - Taux Régie/Build
   - Pipeline pondéré (selon statut : signed, agreed, likely, specul)
   - TJM moyen
   - Compteurs d'offres

---

## L'onglet Exploitation

### Vue d'ensemble

L'onglet Exploitation permet de **modifier directement les données** sans passer par un nouvel import Excel.

### Interface

| Élément | Description |
|---------|-------------|
| **Sélecteur de semaine** | Choisir la semaine à afficher |
| **Barre de recherche** | Filtrer par client, BU, chef de projet |
| **Tableau éditable** | 13 colonnes modifiables |
| **Bouton Sauvegarder** | Enregistre les modifications en base |
| **Bouton + Nouveau projet** | Ajoute un projet vide |

### Modifier une donnée

1. **Double-cliquez** sur la cellule à modifier
2. Saisissez la nouvelle valeur
3. La cellule devient **jaune** (modification non sauvegardée)
4. Cliquez sur **"Sauvegarder les modifications"**

### Colonnes éditables

| Colonne | Type | Valeurs possibles |
|---------|------|-------------------|
| Client | Texte libre | - |
| BU | Texte libre | - |
| Statut | Liste déroulante | EN COURS, PAUSE, TERMINÉ, À VENIR |
| Chef Projet | Texte libre | - |
| Vision Client | Liste déroulante | OK, WARNING, CRITIQUE |
| Vision Interne | Liste déroulante | OK, WARNING, CRITIQUE |
| Acteur | Texte libre | - |
| Action | Texte libre | - |
| DLIC | Date | JJ/MM/AAAA |
| NPS Com. | Nombre | -100 à +100 |
| NPS Projet | Nombre | -100 à +100 |

### Coloration des cellules

- **Rouge clair** : Vision Client en WARNING
- **Orange clair** : Vision Interne en WARNING
- **Vert clair** : Vision OK
- **Jaune** : Cellule modifiée (non sauvegardée)
- **Gris** : Cellule non éditable (ID)

### Ajouter un nouveau projet

1. Cliquez sur **"+ Nouveau projet"**
2. Un projet vide est créé avec le statut "EN COURS"
3. Modifiez les valeurs dans le tableau
4. Cliquez sur **"Sauvegarder les modifications"**

### Recherche et filtrage

1. Tapez dans la barre de recherche
2. Le tableau se filtre automatiquement
3. La recherche s'applique sur toutes les colonnes

---

## L'onglet Analyse

### Évolution des Warnings par Semaine

Graphique à barres montrant pour chaque semaine :
- **Orange** : Warnings Vision Client
- **Jaune** : Warnings Vision Interne

Permet de voir si les warnings augmentent ou diminuent.

### Évolution des Warnings par Mois

Agrégation mensuelle des warnings.
Utilise la dernière semaine de chaque mois.

### Ratio Warnings / Projets Actifs

Courbe montrant le pourcentage de projets en warning.
Permet de relativiser : si on a plus de projets, on peut avoir plus de warnings.

### Actualiser les graphiques

Cliquez sur **"Actualiser les graphiques"** pour recharger les données.

---

## Interprétation des indicateurs

### % Dossiers en Warning

| Valeur | Interprétation |
|--------|----------------|
| 0-10% | Excellent - Situation sous contrôle |
| 10-20% | Bon - Quelques points d'attention |
| 20-30% | Attention - Action requise |
| > 30% | Critique - Plan d'action urgent |

### DLIC dépassées

| Valeur | Action |
|--------|--------|
| 0 | Parfait |
| 1-3 | Traiter dans la journée |
| > 3 | Réunion de crise |

### Acteurs identifiés

| % | Interprétation |
|---|----------------|
| > 90% | Excellent - Responsabilités claires |
| 70-90% | Bon - Quelques clarifications à faire |
| < 70% | Attention - Risque de non-suivi |

---

## Actions courantes

### Changer de semaine

1. Cliquez sur le dropdown en haut à droite
2. Sélectionnez la semaine souhaitée
3. Le dashboard se met à jour

### Voir l'historique

1. Allez dans l'onglet **Analyse**
2. Les graphiques montrent l'évolution sur toutes les semaines importées

### Identifier qui doit agir

1. Dans la section "Actualité Client"
2. Regardez le calendrier "Actions par acteur"
3. Chaque colonne = un acteur
4. La colonne rouge "VIDE" = projets sans acteur assigné

### Voir les RDV de la semaine

1. Dans la section "RDV Client"
2. Le calendrier affiche les RDV par jour
3. Cliquez sur un RDV pour voir la fiche projet (à venir)

---

## Conseils d'utilisation

### Fréquence d'import

- **Recommandé** : Une fois par semaine, le lundi matin
- Importez le fichier de la semaine précédente
- Vérifiez les indicateurs avant de confirmer

### Suivi quotidien

- Consultez le dashboard chaque jour
- Priorisez les DLIC dépassées
- Suivez les projets en warning Vision Client

### Réunion hebdo

- Utilisez l'onglet Analyse pour présenter les tendances
- Le graphique d'évolution montre si la situation s'améliore
- Identifiez les BU ou acteurs avec le plus de warnings

### Export et partage

- Pour l'instant : capture d'écran
- À venir : export PDF et Excel
