# v0.22.1 — Fiabilité des saisies et ergonomie des résultats

**Date :** 31 octobre 2026. **Nature :** correctifs ; aucune équation financière modifiée.

## 1. Défauts corrigés

Les défauts ont été trouvés par un test systématique : chaque champ d'un scénario JSON a été remplacé par une valeur invalide (booléen, texte, décimal, `null`, 1e308, NaN, liste…), puis le scénario a été importé et calculé.

| Défaut | Conséquence avant correction | Correction |
|---|---|---|
| Horizon décimal (`"years": 2.5`) accepté | Validation réussie, puis plantage du calcul | Les mois, années et âges doivent être des entiers |
| Texte remplacé par un nombre (ex. catégorie d'un événement) | Erreur Python non interceptée à l'import (`AttributeError`) | Contrôle du type de chaque champ avant les règles métier |
| Montants énormes (1e308) acceptés | Résultats `NaN`/infinis | Tout montant doit être fini et de valeur absolue ≤ 10¹⁵ (`MAX_ABS_AMOUNT`) |
| Flux ponctuels importés sans limite ni contrôle de description | Fichiers très longs acceptés | 100 flux au maximum, description ≤ 120 caractères |
| Description de flux ponctuel contenant une virgule | Le scénario ne se relançait plus après export puis import (« ligne invalide ») | Texte de l'éditeur écrit au format CSV, avec guillemets si nécessaire |
| Rechargement après déploiement fondé sur une liste de modules écrite à la main | Un nouveau module oublié dans la liste pouvait rester périmé (cf. incident `KeyError('nav_benchmarks')`) | Au changement de version, tous les modules `financial_adviser.*` sont oubliés puis réimportés |

La limite de 10¹⁵ correspond à environ 38 milliards d'euros en VND : elle n'écarte aucun budget de ménage. Un test vérifie qu'avec tous les montants à cette limite, 200 % de rendement et 60 ans, la projection reste finie.

Les entiers JSON (`3000`) restent acceptés dans les champs décimaux : les anciens fichiers exportés se chargent comme avant.

## 2. Refactorisation sans changement de résultat

`engine.py` : l'amortissement du prêt existant et celui du nouveau crédit immobilier utilisent une seule fonction `_amortize` ; les dépenses du foyer ne sont plus calculées deux fois dans `project()`.

**Vérification :** sur 400 scénarios aléatoires (prêts, achat immobilier, enfants, adultes, proches, flux ponctuels et récurrents, événements), `project`, `monte_carlo` et `solve_goal` donnent des résultats **identiques au bit près** à ceux de la v0.22.0. Aucun gain de vitesse n'est revendiqué (pas de mesure avant/après).

## 3. Ergonomie

- **Montants selon la langue :** `1 234,56 €` en français, `€1,234.56` en anglais, `1.234,56 €` / `1.234.567 ₫` en vietnamien ; espace insécable avant le symbole. Mois de réserve et ratios suivent le même séparateur décimal. Les exports CSV/JSON ne changent pas.
- **Après « Lancer la projection » :** le bouton est en bas d'un long formulaire alors que les résultats commencent en haut de la page. Un récapitulatif (« Projection terminée », patrimoine final, alerte de trésorerie négative) reste affiché sous le bouton tant que les saisies n'ont pas changé, avec un lien « Voir les résultats » vers le titre des résultats. Vérifié dans Chromium sur PC (1440×900) et mobile (390×844).
- **Message d'erreur :** « Vérifiez les montants, les dates et les durées saisis » (l'ancien texte ne parlait que des événements), suivi du détail technique de la validation.

## 4. Limites

- Le détail technique de l'erreur est en anglais (nom de champ du modèle).
- Les infobulles des graphiques Plotly gardent le format numérique anglais.
- Les objets d'interface conservés en session lors d'un déploiement restent migrés par `session_compat.py` pour le `Plan` ; les brouillons du foyer et des événements sont des dictionnaires et ne dépendent pas des classes rechargées.

## 5. Tests ajoutés

`tests/test_input_robustness.py`, `tests/test_hot_reload.py`, `tests/test_formatting.py`.
