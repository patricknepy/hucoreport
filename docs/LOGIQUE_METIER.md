# 📋 Documentation Logique Métier - Huco Report

**Projet** : Humans Connexion - Suivi Hebdomadaire GDP  
**Fichier type** : `Suivi_Hebdo_Projet_GDP_HUCO.xlsx`  
**Date de rédaction** : 29 novembre 2025

---

## 🎯 Objectif Global

Automatiser le traitement du fichier Excel de suivi hebdomadaire des projets GDP (Gestion De Projet) pour générer des rapports personnalisés par acteur et monitorer les deadlines automatiquement.

---

## 📊 Structure du Fichier Excel

### Caractéristiques Générales

- **Format** : `.xlsx` multi-feuilles
- **Nombre de feuilles** : ~30 feuilles
  - Guide de suivi
  - Feuilles hebdomadaires (W34, W35, ..., W48, W49, etc.)
  - Feuilles de synthèse (TCD, S39, S42, S43, etc.)

### Structure des En-têtes

⚠️ **IMPORTANT** : Les vrais en-têtes de colonnes sont en **LIGNE 3** (pas ligne 1)

**Lignes spéciales** :
- **Ligne 1** : Catégories de haut niveau (ex: "NPS", "PROJET", etc.)
- **Ligne 2** : Sous-catégories ou métadonnées
- **Ligne 3** : **VRAIS NOMS DE COLONNES** ← À utiliser pour le mapping

---

## 🔍 Colonnes Importantes & Identification

### Stratégie de Détection Intelligente

Pour chaque colonne importante, utiliser une **triple vérification** :

1. ✅ **Nom exact** en ligne 3
2. ✅ **Synonymes/variations** possibles
3. ✅ **Validation croisée** avec ligne 1 (si applicable)
4. ⚠️ **Position de secours** (si nom introuvable)

---

### 📌 Colonne B : Statut Projet

**Identification** :
- Ligne 3 : `"Statut Projet"` ou `"STATUT PROJET"` (insensible casse)
- Synonymes : `"Status"`, `"État"`, `"Statut"`
- Position secours : Colonne B

**Valeurs possibles** :
- `"EN COURS"` / `"Actif"` / `"En cours"`
- `"EN PAUSE"` / `"Pause"` / `"Stand by"`
- `"TERMINÉ"` / `"Terminé"` / `"Fini"`
- `"À VENIR"` / `"A venir"` / `"Planifié"`

**Utilisation** :
- Dashboard : Compteur de projets par statut
- Filtres : Exclure les projets terminés des alertes
- Rapports : Vue d'ensemble de l'activité

---

### 📌 Colonne T : Prochain Acteur

**Identification** :
- Ligne 3 : `"Prochain acteur"` / `"Prochaine action"` / `"Responsable action"`
- Synonymes : `"Qui doit agir"`, `"En attente de"`
- Position secours : Colonne T

**Valeurs possibles** :
- Noms des collaborateurs de l'équipe
- Exemples : `"Benjamin"`, `"Matthieu"`, `"Alexandre"`, `"Paul"`, etc.
- Peut contenir : `"Client"`, `"Externe"`, `"En attente réponse"`

**Utilisation** :
- **Rapports personnalisés par acteur** : Chaque personne reçoit la liste des projets où elle est attendue
- Filtrage des tâches à faire
- Priorisation des actions

---

### 📌 Colonne U : Prochain Échange avec le Client

**Identification** :
- Ligne 3 : `"Prochain échange avec le client"` / `"RDV client"` / `"Prochain RDV"`
- Synonymes : `"Next meeting"`, `"Date RDV"`, `"Échange prévu"`
- Position secours : Colonne U

**Format** : Date (format Excel ou texte)

**Utilisation** :
- Affichage dans les rapports de suivi
- Coordination avec DLIC (colonne W)
- Planification des échanges

---

### 📌 Colonne W : DLIC (Date Limite d'Interaction Client)

**Identification** :
- Ligne 3 : `"DLIC"` (acronyme exact)
- Ligne 1 : Peut contenir indication supplémentaire
- Synonymes : `"Date limite interaction client"`, `"Deadline client"`
- Position secours : Colonne W

**Définition** :
> Date limite à laquelle on a prévu de revenir vers le client MAXIMUM à cette date. C'est une deadline d'interaction, pas un rendez-vous fixe.

**Différence avec Colonne U** :
- **Colonne U** = Rendez-vous confirmé (date fixe)
- **Colonne W (DLIC)** = Date limite maximale pour reprendre contact

