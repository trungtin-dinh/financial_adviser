# Taxonomie des facteurs affectant les projections financières
**Revue de littérature et architecture : 30 octobre 2026.** Inventaire de conception, **pas** validation économétrique ni liste exhaustive de toutes les lois. Les valeurs et probabilités futures ne sont pas inférées des enquêtes générales.

## Usage et niveaux de maturité
- **D** : Calculé dans le moteur actuel (parfois modèle simplifié)
- **E** : Représentable par événement financier explicite; pas de probabilité estimée
- **R** : Référence observable consultable; non appliquée automatiquement
- **N** : À étudier / non modélisé; aucune prédiction produite

Les études consultées ne donnent pas un seul jeu de paramètres universel et une distribution commune FR/VN. Le tableau transpose leurs *dimensions de collecte ou d'analyse* en variables de simulation plausibles : une variable peut être proposée ici sans exister encore dans le moteur.

Les enquêtes de la BCE sur la situation financière des ménages incluent les actifs, dettes, consommation, revenus, retraite, transferts intergénérationnels et contraintes de crédit. Le CFPB distingue le budget courant, les chocs, les dépenses exceptionnelles et les plans de dettes. Les études OCDE sur les risques sociaux prennent en compte l'emploi, le logement, la santé, les enfants, la dépendance, le vieillissement et les risques climatiques/géopolitiques. Les enquêtes officielles Insee et NSO peuvent décrire des profils de ménages, mais ne donnent **pas** la probabilité personnelle d'un incident.

## Profil et composition du ménage

| Facteur / variable candidate | Mécanisme financier | Statut |
|---|---|---|
| Âge et année de naissance | durée d'horizon, changements de carrière/retraite | D |
| Nombre d'adultes et mise en commun du budget | plusieurs revenus, mutualisation des coûts | N |
| Nombre/enfants à charge par âge | garde, scolarité, aides, budget | E |
| Famille monoparentale, garde alternée | répartition des dépenses, transferts | E |
| Situation conjugale et changement de foyer | revenus, logements, fiscalité et transferts | E |
| Personnes âgées dépendantes à charge | temps d'aide et frais récurrents | E |
| Localisation ville/région/ruralité | loyer, transport, prix, couverture | N |
| Situation migratoire / résidence fiscale | droit fiscal, conversion monétaire, transferts | N |
| Niveau d'études et compétences | évolution des revenus, reconversion | E |
| Handicap / besoins d'accessibilité | dépenses, capacités de travail et aides | E |

## Revenus et emploi

| Facteur / variable candidate | Mécanisme financier | Statut |
|---|---|---|
| Salaire net actuel | entrée de trésorerie mensuelle | D |
| Salaire variable, primes, 13e mois | flux saisonniers/ponctuels | E |
| Hausse de salaire et changement de poste | profil temporel des revenus | D |
| Temps partiel et congé parental | baisse temporaire du revenu | E |
| Chômage et durée de recherche | perte de revenu et prestations hypothétiques | E |
| Risque de rupture d'emploi / revenu | distribution d'événements; calibration exigée | N |
| Activité indépendante chiffre d'affaires et charges | volatilité, frais, cotisations | E |
| Revenus de dividendes, intérêts, loyers | entrées, fiscalité et volatilité | N |
| Revenus de pension et calendrier retraite | remplacement du salaire et indexation | N |
| Aides sociales et subventions conditionnelles | transferts et règles nationales | N |
| Pensions alimentaires, cadeaux, remises | flux réguliers ou ponctuels | E |
| Revenus de plusieurs membres du ménage | co-cotisation, risque de corrélation | N |

## Consommation et charges

