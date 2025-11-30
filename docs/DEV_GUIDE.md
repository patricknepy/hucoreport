# 👨‍💻 Guide du Développeur - Huco Report

**Documentation technique pour les développeurs travaillant sur le projet**

---

## 🚀 Démarrage Rapide

### Prérequis

- **Python 3.11+** (recommandé : 3.11.6)
- **Windows 10/11** (OS cible)
- **Git** pour le versioning
- **IDE recommandé** : VS Code, PyCharm

### Installation Environnement de Développement

```bash
# 1. Cloner le projet
cd D:\DEV\Huco_Report

# 2. Créer un environnement virtuel
python -m venv venv

# 3. Activer l'environnement virtuel
venv\Scripts\activate

# 4. Installer les dépendances
pip install -r requirements.txt

# 5. Installer les outils de développement
pip install pytest pytest-qt black flake8

# 6. Lancer l'application
python main.py
```

---

## 📁 Structure du Code

### Conventions de Nommage

- **Fichiers** : `snake_case.py`
- **Classes** : `PascalCase`
- **Fonctions/Méthodes** : `snake_case`
- **Constantes** : `UPPER_SNAKE_CASE`
- **Variables privées** : `_leading_underscore`

### Organisation des Imports

```python
# 1. Imports standard library
import sys
from pathlib import Path

# 2. Imports third-party
import pandas as pd
from PyQt6.QtWidgets import QMainWindow

# 3. Imports locaux
from src.config.settings import APP_NAME
from src.core.excel_parser import ExcelParser
```

---

## 🔧 Développement des Modules

### Module Core - Excel Parser

**Fichier** : `src/core/excel_parser.py`

```python
"""
Parser intelligent de fichiers Excel avec identification automatique des colonnes
"""

import pandas as pd
from pathlib import Path
from typing import Dict, Optional
import json

from src.config.settings import BASE_DIR


class ExcelParser:
    """Parse et analyse les fichiers Excel selon les règles configurées"""
    
    def __init__(self, rules_file: Optional[str] = None):
        """
        Initialise le parser avec les règles d'identification
        
        Args:
            rules_file: Chemin vers le fichier de règles JSON
        """
        if rules_file is None:
            rules_file = BASE_DIR / "src" / "config" / "rules.json"
        
        self.rules = self._load_rules(rules_file)
        self.df: Optional[pd.DataFrame] = None
        self.column_mapping: Dict[str, str] = {}
    
    def _load_rules(self, rules_file: str) -> dict:
        """Charge les règles depuis le fichier JSON"""
        with open(rules_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_file(self, file_path: str) -> pd.DataFrame:
        """
        Charge un fichier Excel
        
        Args:
            file_path: Chemin vers le fichier Excel
            
        Returns:
            DataFrame pandas avec les données
            
        Raises:
            ValueError: Si le fichier n'est pas valide
        """
        try:
            self.df = pd.read_excel(file_path)
            return self.df
        except Exception as e:
            raise ValueError(f"Erreur lors du chargement du fichier : {e}")
    
    def identify_columns(self) -> Dict[str, str]:
        """
        Identifie automatiquement les colonnes selon les règles
        
        Returns:
            Dictionnaire {type_colonne: nom_colonne_réel}
        """
        if self.df is None:
            raise ValueError("Aucun fichier chargé")
        
        # TODO: Implémenter la logique d'identification
        # Utiliser les keywords des règles pour matcher les noms de colonnes
        
        return self.column_mapping
    
    def validate_data(self) -> bool:
        """
        Valide que les données respectent les contraintes
        
        Returns:
            True si valide, False sinon
        """
        # TODO: Implémenter la validation
        return True
```

---

### Module Core - Data Analyzer

**Fichier** : `src/core/data_analyzer.py`

```python
"""
Analyse et transformation des données avec pandas
"""

import pandas as pd
from typing import Dict, List, Optional


class DataAnalyzer:
    """Analyse avancée des données de performance"""
    
    def __init__(self, dataframe: pd.DataFrame):
        """
        Initialise l'analyseur
        
        Args:
            dataframe: DataFrame pandas à analyser
        """
        self.df = dataframe
    
    def create_pivot_table(
        self, 
        index: str, 
        columns: str, 
        values: str, 
        aggfunc: str = 'count'
    ) -> pd.DataFrame:
        """
        Crée un tableau croisé dynamique
        
        Args:
            index: Colonne pour l'index
            columns: Colonne pour les colonnes
            values: Colonne pour les valeurs
            aggfunc: Fonction d'agrégation
            
        Returns:
            DataFrame pivot
        """
        return pd.pivot_table(
            self.df,
            index=index,
            columns=columns,
            values=values,
            aggfunc=aggfunc
        )
    
    def filter_data(self, filters: Dict[str, any]) -> pd.DataFrame:
        """
        Filtre les données selon les critères
        
        Args:
            filters: Dictionnaire {colonne: valeur}
            
        Returns:
            DataFrame filtré
        """
        filtered_df = self.df.copy()
        
        for column, value in filters.items():
            if isinstance(value, list):
                filtered_df = filtered_df[filtered_df[column].isin(value)]
            else:
                filtered_df = filtered_df[filtered_df[column] == value]
        
        return filtered_df
    
    def calculate_kpis(self) -> Dict[str, any]:
        """
        Calcule les indicateurs clés de performance
        
        Returns:
            Dictionnaire des KPIs
        """
        # TODO: Implémenter le calcul des KPIs
        kpis = {
            'total_tasks': len(self.df),
            'completed_tasks': 0,
            'upcoming_deadlines': 0,
            'overdue_tasks': 0,
        }
        
        return kpis
```

