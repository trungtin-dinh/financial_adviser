# Journal de décisions et mises à jour

## 2026-10-30 — Bug sur l'application publique détecté par Chromium

- Premier test réel : le site charge Streamlit mais l'application échoue sur `KeyError('nav_benchmarks')` ; les tests locaux passaient.
- Hypothèse principale : module `ui_i18n` périmé en mémoire après hot reload, bien que GitHub contienne les clés. Rechargement explicite de traduction et redéploiement complet demandé via changement du fichier de dépendances.
- Test de non-régression des libellés de navigation ajouté; nouveau contrôle de l'app publique après CI.


## 2026-10-30 — URL publique et démarche ergonomique

- URL Streamlit communiquée par le propriétaire : https://financial-adviser.streamlit.app/ (lien ajouté au README).
- Référentiel fondé sur NN/g, ISO 9241-210, GOV.UK et WCAG 2.2, avec audit UX priorisé.
- Premier contrôle HTTPS non navigateur bloqué par une boucle de redirections HTTP 303. Remplacé par un test Chromium public (exemple → projection → résultats + rendu mobile) après le workflow CI. Un test de fumée n'est pas un audit exhaustif.
- La description et le lien « Website » dans les métadonnées GitHub nécessitent une modification du champ « About » séparément du README.



## 2026-10-30 — v0.4.0 : catalogue statistique et plan directeur

- Plan d'ensemble et critères d'acceptation : `Documentation/12_PLAN_GLOBAL.md`.
- Sources officielles INSEE/NSO avec unité, année, population et nature moyenne/médiane.
- Données de population incompatibles : lecture seule, sans injection personnelle automatique.
- Inflation World Bank : aperçu et consentement avant application au scénario, jamais présentée comme prévision.
- Les phases nationales, la fiscalité, les probabilités de risques et les études utilisateurs réelles restent non implémentées.


## 2026-10-29 — Refonte v0.2.0 : événements de vie, objectif inverse et parcours utilisateur

- Refondre `app.py` en routeur multipage (`pages/planning.py`, `pages/guide.py`, `pages/sources.py`).
- Réserver les paramètres essentiels au parcours principal (revenus nets, dépenses, objectif, horizon) ; charger une démo seulement sur demande, laisser les taux de simulation optionnels et modifiables.
- Ajouter `LifeEvent` avec flux de revenu, dépense mensuelle supplémentaire et coût ponctuel datés. Aucune probabilité médicale ou familiale n’est inférée.
- Ajouter `solve_goal` pour retrouver trois ajustements indépendants (revenu, dépenses, apport) sous contraintes de patrimoine final et de trésorerie.
- Tester les équations et le chargement des anciens scénarios JSON.
- Revue de conception par personas fictifs documentée ; ne pas prétendre à des essais avec vrais utilisateurs ni à une validation par des experts.
- Recherche UX : Nielsen Norman Group (progressive disclosure et heuristiques), GOV.UK (questions essentielles), Streamlit (navigation), ProjectionLab (événements de dépenses). Voir `09_FACTEURS_DE_VIE_ET_UX.md`.

**Limites restant ouvertes** : édition des événements sur petit écran, taux et taxes FR/VN, risque statistique des événements, audit navigateur et revue humaine.


## 2026-10-29 — Création de la base de connaissances et v0.1.0

**Décisions retenues**

- Développer un moteur Python indépendant de Streamlit, avec états et flux mensuels explicites.
- Viser France et Vietnam dans la structure et les références, mais **ne pas inventer de fiscalité légale** dans la première version.
- Présenter toutes les valeurs par défaut comme des hypothèses fictives et non des statistiques officielles.
- Obtenir l'inflation observée via Banque mondiale **en option** ; ne pas remplacer une hypothèse automatiquement.
- Utiliser des exports JSON/CSV, pas de comptes ni de connexions bancaires.
- Favoriser une interface desktop, sans supposer que le mobile est déjà pleinement validé.
- Lire les codes et documentations de MontePlan, MyFinModel et Monte Carlo Retirement pour éclairer la séparation moteur/UI ; réécrire nos propres calculs.
- Tests unitaires de toutes les équations fondamentales avant diffusion.

**Points à revoir**

- Complexité fiscale FR/VN, année fiscale et résidence, intégration des sources juridiques validées.
- Propriétés statistiques du Monte Carlo et leur interprétation (risque de mauvaise confiance).
- Modélisation d'une trésorerie négative, d'une dette sans actif et des arrondis monétaires.
- Audit du parcours mobile et de l'ensemble des traductions.
- Différence de persistance entre exécution locale et Streamlit Cloud.

**Règle d'entretien** : à chaque incrément, ajouter ici les nouveaux changements, sources confirmées, limites corrigées et fichiers concernés. Ne pas remplacer une référence officielle sans conserver la date et le motif de remplacement.
