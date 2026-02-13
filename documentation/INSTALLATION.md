# Guide d'Installation - Huco Report

## Prérequis

### Pour utiliser le .exe (recommandé)
- Windows 10 ou 11
- Aucun autre logiciel requis

### Pour le développement
- Windows 10 ou 11
- Python 3.11 ou 3.12
- Git (optionnel)

---

## Installation rapide (.exe)

1. **Télécharger** le dossier `HucoReport` depuis le partage réseau
2. **Copier** le dossier où vous voulez (Bureau, Documents, etc.)
3. **Double-cliquer** sur `HucoReport.exe`
4. **C'est prêt !**

### Si Windows Defender bloque l'application

Windows peut bloquer l'exécution car l'application n'est pas signée numériquement.

1. Cliquez sur **"Plus d'infos"** dans l'alerte
2. Cliquez sur **"Exécuter quand même"**

C'est normal et sans danger.

---

## Installation développeur

### Étape 1 : Installer Python

**Via Microsoft Store (recommandé)** :
1. Ouvrez le Microsoft Store
2. Recherchez "Python 3.12"
3. Cliquez "Installer"

**Vérification** :
```bash
python --version
# Doit afficher : Python 3.12.x
```

### Étape 2 : Cloner/Copier le projet

```bash
# Si vous avez Git
git clone [url-du-repo] Huco_Report

# Sinon, copiez simplement le dossier
```

### Étape 3 : Créer l'environnement virtuel

```bash
cd Huco_Report
python -m venv venv_new
```

### Étape 4 : Activer l'environnement

**Windows (CMD)** :
```bash
venv_new\Scripts\activate.bat
```

**Windows (PowerShell)** :
```bash
.\venv_new\Scripts\Activate.ps1
```

**Git Bash** :
```bash
source venv_new/Scripts/activate
```

### Étape 5 : Installer les dépendances

```bash
pip install -r requirements.txt
```

### Étape 6 : Lancer l'application

```bash
python main.py
```

---

## Construire le .exe

### Prérequis
- Environnement virtuel activé
- Toutes les dépendances installées

### Commande

```bash
# Utiliser le script de build
.\BUILD.bat
```

### Résultat

Le dossier `dist/HucoReport/` contient :
- `HucoReport.exe` - L'application
- `_internal/` - Dépendances Python
- `config/` - Configuration
- `img/` - Logo et images

### Distribution

1. Zipper le dossier `dist/HucoReport/`
2. Envoyer le .zip aux utilisateurs
3. Ils n'ont qu'à dézipper et double-cliquer sur l'exe

---

## Structure des dossiers

### En mode développement

```
Huco_Report/
├── venv_new/          # Environnement virtuel (créé par vous)
├── src/               # Code source
├── config/            # Configuration
├── data/              # Base de données locale
├── logs/              # Logs de l'application
├── import/            # Fichiers Excel à importer
├── main.py            # Point d'entrée
└── requirements.txt   # Dépendances
```

### En mode .exe

```
HucoReport/
├── HucoReport.exe     # Application
├── _internal/         # Python et dépendances
├── config/            # Configuration
├── img/               # Logo
├── data/              # (créé automatiquement)
└── logs/              # (créé automatiquement)
```

---

## Résolution des problèmes

### "Python est introuvable"

**Cause** : Python n'est pas dans le PATH ou pas installé.

**Solution** :
1. Installez Python via Microsoft Store
2. Ou téléchargez depuis python.org et cochez "Add to PATH"

### "Module not found"

**Cause** : Dépendances non installées ou mauvais environnement.

**Solution** :
```bash
# Vérifier que le venv est activé
# Le prompt doit afficher (venv_new)

# Réinstaller les dépendances
pip install -r requirements.txt
```

### L'application se ferme immédiatement

**Cause** : Erreur au démarrage (souvent première utilisation).

**Solution** :
1. Regardez les logs : `logs/error.log`
2. Lancez depuis la ligne de commande pour voir l'erreur :
   ```bash
   python main.py
   ```

### "Access denied" ou "Permission denied"

**Cause** : Droits insuffisants sur le dossier.

**Solution** :
- Copiez l'application dans un dossier avec droits d'écriture (Documents, Bureau)
- Évitez `C:\Program Files\`

---

## Mises à jour

### Mise à jour du .exe

1. Téléchargez la nouvelle version
2. Remplacez l'ancien dossier par le nouveau
3. La base de données est conservée dans `%LOCALAPPDATA%\HucoReport\`

### Mise à jour développeur

```bash
# Récupérer les modifications
git pull

# Mettre à jour les dépendances si nécessaire
pip install -r requirements.txt
```