**Utilisation** :
- **Monitoring proactif** : Alertes J-7, J-3, J-1
- **Rapports de deadline** : Projets approchant de leur DLIC
- **Indicateurs de performance** : Respect des délais client

---

### 📌 Colonne X : Date Limite Production

**Identification** :
- Ligne 3 : Nom à confirmer (ex: `"Date limite production"`, `"Deadline prod"`)
- Synonymes : `"DLIP"`, `"Échéance production"`
- Position secours : Colonne X

**Définition** :
> Date limite maximale pour qu'une action de production soit réalisée.

**Utilisation** :
- **Rapports spécifiques pour la production** (Matthieu)
- Monitoring des délais internes
- Alertes de dépassement

---

### 📌 Colonnes N & O : NPS (Net Promoter Score)

**Identification** :
- Colonne N : `"Relation Client Commer."` (NPS Commercial)
- Colonne O : `"Relation Client Projet"` (NPS Projet)

**Format** : Nombre entre -100 et +100

**Plages de score** :
- `-100 à 0` : Mauvaise expérience, clients détracteurs
- `0 à +50` : Expérience moyenne, clients passifs
- `+50 à +100` : Excellente expérience, clients promoteurs

**Utilisation** :
- Dashboard : Indicateur de satisfaction client NPS
- Analyse : NPS moyen par BU, par type de projet
- Rapports : Évolution NPS dans le temps

---

### 📌 Colonnes P & Q : Vision Client & Interne (Actualité)

**Identification** :
- Ligne 1 : Peut contenir indication "NPS" (mais c'est trompeur, ce n'est pas le vrai NPS !)
- Ligne 3 :
  - Colonne P : `"Vision client"`
  - Colonne Q : `"Vision interne"`

**Format** : Texte (valeurs qualitatives)

**Valeurs possibles** :
- `"warning"` ou `"WARNING"` ⚠️ → Alerte, situation à surveiller
- `"bon"` ou `"BON"` ✅ → Situation satisfaisante
- `"à améliorer"` → Nécessite attention
- `"non défini"` → Pas encore évalué
- Vide (cellule vide)

**Utilisation** :
- **Dashboard** : Compteur de projets avec "warning" (vision client et vision interne)
- **Alertes** : Notifier quand un projet passe en "warning"
- **Rapports** : Liste des projets nécessitant attention
- **Différence avec NPS** : Vision qualitative vs score quantitatif

**Important** : Ne pas confondre avec les colonnes N & O qui contiennent le vrai NPS numérique !

---

## 👥 Acteurs & Rôles

### Benjamin
**Rôle** : Direction de Projet  
**Responsabilités** :
- Supervision globale des projets
- Prise de décision stratégique

**Rapports à recevoir** :
- Vue d'ensemble de tous les projets
- Projets en difficulté (NPS négatif, deadlines dépassées)

---

### Matthieu
**Rôle** : Responsable de Production  
**Responsabilités** :
- Gestion de l'équipe de production
- Respect des délais de livraison

**Rapports à recevoir** :
- Projets où il est le "Prochain acteur" (colonne T)
- **Deadlines production** (colonne X) : Tous les projets avec échéances production à J-7, J-3, J-1
- Projets en attente de production

---

### Alexandre
**Rôle** : Service Commercial  
**Responsabilités** :
- Relation client
- Suivi des opportunités commerciales

**Rapports à recevoir** :
- Projets où il est le "Prochain acteur" (colonne T)
- DLIC (colonne W) : Projets nécessitant une interaction client
- Projets en phase avant-vente ou cadrage

---

### Paul
**Rôle** : **Double casquette**
1. Direction Commerciale
2. Direction Générale

**Responsabilités** :
- Vision stratégique commerciale
- Décisions de direction

**Rapports à recevoir** :
- Vue consolidée de l'activité commerciale
- Projets où il est le "Prochain acteur" (colonne T)
- KPIs globaux (NPS, taux de conversion, etc.)

---

## 📅 Gestion des Semaines

### Principe de Sélection Automatique

⚠️ **RÈGLE D'OR** : Toujours analyser la **dernière semaine active** du fichier Excel

**Algorithme de détection** :
```
1. Lister toutes les feuilles du fichier
2. Identifier les feuilles de type "semaine" (format : "du XX au XX - WXX")
3. Extraire le numéro de semaine (W34, W35, ..., W48, etc.)
4. Trier par numéro de semaine décroissant
5. Sélectionner la semaine avec le numéro le plus élevé
```

