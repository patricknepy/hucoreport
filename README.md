# 🚀 Huco Report

**Outil Professionnel de Gestion de Rapports de Performance**

Développé pour **Humans Connexion** - Société de développement informatique

---

## 📋 Vue d'ensemble

Huco Report est un outil Windows moderne et intelligent conçu pour automatiser le traitement des données de performance issues de fichiers Excel. Il permet de créer des tableaux croisés dynamiques avancés, de générer des rapports professionnels et d'automatiser l'envoi de ces rapports avec monitoring des deadlines.

### 🎯 Objectif Principal

Transformer le processus manuel de traitement Excel en un workflow automatisé, permettant aux équipes de se concentrer sur l'analyse plutôt que sur la manipulation de données.

---

## 👤 Contexte Projet

**Chef de Projet** : Consultant / Responsable de Performance @ Humans Connexion

**Mission** : Développer un outil interne pour améliorer l'efficacité de l'équipe de développement dans le suivi et le reporting de performance des projets.

**Public cible** : Équipe de développement informatique de Humans Connexion (distribution facile, zéro configuration technique requise)

---

## ✨ Fonctionnalités

### 📊 Import & Analyse Intelligente
- **Drag & Drop** ou sélection de fichiers Excel (.xlsx, .xls)
- **Identification automatique** des colonnes selon règles configurables :
  - Deadlines / Échéances
  - Status / Statuts
  - Responsables
  - Priorités
  - Projets et descriptions
- **Validation** automatique des données importées

### 📈 Dashboard & Tableaux Croisés Dynamiques
- Visualisation interactive des données
- Filtres multi-critères
- Graphiques et indicateurs clés (KPI)
- Tableaux croisés dynamiques personnalisables

### 📄 Génération de Rapports
- Templates personnalisables
- Export multi-formats (PDF, Excel, HTML)
- Mise en page professionnelle
- Inclusion automatique de graphiques et métriques

### ⚙️ Automatisation & Monitoring
- **Planification** d'envois automatiques de rapports
- **Monitoring des deadlines** :
  - Alertes J-7, J-3, J-1
  - Notifications sur dépassements
- **Envoi email** automatisé
- Configuration de tâches récurrentes (quotidiennes, hebdomadaires, mensuelles)

---

## 🏗️ Architecture Technique

### Stack Technologique
- **Python 3.11+** : Langage principal
- **PyQt6** : Interface graphique moderne
- **Pandas** : Manipulation de données et tableaux croisés dynamiques
- **ReportLab** : Génération de PDF
- **APScheduler** : Planification de tâches
- **SQLAlchemy** : Base de données locale (cache & historique)

### Structure du Projet

```
Huco_Report/
├── src/
│   ├── gui/                        # Interface graphique (PyQt6)
│   │   ├── main_window.py         # Fenêtre principale + 6 onglets
│   │   ├── dashboard_tab.py       # Onglet Dashboard (KPI + graphiques)
│   │   ├── kpi_tab.py             # Onglet KPIs (santé + commercial)
│   │   ├── analysis_tab.py        # Onglet Analyse (évolution warnings)
│   │   ├── exploitation_tab.py    # Onglet Exploitation (tableau éditable)
│   │   └── import_dialog.py       # Dialog d'import Excel
│   │
│   ├── core/                       # Logique métier
│   │   ├── database.py            # Gestion SQLite (46 champs)
│   │   ├── excel_parser.py        # Import & parsing Excel
│   │   ├── excel_validator.py     # Validation structure Excel
│   │   ├── excel_importer.py      # Orchestration import
│   │   ├── commercial_parser.py   # Parser fichier commercial
│   │   └── dashboard_calculator.py # Calculs KPI
│   │
│   └── config/                     # Configuration
│       └── settings.py            # Paramètres globaux (version, etc.)
│
├── config/
│   └── excel_schema.json          # Schéma validation Excel (46 champs)
│
├── data/                           # Données & cache
│   ├── cache.db                   # Base de données SQLite
│   └── templates/                 # Templates de rapports
│
├── documentation/                  # Documentation détaillée
├── img/                           # Images et logo
├── main.py                        # Point d'entrée
├── requirements.txt               # Dépendances Python
├── BUILD.bat                      # Script build .exe
└── LANCER.bat                     # Script lancement dev
```

---

## 🚀 Installation & Démarrage

### Pour les Développeurs

1. **Cloner le projet**
```bash
cd D:\DEV\Huco_Report
```

