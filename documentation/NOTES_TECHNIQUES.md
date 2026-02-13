# Notes Techniques - Problemes Resolus et Pieges a Eviter

**Derniere mise a jour** : 26 Janvier 2026

Ce document recense les problemes rencontres et les solutions appliquees pour faciliter la maintenance future.

---

## 1. Structure du Fichier Excel - ATTENTION

### Le fichier Excel a une structure complexe :

```
Onglet S03 (exemple):
-----------------------
Ligne 3  : En-tetes (Number, Statut Projet, BU, Client, ...)
Ligne 4  : Premier projet (Number = 1)
...
Ligne 27 : Projet (Number = 24)
Ligne 28 : SECTION 2 COMMENCE - Number redémarre a 1 !
Ligne 29 : Projet (Number = 2)
...
Ligne 70+: Donnees peuvent continuer
```

### Problemes identifies :

1. **La colonne Number (A) REDEMARRE a 1** au milieu de certains onglets
   - Consequence : Doublons d'ID si on utilise la colonne Number
   - **Solution** : Toujours utiliser `row_idx + (week_number * 1000)` comme ID unique

2. **Les donnees vont AU-DELA de la ligne 54**
   - Ancienne limite dans le schema : `data_end_row: 54`
   - Realite : Les donnees peuvent aller jusqu'a la ligne 70, 80 ou plus
   - **Solution** : Utiliser `ws.max_row` pour lire dynamiquement

3. **Les colonnes CHANGENT de position selon les semaines**
   - S04 : Vision Client en colonne N
   - S42 : Vision Client en colonne P
   - **Solution** : Detection dynamique par nom d'en-tete (mots-cles)

---

## 2. Regles de Comptage des Projets

### Un projet est valide si :
- Colonne C (BU) est **non vide**
- Colonne D (Client) est **non vide**

### Un projet est "Actif" (EN COURS) si :
- Colonne B (Statut) = "Actif" **exactement**
- ATTENTION : "Non Actif" contient "actif" mais n'est PAS actif !

### Code correct pour verifier le statut :
```python
# MAUVAIS - matche aussi "Non Actif"
if 'actif' in str(statut).lower():

# BON - normalisation exacte
status_mapping = {
    'actif': 'EN COURS',        # Seulement "Actif" exact
    'non actif': 'TERMINE',     # "Non Actif" -> TERMINE
    'pause': 'PAUSE',
}
normalized = str(value).strip().lower()
return status_mapping.get(normalized, value)
```

---

## 3. Emplacement des Fichiers

```
C:\Huco_Report 2\
├── main.py                    # Point d'entree
├── Lancer_HucoReport.bat      # Double-clic pour lancer
├── nouveau.xlsx               # Fichier Excel actuel (peut changer)
│
├── data\
│   └── cache.db               # BASE DE DONNEES SQLITE (pas a la racine!)
│
├── config\
│   └── excel_schema.json      # Schema (data_end_row obsolete)
│
├── src\core\
│   ├── excel_parser.py        # Parsing Excel - FICHIER CRITIQUE
│   ├── database.py            # Gestion SQLite
│   ├── dashboard_calculator.py# Calculs KPI
│   └── paths.py               # get_data_directory() -> data/
│
├── src\gui\
│   ├── main_window.py         # Fenetre principale
│   ├── dashboard_tab.py       # Onglet Dashboard
│   └── analysis_tab.py        # Onglet Analyse (graphiques)
│
└── documentation\             # Cette documentation
```

### ATTENTION : La base de donnees
- Chemin : `C:\Huco_Report 2\data\cache.db` (PAS `C:\Huco_Report 2\cache.db`)
- Defini dans `database.py` via `get_data_directory()`

---

## 4. Bugs Resolus (26 Janvier 2026)

### Bug 1 : Compteur projets actifs faux (37 au lieu de 57)
- **Cause** : Parser limite a ligne 54, donnees vont jusqu'a 70+
- **Solution** : `data_end = ws.max_row` au lieu de `schema['data_end_row']`

### Bug 2 : Projets en double ignores (UNIQUE constraint)
- **Cause** : Colonne Number redemarre a 1 dans certains onglets
- **Solution** : ID = `row_idx + (week_number * 1000)` toujours

### Bug 3 : "Non Actif" compte comme "Actif"
- **Cause** : Test `if 'actif' in statut` matche les deux
- **Solution** : Normalisation exacte avec mapping dictionnaire

### Bug 4 : Colonnes Vision Client/Interne non trouvees
- **Cause** : Position varie selon les semaines (N vs P)
- **Solution** : Detection par mots-cles dans l'en-tete

---

## 5. Comment Debugger les Compteurs

### Verifier le contenu de la base :
```python
import sqlite3
db = sqlite3.connect(r'C:\Huco_Report 2\data\cache.db')
cursor = db.cursor()

# Comptage par semaine
cursor.execute('''
    SELECT week_number, COUNT(*) as total,
           SUM(CASE WHEN status = "EN COURS" THEN 1 ELSE 0 END) as actifs
    FROM projects
    GROUP BY week_number
''')
for row in cursor.fetchall():
    print(f'S{row[0]:02d}: {row[2]} actifs / {row[1]} total')
```

### Verifier le parsing direct :
```python
from src.core.excel_parser import ExcelParser
parser = ExcelParser('config/excel_schema.json')
parser.load_file('nouveau.xlsx')

projects = parser.parse_sheet(3)  # S03
actifs = [p for p in projects if p.get('status') == 'EN COURS']
print(f'S03: {len(actifs)} actifs')
```

### Forcer un reimport :
```python
from src.core.excel_parser import ExcelParser
from src.core.database import Database

parser = ExcelParser('config/excel_schema.json')
parser.load_file('nouveau.xlsx')

db = Database()
db.clear_all()
db.conn.commit()

data = parser.parse_all_weeks()
for week, projects in data.items():
    db.insert_projects_batch(projects)
    db.conn.commit()

db.close()
```

---

## 6. Questions a Poser si Probleme de Comptage

1. **Quel fichier Excel est utilise ?** (nouveau.xlsx, Suivi Hebdo.xlsx, autre?)
2. **Quelle semaine pose probleme ?** (S03, S04, etc.)
3. **Combien de projets actifs attendus ?** (filtrer dans Excel sur "Actif")
4. **La base a-t-elle ete reimportee ?** (verifier date import)
5. **Y a-t-il des sections multiples dans l'onglet ?** (Number qui redemarre a 1)

---

## 7. Lancer l'Application

### En developpement :
```bash
cd "C:\Huco_Report 2"
venv\Scripts\python.exe main.py
```

### Via le lanceur :
Double-clic sur `C:\Huco_Report 2\Lancer_HucoReport.bat`

### Contenu du .bat :
```batch
@echo off
cd /d "C:\Huco_Report 2"
start "" "venv\Scripts\pythonw.exe" "main.py"
```

---

## 8. GitHub

- **Repository** : https://github.com/patricknepy/hucoreport
- **Branche principale** : main

### Pousser les modifications :
```bash
cd "C:\Huco_Report 2"
git add .
git commit -m "Description des changements"
git push
```

---

## 9. Dependances Python

```
PyQt6>=6.4.0
openpyxl>=3.1.0
matplotlib>=3.7.0
```

Installer :
```bash
cd "C:\Huco_Report 2"
venv\Scripts\pip install -r requirements.txt
```