| Facteur / variable candidate | Mécanisme financier | Statut |
|---|---|---|
| Dépenses mensuelles globales | sortie récurrente et surplus | D |
| Loyer, charges, énergie, eau, taxes d'occupation | dépenses contraintes, exposition prix | E |
| Alimentation et habillement | inflation spécifique et taille du foyer | N |
| Transport et mobilité (véhicule, carburant, abonnement) | dépenses + achat/remplacement | E |
| Dépenses santé à charge et franchise | dépenses et couverture; pas de risque médical inventé | E |
| Assurances (habitation, auto, prévoyance, santé) | primes et franchises | E |
| Crèche/garde/éducation/études supérieures | dépenses par étape d'âge | E |
| Culture, vacances, loisirs, cadeaux | dépenses discrétionnaires | E |
| Dépenses ponctuelles: travaux, déménagement, réparation | sorties datées | E |
| Coûts de transition écologique / rénovation | investissements et économies éventuelles | E |
| Inflation différenciée par catégorie | profil de prix personnel vs IPC général | N |
| Flexibilité des dépenses en période de crise | comportement de réduction du budget | N |

## Épargne, liquidité et patrimoine

| Facteur / variable candidate | Mécanisme financier | Statut |
|---|---|---|
| Trésorerie initiale | réserve liquidité | D |
| Investissements initiaux | capital à rendement | D |
| Virements récurrents entre cash et investissement | allocation interne sans revenu nouveau | D |
| Taux de rémunération de trésorerie | croissance des liquidités | D |
| Rendement annuel du portefeuille | croissance du capital; hypothèse non garantie | D |
| Volatilité des investissements | dispersion Monte Carlo simplifiée | D |
| Allocation actions/obligations/monétaire/immobilier | rendement, volatilité et corrélation | N |
| Frais de courtage, gestion, produits | réduction des performances | N |
| Liquidité, délais de rachat, pénalités | capacité de financer événements | N |
| Fiscalité de chaque enveloppe et plus-values | rendement net après impôts | N |
| Valeur logement/terrain et frais d'entretien | actifs réels et charges | N |
| Valeur entreprise, participations non cotées | patrimoine peu liquide, valorisation incertaine | N |
| Héritage, donation et héritabilité | événements et fiscalité | E |

## Crédit et immobilier

| Facteur / variable candidate | Mécanisme financier | Statut |
|---|---|---|
| Capital restant dû | passif initial | D |
| Taux nominal du crédit | échéancier d'amortissement | D |
| Durée résiduelle du crédit | calendrier des échéances | D |
| Taux variable et scénarios de refinancement | risque mensualité/choc de taux | N |
| Assurance emprunteur, garantie, frais de dossier | coût effectif du crédit | N |
| Crédit consommation, étudiant, cartes | sorties et liquidité | N |
| Achat/vente d'un bien | apport, dette, taxes, frais, actif | E |
| Prix du bien et évolution de valeur | patrimoine réel et risque illiquide | N |
| Vacance locative et défaut du locataire | revenu net immobilier, trésorerie | N |
| Taxes foncières et gros travaux | charges saisonnières et imprévues | E |

## Santé, famille et protection sociale

| Facteur / variable candidate | Mécanisme financier | Statut |
|---|---|---|
| Naissance/adoption d'un enfant | dépenses initiales/récurrentes | E |
| Maladie et convalescence | baisse d'activité et soins; scénario utilisateur | E |
| Handicap/incapacité de travail | revenus et frais + prestations | E |
| Décès et survivant, contrat prévoyance | perte de revenus, capital, héritage | N |
| Séparation, divorce et déménagement | coûts et nouveaux budgets | E |
| Dépendance et soins de longue durée | dépense longue et transfert familial | E |
| Exposition au reste à charge médical | couverture, plafonds, dépenses | E |
| Assistance familiale / remises transnationales | transfert de trésorerie et change | E |

## Facteurs macroéconomiques et risques

| Facteur / variable candidate | Mécanisme financier | Statut |
|---|---|---|
| Inflation générale future | pouvoir d'achat du résultat | D |
| Inflation observée et provenance | référence descriptive, jamais prévision | R |
| Choc d'inflation énergie/alimentaire | budget de consommation et revenu réel | N |
| Croissance réelle des salaires/productivité | dynamique des revenus | D |
| Taux d'intérêt directeur et taux du marché | épargne, coût du crédit, valorisations | N |
| Risque de krach / séquence des rendements | soutenabilité retraits, patrimoine | N |
| Corrélation marchés/chômage/revenu | risque systémique conjoint | N |
| Risque de change EUR/VND et inflation FX | conversion, transferts, bilan multidevise | N |
| Crise géopolitique ou catastrophe naturelle | dégâts, interruption revenu, coûts | E |
| Risque climatique local et assurance | dommages/franchises/prime | N |
| Changement de lois fiscales ou prestations | impôts/revenus disponibles | N |
| Changement de politique retraite et démographie | date de retraite, pensions, services | N |

