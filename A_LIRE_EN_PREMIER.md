# 📌 À LIRE EN PREMIER - Reprise du Code

**Date** : 30 janvier 2026
**Projet** : Huco Report - Humans Connexion
**Statut** : En développement actif

---

## ✅ CE QUI FONCTIONNE AUJOURD'HUI

### **1. Import Excel Complet** 🎯
- ✅ Validation structure (schéma JSON de référence)
- ✅ Détection colonnes avec normalisation (retours à la ligne, etc.)
- ✅ Simulation avec indicateurs pertinents :
  - DLIC cette semaine
  - DLIC dépassées
  - % dossiers actifs avec acteur identifié
- ✅ Import réel en base SQLite
- ✅ Écrasement complet de la base à chaque import (philosophie "miroir")
- ✅ Sauvegarde automatique fichier Excel avec date/heure
- ✅ Gestion des lignes vides (ignore si A, C ou D vide)
- ✅ Normalisation statuts : "Actif" → "EN COURS", "Pause" → "PAUSE", "Non Actif" → "TERMINÉ"

### **2. Conversion Intelligente des Données** 🧠
- ✅ Dates multiples formats :
  - JJ/MM/AAAA, AAAA-MM-DD
  - Mois seul "2025-11" → 30/11/2025 (dernier jour)
  - Semaine "S48" → Dimanche de la semaine
  - Texte "Novembre 2025" → 30/11/2025
- ✅ Booléens : "X" ou "x" → True
- ✅ Statuts normalisés automatiquement
- ✅ Détection WARNING : "WARNING !", "warning", etc. (LIKE '%warning%')

### **3. Dashboard Fonctionnel** 📊
- ✅ Dropdown sélection semaine
- ✅ Chargement automatique au démarrage (pas besoin de réimporter)
- ✅ **Vue Globale** (3 colonnes) :
  - Gauche : Total projets + Actifs + Dispositif mensuel + Dispositifs augmentables
  - Milieu : Graphique "Projets actifs par BU"
  - Droite : Graphique "Projets par Chef de projet"
- ✅ **Actualité Client** (3 colonnes) :
  - Gauche : Warning Vision Client + Warning Vision Interne
  - Milieu : Graphique "Warnings par BU"
  - Droite : Graphique "Actions par acteur" (warnings uniquement)
- ✅ **Actions & Deadlines** :
  - DLIC/DLI à traiter cette semaine
  - DLIC/DLI dépassées
  - DLIC vides
- ✅ **RDV Client** cette semaine (liste cliquable)

### **4. Onglet Exploitation** 📝 (NOUVEAU - Janvier 2026)
- ✅ Tableau éditable avec 13 colonnes (ID, Client, BU, Statut, Chef Projet, Vision Client/Interne, etc.)
- ✅ Modification directe en base de données (double-clic pour éditer)
- ✅ Ajout de nouveaux projets (bouton "+ Nouveau projet")
- ✅ Recherche/filtrage par client, BU, chef de projet
- ✅ Sélecteur de semaine
- ✅ Coloration conditionnelle (warnings en rouge/orange, statuts colorés)
- ✅ Sauvegarde avec confirmation et surlignage des modifications

### **5. Onglet KPIs** 📊 (NOUVEAU - Janvier 2026)
- ✅ Indicateurs de santé du portefeuille
- ✅ KPIs commerciaux avec chargement fichier input.xlsx
- ✅ Pipeline pondéré (signed, agreed, likely, specul)
- ✅ Taux Régie/Build

### **6. Interface Professionnelle** 🎨
- ✅ Plein écran au lancement
- ✅ Logo Humans Connexion intégré
- ✅ Section import compacte et discrète
- ✅ 6 onglets : Dashboard, KPIs, Analyse, Exploitation, Rapports, Automatisation
- ✅ Graphiques matplotlib (barres horizontales)
- ✅ Responsive design

### **5. Distribution** 📦
- ✅ Script `BUILD.bat` pour créer .exe autonome
- ✅ Chemins absolus (compatible .exe et dev)
- ✅ Dossier complet prêt à distribuer
- ✅ Documentation distribution complète

---

## 📊 État de la Base de Données

### **Structure : 46 champs**
- 3 métadonnées (id, week_number, import_date)
- 43 champs Excel mappés

### **Mapping Colonnes Critiques** (corrigé) :
- A → `id_projet` (INTEGER)
- D → `client_name` (TEXT) [Colonne renommée "Projet" → "Client"]
- N → `nps_commercial` (INTEGER -100 à +100)
- O → `nps_project` (INTEGER -100 à +100)
- P → `vision_client` (TEXT: "WARNING !", "bon", etc.)
- Q → `vision_internal` (TEXT: "WARNING !", etc.)
- AS → `dispositif_expandable` (TEXT: "oui", "oui+", "non")

