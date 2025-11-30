# 🔧 Guide Git - Huco Report

Guide pratique pour gérer les versions et protéger ton code.

---

## 📌 Concepts Clés

### **Git = Historique Local**
```
Git stocke TOUT l'historique sur ton PC
📍 Localisation : D:\DEV\Huco_Report\.git\

Avantages :
✅ Revenir à n'importe quelle version
✅ Tester sans casser le code stable
✅ Savoir QUI a changé QUOI et QUAND
✅ Fonctionne HORS LIGNE
```

### **Branches = Lignes de Développement Parallèles**
```
master (ou main)
├── Version stable (v1.0.0)
└── Utilisée pour les distributions

develop
├── Développement quotidien
├── Nouvelles fonctionnalités en cours
└── Base pour les branches features

feature/ai-assistant
├── Fonctionnalité isolée
├── Tests sans impacter develop
└── Merge dans develop quand prêt
```

---

## 🎯 Commandes Essentielles

### **Voir où tu es**
```powershell
# Quelle branche ?
git branch

# Quels fichiers modifiés ?
git status

# Historique des commits
git log --oneline --graph --all
```

---

### **Sauvegarder ton Travail**

#### **Commit Simple** (tous les jours)
```powershell
# Étape 1 : Voir ce qui a changé
git status

# Étape 2 : Ajouter les fichiers modifiés
git add .

# Étape 3 : Sauvegarder avec message
git commit -m "fix: correction bug dashboard dispositifs"
```

#### **Conventions de Messages**
```
feat: nouvelle fonctionnalité
fix: correction de bug
docs: documentation uniquement
style: formatage (pas de changement de code)
refactor: refactorisation (pas de changement de comportement)
test: ajout de tests
chore: maintenance (build, config, etc.)

Exemples :
✅ feat: ajout onglet Analyse avec filtres
✅ fix: correction compteur DLIC dépassées
✅ docs: mise à jour CHANGELOG.md
✅ refactor: extraction méthode calculate_kpis()
```

---

### **Créer une Version Stable**

```powershell
# Étape 1 : S'assurer d'être sur develop
git checkout develop

# Étape 2 : Tout commiter
git add .
git commit -m "feat: onglet Analyse complet"

# Étape 3 : Merge dans master
git checkout master
git merge develop

# Étape 4 : Créer le tag de version
git tag -a v1.1.0 -m "Release 1.1.0 - Ajout onglet Analyse"

# Étape 5 : Retourner sur develop
git checkout develop
```

---

### **Travailler sur une Fonctionnalité Isolée**

```powershell
# Étape 1 : Créer une branche depuis develop
git checkout develop
git checkout -b feature/assistant-ia

# Étape 2 : Développer et commiter régulièrement
git add .
git commit -m "feat: intégration Azure OpenAI"
git commit -m "feat: ajout function calling"
git commit -m "fix: gestion erreurs API"

# Étape 3 : Quand terminé, merger dans develop
git checkout develop
git merge feature/assistant-ia

# Étape 4 : (Optionnel) Supprimer la branche feature
git branch -d feature/assistant-ia
```

---

### **Revenir en Arrière (IMPORTANT !)**

#### **Annuler modifications NON commitées**
```powershell
# Annuler TOUS les changements depuis dernier commit
git reset --hard

# Annuler changements sur UN fichier
git checkout -- src/gui/dashboard_tab.py
```

#### **Revenir à une version précédente**
```powershell
# Voir les versions disponibles
git tag

# Revenir temporairement à v1.0.0 (lecture seule)
git checkout v1.0.0

# Revenir à develop pour continuer
git checkout develop

# CRÉER une nouvelle branche depuis v1.0.0
git checkout v1.0.0
git checkout -b hotfix/correction-urgente
```

#### **Annuler le DERNIER commit** (si erreur)
```powershell
# Garder les modifications (recommandé)
git reset --soft HEAD~1

# Supprimer complètement le commit et les modifs
git reset --hard HEAD~1
```

---

## 🚨 Scénarios de Secours

### **Scénario 1 : J'ai tout cassé !**
```powershell
# Solution : Revenir au dernier commit
git reset --hard

# Résultat : Tous les fichiers reviennent à leur état du dernier commit
```

---

### **Scénario 2 : Le build ne fonctionne plus !**
```powershell
# Solution : Revenir à la dernière version stable
git checkout v1.0.0

# Tester le build
.\BUILD.bat

# Si ça marche, identifier le problème dans develop
git checkout develop
git log --oneline

# Revenir à un commit spécifique
git checkout abc1234
```

---

### **Scénario 3 : Comparer 2 versions**
```powershell
# Voir les différences entre develop et master
git diff master develop

# Voir les différences entre 2 tags
git diff v1.0.0 v1.1.0

# Voir les différences sur UN fichier
git diff v1.0.0 v1.1.0 -- src/gui/dashboard_tab.py
```