## Décisions et objectifs

| Facteur / variable candidate | Mécanisme financier | Statut |
|---|---|---|
| Objectif de patrimoine net | cible de projection | D |
| Horizon de projection | durée des intérêts composés | D |
| Apport, effort mensuel ou réduction de dépense nécessaires | solution inverse isolée | D |
| Priorité entre plusieurs objectifs | arbitrage et calendrier | N |
| Tolérance au risque / aversion aux pertes | contraintes, pas rendements garantis | N |
| Taux de retrait futur et longévité | épuisement du capital, séquence | N |
| Changement comportemental lié au stress financier | dépenses/épargne endogènes | N |
| Réserve d'urgence cible en mois de charges | résilience et liquidité | N |
| Contraintes de capital non négatif en cours de vie | faisabilité par mois | D |
| Provenance des hypothèses et millésime des règles | reproductibilité et transparence | N |

## Modélisation, dépendances et précautions

### Flux, bilan et calendrier
- Simuler chaque **mois** et distinguer **stocks** (cash, actifs, dettes) des **flux** (salaires, dépenses, frais, retraits, héritage).
- Conservation des transferts internes : virer 100 du compte courant vers un portefeuille ne crée pas 100 de patrimoine supplémentaire.
- Actif immobilier et crédit associé doivent être modélisés ensemble pour le patrimoine net (l'actuel moteur ne crée pas d'actif immobilier en contrepartie de la dette).
- Événement : mois de début, durée, coût ponctuel, variation du revenu net, dépense mensuelle supplémentaire, date éventuelle de fin. Les hypothèses doivent rester librement éditables.
- Les impôts et prestations sont des règles **date/version/pays** et doivent être testés avant d'influencer une simulation; les cas transfrontaliers nécessitent une validation spécialisée.

### Taux et prix
- Taux annuel effectif vers mensuel : r_m=(1+r_a)^(1/12)−1, si r_a représente un rendement annuel effectif constant.
- Pouvoir d'achat : V_réel(t)=V_nominal(t)/∏_(k=1)^t(1+π_k), π_k étant l'inflation du mois k. L'IPC historique n'est pas π_k futur.
- Salaire nominal et salaire réel ne doivent pas être mélangés. Les flux datés peuvent relever d'une inflation spécifique (éducation/énergie/soins) plutôt que du seul IPC général.

### Incertitudes : trois niveaux distincts
1. **Déterministe** : utilisateur explicite « deux ans sans emploi, puis reprise »; coûts et dates paramétrés.
2. **Sensibilité / stress** : plusieurs trajectoires plausibles, sans prétendre aux probabilités; p. ex. dépense de santé +30 %, inflation plus forte, revenus plus faibles.
3. **Probabiliste calibrée** : distributions, corrélations, fréquence/durée des événements, estimation conditionnelle à l'âge/régime/localisation. Exige données vérifiées et hypothèses discutables, tests de calibration et analyse des biais. **Ne pas inventer de risque médical personnel**, ni transformer « x % préoccupés par le chômage » en probabilité de perdre son emploi.

### Interdépendances importantes
- Naissance → frais de garde + éventuelle baisse du temps de travail + prestations + évolution de l'impôt.
- Chômage → baisse de revenu + éventuelles allocations + ajustement des dépenses + report des investissements + risque de dette.
- Maladie → perte de salaire + soins remboursés/non remboursés + prévoyance + éventuel proche aidant.
- Achat immobilier → apport + frais + prêt + charges + valeur du bien + liquidité réduite; éviter **double comptage**.
- Crise économique → rendements, inflation, salaires, emploi et valeur immobilière **corrélés**.
- Expatriation FR/VN → devise, impôt, pension, prestations, coût de la vie, transfert et conventions. Ne pas réduire à un taux de change.

## Paramètres à exposer à l'utilisateur (stratégie UX)