### **Fichiers Importés** :
- 8 semaines : S39, S42, S43, S44, S45, S46, S47, S48
- ~51 projets par semaine
- ~384 projets valides au total

---

## ⚠️ Points d'Attention

### **1. Détection WARNING**
Le texte exact dans Excel est : **"WARNING !"** (majuscules + espace + !)  
→ Détection : `LIKE '%warning%'` (insensible à la casse)

### **2. Dispositif augmentable**
Type = **TEXT** (pas BOOLEAN)  
Valeurs : "oui", "oui+", "non", vide  
→ Comptage : `LIKE '%oui%'`

### **3. Chef de projet**
Colonne Excel : "Chef de projet"  
Champ base : `project_manager`  
Graphiques triés par ordre alphabétique

---

## 🔧 CE QUI RESTE À FAIRE

### **✅ TERMINÉ : Onglet EXPLOITATION** 📝

#### **Grille de données éditable** (Implémenté dans `exploitation_tab.py`)
- [x] Tableau Excel-like avec 13 colonnes éditables
- [x] Modification directe en base de données
- [x] Recherche globale (filtre dynamique)
- [x] Ajout de nouveaux projets
- [x] Sélecteur de semaine
- [x] Coloration conditionnelle (warnings, statuts)
- [x] Sauvegarde avec confirmation

---

### **Priorité 1 : Améliorations Onglet ANALYSE** 📈

#### **Fonctionnalités restantes**
- [ ] Tri par colonne (clic sur en-tête)
- [ ] Filtres par colonne (dropdown comme Excel)
- [ ] Export Excel/CSV
- [ ] Double-clic sur ligne → Fiche projet

**Technologie** : QTableWidget ou QTableView + Pandas

**Complexité** : Moyenne (1-2 jours)

---

#### **🤖 Assistant IA** (Optionnel mais impressionnant)

**Fonctionnalités** :
- [ ] Dialog chat IA
- [ ] Compréhension langage naturel
- [ ] Function calling (outils Python)
- [ ] Génération de filtres SQL
- [ ] Génération d'emails
- [ ] Réponses aux questions métier

**Exemples d'usage** :
- "Montre les dossiers d'Elsa avec action attendue"
- "Prépare un mail pour Matthieu avec ses DLIC urgentes"
- "Quels sont les commentaires sur le client HEMAC ?"
- "Exporte les projets en warning en Excel"

**Technologie** : Azure OpenAI + Function Calling

**Coût estimé** : 
- Développement/test : ~1-2€/mois (50 requêtes)
- Production : ~5-10€/mois (200 requêtes)
- Avec crédit gratuit Azure (200$) = Gratuit pendant 2-3 ans

**Protection** :
- Code d'activation : "HUCO_INTERNAL"
- Quota : 200 requêtes/mois pour toute l'équipe
- Reset automatique le 1er du mois

**Complexité** : Moyenne-Élevée (2-3 jours)

---

### **Priorité 2 : Onglet RAPPORTS** 📄

#### **Génération PDF**
- [ ] Rapport hebdomadaire global (S48)
- [ ] Rapport personnalisé par acteur
- [ ] Rapport par BU
- [ ] Alerte DLIC urgentes

**Technologie** : ReportLab (déjà installé)

**Complexité** : Moyenne (1-2 jours)

---

#### **Génération Excel**
- [ ] Export dashboard en Excel
- [ ] Export données filtrées
- [ ] Tableaux croisés dynamiques

**Technologie** : openpyxl + pandas

**Complexité** : Facile (0.5-1 jour)

---

#### **Envoi Email**
- [ ] Configuration SMTP
- [ ] Envoi avec pièce jointe (PDF/Excel)
- [ ] Templates email professionnels
- [ ] Stockage sécurisé mot de passe

**Technologie** : smtplib + secure-smtplib

**Complexité** : Moyenne (1 jour)

---

### **Priorité 3 : Onglet AUTOMATISATION** ⚙️

#### **Planification tâches**
- [ ] Rapport hebdomadaire automatique (ex: Lundi 8h)
- [ ] Monitoring DLIC (quotidien à 9h)
- [ ] Alertes email si DLIC < 3 jours
- [ ] Rapport personnalisé par acteur (hebdo)

**Technologie** : APScheduler (déjà installé)

**Complexité** : Moyenne (1-2 jours)

---

### **Priorité 4 : Fiche Projet Détaillée** 📋

#### **Modal/Dialog fiche complète**
- [ ] Afficher toutes les infos d'un projet
- [ ] Navigation projet précédent/suivant
- [ ] Modifier certains champs (commentaires)
- [ ] Historique semaines (S47, S48, etc.)

**Technologie** : QDialog personnalisé

**Complexité** : Facile (0.5-1 jour)

---

## 🎯 Plan de Développement Recommandé

