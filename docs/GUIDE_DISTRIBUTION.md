# 📦 Guide de Distribution - Huco Report

## 🎯 Objectif

Créer un package autonome de Huco Report pour distribution à l'équipe.

---

## 🛠️ Création du package

### Étape 1 : Builder l'application

Double-cliquez sur **`BUILD.bat`**

Le script va :
1. ✅ Nettoyer les anciens builds
2. ✅ Créer l'exécutable avec PyInstaller
3. ✅ Copier les fichiers nécessaires (config, img)
4. ✅ Créer un README utilisateur
5. ✅ Préparer le dossier de distribution

**Durée** : 2-5 minutes selon la machine

---

### Étape 2 : Récupérer le package

Après le build, vous trouverez :

```
dist/
└── HucoReport/           ← DOSSIER À DISTRIBUER
    ├── HucoReport.exe    ← L'application
    ├── _internal/        ← Dépendances (NE PAS SUPPRIMER)
    ├── config/           ← Configuration
    │   └── excel_schema.json
    ├── img/              ← Logo
    │   └── cropped-logo-groupe-huco.webp
    ├── data/             ← Base de données (vide au départ)
    └── README.txt        ← Instructions utilisateur
```

---

## 📤 Distribution

### Option 1 : ZIP (Recommandé)

```powershell
# Compresser le dossier
Compress-Archive -Path "dist\HucoReport" -DestinationPath "HucoReport_v1.0.zip"
```

**Avantages** :
- ✅ Facile à envoyer par email
- ✅ Taille : ~150-200 MB
- ✅ Décompression simple

---

### Option 2 : Partage réseau

Copiez le dossier `dist\HucoReport\` sur un partage réseau :

```
\\serveur\partage\HucoReport\
```

**Avantages** :
- ✅ Mise à jour centralisée
- ✅ Pas de téléchargement
- ❌ Nécessite accès réseau

---

### Option 3 : Clé USB

Copiez le dossier sur une clé USB et distribuez physiquement.

---

## 👥 Installation côté utilisateur

### Pour vos collègues :

1. **Décompresser** le ZIP (ou copier le dossier)
2. **Ouvrir** le dossier `HucoReport`
3. **Double-cliquer** sur `HucoReport.exe`
4. **C'est tout !** ✅

**Aucune installation requise** :
- ❌ Pas de Python à installer
- ❌ Pas de pip
- ❌ Pas de venv
- ❌ Pas de dépendances

---

## ⚠️ Problèmes courants

### 1. Antivirus bloque le .exe

**Cause** : Les .exe générés par PyInstaller sont parfois détectés comme suspects.

**Solution** :
- Ajouter une exception dans l'antivirus
- Ou demander à l'IT d'approuver le fichier

---

### 2. "Fichier introuvable : config/excel_schema.json"

**Cause** : Les fichiers config/ ou img/ n'ont pas été copiés.

**Solution** :
- Relancer `BUILD.bat`
- Vérifier que les dossiers sont présents

---

### 3. Application lente au démarrage

**Cause** : Première extraction des dépendances.

**Solution** :
- Normal, patience (5-10 secondes)
- Les lancements suivants seront plus rapides

---

## 🔄 Mise à jour

Pour distribuer une nouvelle version :

1. **Modifier le code** source
2. **Relancer** `BUILD.bat`
3. **Renommer** le ZIP : `HucoReport_v1.1.zip`
4. **Distribuer** la nouvelle version

**Attention** : Les utilisateurs devront supprimer l'ancien dossier et décompresser le nouveau.

---

## 📊 Taille approximative

- **Dossier non compressé** : ~350 MB
- **ZIP** : ~150-200 MB
- **Contenu** :
  - Python embarqué
  - PyQt6
  - Pandas, openpyxl
  - Matplotlib
  - Toutes les dépendances

---

## 🎯 Checklist avant distribution

- [ ] `BUILD.bat` exécuté sans erreur
- [ ] `HucoReport.exe` présent dans `dist\HucoReport\`
- [ ] Dossier `config\` présent avec `excel_schema.json`
- [ ] Dossier `img\` présent avec le logo
- [ ] `README.txt` créé
- [ ] Test de l'exe sur votre machine
- [ ] ZIP créé (optionnel)

---

## 📞 Support

Pour toute question sur la distribution :
- Contactez le service informatique
- Consultez la documentation développeur

---

**© 2025 Humans Connexion - Tous droits réservés**