**Toujours visibles pour une première projection :** pays/devise, revenu net mensuel, dépenses mensuelles, trésorerie initiale, investissement initial, objectif et horizon. Regrouper mais ne pas masquer les hypothèses modifiables de rendement, inflation, croissance, dette et événements; une aide courte explique chaque unité.

**Demandés seulement lorsque pertinents :** enfants, aidants, soins, chômage, logement, crédit et transferts (sélection explicite d'une situation). Les champs restent repérables et n'exigent jamais de données médicales identifiantes.

**Références statistiques :** afficher séparément moyenne/médiane, unité, champ, année de collecte/publication et source; pas d'autofill d'une moyenne « par habitant » dans le revenu net d'un ménage.

**Non implémenté :** afficher « non encore modélisé » dans la documentation, sans présenter un champ décoratif qui ne change pas les résultats.

## Références primaires et périmètre

- BCE / *Household Finance and Consumption Survey* : https://www.ecb.europa.eu/stats/ecb_surveys/hfcs/html/index.en.html — structure de bilan/flux et conditions socio-démographiques.
- Deutsche Bundesbank / PHF survey methodology : https://www.bundesbank.de/en/bundesbank/research/panel-on-household-finances-phf/methodology-617406 — neuf modules du questionnaire.
- OCDE / *More Effective Social Protection for Stronger Economic Growth*, 2025 : https://www.oecd.org/en/publications/more-effective-social-protection-for-stronger-economic-growth_3947946a-en.html — catégories de risques perçus (les perceptions ne sont pas des fréquences personnelles).
- OCDE / *Pensions at a Glance 2025* : https://www.oecd.org/en/publications/pensions-at-a-glance-2025_e40274c1-en.html — retraite/longévité/cadre réglementaire.
- OCDE/INFE / Financial Literacy Survey et Toolkit 2026 : https://doi.org/10.1787/92f2d439-en — bien-être, littératie, résilience.
- CFPB / *Your Money, Your Goals* : https://www.consumerfinance.gov/consumer-tools/educator-tool/your-money-your-goals/toolkit/ — budget, revenus, dépenses, événements, dettes et plans.
- Fed / *SHED 2025*, rapport publié mai 2026 : https://www.federalreserve.gov/consumerscommunities/shed.htm — fragilité des ménages, santé, retraite, emploi; exemple des dimensions pertinentes, non de données FR/VN.
- Insee / *Budget de famille* : https://www.insee.fr/fr/statistiques/4648335 — dépenses par niveau de vie, type de ménage et logement (données 2017, **ne pas présenter comme 2026**).
- Insee / *La consommation des ménages en 2025* : https://www.insee.fr/fr/statistiques/9006503 — consommation, prix et pouvoir d'achat.
- NSO Vietnam / VHLSS 2024, publié mars 2026 : https://www.nso.gov.vn/en/data-and-statistics/2026/03/results-of-the-viet-nam-household-living-standards-survey-2024/ — emploi, revenu, dépenses, logement, santé, scolarité.
- OMS Europe / dépenses catastrophiques de santé : https://www.who.int/europe/news/item/05-12-2024-up-to-1-in-5-households-in-europe-experience-catastrophic-spending-because-of-health-care-costs--new-who-digital-platform-shows — importance des restes à charge, **sans transposer le pourcentage à un individu**.
- GIEC / AR6 2023 : https://www.ipcc.ch/report/sixth-assessment-report-cycle/ — catégories de risques physiques et d'adaptation.

## Priorisation des extensions futures
1. Améliorer **les flux et le bilan** avant d'ajouter des « probabilités » : dépenses par catégorie, actifs réels, plusieurs dettes, frais.
2. Ensuite **événements composites** (enfant, chômage, santé) explicitement paramétrables, puis protections/assurances et prestations.
3. Séparer règles **France**, **Vietnam**, passage entre pays et sources officielles versionnées.
4. Ajouter chocs macro et corrélations **uniquement après qualification des hypothèses**.
5. Faire relire le modèle et les libellés par experts (économiste/actuaire/fiscaliste FR-VN) et tester avec **participants réels** avant de déclarer une version finale.