---

### Module Reporting - Report Generator

**Fichier** : `src/reporting/generator.py`

```python
"""
Génération de rapports dans différents formats
"""

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
import pandas as pd
from pathlib import Path
from datetime import datetime


class ReportGenerator:
    """Génère des rapports professionnels"""
    
    def __init__(self, data: pd.DataFrame, template: str = "default"):
        """
        Initialise le générateur de rapports
        
        Args:
            data: Données à inclure dans le rapport
            template: Nom du template à utiliser
        """
        self.data = data
        self.template = template
    
    def generate_pdf(self, output_path: str, title: str) -> str:
        """
        Génère un rapport PDF
        
        Args:
            output_path: Chemin de sortie du PDF
            title: Titre du rapport
            
        Returns:
            Chemin du fichier généré
        """
        c = canvas.Canvas(output_path, pagesize=A4)
        width, height = A4
        
        # En-tête
        c.setFont("Helvetica-Bold", 20)
        c.drawString(2*cm, height - 2*cm, title)
        
        # Date
        c.setFont("Helvetica", 10)
        c.drawString(2*cm, height - 3*cm, f"Généré le : {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        
        # TODO: Ajouter le contenu du rapport
        
        c.save()
        return output_path
    
    def generate_excel(self, output_path: str) -> str:
        """
        Génère un rapport Excel
        
        Args:
            output_path: Chemin de sortie
            
        Returns:
            Chemin du fichier généré
        """
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            self.data.to_excel(writer, sheet_name='Rapport', index=False)
        
        return output_path
```

---

## 🧪 Tests

### Structure des Tests

```python
# tests/test_core/test_excel_parser.py

import pytest
import pandas as pd
from src.core.excel_parser import ExcelParser


class TestExcelParser:
    """Tests du parser Excel"""
    
    @pytest.fixture
    def parser(self):
        """Fixture : instance du parser"""
        return ExcelParser()
    
    @pytest.fixture
    def sample_excel(self, tmp_path):
        """Fixture : fichier Excel de test"""
        df = pd.DataFrame({
            'Projet': ['Projet A', 'Projet B'],
            'Deadline': ['2025-12-31', '2025-11-30'],
            'Status': ['En cours', 'Terminé']
        })
        
        file_path = tmp_path / "test.xlsx"
        df.to_excel(file_path, index=False)
        return file_path
    
    def test_load_file_success(self, parser, sample_excel):
        """Test : chargement réussi d'un fichier"""
        df = parser.load_file(str(sample_excel))
        assert len(df) == 2
        assert 'Projet' in df.columns
    
    def test_load_file_invalid(self, parser):
        """Test : fichier invalide"""
        with pytest.raises(ValueError):
            parser.load_file("fichier_inexistant.xlsx")
```

### Lancer les Tests

```bash
# Tous les tests
pytest tests/

# Tests avec couverture
pytest tests/ --cov=src --cov-report=html

# Tests d'un module spécifique
pytest tests/test_core/test_excel_parser.py -v
```

---

## 🎨 Style et Qualité du Code

### Formatter avec Black

```bash
# Formater tout le code
black src/ tests/

# Vérifier sans modifier
black src/ tests/ --check
```

### Linter avec Flake8

```bash
# Analyser le code
flake8 src/ tests/ --max-line-length=100
```

### Configuration `.flake8`

```ini
[flake8]
max-line-length = 100
exclude = venv,__pycache__,.git
ignore = E203,W503
```

---

## 🐛 Debugging

### Logging

```python
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Utilisation
logger.debug("Message de debug")
logger.info("Information")
logger.warning("Avertissement")
logger.error("Erreur")
```

---

## 📦 Build & Distribution

### Créer l'Exécutable

```bash
# Build simple
pyinstaller main.py --onefile --windowed --name HucoReport

# Build avec options avancées
pyinstaller --onefile ^
            --windowed ^
            --name HucoReport ^
            --icon=assets/icon.ico ^
            --add-data "src/config/rules.json;src/config" ^
            --hidden-import=PyQt6.QtCore ^
            --hidden-import=PyQt6.QtGui ^
            --hidden-import=PyQt6.QtWidgets ^
            main.py
```

### Tester l'Exécutable

```bash
cd dist
HucoReport.exe
```

---

## 🔄 Workflow Git

### Branches

- `main` : Production stable
- `develop` : Développement actif
- `feature/nom-fonctionnalité` : Nouvelles fonctionnalités
- `bugfix/nom-bug` : Corrections de bugs

### Commits

Format : `type(scope): message`

Exemples :
```
feat(parser): ajout identification automatique colonnes
fix(gui): correction bug import fichier
docs(readme): mise à jour installation
refactor(core): simplification DataAnalyzer
test(parser): ajout tests validation
```

---

## 📚 Ressources Utiles

### Documentation

- [PyQt6 Examples](https://github.com/PyQt6/examples)
- [Pandas Cheat Sheet](https://pandas.pydata.org/Pandas_Cheat_Sheet.pdf)
- [ReportLab User Guide](https://www.reportlab.com/docs/reportlab-userguide.pdf)

### Outils

- **DB Browser for SQLite** : Visualiser la base de données
- **Qt Designer** : Créer des interfaces graphiquement
- **Postman** : Tester les APIs (futures intégrations)

---

<p align="center">
  <strong>Happy Coding! 🚀</strong><br>
  <em>Questions ? Contactez le responsable du projet</em>
</p>

