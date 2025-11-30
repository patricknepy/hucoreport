# 📝 Changelog - Huco Report

Toutes les modifications notables de ce projet sont documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/lang/fr/).

---

## [1.0.0] - 2025-11-30

### ✅ Ajouté
- **Import Excel automatique**
  - Validation structure (43 champs + 3 métadonnées)
  - Détection intelligente des colonnes
  - Simulation avant import (DLIC, acteurs, warnings)
  - Conversion dates multiples formats (jour/mois/semaine)
  - Normalisation statuts (Actif → EN COURS, etc.)
  - Écrasement complet base de données (philosophie "miroir")
  - Sauvegarde automatique fichier avec date/heure
  
- **Dashboard Complet**
  - Dropdown sélection semaine
  - Chargement automatique au démarrage
  - **Vue Globale** (3 colonnes) :
    - Total projets + Actifs
    - Dispositif mensuel (jours)
    - Dispositifs augmentables (compteur)
    - Graphique "Projets actifs par BU"
    - Graphique "Projets par Chef de projet"
  - **Actualité Client** (3 colonnes) :
    - Warning Vision Client/Interne
    - Graphique "Warnings par BU"
    - Graphique "Actions par acteur"
  - **Actions & Deadlines** :
    - DLIC/DLI à traiter cette semaine
    - DLIC/DLI dépassées
    - DLIC vides (projets actifs)
  - **RDV Client** cette semaine (liste détaillée)
  
- **Interface Professionnelle**
  - Plein écran au lancement
  - Logo Humans Connexion dans le header
  - Section import compacte et discrète
  - 4 onglets : Dashboard, Analyse, Rapports, Automatisation
  - 4 graphiques matplotlib (barres horizontales)
  - Tri alphabétique automatique
  
- **Distribution**
  - Script BUILD.bat pour créer .exe autonome
  - Chemins absolus (compatible .exe et dev)
  - Dossier complet prêt à distribuer (~250 Mo)
  - Guide de distribution complet
  
- **Documentation**
  - 7 fichiers docs/ (architecture, métier, import, etc.)
  - A_LIRE_EN_PREMIER.md (reprise rapide)
  - README.md complet
  - Guide développeur
  
- **Base de Données**
  - SQLite local (46 champs)
  - Schéma SQL déclaratif
  - Indexes pour performance
  - Mapping flexible via excel_schema.json

### 🔧 Technique
- Python 3.10+
- PyQt6 (interface)
- Pandas (manipulation Excel)
- Matplotlib (graphiques)
- SQLite (base de données)
- PyInstaller (distribution)
- Git + branches (develop/master)

### 📊 Statistiques
- 41 fichiers
- ~8700 lignes de code
- 8 semaines de données importables (S39-S48)
- ~51 projets par semaine

---

## [Non publié] - À venir

### 🚀 Prévu pour v1.1.0
- Onglet **Analyse** :
  - Grille de données Excel-like
  - Filtres par colonne
  - Tri dynamique
  - Export Excel/CSV
  - Recherche globale
  
- Onglet **Rapports** :
  - Génération PDF professionnelle
  - Export Excel avancé
  - Templates email
  - Envoi automatique
  
- Onglet **Automatisation** :
  - Planification tâches (hebdo/quotidien)
  - Monitoring DLIC automatique
  - Alertes email si deadline < 3 jours

### 🤖 Prévu pour v1.2.0
- **Assistant IA** (Azure OpenAI)
  - Chat en langage naturel
  - Function calling (filtres, exports, emails)
  - Compréhension métier
  - Code d'activation + quota (200 req/mois)

### 🔮 Idées Futures
- Fiche projet détaillée (modal)
- Historique comparaison semaines
- Tableaux de bord personnalisables
- Système de mise à jour auto
- Mode sombre
- Export PowerPoint
- Télémétrie usage (anonyme)

---

## Types de Changements

- **Ajouté** : Nouvelles fonctionnalités
- **Modifié** : Changements aux fonctionnalités existantes
- **Déprécié** : Fonctionnalités bientôt retirées
- **Retiré** : Fonctionnalités retirées
- **Corrigé** : Corrections de bugs
- **Sécurité** : Vulnérabilités corrigées

---

## Liens

- [Documentation complète](./README.md)
- [Guide de distribution](./GUIDE_DISTRIBUTION.md)
- [Architecture](./docs/ARCHITECTURE.md)
- [Reprise du code](./A_LIRE_EN_PREMIER.md)

