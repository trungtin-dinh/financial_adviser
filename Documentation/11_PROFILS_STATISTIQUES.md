# Profils statistiques et préremplissage documenté — décision de conception

**Créé : 30 octobre 2026 · Statut : conception, NON implémenté dans v0.3.0.**

## Objectif

Permettre un premier scénario pour une personne débutante à partir d'indicateurs officiels **sans prétendre connaître ses finances personnelles**. Prévoir un bouton volontaire `Consulter les références statistiques` puis un aperçu des champs qui pourraient être préremplis, avec confirmation explicite.

## Trois catégories de paramètres

1. **Observations historiques descriptives** : distributions de revenus, consommation, inflation passée, taux administrés, taux observés. Elles exigent pays, définition, unité, population, année de référence, date de publication, nom de la statistique (médiane/moyenne/décile) et URL source.
2. **Hypothèses futures de scénario** : croissance salariale, rendement des placements, inflation prospective, risque de chômage. Les observations ne doivent jamais être prises pour des prévisions ou probabilités personnelles. Conserver des valeurs de simulation éditables séparées des observations.
3. **Choix individuels** : enfant, santé, achat, patrimoine, dettes, horizon de vie, objectifs. Aucune « médiane nationale » ne remplace ces choix. Initialiser neutre (souvent zéro ou aucun événement), demander les données essentielles si nécessaire.

## Références concrètes, vérifiées le 30/10/2026

| Pays | Donnée observée | Valeur | Période | Statistique et population | Utilisation |
| --- | --- | ---: | --- | --- | --- |
| FR | Salaire mensuel net du privé en équivalent temps plein | 2 238 EUR | 2025 | Médiane des salariés du privé en EQTP, **net de cotisations sociales mais pas nécessairement net après impôt sur le revenu** | Afficher comme repère, ne pas injecter directement dans `monthly_income` (qui exige un net après impôts) |
| FR | Niveau de vie mensuel pour personne seule (équivalent à la médiane des unités de consommation) | 2 228 EUR | 2024 | Médiane de niveau de vie, France métropolitaine, champ de l'enquête ERFS ; ce n'est PAS le salaire médian ni nécessairement le revenu réel de chaque ménage | Afficher comme repère contextualisé ; ne pas appliquer à tous les foyers |
| VN | Revenu moyen mensuel par personne | 5,415 millions VND | 2024 | **Moyenne** par habitant, et non médiane, enquête sur les conditions de vie des ménages | Repère seulement ; ne pas prétendre qu'il s'agit de la médiane d'un salaire ou d'un ménage |
| VN | Dépense moyenne mensuelle par personne | 2,977 millions VND | 2024 | **Moyenne**, et non médiane, par habitant | Repère ; ne pas en déduire une épargne médiane |

Sources :
- INSEE, *Les salaires dans le secteur privé en 2025*, publication octobre 2026 : https://www.insee.fr/fr/statistiques/9087193
- INSEE, *Niveau de vie et pauvreté en 2024*, publication 9 juillet 2026 : https://www.insee.fr/fr/statistiques/9019316
- National Statistics Office of Vietnam, *Results of the Viet Nam Household Living Standards Survey 2024*, publié mars 2026 : https://www.nso.gov.vn/en/data-and-statistics/2026/03/results-of-the-viet-nam-household-living-standards-survey-2024/
- NSO, *Health and living standards 2024*, tableau national : https://www.nso.gov.vn/wp-content/uploads/2026/01/NG-TONG-CUC-2024_OKIN_Final.pdf

**Important :** la médiane du revenu moins la médiane des dépenses ne constitue pas la médiane de l'épargne ; ne jamais calculer une « capacité d'épargne médiane » en soustrayant des médianes issues de distributions différentes.

## Parcours d'interface proposé

1. Choisir pays et devise, facultativement région et composition du ménage / situation professionnelle, sans imposer les données sensibles.
2. Ouvrir `Références statistiques` pour lire la définition, l'année de collecte et la date de publication.
3. Afficher un aperçu des valeurs proposées, champs applicables et non applicables (par exemple « indicateur non comparable » ou « médiane indisponible »). Le bouton d'application n'est actif que pour les indicateurs dont la définition correspond à celle du champ.
4. Appliquer **seulement après consentement explicite**, en conservant les champs personnels et les événements déjà saisis ; toute valeur reste modifiable et identifiable comme suggérée.
5. Permettre `Restaurer mes valeurs` ou `Annuler le préremplissage` ; sérialiser sources et versions avec le scénario. Jamais de mutation silencieuse à l'ouverture.
6. Actualisation opt-in / bouton indépendant. Si réseau indisponible ou source imprécise, utiliser le dernier jeu versionné clairement daté ou ne pas préremplir.

## Architecture de la source de données

Une observation sera typée par `country`, `region`, `population`, `household_type`, `metric_id`, `statistic` (median/mean/percentile), `value`, `unit`, `period`, `published_on`, `retrieved_on`, `source_url`, `comparability`, `autofill_allowed`, `quality_flags`.

Une règle de correspondance stricte entre unités et définitions interdit d'utiliser un salaire avant impôt comme revenu mensuel disponible après impôt, une moyenne comme médiane ou une statistique par personne comme un budget familial. Données et règles doivent être conservées indépendamment du code UI, archivées et testées.

## Critères d'acceptation

- Aucun chiffre ne paraît « officiel » sans source, période de référence et définition.
- Aucune confusion moyenne/médiane, brut/net, ménage/personne, passé/prévision.
- Le bouton de préremplissage ne touche jamais aux événements de vie ni aux valeurs volontairement remplies.
- Une source indisponible ne conduit ni à inventer une valeur ni à choisir par défaut une autre statistique.
- Traduction complète FR/EN/VI des contrôles, avertissements, unités, sources et vues.
- Tests desktop/mobile : lisibilité des repères, confirmation avant écrasement, annulation et stabilité du formulaire.

**Ordre conseillé :** consolider d'abord la v0.3.0 responsive multilingue ; implémenter ensuite un explorateur de références en lecture seule avant d'autoriser le préremplissage automatique.
