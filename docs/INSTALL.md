# 📦 Installation - Huco Report

## 🚀 Installation pour Développement

### 1️⃣ Prérequis

- **Python 3.11+** : [Télécharger Python](https://www.python.org/downloads/)
- **Git** (optionnel) : [Télécharger Git](https://git-scm.com/downloads)

### 2️⃣ Étapes d'Installation

#### Option A : Clonage depuis Git (si projet versionné)
```powershell
# Naviguer vers le dossier de développement
cd D:\DEV

# Cloner le projet
git clone [URL_DU_REPO] Huco_Report
cd Huco_Report
```

#### Option B : Projet déjà en local
```powershell
# Naviguer vers le projet
cd D:\DEV\Huco_Report
```

### 3️⃣ Créer l'Environnement Virtuel

```powershell
# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement virtuel
.\venv\Scripts\activate

# Vous devriez voir (venv) dans votre terminal
```

### 4️⃣ Installer les Dépendances

```powershell
# Installer toutes les dépendances
pip install -r requirements.txt

# Attendre quelques minutes pour l'installation...
```

### 5️⃣ Lancer l'Application

```powershell
# Lancer Huco Report
python main.py
```

✅ **L'application devrait se lancer avec une interface graphique !**

---

## 🎯 Installation pour Utilisateurs Finaux

### Méthode Simple (Fichier .exe)

1. **Télécharger** le fichier `HucoReport.exe`
2. **Double-cliquer** sur le fichier
3. **C'est tout !** Aucune installation requise

> 💡 **Note** : Le fichier .exe sera disponible après le build de production

---

## 🛠️ Build de l'Exécutable (pour distribution)

### Installer PyInstaller

```powershell
pip install pyinstaller
```

### Créer le fichier .exe

```powershell
# Build simple
pyinstaller --onefile --windowed --name HucoReport main.py

# Build avancé avec icône et données
pyinstaller --onefile --windowed --name HucoReport --icon=assets/icon.ico --add-data "config/excel_schema.json;config" main.py
```

### Trouver l'exécutable

```powershell
# Le fichier .exe se trouve dans :
cd dist
dir HucoReport.exe
```

### Distribuer le fichier

1. Copier `dist/HucoReport.exe`
2. Partager avec l'équipe
3. Double-cliquer pour lancer

---

## ⚠️ Résolution de Problèmes

### Erreur : "Python n'est pas reconnu"

**Solution** : Installer Python et cocher "Add Python to PATH" lors de l'installation

### Erreur : "pip n'est pas reconnu"

**Solution** :
```powershell
python -m ensurepip --upgrade
```

### Erreur : "venv\Scripts\activate ne fonctionne pas"

**Solution** : Politique d'exécution PowerShell
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\venv\Scripts\activate
```

### Erreur lors de l'installation de PyQt6

**Solution** : Mettre à jour pip
```powershell
python -m pip install --upgrade pip
pip install PyQt6
```

### L'application ne se lance pas

**Vérifications** :
1. L'environnement virtuel est activé ? `(venv)` visible
2. Toutes les dépendances sont installées ? `pip list`
3. Vous êtes dans le bon dossier ? `dir main.py`

---

## 📋 Checklist Post-Installation

- [ ] Python 3.11+ installé
- [ ] Environnement virtuel créé et activé
- [ ] Dépendances installées (`pip list` montre PyQt6, pandas, etc.)
- [ ] Application se lance avec `python main.py`
- [ ] Interface graphique s'affiche correctement

---

## 📞 Support

En cas de problème persistant :
1. Vérifier la documentation dans `docs/`
2. Contacter le responsable du projet
3. Consulter les logs dans `logs/app.log`

---

<p align="center">
  <strong>Installation réussie ? Bienvenue dans Huco Report ! 🎉</strong>
</p>

