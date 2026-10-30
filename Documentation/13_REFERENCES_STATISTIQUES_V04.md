# Références statistiques et préremplissage contrôlé — réalisation v0.4

**Date de revue du catalogue : 30 octobre 2026.** Les valeurs archivées représentent la dernière observation **sélectionnée et vérifiée** par source ; le catalogue n'est pas automatiquement une liste exhaustive des publications futures.

## Sources officielles vérifiées

- **France (Insee), salaires privés 2025** : médiane 2 238 EUR net social mensuel en équivalent temps plein ; publication du 22/10/2026, https://www.insee.fr/fr/statistiques/9087193 ; **non comparable directement** au revenu disponible net après impôt saisi dans l'application.
- **France (Insee), niveau de vie 2024** : niveau médian équivalisé 2 228 EUR/mois pour une personne seule ; publication du 09/07/2026, https://www.insee.fr/fr/statistiques/9019316 ; **ni salaire individuel ni revenu familial sans hypothèse d'unités de consommation**.
- **Vietnam (NSO), revenus 2025 provisoires** : revenu **moyen** mensuel **par personne**, environ 5,9 millions VND ; publication janvier 2026, https://www.nso.gov.vn/en/data-and-statistics/2026/01/press-release-social-economic-situation-in-the-fourth-quarter-and-2025/ ; **pas une médiane**.
- **Vietnam (NSO), dépenses 2024** : dépenses totales **moyennes** par personne, proches de 3 millions VND/mois (valeur arrondie) ; https://www.nso.gov.vn/tin-tuc-thong-ke/2025/05/thong-cao-bao-chi-ket-qua-khao-sat-muc-song-dan-cu-nam-2024/ ; **pas un budget familial**.
- **Inflation passée** : Banque mondiale FP.CPI.TOTL.ZG pour FRA/VNM, consultation manuelle facultative et cache 24h ; https://api.worldbank.org/ et https://datahelpdesk.worldbank.org/knowledgebase/articles/889392.

## Contrat technique et expérience utilisateur

1. Le fichier `data/statistical_references.json` sauvegarde la source, l'année statistique, la période de publication (jour ou mois), l'unité, le pays, le caractère médiane/moyenne et la population.
2. Le module `statistical_references.py` valide la structure, l'unité monétaire, le domaine officiel, les dates et les définitions ; les références comparativement inadaptées sont interdites pour l'autoremplissage.
3. La page distincte `Références statistiques` ne modifie aucune entrée personnelle lorsque l'utilisateur consulte les médianes/moyennes.
4. L'inflation est la seule hypothèse statistique appliquable en v0.4 ; **son taux passé est explicitement décrit comme simple hypothèse de scénario, sans valeur prédictive**.
5. L'utilisateur clique sur « Vérifier le taux d'inflation observé », lit le pays/l'année/la source et le comparatif avant/après, coche son consentement, puis « Appliquer ». Aucun changement lors d'une panne réseau, d'une valeur invalide, d'un pays différent ou sans consentement.
6. Seul `inflation_pct` du dernier scénario sauvegardé est modifié. Les revenus, dépenses, actifs, objectifs et événements de vie sont préservés ; les résultats calculés antérieurement sont marqués obsolètes.
7. Les données de référence sont traduites par un catalogue FR/EN/VI spécifique. Les noms d'organismes, unités et URL restent invariants.

## Limites et suites dépendantes de la qualité des sources

- Aucun « profil médian universel » ni génération de salaires/dépenses à partir d'un couple de statistiques incompatibles.
- Pas encore de données officielles de consommation française pleinement compatibles avec le champ de budget, ni de distribution vietnamienne après impôt et ménage contextualisé.
- Les valeurs de portefeuille ou rendement futur ne peuvent pas être déduites d'une médiane démographique.
- Pas de synchronisation ni validation juridique automatisée, ni stockage durable des sources utilisées dans le JSON de scénario v1.
- Des tests automatiques dans GitHub Actions ne remplacent pas des entretiens réels ou la validation de spécialistes.