2. **Créer un environnement virtuel**
```bash
python -m venv venv
venv\Scripts\activate
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Lancer l'application**
```bash
python main.py
```

### Pour les Utilisateurs (Distribution)

**Simple et rapide** : Double-cliquer sur `HucoReport.exe`

Aucune installation Python requise ! Le fichier `.exe` contient tout le nécessaire.

---

## 📦 Build de Distribution

Pour créer le fichier `.exe` distribuable :

```bash
pyinstaller --onefile --windowed --name HucoReport --icon=assets/icon.ico main.py
```

Le fichier sera généré dans `dist/HucoReport.exe` (~50MB)

---

## 🎨 Interface Utilisateur

L'interface est divisée en **6 onglets** principaux :

### 📊 Dashboard
Vue d'ensemble des données avec indicateurs clés de performance (KPI, graphiques par BU, par CP)

### 📈 KPIs
Indicateurs de santé du portefeuille et performance commerciale (pipeline pondéré, taux régie/build)

### 📉 Analyse
Graphiques d'évolution des warnings par semaine et par mois

### 📝 Exploitation
Tableau éditable pour modifier les données directement (sans réimport Excel)

### 📄 Rapports
Génération et envoi de rapports professionnels (en développement)

### ⚙️ Automatisation
Configuration des tâches automatiques et monitoring des deadlines (en développement)

---

## ⚙️ Configuration

### Configuration Excel

Le schéma de validation Excel est défini dans `config/excel_schema.json`. Ce fichier contient la structure attendue des fichiers Excel importés, incluant les noms de colonnes, types de données et contraintes.

### Configuration Email (à venir)

Prochaine version : Configuration via l'interface pour l'envoi automatique de rapports.

---

## 🧪 Tests

Lancer les tests unitaires :

```bash
pytest tests/ -v
```

---

## 📚 Bonnes Pratiques Respectées

✅ **Architecture modulaire** : Séparation claire entre GUI, logique métier et reporting

✅ **Code propre** : Respect PEP 8, commentaires explicatifs, docstrings

✅ **Testabilité** : Structure facilitant les tests unitaires

✅ **Scalabilité** : Facile d'ajouter de nouvelles fonctionnalités

✅ **Maintenance** : Code lisible et bien organisé

✅ **Distribution facile** : Packaging en un seul fichier exécutable

✅ **UX moderne** : Interface intuitive et professionnelle

---

## 📖 Documentation Complémentaire

### 📌 **À lire en premier**
- [A_LIRE_EN_PREMIER.md](./A_LIRE_EN_PREMIER.md) - 🔴 **REPRISE DU CODE**
- [CHANGELOG.md](./CHANGELOG.md) - 📝 **Historique des versions**

### Architecture & Contexte
- [ARCHITECTURE.md](./docs/ARCHITECTURE.md) - Architecture détaillée
- [CONTEXT.md](./docs/CONTEXT.md) - Contexte projet et objectifs

### Spécifications Métier
- [LOGIQUE_METIER.md](./docs/LOGIQUE_METIER.md) - Logique métier et colonnes
- [LOGIQUE_IMPORT.md](./docs/LOGIQUE_IMPORT.md) - Spécifications d'import Excel
- [SCHEMA_DATABASE.md](./docs/SCHEMA_DATABASE.md) - Schéma base de données SQLite
- [DASHBOARD_SPECS.md](./docs/DASHBOARD_SPECS.md) - Spécifications dashboard

### Guides
- [DEV_GUIDE.md](./docs/DEV_GUIDE.md) - Guide développeur
- [INSTALL.md](./docs/INSTALL.md) - 📦 Installation et dépendances
- [GUIDE_GIT.md](./docs/GUIDE_GIT.md) - 🔧 Guide Git complet (Versioning)
- [GIT_RESUME.md](./docs/GIT_RESUME.md) - ⚡ Résumé Git (Commandes rapides)
- [GUIDE_DISTRIBUTION.md](./docs/GUIDE_DISTRIBUTION.md) - 📦 Guide de distribution

---

## 📝 Changelog

### Version 0.8beta (Mars 2026)
- 🎨 **Nouvelle charte graphique HuCo** : Couleurs corporate (bleu #0166FE, orange #FE4502)
- 📊 **Visualisation PIPE** : Jours facturables en main par projet et par CDP
- 📈 **Graphique correlation** : Nb Projets vs PIPE (double axe) pour detecter les anomalies
- 🔴 **Alerte projets a 0j** : Projets sans visibilite affiches en rouge avec label "0j !"
- 📊 **Ordre chronologique** : Graphiques d'evolution de gauche (ancien) a droite (recent)
- 📝 **Documentation metier enrichie** : Section PIPE et performance CDP

### Version 0.7.0 (Janvier 2026)
- ✨ **Onglet Exploitation** : Tableau éditable avec modification directe en base
- 📊 **Onglet KPIs** : Indicateurs santé portefeuille + performance commerciale
- 🔧 Amélioration du parser commercial (pipeline pondéré)
- 📝 Mise à jour complète de la documentation

### Version 1.0.0 (Novembre 2025)
- ✨ Interface graphique complète (4 onglets)
- 📊 Import et analyse Excel
- 📄 Génération de rapports (placeholder)
- ⚙️ Système d'automatisation (placeholder)
- 🎯 Première version stable

---

## 🤝 Contribution

Ce projet est développé en interne pour **Humans Connexion**.

Pour toute suggestion ou amélioration, contacter le responsable du projet.

---

## 📧 Contact

**Humans Connexion**
Société de développement informatique

**Chef de Projet** : Consultant / Responsable de Performance

---

## 📄 Licence

© 2025 Humans Connexion - Usage interne uniquement

---

<p align="center">
  <strong>Développé avec ❤️ pour Humans Connexion</strong>
</p>