---

### **Scénario 4 : Historique détaillé d'un fichier**
```powershell
# Voir tous les commits qui ont modifié ce fichier
git log --oneline -- src/core/dashboard_calculator.py

# Voir les modifications ligne par ligne
git blame src/core/dashboard_calculator.py
```

---

## 📦 Workflow Complet de Distribution

### **Créer une Release v1.1.0**

```powershell
# ═══════════════════════════════════════════════════════
# ÉTAPE 1 : Finaliser develop
# ═══════════════════════════════════════════════════════
git checkout develop
git status  # S'assurer que tout est commité
git add .
git commit -m "feat: onglet Analyse + filtres terminé"

# ═══════════════════════════════════════════════════════
# ÉTAPE 2 : Créer branche release
# ═══════════════════════════════════════════════════════
git checkout -b release/v1.1.0

# Mettre à jour VERSION dans settings.py
# (Tu peux le faire manuellement ou automatiquement)

git add src/config/settings.py
git commit -m "chore: bump version to 1.1.0"

# ═══════════════════════════════════════════════════════
# ÉTAPE 3 : Build PRÉ-PROD
# ═══════════════════════════════════════════════════════
.\BUILD.bat

# Renommer le dossier
cd dist
mv HucoReport HucoReport_v1.1.0-beta
cd ..

# Tester sur 2-3 PC (toi + collègues)
# Corriger les bugs si nécessaire :
git add .
git commit -m "fix: correction bug graphiques"
.\BUILD.bat  # Re-build

# ═══════════════════════════════════════════════════════
# ÉTAPE 4 : Validation → Production
# ═══════════════════════════════════════════════════════
# Si tout OK après tests, merger dans master
git checkout master
git merge release/v1.1.0

# Créer le tag
git tag -a v1.1.0 -m "Release 1.1.0 - Onglet Analyse + Filtres"

# Merger aussi dans develop (pour garder les corrections)
git checkout develop
git merge release/v1.1.0

# Supprimer la branche release
git branch -d release/v1.1.0

# ═══════════════════════════════════════════════════════
# ÉTAPE 5 : Build PRODUCTION
# ═══════════════════════════════════════════════════════
git checkout master
.\BUILD.bat

cd dist
mv HucoReport HucoReport_v1.1.0
cd ..

# Zipper et distribuer
# Mettre à jour CHANGELOG.md
```

---

## 🎯 Résumé Visuel

```
Flux de Travail Quotidien
─────────────────────────────────────────────────────

1. Développement
   └─ Branche : develop
      └─ Commits réguliers

2. Nouvelle Fonctionnalité
   └─ Branche : feature/xxx
      └─ Merge dans develop quand prêt

3. Préparer Release
   └─ Branche : release/v1.x.0
      └─ Build beta → Tests
      └─ Corrections bugs
      └─ Merge dans master + develop

4. Version Stable
   └─ Branche : master
      └─ Tag : v1.x.0
      └─ Build final
      └─ Distribution équipe
```

---

## 🔑 Commandes Rapides

```powershell
# Statut actuel
git status

# Sauvegarder travail
git add . && git commit -m "fix: correction bug"

# Voir historique
git log --oneline --graph --all

# Changer de branche
git checkout develop
git checkout master

# Annuler changements
git reset --hard

# Voir versions
git tag

# Revenir à version
git checkout v1.0.0

# Créer nouvelle version
git tag -a v1.1.0 -m "Release 1.1.0"
```

---

## 💡 Bonnes Pratiques

### ✅ À FAIRE
- Commit régulièrement (plusieurs fois par jour)
- Messages clairs et descriptifs
- Toujours développer sur `develop` (jamais sur `master`)
- Tester avant de merger dans `master`
- Créer un tag pour chaque distribution

### ❌ À NE PAS FAIRE
- Modifier directement sur `master`
- Commits avec message "update" ou "fix"
- Oublier de commiter avant de changer de branche
- Supprimer le dossier `.git\`
- Forcer les opérations (`--force`) sans comprendre

---

## 📞 Aide Rapide

```powershell
# Si tu es perdu
git status
git branch

# Si tu as cassé quelque chose
git reset --hard

# Si tu veux revenir en arrière
git checkout v1.0.0

# Si tu veux voir l'historique
git log --oneline --graph --all

# Si tu veux de l'aide sur une commande
git help <commande>
git help commit
git help branch
```

---

## 🔗 Ressources

- [Documentation Git officielle](https://git-scm.com/doc)
- [Git Cheat Sheet](https://education.github.com/git-cheat-sheet-education.pdf)
- [Conventional Commits](https://www.conventionalcommits.org/fr/)
- [Semantic Versioning](https://semver.org/lang/fr/)

---

**Conseil** : Imprime ce guide et garde-le près de ton PC ! 🖨️

