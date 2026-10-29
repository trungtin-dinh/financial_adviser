# Architecture technique, dépendances et contrats de données

## 1. Structure actuelle

```text
app.py                           # Interface Streamlit, interaction/session
financial_adviser/
  __init__.py                     # Version
  models.py                       # Dataclasses Plan, OneOff + validation
  engine.py                       # Calculs mensuels et Monte Carlo indépendants
  io.py                           # Export/import JSON versionné
  i18n.py                         # Chaînes FR / EN / VI
  sources.py                      # API Banque mondiale
rules/catalogue.json             # Références officielles, PAS de taux fiscaux actifs
Documentation/                   # Dossier de connaissances versionné
tests/test_engine.py             # Tests de calcul et d'import/export
.streamlit/config.toml           # Thème et taille de chargement
```

**Interdiction architecturale :** `engine.py` ne dépend jamais de Streamlit, d'un compte bancaire ou d'une API externe. Les calculs restent possibles hors ligne.

## 2. Contrat de `Plan`

- `country ∈ {FR,VN}` ; `currency ∈ {EUR,VND}`. Leur cohérence est assurée dans l'interface par les modèles de démonstration ; un import JSON peut explicitement associer toute combinaison pour la simulation, sans conversion implicite.
- Revenus mensuels **nets**, dépenses mensuelles **hors remboursements de prêt et virements internes**, capitaux et objectifs dans une seule monnaie.
- Taux en **pour cent par an** et non en décimales ; les valeurs 5.0 signifient 5 %.
- Durée 1–60 ans, événements au mois 1..12*years, montants signés, 100 événements au plus dans le parseur UI.
- `initial_cash >= 0`, `initial_investments >= 0`, `loan_balance >= 0`, `goal >= 0`, `monthly_investment >= 0`.
- Le moteur autorise temporairement une **trésorerie négative** résultant des flux, avec avertissement.
- Le fichier JSON embarque `schema_version = 1`, et non la version de l'application ; les anciens schémas doivent être migrés explicitement.

## 3. Fonctions publiques

```python
from financial_adviser.models import Plan, OneOff
from financial_adviser.engine import project, monte_carlo
from financial_adviser.io import dump_plan, load_plan

plan = Plan(years=10, one_offs=(OneOff(12, -1000, 'example'),))
monthly_dataframe = project(plan)
summary = monte_carlo(plan, n_paths=1000, seed=42)
json_text = dump_plan(plan)
restored = load_plan(json_text)
```

Colonnes du dataframe : `month`, `year`, `cash`, `investments`, `loan_balance`, `net_worth`, `net_worth_real`, `purchasing_power_factor`, `income`, `expenses`, `loan_payment`, `one_off`. Ligne 0 = situation initiale, autres lignes = fin de chaque mois. Les sorties Monte Carlo comprennent quantiles mensuels de patrimoine net **nominal**, fraction d'atteinte de l'objectif final et indicateur de trésorerie négative.

## 4. Gestion de session

`st.session_state.plan` = dernier formulaire soumis ou importé. `st.session_state.result` = snapshot des calculs issus du plan, incluant `Plan` ; changer de pays réinitialise le modèle de démonstration et efface les résultats. Le formulaire n'est appliqué qu'au clic **Run**. Les comparaisons partent du plan validé, pas des changements encore non soumis.

**Absence de stockage persistant des scénarios :** exporter le JSON est nécessaire pour ne pas perdre la configuration. Sur Streamlit Cloud, des données de saisie traversent le serveur d'hébergement. Aucune garantie de stockage strictement local n'est revendiquée.

## 5. Modules futurs et contrats souhaités

```text
core/asset_ledger.py          -> AccountBalance, dated cash flow, invariants
core/currency.py              -> FX rate, source, timestamp, currency pair
models/asset_returns.py      -> ReturnModel.sample(seed, n, assets)
models/inflation.py           -> InflationModel.sample(...)
countries/base.py            -> CountryRules.calculate(context, tax_year, rule_version)
countries/fr/*               -> Séparer impôts / prélèvements / épargne
countries/vn/*               -> Séparer PIT / assurances / instruments
rules/registry.py            -> VerifiedRule(id, source, effective_date, status)
updates/collector.py         -> Fetch + validate + diff (sans activation automatique)
storage/scenarios.py         -> Schema migrations, versions, provenance
reports/                     -> CSV, HTML, PDF (à valider)
```

Une interface `CountryRules` devrait retourner une **décomposition** (bases, exemptions, retenues, total, sources) et signaler les cas non pris en charge ; elle ne doit jamais inventer un taux de remplacement.

## 6. Versionnage et publication

- `v0.1.0` = socle pédagogique, non fiscal. Les versions futures indiqueront explicitement les nouvelles capacités et limites.
- Le catalogue légal est révisé indépendamment du calcul. Une règle `status = documented_not_automatically_applied` n'autorise aucune utilisation dans le moteur.
- Releases GitHub possibles après tests et revue ; aucune publication de release ni déploiement n'est effectué automatiquement.
- Ne pas recopier du code tiers sans respecter sa licence ; les dépôts du benchmark servent uniquement de références de conception.
