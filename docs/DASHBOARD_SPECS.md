# 📊 Spécifications Dashboard - Huco Report

**Document Technique**  
**Date** : 29 novembre 2025

---

## 🎯 Objectif

Afficher une vue d'ensemble des indicateurs clés de performance pour la semaine sélectionnée.

---

## 🖥️ Interface Dashboard

### Layout Général

```
┌─────────────────────────────────────────────────────────────┐
│ 📊 DASHBOARD                                                │
│                                                             │
│ Afficher la semaine : [S48 ▼]  ← Dropdown                  │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ 📈 VUE GLOBALE                                              │
│   ┌─────────────────┐  ┌─────────────────┐                │
│   │ Total projets   │  │ Projets actifs  │                │
│   │      51         │  │      35         │                │
│   └─────────────────┘  └─────────────────┘                │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ ⚠️ ACTUALITÉ CLIENT                                         │
│   ┌─────────────────────────────┐  ┌────────────────────┐ │
│   │ Warning Vision Client (P)   │  │ Warning Vision     │ │
│   │           5                 │  │ Interne (Q): 3     │ │
│   └─────────────────────────────┘  └────────────────────┘ │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ 📅 ACTIONS & DEADLINES CETTE SEMAINE                        │
│   • DLIC à traiter (non dépassée)     : 8                  │
│   • DLI à traiter (non dépassée)      : 4                  │
│   • DLIC dépassées                    : 5  🔴              │
│   • DLI dépassées                     : 2  🔴              │
│   • DLIC vides (projets actifs)       : 7  ⚠️              │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ 🤝 RENDEZ-VOUS CLIENT CETTE SEMAINE                         │
│   3 rendez-vous programmés :                                │
│                                                             │
│   ┌─────────────────────────────────────────────┐          │
│   │ • 02/12/2025 - HEMAC            [Voir détail] │          │
│   │ • 04/12/2025 - Proarchives      [Voir détail] │          │
│   │ • 05/12/2025 - MIDI2I           [Voir détail] │          │
│   └─────────────────────────────────────────────┘          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Indicateurs Détaillés

### 1. Vue Globale (3 colonnes)

**Organisation** :
```
[Gauche - Stats]           [Milieu - Graphique]          [Droite - Graphique]
Total projets: 51          📊 Projets actifs par BU      📊 Projets par Chef de projet
Projets actifs: 47         (bâtons bleus)                (bâtons bleus)
Dispositif mensuel: 120j   Ordre alphabétique            Ordre alphabétique
Dispositifs augment.: 15
```

#### **Total Projets**
```sql
SELECT COUNT(*) as total
FROM projects
WHERE week_number = ?;
```

#### **Projets Actifs**
```sql
SELECT COUNT(*) as actifs
FROM projects
WHERE week_number = ?
  AND status = 'EN COURS';
```

#### **Dispositif Mensuel** (NOUVEAU)
```sql
SELECT COALESCE(SUM(days_dispositif_monthly), 0) 
FROM projects 
WHERE week_number = ? 
  AND status = 'EN COURS'
  AND days_dispositif_monthly IS NOT NULL;
```

#### **Dispositifs Augmentables** (NOUVEAU)
```sql
SELECT COUNT(*) 
FROM projects 
WHERE week_number = ? 
  AND status = 'EN COURS'
  AND LOWER(dispositif_expandable) LIKE '%oui%';
```

#### **Projets Actifs par BU** (Graphique)
```sql
SELECT 
    COALESCE(bu, 'Non défini') as bu,
    COUNT(*) as count
FROM projects
WHERE week_number = ?
  AND status = 'EN COURS'
GROUP BY bu
ORDER BY LOWER(bu) ASC;
```

#### **Projets par Chef de Projet** (Graphique)
```sql
SELECT 
    COALESCE(project_manager, 'Non défini') as project_manager,
    COUNT(*) as count
FROM projects
WHERE week_number = ?
  AND status = 'EN COURS'
GROUP BY project_manager
ORDER BY LOWER(project_manager) ASC;
```

---

### 2. Actualité Client (3 colonnes)

**Organisation** :
```
[Gauche - Stats]           [Milieu - Graphique]          [Droite - Graphique]
Warning Vision Client: 5   📊 Warnings par BU            📊 Actions par acteur
Warning Vision Interne: 3  (bâtons orange)               (bâtons orange)
                           Ordre alphabétique            Ordre alphabétique