### **Phase 1 : Analyse & Visualisation** (3-4 jours)
1. Grille de données avec filtres (Analyse)
2. Fiche projet détaillée
3. Export Excel/CSV

### **Phase 2 : Rapports** (2-3 jours)
1. Génération PDF
2. Templates professionnels
3. Export Excel avancé

### **Phase 3 : IA (Optionnel mais WOW)** (2-3 jours)
1. Intégration Azure OpenAI
2. Chat IA avec function calling
3. Code d'activation + quota

### **Phase 4 : Automatisation** (2-3 jours)
1. Planification tâches
2. Monitoring DLIC
3. Configuration email

### **Phase 5 : Finitions** (1-2 jours)
1. Tests complets
2. Documentation utilisateur
3. Build final .exe
4. Formation équipe

**TOTAL : 10-15 jours de développement**

---

## 📚 Documentation À Mettre À Jour

### **À compléter :**

1. ✅ **DASHBOARD_SPECS.md** - Ajouter :
   - Dispositif mensuel
   - Dispositifs augmentables
   - 4 graphiques à bâton
   - Organisation 3 colonnes

2. ✅ **SCHEMA_DATABASE.md** - Corriger :
   - `dispositif_expandable` : BOOLEAN → TEXT

3. ⏳ **ANALYSE_SPECS.md** - À créer :
   - Grille de données
   - Filtres
   - Assistant IA

4. ⏳ **RAPPORTS_SPECS.md** - À créer :
   - Templates PDF
   - Export Excel
   - Configuration email

5. ⏳ **AI_INTEGRATION.md** - À créer :
   - Azure OpenAI vs alternatives
   - Function calling
   - Sécurité et conformité
   - Coûts

---

## 🔑 Commandes Utiles

### **Développement**
```powershell
# Lancer l'app
.\LANCER.bat

# Ou directement
venv\Scripts\python.exe main.py
```

### **Build .exe**
```powershell
# Créer package de distribution
.\BUILD.bat

# Résultat dans : dist\HucoReport\
```

### **Nettoyage base**
```powershell
# Si besoin de recréer la base
del data\cache.db
```

---

## 📞 Questions En Suspens

### **Pour l'IA :**
1. Azure OpenAI ou OpenAI direct pour tests ?
2. Code d'activation simple ou système de quota ?
3. Intégration prioritaire ou après les autres fonctionnalités ?

### **Pour l'Analyse :**
1. Tableaux personnalisés sur mesure (à définir) ?
2. Quels filtres exactement ?
3. Comparaison de semaines ?

### **Pour les Rapports :**
1. Destinataires des rapports hebdo ?
2. Templates spécifiques ?
3. Serveur SMTP de Humans Connexion ?

### **Pour l'Automatisation :**
1. Fréquence monitoring DLIC ?
2. Qui reçoit les alertes ?
3. Configuration par utilisateur ou globale ?

---

## 🚀 Pour Demain

1. **Relire ce fichier** pour te remettre dans le contexte
2. **Décider** : IA d'abord ou Analyse/Rapports ?
3. **Lancer** `LANCER.bat` pour tester ce qui existe
4. **Continuer** là où on s'est arrêté

---

## 📂 Fichiers Modifiés Récemment (Janvier 2026)

### **Backend (27-29 Janvier 2026)**
- `src/core/database.py` - Chemins absolus améliorés pour .exe
- `src/core/commercial_parser.py` - Parser commercial avec pondérations pipeline
- `src/core/dashboard_calculator.py` - Calculs KPI + dispositifs + graphiques

### **Frontend (27 Janvier 2026)**
- `src/gui/main_window.py` - 6 onglets (ajout KPIs + Exploitation)
- `src/gui/exploitation_tab.py` - **NOUVEAU** Tableau éditable complet
- `src/gui/kpi_tab.py` - KPIs santé portefeuille + commerciaux

### **Distribution**
- `BUILD.bat` - Script build .exe
- `LANCER.bat` - Lancement dev

### **Documentation (30 Janvier 2026)**
- Mise à jour des docs pour refléter les nouveaux onglets

---

## 🎯 Objectif Final

**Livrer un outil professionnel permettant :**

1. ✅ Import Excel automatique
2. ✅ Dashboard KPI temps réel
3. ✅ Onglet KPIs (santé portefeuille + commerciaux)
4. ✅ Onglet Exploitation (tableau éditable)
5. ⏳ Analyse de données avancée (tri, filtres, export)
6. ⏳ Génération rapports PDF/Excel
7. ⏳ Envoi email automatique
8. ⏳ Assistant IA (optionnel mais impressionnant)
9. ⏳ Monitoring deadline
10. ✅ Distribution .exe autonome

**Progression : ~55% terminé** 🚀

---

<p align="center">
  <strong>Bon courage pour demain !</strong><br>
  <em>Le plus dur est fait, le reste c'est de la finition 💪</em>
</p>

