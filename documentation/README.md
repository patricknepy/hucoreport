# HUCO REPORT - Documentation Technique et Fonctionnelle

**Version** : 0.6.7
**Entreprise** : Humans Connexion (Groupe HUCO)
**Dernière mise à jour** : 26 Janvier 2026

---

## Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Documentation métier](./METIER.md)
3. [Architecture technique](./ARCHITECTURE.md)
4. [Guide d'installation](./INSTALLATION.md)
5. [Guide utilisateur](./UTILISATION.md)
6. [Dictionnaire de données](./DICTIONNAIRE_DONNEES.md)
7. **[Notes techniques - BUGS RESOLUS](./NOTES_TECHNIQUES.md)** ← A LIRE EN PRIORITE

---

## Vue d'ensemble

### Qu'est-ce que Huco Report ?

**Huco Report** est un outil de pilotage de performance pour ESN (Entreprise de Services du Numérique), anciennement appelées SSII. Il permet au **Responsable Performance** de :

- Importer les données hebdomadaires depuis un fichier Excel de suivi GDP (Gestion De Projet)
- Visualiser les indicateurs clés de performance (KPI) sur un dashboard
- Suivre l'évolution des **warnings** (alertes clients et internes)
- Identifier les **deadlines** (DLIC/DLI) à traiter
- Analyser les tendances par BU, par chef de projet, par acteur

### Public cible

- **Responsable Performance** : Utilisateur principal
- **Direction** : Consultation des dashboards
- **Chefs de projet** : Consultation de leurs dossiers

### Technologies utilisées

| Composant | Technologie |
|-----------|-------------|
| Langage | Python 3.12 |
| Interface | PyQt6 |
| Base de données | SQLite |
| Graphiques | Matplotlib |
| Parsing Excel | openpyxl |

---

## Structure du projet

```
Huco_Report_066/
├── main.py                 # Point d'entrée
├── requirements.txt        # Dépendances Python
├── BUILD.bat              # Script de build .exe
├── LANCER.bat             # Script de lancement dev
│
├── src/
│   ├── core/              # Logique métier
│   │   ├── database.py    # Gestion SQLite
│   │   ├── excel_parser.py    # Parsing Excel
│   │   ├── excel_validator.py # Validation structure
│   │   ├── excel_importer.py  # Orchestration import
│   │   ├── dashboard_calculator.py # Calculs KPI
│   │   └── paths.py       # Gestion chemins
│   │
│   ├── gui/               # Interface graphique
│   │   ├── main_window.py # Fenêtre principale
│   │   ├── dashboard_tab.py   # Onglet Dashboard
│   │   ├── analysis_tab.py    # Onglet Analyse
│   │   └── import_dialog.py   # Dialogue d'import
│   │
│   └── config/            # Configuration
│       └── settings.py    # Paramètres app
│
├── config/
│   └── excel_schema.json  # Schéma de validation Excel
│
├── data/                  # Base de données SQLite
├── logs/                  # Fichiers de log
├── img/                   # Images et logo
├── import/                # Fichiers Excel à importer
├── Export huco/           # Exports
│
└── documentation/         # Cette documentation
```

---

## Concepts clés

### Semaine (Week)
- Les données sont organisées par **semaine** (S01 à S52/S53)
- Chaque onglet Excel correspond à une semaine
- Le tri utilise la logique **6 mois glissants** (ex: S04 > S03 > S02 > S01 > S52 > S51...)

### Warning
- **Vision Client** : Le client a exprimé une insatisfaction
- **Vision Interne** : Le chef de projet anticipe un problème avant que le client ne le remarque

### DLIC / DLI
- **DLIC** : Date Limite Interne Client (engagement vis-à-vis du client)
- **DLI** : Date Limite Interne (deadline interne)

### Acteur (Next Actor)
- Personne responsable de la prochaine action sur un dossier en warning
- Permet d'identifier qui doit agir

---

## Liens rapides

- [Documentation métier complète](./METIER.md)
- [Architecture et code](./ARCHITECTURE.md)
- [Installation](./INSTALLATION.md)
- [Guide utilisateur](./UTILISATION.md)