```

#### **Warning Vision Client (Colonne P)**
```sql
SELECT COUNT(*) as warning_client
FROM projects
WHERE week_number = ?
  AND status = 'EN COURS'
  AND (LOWER(vision_client) LIKE '%warning%' OR vision_client LIKE '%WARNING%');
```

**Note** : Texte exact dans Excel = **"WARNING !"** (majuscules + espace + !)

#### **Warning Vision Interne (Colonne Q)**
```sql
SELECT COUNT(*) as warning_interne
FROM projects
WHERE week_number = ?
  AND status = 'EN COURS'
  AND (LOWER(vision_internal) LIKE '%warning%' OR vision_internal LIKE '%WARNING%');
```

#### **Warnings par BU** (Graphique)
```sql
SELECT 
    COALESCE(bu, 'Non défini') as bu,
    COUNT(*) as count
FROM projects
WHERE week_number = ?
  AND status = 'EN COURS'
  AND (LOWER(vision_client) LIKE '%warning%' OR LOWER(vision_internal) LIKE '%warning%')
GROUP BY bu
ORDER BY LOWER(bu) ASC;
```

#### **Actions par Acteur** (Graphique - Warnings uniquement)
```sql
-- Avec acteur défini
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
ORDER BY LOWER(next_actor) ASC;

-- Sans acteur (VIDE - en rouge)
SELECT COUNT(*) 
FROM projects
WHERE week_number = ?
  AND status = 'EN COURS'
  AND (LOWER(vision_client) LIKE '%warning%' OR LOWER(vision_internal) LIKE '%warning%')
  AND (next_actor IS NULL OR next_actor = '');
```

---

### 3. Actions & Deadlines Cette Semaine

#### **DLIC à traiter cette semaine**
```sql
-- DLIC dans la semaine calendaire actuelle ET non dépassée
SELECT COUNT(*) as dlic_semaine
FROM projects
WHERE week_number = ?
  AND status = 'EN COURS'
  AND dlic IS NOT NULL
  AND dlic >= date('now')  -- Pas encore dépassée
  AND dlic BETWEEN date('now', 'weekday 0', '-6 days')  -- Lundi
                   AND date('now', 'weekday 0')         -- Dimanche
```

**Logique** :
- Semaine calendaire = du lundi au dimanche
- DLIC ≥ aujourd'hui (pas dépassée)
- DLIC entre le lundi et le dimanche de cette semaine

#### **DLI à traiter cette semaine**
```sql
-- Même logique que DLIC mais avec dli
SELECT COUNT(*) as dli_semaine
FROM projects
WHERE week_number = ?
  AND status = 'EN COURS'
  AND dli IS NOT NULL
  AND dli >= date('now')
  AND dli BETWEEN date('now', 'weekday 0', '-6 days')
                  AND date('now', 'weekday 0')
```

#### **DLIC dépassées**
```sql
SELECT COUNT(*) as dlic_depassees
FROM projects
WHERE week_number = ?
  AND status = 'EN COURS'
  AND dlic IS NOT NULL
  AND dlic < date('now');  -- Date passée
```

#### **DLI dépassées**
```sql
SELECT COUNT(*) as dli_depassees
FROM projects
WHERE week_number = ?
  AND status = 'EN COURS'
  AND dli IS NOT NULL
  AND dli < date('now');
```

#### **DLIC vides (projets actifs)**
```sql
SELECT COUNT(*) as dlic_vides
FROM projects
WHERE week_number = ?
  AND status = 'EN COURS'
  AND (dlic IS NULL OR dlic = '');
