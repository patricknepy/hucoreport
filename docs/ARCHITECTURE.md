# 🏗️ Architecture Technique - Huco Report

**Document de référence pour l'architecture du projet**

---

## 📐 Principes d'Architecture

### Objectifs Principaux

1. **Modularité** : Composants indépendants et réutilisables
2. **Maintenabilité** : Code facile à comprendre et à modifier
3. **Scalabilité** : Facilité d'ajout de nouvelles fonctionnalités
4. **Performance** : Traitement rapide de gros fichiers Excel
5. **Professionnalisme** : Respect des standards de l'industrie

### Patterns Utilisés

- **MVC (Model-View-Controller)** : Séparation interface / logique métier
- **Repository Pattern** : Abstraction de la couche de données
- **Strategy Pattern** : Pour les différents formats de rapports
- **Observer Pattern** : Pour les notifications et événements
- **Singleton** : Pour la configuration globale

---

## 🗂️ Structure des Modules

### 1. Module GUI (`src/gui/`)

**Responsabilité** : Interface utilisateur et interactions

#### `main_window.py`
- Fenêtre principale de l'application
- Gestion des menus et de la navigation
- Coordination entre les différents onglets

#### `dashboard.py` (À développer)
- Affichage des indicateurs de performance
- Graphiques interactifs (matplotlib/seaborn)
- Filtres et sélections

#### `report_builder.py` (À développer)
- Interface de création de rapports
- Sélection de templates
- Configuration des paramètres de rapport

#### `settings_dialog.py` (À développer)
- Configuration de l'application
- Paramètres email
- Gestion des règles d'identification

---

### 2. Module Core (`src/core/`)

**Responsabilité** : Logique métier et traitement des données

#### `excel_parser.py` (À développer)
```python
class ExcelParser:
    """Parse les fichiers Excel selon les règles définies"""
    
    def load_file(self, file_path: str) -> pd.DataFrame
    def identify_columns(self, df: pd.DataFrame) -> dict
    def validate_data(self, df: pd.DataFrame) -> bool
```

#### `data_analyzer.py` (À développer)
```python
class DataAnalyzer:
    """Analyse et transforme les données"""
    
    def create_pivot_table(self, data: pd.DataFrame, config: dict)
    def filter_data(self, data: pd.DataFrame, filters: dict)
    def calculate_kpis(self, data: pd.DataFrame) -> dict
```

#### `rule_engine.py` (À développer)
```python
class RuleEngine:
    """Moteur de règles pour l'identification automatique"""
    
    def load_rules(self, rules_file: str)
    def apply_rules(self, dataframe: pd.DataFrame)
    def detect_column_type(self, column: pd.Series)
```

#### `data_model.py` (À développer)
```python
class Project:
    """Modèle de données pour un projet"""
    
class Task:
    """Modèle de données pour une tâche"""
    
class Report:
    """Modèle de données pour un rapport"""
```

---

### 3. Module Reporting (`src/reporting/`)

**Responsabilité** : Génération et envoi de rapports

#### `generator.py` (À développer)
```python
class ReportGenerator:
    """Génère des rapports dans différents formats"""
    
    def generate_pdf(self, data: pd.DataFrame, template: str)
    def generate_excel(self, data: pd.DataFrame, template: str)
    def generate_html(self, data: pd.DataFrame, template: str)
```

#### `email_service.py` (À développer)
```python
class EmailService:
    """Gère l'envoi d'emails"""
    
    def send_report(self, report_path: str, recipients: list)
    def send_deadline_alert(self, tasks: list)
```

#### `scheduler.py` (À développer)
```python
class ReportScheduler:
    """Planifie l'exécution automatique de rapports"""
    
    def schedule_report(self, config: dict)
    def monitor_deadlines(self)
    def execute_scheduled_tasks(self)
```

---

### 4. Module Config (`src/config/`)

**Responsabilité** : Configuration et paramètres

#### `settings.py`
- Chemins de fichiers
- Configuration globale
- Paramètres par défaut

#### `rules.json`
- Règles d'identification des colonnes
- Keywords de détection
- Formats de données

---

## 🔄 Flux de Données

### 1. Import de Fichier Excel

```
Utilisateur → GUI (main_window.py)
    ↓
ExcelParser.load_file()
    ↓
RuleEngine.apply_rules()
    ↓
Validation des données
    ↓
Stockage en cache (SQLite)
    ↓
Mise à jour du Dashboard
```

### 2. Génération de Rapport

```
Utilisateur sélectionne données + template
    ↓
DataAnalyzer.create_pivot_table()
    ↓
ReportGenerator.generate_pdf()
    ↓
Sauvegarde du rapport
    ↓
(Optionnel) EmailService.send_report()
```

### 3. Monitoring Automatique

