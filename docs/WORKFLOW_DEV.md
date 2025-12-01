# 🚀 Guide Workflow Développement - Huco Report

**Guide ultra-simple pour travailler en toute sécurité**

---

## ✅ Vérifier où tu es AVANT de coder

### **1. Quelle branche ?**
```powershell
git branch
```

**Résultat attendu** :
```
* develop    ← Tu es ici (ASTÉRISQUE)
  main
```

✅ **ASTÉRISQUE sur `develop`** = Tu peux coder !  
❌ **ASTÉRISQUE sur `main`** = DANGER ! Change de branche :
```powershell
git checkout develop
```

---

### **2. Quels fichiers modifiés ?**
```powershell
git status
```

**Lecture** :
- ✅ `On branch develop` = Tu es au bon endroit
- ⚠️ `Changes not staged` = Fichiers modifiés mais pas sauvegardés
- 📝 `Untracked files` = Nouveaux fichiers jamais vus par Git

---

## 🎯 Workflow Quotidien (3 étapes)

### **ÉTAPE 1 : Vérifier que tu es sur `develop`**
```powershell
git branch
```

**Si tu n'es PAS sur develop** :
```powershell
git checkout develop
```

---

### **ÉTAPE 2 : Coder normalement**
- Ouvre Cursor / VS Code
- Modifie tes fichiers
- Teste avec `python main.py` ou `.\LANCER.bat`
- Continue jusqu'à ce que ça fonctionne

---

### **ÉTAPE 3 : Sauvegarder ton travail**
```powershell
# Voir ce qui a changé
git status

# Ajouter TOUS les fichiers modifiés
git add .

# Sauvegarder avec un message clair
git commit -m "fix: correction compteur warnings"

# Exemples de messages :
# - "feat: ajout filtres dans onglet Analyse"
# - "fix: correction bug import Excel"
# - "docs: mise à jour README"
```

**✅ Fait ! Ton travail est sauvegardé dans l'historique**

---

## 🔄 Résumé Visuel

```
┌─────────────────────────────────────────┐
│  1. Vérifier branche                    │
│     git branch                          │
│     → * develop ✅                      │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│  2. Coder normalement                   │
│     - Modifier fichiers                 │
│     - Tester                            │
│     - Répéter jusqu'à satisfaction      │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│  3. Sauvegarder                         │
│     git add .                           │
│     git commit -m "message"             │
│     → ✅ Sauvegardé !                   │
└─────────────────────────────────────────┘
```

---

## 🚨 Scénarios Fréquents

### **Scénario 1 : Je suis sur `main` par erreur**

```powershell
# Vérifier
git branch
# Résultat : * main ❌

# Solution
git checkout develop
git branch
# Résultat : * develop ✅
```

---

### **Scénario 2 : J'ai oublié sur quelle branche je suis**

```powershell
# Commande simple
git branch

# Ou voir plus de détails
git status
# Première ligne : "On branch develop" ✅
```

---

### **Scénario 3 : J'ai modifié des fichiers mais je veux changer de branche**

```powershell
# Option A : Sauvegarder avant de changer
git add .
git commit -m "wip: modifications en cours"
git checkout main  # Puis revenir après
git checkout develop

# Option B : Annuler les modifications
git checkout -- .  # ⚠️ PERDU ! Tous les changements supprimés
```

---

### **Scénario 4 : Je veux tester sans casser develop**

```powershell
# Créer une branche de test
git checkout develop
git checkout -b test/ma-fonctionnalite

# Développer normalement
# Tester

# Si ça marche : merger dans develop
git checkout develop
git merge test/ma-fonctionnalite
git branch -d test/ma-fonctionnalite  # Supprimer la branche

# Si ça ne marche pas : revenir sur develop
git checkout develop
git branch -D test/ma-fonctionnalite  # Supprimer la branche (même si non mergée)
```

---

## ✅ Checklist Avant de Coder

Avant de commencer à modifier des fichiers :

```powershell
[ ] git branch           → Vérifier que * develop
[ ] git status           → Voir ce qui a changé depuis hier
```

---

## ✅ Checklist Après Avoir Codé

Avant de fermer ton PC :

```powershell
[ ] git status           → Voir ce qui a changé
[ ] git add .            → Ajouter les fichiers
[ ] git commit -m "..."  → Sauvegarder avec message clair
```

---

## 🎯 Règle d'Or

> **TOUJOURS développer sur `develop`**  
> **JAMAIS sur `main`** (sauf pour créer une version stable)

---

## 📊 Commandes Essentielles

```powershell
# Voir la branche actuelle
git branch

# Changer de branche
git checkout develop

# Voir l'état
git status

# Sauvegarder
git add .
git commit -m "message clair"

# Voir l'historique
git log --oneline -10

# Annuler les changements
git reset --hard  # ⚠️ ATTENTION : supprime tout !
```

---

## 💡 Exemples Concrets

### **Exemple 1 : Début de journée**

```powershell
# Vérifier où tu es
PS D:\DEV\Huco_Report> git branch
* develop    ✅ Parfait !

# Voir ce qui a changé depuis hier
PS D:\DEV\Huco_Report> git status
On branch develop
nothing to commit, working tree clean  ✅ Rien à sauvegarder

# C'est bon, tu peux coder !
```

---

### **Exemple 2 : Après avoir codé**

```powershell
# Voir ce qui a changé
PS D:\DEV\Huco_Report> git status
On branch develop
Changes not staged for commit:
        modified:   src/gui/dashboard_tab.py
        modified:   src/core/dashboard_calculator.py

# Sauvegarder
PS D:\DEV\Huco_Report> git add .
PS D:\DEV\Huco_Report> git commit -m "fix: correction compteur warnings vision interne"
[develop abc1234] fix: correction compteur warnings vision interne
 2 files changed, 15 insertions(+), 3 deletions(-)

✅ Sauvegardé !
```

---

### **Exemple 3 : Erreur de branche**

```powershell
# Oups, je suis sur main !
PS D:\DEV\Huco_Report> git branch
* main       ❌ Mauvaise branche !
  develop

# Solution
PS D:\DEV\Huco_Report> git checkout develop
Switched to branch 'develop'

PS D:\DEV\Huco_Report> git branch
  main
* develop    ✅ Bonne branche maintenant !
```

---

## 📞 Aide Rapide

```powershell
# Je suis perdu
git branch && git status

# Je veux sauvegarder
git add . && git commit -m "wip: modifications"

# Je veux annuler tout
git reset --hard  # ⚠️ ATTENTION !

# Je veux voir l'historique
git log --oneline --graph -10
```

---

## 🎓 Rappel des Branches

| Branche | Usage | Modifiable ? |
|---------|-------|--------------|
| `develop` | **Développement quotidien** | ✅ **OUI** - C'est ici que tu codes |
| `main` | Versions stables (distributions) | ❌ **NON** - Seulement pour releases |

---

**🎯 Règle simple** : Si tu codes, tu DOIS être sur `develop` !

---

<p align="center">
  <strong>Si tu as un doute, lance :</strong><br>
  <code>git branch</code><br>
  <em>Et vérifie que l'astérisque est sur develop !</em>
</p>