```

**Interprétation** : Projets actifs sans date limite d'interaction client définie → ⚠️ Problème de suivi

---

### 4. Rendez-vous Client Cette Semaine

#### **Liste des RDV**
```sql
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
ORDER BY next_client_exchange ASC;
```

**Affichage** :
- Date formatée (JJ/MM/AAAA)
- Nom du client (colonne D)
- Bouton "Voir détail" → Fiche projet (à développer plus tard)

---

## 🎨 Éléments Visuels

### Codes Couleur

```python
# Couleurs sémantiques
COLOR_SUCCESS = "#4CAF50"  # Vert
COLOR_WARNING = "#FF9800"  # Orange
COLOR_DANGER = "#F44336"   # Rouge
COLOR_INFO = "#2196F3"     # Bleu
COLOR_NEUTRAL = "#666666"  # Gris
```

**Utilisation** :
- Total projets / Projets actifs → Bleu (info)
- Warning vision client/interne → Orange
- DLIC/DLI dépassées → Rouge
- DLIC vides → Orange
- RDV client → Vert (si présents)

### Icônes

```
📈 Vue globale
⚠️ Warnings
📅 Deadlines
🤝 Rendez-vous
🔴 Dépassé
```

---

## 🔄 Interactions Utilisateur

### Dropdown Semaine

```python
def on_week_changed(self, week_number: int):
    """
    Appelé quand l'utilisateur change de semaine dans le dropdown
    
    Actions :
    1. Mettre à jour self.current_week
    2. Rafraîchir tous les indicateurs
    3. Recharger la liste des RDV
    """
```

**Contenu du dropdown** :
```sql
-- Liste des semaines disponibles en base
SELECT DISTINCT week_number
FROM projects
ORDER BY week_number DESC;
```

**Affichage** : `S48 (Semaine 48)`, `S47 (Semaine 47)`, etc.

**Défaut** : Semaine la plus récente (numéro le plus élevé)

---

### Clic sur RDV Client

```python
def on_rdv_clicked(self, id_projet: int):
    """
    Appelé quand l'utilisateur clique sur un RDV
    
    Pour l'instant : Message "Fiche projet à développer"
    Plus tard : Ouvre fiche détaillée du projet
    """
```

**Fiche détaillée (future)** :
- Actualité Projet (colonne Y)
- Actualité Commerciale (colonne Z)
- Actualité Technique (colonne AA)
- Toutes les infos du projet

---

## 📐 Layout Qt

```python
# src/gui/dashboard_tab.py

class DashboardTab(QWidget):
    
    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # 1. En-tête avec dropdown semaine
        header = self.create_header()
        main_layout.addWidget(header)
        
        # 2. Vue globale (2 cartes côte à côte)
        vue_globale = self.create_vue_globale()
        main_layout.addWidget(vue_globale)
        
        # 3. Actualité client (2 cartes warning)
        actualite = self.create_actualite_client()
        main_layout.addWidget(actualite)
        
        # 4. Actions & Deadlines (liste)
        deadlines = self.create_deadlines_section()
        main_layout.addWidget(deadlines)
        
        # 5. RDV Client (liste cliquable)
        rdv = self.create_rdv_section()
        main_layout.addWidget(rdv)
        
        main_layout.addStretch()
        self.setLayout(main_layout)
```

---

## 🧮 Classe Calculator

```python
# src/core/dashboard_calculator.py

class DashboardCalculator:
    """Calcule tous les indicateurs du dashboard"""
    
    def __init__(self, week_number: int):
        self.week = week_number
        self.db = Database()
    
    def get_all_indicators(self) -> dict:
        """Retourne dictionnaire avec tous les indicateurs"""
        return {
            "total_projets": self._count_total(),
            "projets_actifs": self._count_actifs(),
            "warning_client": self._count_warning_client(),
            "warning_interne": self._count_warning_interne(),
            "dlic_semaine": self._count_dlic_semaine(),
            "dli_semaine": self._count_dli_semaine(),
            "dlic_depassees": self._count_dlic_depassees(),
            "dli_depassees": self._count_dli_depassees(),
            "dlic_vides": self._count_dlic_vides(),
            "rdv_client": self._get_rdv_client()
        }
    
    def _count_total(self) -> int:
        """Compte total projets"""
        query = "SELECT COUNT(*) FROM projects WHERE week_number = ?"
        return self.db.execute_scalar(query, [self.week])
    
    # ... autres méthodes
```

---

## 🎯 Prochaines Étapes

1. ✅ Créer `src/core/database.py` (connexion SQLite)
2. ✅ Créer `src/core/dashboard_calculator.py` (calculs)
3. ✅ Créer `src/gui/dashboard_tab.py` (interface)
4. ⏳ Tester avec données réelles

---

<p align="center">
  <strong>Spécifications Dashboard - Huco Report</strong><br>
  <em>Vue d'ensemble claire et actionnable</em>
</p>