```
ReportScheduler (background)
    ↓
Vérification des deadlines (toutes les heures)
    ↓
Si deadline proche ou dépassée:
    ↓
Génération de rapport d'alerte
    ↓
Envoi email automatique
```

---

## 💾 Base de Données

### Structure SQLite (`data/cache.db`)

#### Table `projects`
```sql
CREATE TABLE projects (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

#### Table `tasks`
```sql
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY,
    project_id INTEGER,
    description TEXT,
    deadline DATE,
    status TEXT,
    responsible TEXT,
    priority TEXT,
    FOREIGN KEY (project_id) REFERENCES projects(id)
);
```

#### Table `reports`
```sql
CREATE TABLE reports (
    id INTEGER PRIMARY KEY,
    name TEXT,
    created_at TIMESTAMP,
    file_path TEXT,
    format TEXT
);
```

#### Table `schedules`
```sql
CREATE TABLE schedules (
    id INTEGER PRIMARY KEY,
    report_type TEXT,
    frequency TEXT,
    next_execution TIMESTAMP,
    recipients TEXT,
    active BOOLEAN
);
```

---

## 🎨 Interface Utilisateur

### Design Principles

1. **Clarté** : Information hiérarchisée et lisible
2. **Accessibilité** : Boutons et textes de taille suffisante
3. **Feedback visuel** : Confirmations, erreurs, chargements
4. **Cohérence** : Palette de couleurs et typo uniformes
5. **Efficacité** : Maximum 3 clics pour toute action

### Palette de Couleurs

```css
Primaire : #4CAF50 (Vert) - Actions principales
Secondaire : #2196F3 (Bleu) - Informations
Accent : #FF9800 (Orange) - Alertes
Danger : #F44336 (Rouge) - Erreurs
Neutre : #666666 (Gris) - Texte secondaire
```

---

## 🔒 Sécurité

### Données Sensibles

- **Mots de passe email** : Stockés en local avec chiffrement (keyring)
- **Fichiers Excel** : Jamais envoyés en ligne, traitement 100% local
- **Base de données** : Stockage local uniquement

### Validation des Entrées

- Validation des fichiers Excel avant traitement
- Sanitization des chemins de fichiers
- Vérification des formats de données

---

## 📊 Performance

### Optimisations

1. **Chunking** : Lecture de gros fichiers Excel par morceaux
2. **Caching** : Mise en cache des données fréquemment utilisées
3. **Lazy loading** : Chargement à la demande des onglets
4. **Threading** : Opérations longues en arrière-plan (Qt threads)

### Limites Recommandées

- Fichiers Excel : jusqu'à 100 000 lignes (performances optimales)
- Rapports PDF : jusqu'à 50 pages
- Tâches planifiées : maximum 20 simultanées

---

## 🧪 Tests

### Structure des Tests

```
tests/
├── test_gui/
│   └── test_main_window.py
├── test_core/
│   ├── test_excel_parser.py
│   ├── test_data_analyzer.py
│   └── test_rule_engine.py
└── test_reporting/
    ├── test_generator.py
    └── test_email_service.py
```

### Types de Tests

1. **Tests unitaires** : Chaque fonction/méthode isolée
2. **Tests d'intégration** : Flux complets de données
3. **Tests GUI** : Interactions utilisateur (pytest-qt)

---

## 🚀 Déploiement

### Build avec PyInstaller

```bash
pyinstaller --onefile \
            --windowed \
            --name HucoReport \
            --icon=assets/icon.ico \
            --add-data "src/config/rules.json;src/config" \
            --hidden-import=PyQt6 \
            main.py
```

### Structure du Package

```
HucoReport.exe        (~50MB, tout inclus)
├── Python runtime
├── PyQt6
├── Pandas + dépendances
├── Configuration par défaut
└── Assets (icônes, templates)
```

---

## 🔮 Évolutions Futures

### Phase 2 (Court terme)
- Export vers Power BI / Tableau
- Intégration API (Jira, Trello)
- Templates de rapports avancés

### Phase 3 (Moyen terme)
- Version web (Django/Flask)
- Collaboration multi-utilisateurs
- Base de données centralisée

### Phase 4 (Long terme)
- IA pour prédictions de deadlines
- Recommandations automatiques
- Intégration complète ERP

---

## 📚 Ressources & Références

### Documentation Officielle
- [PyQt6 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [ReportLab Documentation](https://www.reportlab.com/docs/)

### Standards & Best Practices
- [PEP 8 - Style Guide for Python Code](https://peps.python.org/pep-0008/)
- [Clean Code Principles](https://www.amazon.com/Clean-Code-Handbook-Software-Craftsmanship/dp/0132350882)

---

<p align="center">
  <strong>Architecture conçue pour Humans Connexion</strong><br>
  <em>Évolutive, maintenable et professionnelle</em>
</p>