**Exemples** :
- Si dernière feuille = `"du 25 nov au 29 nov - W48"` → **Sélectionner W48**
- Si nouvelle feuille = `"du 02 déc au 06 déc - W49"` → **Sélectionner W49**

**Logique de fallback** :
- Si aucune feuille "Wxx" détectée → Prendre la dernière feuille (exclure "TCD", "Guide", "Sxx")

---

## 📊 Dashboard - Indicateurs Clés

### 1. Vue d'Ensemble des Projets

**Basé sur Colonne B (Statut Projet)** :

```
┌─────────────────────────────────────┐
│  TOTAL PROJETS : 45                 │
├─────────────────────────────────────┤
│  ✅ EN COURS       : 28  (62%)      │
│  ⏸️ EN PAUSE       : 12  (27%)      │
│  ✔️ TERMINÉS       : 3   (7%)       │
│  📅 À VENIR        : 2   (4%)       │
└─────────────────────────────────────┘
```

### 2. Monitoring des Deadlines

**DLIC (Colonne W) - Interaction Client** :
```
┌─────────────────────────────────────┐
│  🔴 DLIC DÉPASSÉES       : 5        │
│  🟠 DLIC < 3 JOURS       : 8        │
│  🟡 DLIC < 7 JOURS       : 12       │
│  🟢 DLIC > 7 JOURS       : 20       │
└─────────────────────────────────────┘
```

**Production (Colonne X)** :
```
┌─────────────────────────────────────┐
│  🔴 PROD DÉPASSÉE        : 2        │
│  🟠 PROD < 3 JOURS       : 4        │
│  🟡 PROD < 7 JOURS       : 7        │
└─────────────────────────────────────┘
```

### 3. Satisfaction Client (NPS)

**Basé sur Colonnes P & Q** :
```
┌─────────────────────────────────────┐
│  NPS MOYEN CLIENT    : +42          │
│  NPS MOYEN INTERNE   : +38          │
│                                     │
│  Écart moyen         : +4           │
└─────────────────────────────────────┘

Distribution :
🔴 NPS Négatif (-100 à 0)  : 3 projets
🟡 NPS Passif (0 à +50)     : 28 projets
🟢 NPS Promoteur (+50+)     : 14 projets
```

### 4. Répartition par Acteur

**Basé sur Colonne T (Prochain acteur)** :
```
┌─────────────────────────────────────┐
│  Benjamin    : 8 actions en attente │
│  Matthieu    : 12 actions           │
│  Alexandre   : 15 actions           │
│  Paul        : 5 actions            │
│  Client      : 10 en attente client │
└─────────────────────────────────────┘
```

---

## 📄 Rapports Automatisés

### Rapport 1 : Rapport Hebdomadaire Personnalisé par Acteur

**Fréquence** : Chaque lundi matin 8h  
**Destinataires** : Benjamin, Matthieu, Alexandre, Paul

**Contenu pour chaque acteur** :
```
===========================================
RAPPORT HEBDOMADAIRE - [NOM]
Semaine W[XX] du [DATE] au [DATE]
===========================================

📋 VOS ACTIONS EN ATTENTE : [N] projets

[TABLEAU]
Projet | Statut | DLIC | Prochain échange | Priorité | NPS
-------|--------|------|------------------|----------|----
...

🔴 URGENCES (DLIC < 3 jours) :
- [Projet A] - DLIC : [Date]
- [Projet B] - DLIC : [Date]

⚠️ ATTENTION (DLIC < 7 jours) :
- [Projet C] - DLIC : [Date]

📊 VOS INDICATEURS :
- Projets actifs : X
- Taux de respect des DLIC : XX%
- NPS moyen de vos projets : XX

===========================================
```

**Logique de génération** :
1. Filtrer tous les projets où Colonne T = Nom de l'acteur
2. Exclure les projets "TERMINÉS"
3. Trier par DLIC (colonne W) croissante
4. Ajouter indicateurs de couleur selon urgence

---

### Rapport 2 : Rapport Production (Matthieu)

**Fréquence** : Chaque lundi + alertes en temps réel  
**Destinataire** : Matthieu

**Contenu spécifique** :
```
===========================================
RAPPORT PRODUCTION - Matthieu
Semaine W[XX]
===========================================

🏭 DEADLINES PRODUCTION (Colonne X) :

🔴 DÉPASSÉES :
- [Projet] - Deadline : [Date] (⚠️ +3 jours de retard)

🟠 URGENTES (< 3 jours) :
- [Projet] - Deadline : [Date]

🟡 PROCHAINES (< 7 jours) :
- [Projet] - Deadline : [Date]

📋 ACTIONS OÙ VOUS ÊTES ATTENDU (Colonne T) :
[Même logique que rapport personnalisé]

===========================================
```

