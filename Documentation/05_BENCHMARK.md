# Étude des applications comparables

**Date de collecte : 2026-10-29.** Sources publiques, dépôts GitHub et documentations ; seules certaines entrées et architectures ont été lues, **aucune vérification exhaustive ni exécution des applications tierces**.

| Projet | Type | Enseignements | Limites pour notre périmètre |
|---|---|---|---|
| [MontePlan](https://github.com/engineerinvestor/monteplan) | Python, Streamlit, simulateur Monte Carlo | Architecture avec moteur pur Python, UI séparée ; modèles de rendement/stratégies de retrait ; analyse de sensibilité | Fiscalité surtout américaine ; ne pas réutiliser les règles légales |
| [MyFinModel](https://github.com/Blockish/myfinmodel) | Python/Streamlit, planification retraite | Session state, scénarios et détection de paramètres ayant changé depuis le calcul, lanceur portable local | Cas des retraités US ; architecture adaptée à ce contexte |
| [Monte Carlo Retirement](https://github.com/cakesandcode/monte-carlo-retirement) | Python/Streamlit | Module `ARCHITECTURE.md`, séparation inflation/returns/portfolio/tax, exports | Assumptions US, couche fiscale non transposable |
| [Wealthfolio](https://github.com/wealthfolio/wealthfolio) | Suivi du patrimoine local-first | UX, import, contrôle des données, restitution claire | Stack différente, beaucoup de fonctionnalités non prioritaires |
| [Actual Budget](https://github.com/actualbudget/actual) | Budget personnel open source | Parcours d'intégration, budget simple, synchronisation optionnelle | Prédominance du budget et non de la projection patrimoniale |
| [Ghostfolio](https://github.com/ghostfolio/ghostfolio) | Suivi de portefeuille | Performance/diversification, agrégation de positions | Produit de suivi, pas moteur fiscal FR/VN |
| [Firefly III](https://github.com/firefly-iii/firefly-iii) | Budget / transactions | Catégorisation, comptabilité, API | Prise en main et maintenance plus lourdes |
| [ProjectionLab](https://projectionlab.com/help/using-what-if) | Application propriétaire | Comparaison what-if et événements chronologiques | Source propriétaire : observation des interactions uniquement |
| [Finary](https://help.finary.com/fr/articles/15301061-creer-et-suivre-mes-objectifs) | Application propriétaire | Navigation par objectifs financiers | Propriétaire ; fonctionnalités susceptibles d'évoluer |
| [MISA Sổ Thu Chi](https://sothuchi.misa.vn/) | Application vietnamienne | Vocabulaire et besoins quotidiens VN | Budget plutôt que projection complexe |

## Code effectivement consulté pour cadrage

- `engineerinvestor/monteplan/README.md` et `app/Home.py` : structure UI, modèles de simulation, démarrage de scénarios.
- `Blockish/myfinmodel/README.md` et `app.py` : structure Streamlit, déclenchement de simulation, indicateur de résultats périmés.
- `cakesandcode/monte-carlo-retirement/README.md` et `ARCHITECTURE.md` : contrats de configuration, moteurs spécialisés, flux de données.
- `actualbudget/actual/README.md` : modèle local-first, conception communautaire et installation.

## Leçons UX et remontées communautaires

Retour de discussions Reddit sur les outils de budget auto-hébergés : certains utilisateurs valorisent une installation simple et les transactions importées, d'autres remontent la complexité de la configuration, la catégorisation et la maintenance. Ces discussions sont **des signaux qualitatifs et non des enquêtes représentatives**. Références accessibles via les rubriques communauté/issues des dépôts :

- [Actual Budget — feature requests](https://github.com/actualbudget/actual/issues?q=is%3Aissue+label%3A%22needs+votes%22)
- [Wealthfolio — issues](https://github.com/wealthfolio/wealthfolio/issues)
- [Firefly III — issues](https://github.com/firefly-iii/firefly-iii/issues)

## Décisions issues du benchmark

1. Un mode simple opérationnel, avec quelques entrées et une première projection immédiate.
2. Paramètres avancés disponibles sans complexifier le parcours initial.
3. Moteur indépendant de Streamlit, important pour les tests et futures interfaces.
4. Différence visible entre hypothèses, observations et résultats ; avertissements sur les probabilités.
5. Sauvegarde explicite et reproduction des résultats.
6. Veille fiscale **séparée** du mécanisme de calcul, avec approbation et tests.

Il n'existe pas dans cette sélection de moteur FR/VN exhaustif validé ; les algorithmes fiscaux doivent être conçus et testés à partir des textes officiels pertinents.
