# KPIs - Tableau de Bord SSII/ESN

**Dernière mise à jour** : 26 Janvier 2026

Ce document recense les KPIs pertinents pour le pilotage du portefeuille client d'une SSII/ESN.

---

## 1. SANTÉ DU PORTEFEUILLE

| KPI | Description | Données disponibles |
|-----|-------------|---------------------|
| **Taux de projets sains** | % projets sans warning (ni Client ni Interne) | ✅ vision_client, vision_internal |
| **Taux d'alerte anticipée** | % warnings Internes avant warning Client (le CP anticipe) | ✅ vision_client, vision_internal |
| **Projets à risque** | Projets avec warning Client ET Interne simultané | ✅ |
| **Durée moyenne en warning** | Nb semaines qu'un projet reste en warning | ✅ Historique par semaine |
| **Tendance warnings** | ↑ ou ↓ par rapport à la semaine précédente | ✅ |

---

## 2. PILOTAGE OPÉRATIONNEL

| KPI | Description | Données disponibles |
|-----|-------------|---------------------|
| **Taux de DLIC respectées** | % DLIC non dépassées | ✅ dlic |
| **Délai moyen de retard DLIC** | Nb jours moyen de dépassement | ✅ dlic |
| **Projets sans deadline** | Projets actifs sans DLIC définie | ✅ |
| **Charge par acteur** | Nb actions en attente par personne | ✅ next_actor |
| **Actions sans responsable** | Projets en warning sans acteur assigné | ✅ |

---

## 3. COMMERCIAL & REVENUS

| KPI | Description | Données disponibles |
|-----|-------------|---------------------|
| **Jours vendus totaux** | Somme des jours facturables | ✅ days_sold, days_dispositif_monthly |
| **Potentiel d'upsell** | Clients avec "dispositif augmentable = oui+" | ✅ dispositif_expandable |
| **Pipeline maintenance** | Nb clients avec potentiel TMA identifié | ✅ potential_maintenance |
| **Pipeline hébergement** | Nb clients avec potentiel hosting | ✅ potential_hosting |
| **Nouveaux projets potentiels** | Clients avec opportunité détectée | ✅ potential_new_projects |
| **Taux de fidélisation** | Clients actifs depuis > 6 mois | ⚠️ À calculer via historique |

---

## 4. RELATION CLIENT

| KPI | Description | Données disponibles |
|-----|-------------|---------------------|
| **NPS moyen Commercial** | Moyenne relation client commerciale | ✅ nps_commercial |
| **NPS moyen Projet** | Moyenne relation client projet | ✅ nps_project |
| **Clients à risque de churn** | Warning Client > 2 semaines consécutives | ✅ Historique |
| **Fréquence échanges client** | Délai moyen entre RDV client | ✅ last_client_exchange, next_client_exchange |
| **Clients "silencieux"** | Pas d'échange depuis > 2 semaines | ✅ |

---

## 5. PERFORMANCE PAR BU / CHEF DE PROJET

| KPI | Description | Données disponibles |
|-----|-------------|---------------------|
| **Projets par BU** | Répartition de la charge | ✅ bu |
| **Warnings par BU** | Quelle BU a le plus de problèmes | ✅ |
| **Charge par CP** | Nb projets actifs par chef de projet | ✅ project_manager |
| **Taux de warning par CP** | Quel CP a le plus de difficultés | ✅ |
| **Performance comparée** | Classement CP par % projets sains | ✅ |

---

## 6. VISION STRATÉGIQUE (Direction)

| KPI | Description | Utilité |
|-----|-------------|---------|
| **Indice de santé global** | Score 0-100 combinant plusieurs KPIs | Vue synthétique |
| **Prévision de charge** | Estimation projets à venir | Planification RH |
| **Concentration client** | % CA sur top 3 clients | Risque dépendance |
| **Mix contrat** | Répartition forfait / régie | Stratégie commerciale |
| **Taux de transformation** | Potentiel détecté → projet signé | Efficacité commerciale |

---

## 7. ALERTES AUTOMATIQUES

| Alerte | Déclencheur |
|--------|-------------|
| 🔴 **Client en danger** | Warning Client > 3 semaines |
| 🟡 **Opportunité commerciale** | Client sain + potentiel upsell détecté |

---

## Sources de données

### Fichier principal : Suivi Hebdo (nouveau.xlsx)
- Données projets par semaine
- Warnings, deadlines, acteurs
- Potentiels commerciaux

### Fichier complémentaire : input.xlsx (Input Commercial)

**Onglet : HUMAN'S**

| Colonne | Description |
|---------|-------------|
| Client | Nom du client |
| Offre | Type d'offre (Régie, Assistance/Consulting, etc.) |
| Project | Nom du projet |
| BU | Business Unit (REGIE, etc.) |
| Id_project | Code projet (HC240105, etc.) |
| Contract Document | Document contractuel |
| Comment | Commentaires |
| Scenario | W=Worst, E=Expected, B=Best |
| Status | Statut commercial |
| TJM | Taux Journalier Moyen |
| Days | Nombre de jours |
| Rev1-Rev4 | Revenus par période |
| Rev2025 | Revenu total 2025 |
| Jan-Dec | Détail mensuel prévu |
| JanR-DecR | Détail mensuel réalisé |

**KPIs possibles avec ces données :**
- CA prévisionnel par scénario (W/E/B)
- TJM moyen par BU
- Taux de réalisation (Réalisé vs Prévu)
- Pipeline commercial
- Charge prévisionnelle mensuelle

---

## Implémentation

### Phase 1 - Onglet KPI (Santé du portefeuille) ✅
- Taux de projets sains
- Taux d'alerte anticipée
- Projets à risque
- Tendance warnings

### Phase 2 - KPIs Commerciaux (input.xlsx) ✅
- **Taux Régie/Build** : Répartition des projets par type d'offre
- **Pipeline pondéré** : CA pondéré par probabilité
  - Signed = 100%
  - Agreed (A) = 80%
  - Likely (L) = 50%
  - Specul (Spec) = 20%
- **Taux de réalisation** : Réalisé vs Prévu
- **TJM Moyen** : Taux journalier moyen
- **Compteurs par statut** : Signed, Agreed, Likely

### Module commercial_parser.py

```python
from src.core.commercial_parser import CommercialParser

parser = CommercialParser()
parser.load_file("input.xlsx")
parser.parse_sheet()  # Parse l'onglet HUMAN'S
kpis = parser.calculate_kpis()

# Résultat :
{
    'taux_regie': 45.2,        # % de projets en régie
    'taux_build': 54.8,        # % de projets build/forfait
    'pipeline_total': 500000,   # CA total
    'pipeline_pondere': 380000, # CA pondéré par probabilité
    'taux_realisation': 72.5,   # % réalisé vs prévu
    'tjm_moyen': 650,          # TJM moyen
    'nb_projets_signed': 12,
    'nb_projets_agreed': 8,
    'nb_projets_likely': 5,
    'nb_projets_specul': 3,
}
```

### Phase 3 - À définir
- Graphiques d'évolution commerciale
- Prévisions de CA