---

### Rapport 3 : Alertes DLIC Automatiques

**Fréquence** : Quotidienne (vérification à 9h)  
**Destinataire** : Acteur concerné (Colonne T)

**Déclenchement** :
- J-7 : Email d'information
- J-3 : Email d'alerte
- J-1 : Email urgent
- J+1 : Email de dépassement (avec copie à Benjamin)

**Exemple de message (J-3)** :
```
Objet : [ALERTE] DLIC dans 3 jours - Projet [NOM]

Bonjour [ACTEUR],

⚠️ Le projet "[NOM DU PROJET]" nécessite une interaction client 
dans 3 JOURS maximum.

📅 DLIC : [DATE]
📊 Statut : [STATUT]
👤 Prochain acteur : [NOM]
📞 Prochain échange prévu : [DATE si rempli]

[Lien vers le projet dans le fichier Excel]

Action requise : Planifier l'interaction client avant le [DATE]
```

---

### Rapport 4 : Dashboard Direction (Benjamin & Paul)

**Fréquence** : Hebdomadaire + mensuel  
**Destinataires** : Benjamin, Paul

**Contenu** :
- Vue d'ensemble complète (tous les indicateurs)
- Analyse NPS global
- Taux de respect des deadlines
- Projets en difficulté
- Recommandations

---

## 🗄️ Architecture Base de Données

### Pourquoi une Base de Données ?

✅ **Avantages** :
1. **Flexibilité** : Colonnes ajoutées/déplacées → Juste mise à jour du mapping
2. **Historique** : Conservation de l'évolution semaine par semaine
3. **Performance** : Requêtes SQL rapides pour filtres/rapports
4. **Robustesse** : Code ne casse pas si structure Excel change
5. **Évolutivité** : Facile d'ajouter de nouvelles analyses

---

### Schéma de Base de Données Proposé

#### Table `projects`
```sql
CREATE TABLE projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_name TEXT NOT NULL,
    week_number INTEGER NOT NULL,      -- W48, W49, etc.
    import_date TIMESTAMP,
    
    -- Colonnes métier
    status TEXT,                        -- Colonne B
    next_actor TEXT,                    -- Colonne T
    next_client_meeting DATE,           -- Colonne U
    dlic DATE,                          -- Colonne W (Date Limite Interaction Client)
    production_deadline DATE,           -- Colonne X
    nps_client INTEGER,                 -- Colonne P
    nps_internal INTEGER,               -- Colonne Q
    
    -- Métadonnées
    raw_data TEXT,                      -- JSON complet de la ligne (toutes colonnes)
    
    UNIQUE(project_name, week_number)
);
```

#### Table `column_mapping`
```sql
CREATE TABLE column_mapping (
    id INTEGER PRIMARY KEY,
    column_key TEXT UNIQUE,             -- 'status', 'dlic', 'next_actor', etc.
    excel_column_name TEXT,             -- Nom réel trouvé dans le fichier
    excel_column_index INTEGER,         -- Position (A=0, B=1, etc.)
    synonyms TEXT,                      -- JSON array des synonymes
    validation_line1 TEXT,              -- Validation croisée ligne 1
    last_updated TIMESTAMP
);
```

#### Table `alerts`
```sql
CREATE TABLE alerts (
    id INTEGER PRIMARY KEY,
    project_id INTEGER,
    alert_type TEXT,                    -- 'DLIC', 'PRODUCTION', 'NPS'
    severity TEXT,                      -- 'INFO', 'WARNING', 'URGENT', 'CRITICAL'
    alert_date DATE,
    sent BOOLEAN DEFAULT 0,
    sent_at TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id)
);
```

#### Table `reports_history`
```sql
CREATE TABLE reports_history (
    id INTEGER PRIMARY KEY,
    report_type TEXT,                   -- 'WEEKLY_PERSONAL', 'PRODUCTION', 'DASHBOARD'
    recipient TEXT,
    week_number INTEGER,
    generated_at TIMESTAMP,
    sent_at TIMESTAMP,
    file_path TEXT
);
```

---

### Flux de Traitement

