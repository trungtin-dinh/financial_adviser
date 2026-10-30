# Journal de décisions et mises à jour

## 2026-10-30 — v0.7.0 candidate : cycle de vie des ménages

- Profils facultatifs pour plusieurs enfants, âge au démarrage, mois d'arrivée, âge de fin de soutien (25 ans par défaut, modifiable), coûts mensuels par tranches d'âge et postes de consommation.
- Inclusion dans le budget courant traitée explicitement pour éviter le double comptage; fin de soutien libérant les dépenses précédemment incluses.
- Profils facultatifs d'adultes, charges par âge et retraite hypothétique avec part du revenu net du ménage. Les personnes déjà retraitées ne subissent aucune seconde conversion de salaire.
- Références et réserves scientifiques documentées dans `21_CYCLE_VIE_BUDGET_FAMILIAL.md` ; pas de coût médian par enfant inventé ni de pension réglementaire calculée.
- Vérifications locales ciblées du moteur et des traductions; pas de tests navigateur/public revendiqués. Actions GitHub toujours en déclenchement manuel, sans notification automatique de push.



## 2026-10-30 — v0.6.0 : scénarios éditables et interactions prévisibles

- Six modèles de risque déterministes paramétrés depuis le budget, sans faux taux de probabilité.
- Comparaison de stress indépendante du scénario de référence, patrimoine final et trésorerie minimale.
- Confirmation pour changer le pays ou remplacer le plan par l'exemple.
- Résultats montrés après calcul sans `st.rerun()` inopiné; champs numériques accessibles au clavier au lieu de curseurs critiques.
- Audit et limites dans `20_REDESIGN_V06.md`; tests du nouveau module ciblés localement. Tests complets navigateur et revue indépendante encore en attente.
- Aucun workflow GitHub Actions réactivé automatiquement.



## 2026-10-30 — Refonte ergonomique et notifications

- Suppression des déclencheurs GitHub Actions automatiques; exécution manuelle seulement. La préférence e-mail GitHub nécessite un réglage du compte.
- Inventaire sourcé de 87 facteurs financiers, économiques et sociaux; séparation calculé / événement explicite / référence descriptive / non implémenté.
- UI simplifiée : paramètres toujours visibles, ordre de lecture unique données → résultats → objectif → comparaison, pays/langue visibles, état périmé des résultats et coût cumulé des événements.
- Ajout d'un protocole de tests synthétiques et d'une liste de relecteurs indépendants à consulter. **Aucun véritable participant ni expert indépendant recruté** ; version candidate et non finale.



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