```
1. IMPORT EXCEL
   ├─ Détecter dernière semaine active (W48)
   ├─ Identifier ligne des en-têtes (ligne 3)
   ├─ Mapper les colonnes intelligemment
   │  ├─ Recherche par nom exact
   │  ├─ Recherche par synonymes
   │  ├─ Validation croisée ligne 1
   │  └─ Position de secours
   ├─ Sauvegarder mapping dans `column_mapping`
   └─ Importer données dans `projects`

2. ANALYSE & CALCUL
   ├─ Calculer indicateurs dashboard
   ├─ Détecter les alertes (deadlines proches/dépassées)
   └─ Sauvegarder dans `alerts`

3. GÉNÉRATION RAPPORTS
   ├─ Requêtes SQL par acteur
   ├─ Génération PDF/Excel
   ├─ Envoi automatique emails
   └─ Logging dans `reports_history`
```

---

## 🛡️ Gestion de la Flexibilité

### Problème : Colonnes ajoutées/déplacées

**Solution : Système de Mapping Intelligent**

#### Étape 1 : Configuration Initiale (fichier `column_rules.json`)

```json
{
  "status": {
    "preferred_names": ["Statut Projet", "STATUT PROJET", "Status"],
    "synonyms": ["État", "Statut", "State"],
    "fallback_column": "B",
    "validation_line1": null,
    "required": true
  },
  "dlic": {
    "preferred_names": ["DLIC"],
    "synonyms": ["Date limite interaction client", "Deadline client"],
    "fallback_column": "W",
    "validation_line1": null,
    "required": true
  },
  "next_actor": {
    "preferred_names": ["Prochain acteur", "Prochaine action"],
    "synonyms": ["Qui doit agir", "Responsable action"],
    "fallback_column": "T",
    "required": true
  },
  "nps_client": {
    "preferred_names": ["Vision client"],
    "validation_line1": "NPS",
    "fallback_column": "P",
    "required": false
  },
  "nps_internal": {
    "preferred_names": ["Vision interne"],
    "validation_line1": "NPS",
    "fallback_column": "Q",
    "required": false
  }
}
```

#### Étape 2 : Interface de Validation

Lors de l'import, si une colonne importante n'est pas trouvée automatiquement :

```
┌──────────────────────────────────────────────┐
│  ⚠️ Validation Mapping des Colonnes          │
├──────────────────────────────────────────────┤
│                                              │
│  ❌ Colonne "DLIC" non trouvée               │
│                                              │
│  Colonnes détectées dans le fichier :       │
│    [ ] Colonne V : "Date limite client"     │
│    [X] Colonne W : "DLIC nouveau format"    │
│    [ ] Colonne X : "Deadline production"    │
│                                              │
│  👉 Sélectionnez la bonne colonne           │
│                                              │
│  [Valider]  [Utiliser position secours: W]  │
└──────────────────────────────────────────────┘
```

---

## 🚀 Fonctionnalités Futures

### Phase 2
- Export vers Power BI
- Intégration calendrier (Outlook/Google Calendar)
- Notifications push (navigateur)

### Phase 3
- API REST pour consultation externe
- Application mobile de consultation
- Prédictions IA sur les délais

---

## 📝 Notes Importantes

### Points d'Attention

1. **Encodage** : Le fichier Excel peut contenir des caractères accentués → Utiliser `encoding='utf-8'`

2. **Dates** : Vérifier le format des dates Excel (peuvent être en numérique Excel ou texte)

3. **Semaines** : Numéros de semaine peuvent avoir des formats variés :
   - `W48`, `w48`, `S48`, `Semaine 48`
   - Toujours normaliser en extraction

4. **Noms d'acteurs** : Attention aux variations :
   - `"Benjamin"` vs `"Benjamin D."` vs `"Ben"`
   - Créer un dictionnaire de normalisation

5. **Projets terminés** : Ne pas les inclure dans les alertes actives mais les garder pour historique/stats

---

## 🎯 Résumé des Priorités

### Priorité 1 - MVP
- ✅ Import fichier Excel avec mapping intelligent
- ✅ Détection automatique dernière semaine
- ✅ Dashboard avec compteurs (projets par statut)
- ✅ Identification colonnes critiques (B, T, W, P, Q)

### Priorité 2 - Rapports de base
- ✅ Rapport hebdomadaire personnalisé par acteur
- ✅ Alertes DLIC (J-7, J-3, J-1)
- ✅ Rapport production (Matthieu)

### Priorité 3 - Automatisation
- ✅ Planification automatique des envois
- ✅ Monitoring continu des deadlines
- ✅ Historique et statistiques

### Priorité 4 - Optimisation
- ✅ Interface de configuration du mapping
- ✅ Templates de rapports personnalisables
- ✅ Analyses avancées (tendances, prédictions)

---

<p align="center">
  <strong>Documentation créée pour Huco Report - Humans Connexion</strong><br>
  <em>Flexible, robuste et évolutif</em>
</p>

