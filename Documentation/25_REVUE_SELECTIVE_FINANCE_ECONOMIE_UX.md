# Revue sélective de dépôts financiers, économiques et UX — Financial Adviser

**Date de revue : 30 octobre 2026.** **Portée : 36 dépôts repérés et consultés au niveau approprié ; 14 sources examinées plus en détail.** Ceci est un dossier de connaissances et d'aide à la décision, **pas une preuve de validation financière ni une autorisation de réutiliser le code**.

## 1. Méthode et niveau de confiance

La sélection privilégie les besoins propres à **Financial Adviser** : simulateur pédagogique de budget et patrimoine de ménage, pas logiciel bancaire ni plateforme de trading. Les critères sont : adéquation à l'usage, précision des conventions, transparence des hypothèses, qualité des garde-fous, ergonomie, coût de maintenance et licence.

Trois degrés de lecture sont distingués :
- **Étude ciblée :** page spécialisée DeepWiki, documentation technique ou source primaire examinée ; les enseignements figurent au tableau analytique ci-dessous.
- **Aperçu :** présentation générale DeepWiki ou README du projet, suffisante pour identifier son intérêt, insuffisante pour valider une méthode détaillée.
- **Repérage :** description et état du dépôt via GitHub uniquement ; **aucune** méthode n'est attribuée à ces références sans étude complémentaire.

**Précaution :** DeepWiki est une synthèse automatisée indexée à une date donnée, parfois ancienne. Vérifier la version actuelle, les hypothèses mathématiques, les tests et la licence **dans les sources primaires** avant toute adaptation. « P1/P2/P3 » ci-dessous est une priorité **pour notre produit**, jamais un classement scientifique des dépôts. Les projets archivés ou peu actifs servent éventuellement de références conceptuelles, **pas** de dépendances recommandées.

## 2. Inventaire traçable — 36 dépôts

| N° | Dépôt | Domaine | Vérification réalisée | Priorité | Ce que nous en retenons |
|---:|---|---|---|---|---|
| 01 | [actualbudget/actual](https://github.com/actualbudget/actual) | Finances personnelles | DeepWiki détaillé | P1 | Échéanciers, budgets ciblés et modèles de dépenses |
| 02 | [firefly-iii/firefly-iii](https://github.com/firefly-iii/firefly-iii) | Finances personnelles | DeepWiki détaillé | P1 | Objectifs virtuels, conservation de l'argent, garde-fous |
| 03 | [afadil/wealthfolio](https://github.com/afadil/wealthfolio) | Finances personnelles | DeepWiki détaillé | P1 | Retraite, scénarios de choc, objectifs et diagnostics |
| 04 | [maybe-finance/maybe](https://github.com/maybe-finance/maybe) | Finances personnelles | DeepWiki détaillé; dépôt archivé | P2 | Bilan et réconciliation, pas un composant à reprendre |
| 05 | [ghostfolio/ghostfolio](https://github.com/ghostfolio/ghostfolio) | Finances personnelles | README original | P2 | Répartition du patrimoine et visualisation |
| 06 | [kresusapp/kresus](https://github.com/kresusapp/kresus) | Finances personnelles | DeepWiki aperçu | P3 | Regroupement des opérations, confidentialité |
| 07 | [beancount/beancount](https://github.com/beancount/beancount) | Finances personnelles | DeepWiki aperçu | P2 | Invariants comptables et traçabilité |
| 08 | [ledger/ledger](https://github.com/ledger/ledger) | Finances personnelles | Métadonnées GitHub | P3 | Écritures en partie double |
| 09 | [beancount/fava](https://github.com/beancount/fava) | Finances personnelles | Métadonnées GitHub | P3 | Navigation dans des résultats comptables |
| 10 | [moneymanagerex/moneymanagerex](https://github.com/moneymanagerex/moneymanagerex) | Finances personnelles | Métadonnées GitHub | P3 | Saisie et regroupement des dépenses |
| 11 | [dcajasn/Riskfolio-Lib](https://github.com/dcajasn/Riskfolio-Lib) | Modélisation financière | DeepWiki détaillé | P2 | Mesures de risque de perte et optimisation robuste |
| 12 | [robertmartin8/PyPortfolioOpt](https://github.com/robertmartin8/PyPortfolioOpt) | Modélisation financière | DeepWiki détaillé | P2 | Covariances, hypothèses de rendement et contraintes |
| 13 | [cvxgrp/cvxportfolio](https://github.com/cvxgrp/cvxportfolio) | Modélisation financière | README original | P3 | Contraintes et coûts explicites en optimisation |
| 14 | [polakowo/vectorbt](https://github.com/polakowo/vectorbt) | Modélisation financière | DeepWiki aperçu | P3 | Comparaison vectorisée de scénarios |
| 15 | [mementum/backtrader](https://github.com/mementum/backtrader) | Modélisation financière | DeepWiki aperçu; ancien dépôt | Exclu | Trading et ordres, hors cible |
| 16 | [quantopian/zipline](https://github.com/quantopian/zipline) | Modélisation financière | DeepWiki aperçu; ancien dépôt | Exclu | Backtest transactionnel, hors cible |
| 17 | [quantopian/empyrical](https://github.com/quantopian/empyrical) | Modélisation financière | DeepWiki détaillé | P2 | Drawdown, risque baissier et rapports |
| 18 | [quantopian/pyfolio](https://github.com/quantopian/pyfolio) | Modélisation financière | Métadonnées GitHub; ancien dépôt | P3 | Diagnostics de performance historiques |
| 19 | [bashtage/arch](https://github.com/bashtage/arch) | Modélisation financière | README et documentation | P2 | Volatilité variable, bootstrap, diagnostics |
| 20 | [statsmodels/statsmodels](https://github.com/statsmodels/statsmodels) | Modélisation financière | DeepWiki détaillé | P2 | Séries temporelles, validation et estimation |
| 21 | [OpenBB-finance/OpenBB](https://github.com/OpenBB-finance/OpenBB) | Données | DeepWiki aperçu | P3 | Séparation des fournisseurs, métadonnées de provenance |
| 22 | [ranaroussi/yfinance](https://github.com/ranaroussi/yfinance) | Données | DeepWiki aperçu | P3 | Contrôle de fraîcheur et réparation de séries |
| 23 | [pydata/pandas-datareader](https://github.com/pydata/pandas-datareader) | Données | DeepWiki aperçu | P3 | Chargement traçable de séries économiques |
| 24 | [econ-ark/HARK](https://github.com/econ-ark/HARK) | Économie et règles | README et documentation scientifique | P2 | Chocs de revenu et décisions de consommation |
| 25 | [PolicyEngine/policyengine-core](https://github.com/PolicyEngine/policyengine-core) | Économie et règles | README original | P2 | Modèle de règles nationales versionnées |
| 26 | [PolicyEngine/policyengine-us](https://github.com/PolicyEngine/policyengine-us) | Économie et règles | Métadonnées GitHub | P3 | Micro-simulation sociofiscale américaine |
| 27 | [PolicyEngine/policyengine-uk](https://github.com/PolicyEngine/policyengine-uk) | Économie et règles | Métadonnées GitHub | P3 | Micro-simulation sociofiscale britannique |
| 28 | [PSLmodels/Tax-Calculator](https://github.com/PSLmodels/Tax-Calculator) | Économie et règles | README original | P3 | Paramètres fiscaux datés, juridiction US |
| 29 | [PSLmodels/OG-Core](https://github.com/PSLmodels/OG-Core) | Économie et règles | Métadonnées GitHub | Exclu | Équilibre intergénérationnel trop éloigné du besoin |
| 30 | [openfisca/openfisca-france](https://github.com/openfisca/openfisca-france) | Économie et règles | README officiel | P2 | Règles françaises explicites et datées |
| 31 | [openfisca/openfisca-core](https://github.com/openfisca/openfisca-core) | Économie et règles | Métadonnées GitHub | P2 | Moteur générique de variables et de règles |
| 32 | [gristlabs/grist-core](https://github.com/gristlabs/grist-core) | UX et outils | DeepWiki aperçu | P3 | Validation, annulation et séparation saisie/vue |
| 33 | [finos/perspective](https://github.com/finos/perspective) | UX et outils | DeepWiki aperçu | P3 | Filtres et exploration interactive |
| 34 | [marimo-team/marimo](https://github.com/marimo-team/marimo) | UX et outils | DeepWiki aperçu | P3 | Dépendances et recalcul transparent des résultats |
| 35 | [streamlit/streamlit](https://github.com/streamlit/streamlit) | UX et outils | DeepWiki aperçu | P1 | Contrôles de saisie, état et navigation multipage |
| 36 | [plotly/plotly.py](https://github.com/plotly/plotly.py) | UX et outils | Métadonnées GitHub | P2 | Graphiques avec comparaisons et explications |

La liste inclut volontairement des projets **écartés** : l'objectif est d'exercer un filtre, non d'accumuler des fonctionnalités. La couverture est inégale et les 36 dépôts n'ont pas reçu un audit du code complet.

## 3. Études ciblées et enseignements vérifiables

| Source examinée | Constat issu de la source | Transposition envisagée — proposition, pas fonctionnalité actuelle |
|---|---|---|
| [Actual — échéances et budgets](https://deepwiki.com/actualbudget/actual/5.5-schedules-and-recurring-transactions) | Échéances uniques ou périodiques, dates attendues, suivi du statut; modèles par montant, périodicité ou cible | Adopter un calendrier explicite des flux plutôt qu'une moyenne masquant les mois déficitaires |
| [Firefly III — objectifs](https://deepwiki.com/firefly-iii/firefly-iii/4.4-piggy-banks-and-savings-goals) | Les cagnottes sont virtuelles, liées à des comptes réels, avec règles de capacité | Conserver la même somme d'argent dans le patrimoine tout en affectant des fractions non redondantes aux objectifs |
| [Wealthfolio — FIRE et risque](https://deepwiki.com/afadil/wealthfolio/5.7-fire-planner-and-goals) | Retraite, retraits, chocs d'inflation, analyse de sensibilité, aléa conjoint rendement-inflation selon hypothèses de ce projet | Séparer la phase de décumulation; tester un krach au début de la retraite et des chocs macroéconomiques cohérents |
| [Wealthfolio — diagnostics](https://deepwiki.com/afadil/wealthfolio/2.7-health-center-and-portfolio-diagnostics) | Contrôles de qualité des données et avertissements de gravité variable | Afficher alertes sur hypothèses incompatibles et données obsolètes, sans prétendre valider les finances de l'utilisateur |
| [Maybe — réconciliation](https://deepwiki.com/maybe-finance/maybe/6.3-valuations-and-balance-reconciliation) | Modification du solde à une date donnée avec prévisualisation de l'effet sur l'historique | S'inspirer des confirmations et des comparaisons avant/après; ne pas importer le système de transactions |
| [PyPortfolioOpt — risque](https://deepwiki.com/robertmartin8/PyPortfolioOpt/2.2-risk-models) | Estimation de matrices de covariance et méthodes de réduction d'instabilité | Toute option multiactifs exige des hypothèses documentées et tests de sensibilité; ne pas optimiser sur de faux paramètres |
| [Riskfolio-Lib — risque baissier](https://deepwiki.com/dcajasn/Riskfolio-Lib) | Mesures de risque variées, notamment perte extrême et drawdown | Comparer quantiles et perte maximale, sans confondre risque boursier avec sécurité budgétaire du ménage |
| [Empyrical — métriques](https://deepwiki.com/quantopian/empyrical/2.2-risk-metrics) | Métriques de perte maximale, volatilité et performance | Ajouter des indicateurs expliqués et bien définis, pas des ratios de trading incompréhensibles |
| [arch — incertitudes](https://bashtage.github.io/arch/) | ARCH/GARCH, bootstrap et tests économétriques | Modèle candidat si des données calibrables sont disponibles; éviter des paramètres non fondés |
| [HARK — choix des ménages](https://docs.econ-ark.org/docs/overview/index.html) | Modèles consommation-épargne, hétérogénéité et chocs de revenu | Mieux représenter les contraintes de liquidité et les chocs de revenu sans promettre de comportement optimal |
| [OpenFisca — règles datées](https://github.com/openfisca/openfisca-france) | Moteur sociofiscal et règles françaises maintenues | Lier chaque règle future à juridiction, période d'application et source; intégration éventuelle distincte |
| [PolicyEngine — architecture des règles](https://github.com/PolicyEngine/policyengine-core) | Paramètres, variables et simulations de réformes organisés par juridiction | Inspirer une architecture des règles mais ne pas appliquer un modèle US/UK au calcul français ou vietnamien |
| [Streamlit — conception](https://deepwiki.com/streamlit/streamlit/6-ui-elements-and-rendering) | Gestion d'état, éléments d'interface et navigation | Réduire les saisies initiales, fiabiliser les états obsolètes et les messages de recalcul |
| [Perspective — exploration](https://deepwiki.com/finos/perspective/) | Filtres, agrégations, pivots et tableaux explorables | Préférer quelques interactions utiles au lieu d'un tableau de bord surchargé |

**Attention aux transferts de méthodes :**
- Une **prévision de volatilité boursière** ne fournit pas une probabilité personnelle de chômage.
- Une **loi fiscale américaine ou britannique** ne décrit pas les règles françaises ou vietnamiennes.
- Une corrélation rendement-inflation utilisée dans un autre simulateur ne doit pas devenir une « vérité » ; il faut l'exposer comme **hypothèse testable**.
- Des outils de suivi d'actifs réels ne signifient pas que Financial Adviser doit demander une connexion bancaire ou conserver des données personnelles sur un serveur.

## 4. État de Financial Adviser servant de référence

En l'état du dépôt examiné, le calcul fonctionne **mensuellement**, avec revenus et dépenses courants, investissements, trésorerie, dette amortissable, événements saisis et modifications de budget liées aux enfants, adultes et autres proches. Les résultats distinguent patrimoine nominal/réel et scénarios stress, objectif inverse, simulation Monte Carlo simplifiée et références statistiques.

**Limites déjà identifiées :**
1. Le Monte Carlo varie les **rendements d'investissement** ; revenus, dépenses, inflation et calendrier restent déterministes. La « fréquence de trésorerie négative » est alors généralement **0 % ou 100 %**, pas une probabilité réaliste de crise de liquidité.
2. Une trésorerie négative signifie **déficit non financé** ; le modèle ne vend pas automatiquement les placements et ne simule ni prêt de secours ni frais de découvert.
3. Les dépenses de référence peuvent masquer une **saisonnalité** (assurances annuelles, frais de rentrée, taxes ou événements récurrents) ; les saisies d'événements ponctuels ne forment pas encore un gestionnaire d'échéances générique.
4. La dette n'ajoute pas automatiquement de bien immobilier à l'actif. La décomposition patrimoine total / liquidités / actifs illiquides reste partielle.
5. Le calcul des pensions et des dépenses familiales repose sur des **hypothèses** ; les règles sociofiscales FR/VN détaillées ne sont pas intégrées.

Ces constats viennent des conventions et du moteur actuellement documentés ; ils ne sont pas des défauts que l'on doit masquer, mais des points de décision mesurables.

## 5. Recommandations hiérarchisées

### P0 — solidité avant richesse fonctionnelle

1. **Contrats comptables explicites** : assurer à chaque mois l'égalité actifs − passifs = patrimoine net ; contrôler que tout transfert interne a un effet net nul avant rendement ; afficher les déficits de trésorerie sans imaginer leur financement.
2. **Convention de mesure non ambiguë** : distinguer flux, stocks, nominal, réel, date des versements et frais éventuels ; l'objectif nominal ne doit jamais être présenté comme un objectif en pouvoir d'achat.
3. **Diagnostic de scénario** : alertes pour prélèvements supérieurs au surplus, dépenses comptées deux fois, coûts familiaux incohérents, horizon inférieur au soutien, résultats obsolètes après saisie.
4. **Vérification numérique** : cas limites zéro rendement, zéro dette, taux nul, échéance finale, événement hors horizon, millions de valeurs VND, inflation élevée, revenus qui s'arrêtent.

### P1 — fonctionnalités à forte valeur d'usage

5. **Échéances et saisonnalité** : montant, début, périodicité (mensuel, trimestriel, annuel), éventuelle fin ; calendrier des sorties, graphique de trésorerie et mois de tension. Pas besoin de connexion bancaire.
6. **Objectifs multiples non redondants** : associer des enveloppes virtuelles à un capital réel, vérifier que leur somme n'excède pas le capital affectable et qu'un apport interne ne crée pas d'argent.
7. **Décumulation / retraite** : retraits périodiques, séquence défavorable de rendements, réserve de sécurité et règles d'épuisement d'actifs **définies par l'utilisateur** ; ne pas prétendre calculer ses droits à pension.
8. **Stress et Monte Carlo séparés** : scénario central déterministe, tests de chocs explicites, puis simulations aléatoires avec paramètres identifiés ; ne jamais appeler « probabilité de sécurité » un simple pourcentage de simulations mal calibrées.
9. **Explications dans les résultats** : accompagnement « pourquoi ce résultat ? », flux majeurs, paramètres dominants et limites ; une comparaison ne doit pas attribuer causalement un effet à plusieurs paramètres modifiés en même temps.

### P2 — approfondissement soumis à validation

10. **Simulations macro-financières cohérentes** : proposer des états explicites (inflation, croissance, crise) avant toute modélisation de corrélations ; calibrer et tester les dépendances si données pertinentes disponibles.
11. **Bilan élargi** : comptes, immobilier, autres actifs, dettes associées, différences liquide/illiquide, éventuelle revalorisation ; ne pas additionner automatiquement la valeur d'un bien absent du scénario.
12. **Références nationales contrôlées** : France (Insee, Banque de France, DREES, OpenFisca à titre d'étude de faisabilité), Vietnam (NSO et sources officielles adaptées). Pour chaque donnée : source, période observée, unité, couverture, date d'accès. Les calculs réglementaires exigent un versionnement propre.
13. **Mesures de risque robustes** : baisse maximale, quantiles de patrimoine, probabilité de franchir des seuils sous un modèle *précisément défini* ; éventuellement étude du risque conditionnel de perte, sans le substituer aux contraintes de budget.

### P3 — utile pour la recherche, non prioritaire pour le produit

Optimisation d'un portefeuille multi-actifs, backtesting d'ordres, synchronisation bancaire, trading en direct, modèles d'équilibre général et apprentissage automatique financier. Leur complexité, leurs données et leurs risques dépassent aujourd'hui le périmètre d'un outil pédagogique de projection des finances d'un ménage.

## 6. Grille de décision pour chaque prochaine idée

Avant d'implémenter une fonctionnalité, répondre par écrit :
1. **Quel besoin utilisateur** et **quelle décision** l'indicateur aidera-t-il réellement ?
2. Quelle grandeur est modélisée ? **Unité, repère temporel, stock/flux, nominal/réel, devise** ?
3. D'où viennent les paramètres ? **Valeurs fictives**, **saisie**, **observation datée**, **règle officielle**, ou **calibration** ?
4. Quelles dépendances et quels mécanismes de financement sont **absents** ?
5. Quels **cas limites**, **invariants** et **scénarios contradictoires** vérifier ?
6. Quel coût UX mobile, temps de calcul, disponibilité des données, dette technique et impact sur la confidentialité ?
7. La licence et les droits d'auteur permettent-ils la réutilisation souhaitée ? **L'inspiration conceptuelle ne donne aucun droit automatique de copier du code**.

**Critère d'adoption :** un indicateur n'entre dans l'application que si sa définition et ses limites peuvent être expliquées naturellement aux utilisateurs en **français, anglais et vietnamien**.

## 7. Liste courte des références à revisiter en premier

1. [Wealthfolio — FIRE Planner](https://deepwiki.com/afadil/wealthfolio/5.7-fire-planner-and-goals) : retraits, inflation, séquence de rendement et objectifs concurrents.
2. [Actual Budget — recurring schedules](https://deepwiki.com/actualbudget/actual/5.5-schedules-and-recurring-transactions) : périodicité, dates et tension de trésorerie.
3. [Firefly III — savings goals](https://deepwiki.com/firefly-iii/firefly-iii/4.4-piggy-banks-and-savings-goals) : enveloppes virtuelles sans double comptage.
4. [Wealthfolio — Health Center](https://deepwiki.com/afadil/wealthfolio/2.7-health-center-and-portfolio-diagnostics) : erreurs compréhensibles et diagnostic.
5. [OpenFisca France](https://github.com/openfisca/openfisca-france) et [PolicyEngine Core](https://github.com/PolicyEngine/policyengine-core) : penser correctement les règles datées, **sans** intégrer de calcul fiscal non vérifié.
6. [HARK](https://docs.econ-ark.org/docs/overview/index.html) : questionner les hypothèses comportementales de consommation et d'épargne.

## 8. Périmètre et statut des travaux

**Terminé dans cette revue :** repérage et classement de 36 dépôts, approfondissement sélectif de 14 références, inventaire des transferts pertinents et des refus, priorisation pour Financial Adviser. **Non effectué :** audit complet de chacun des 36 codes sources, reproduction des résultats quantitatifs des projets tiers, évaluation de leurs performances, vérification de chaque licence pour une intégration précise, test utilisateur externe et modification du moteur de Financial Adviser.

**Décision :** conserver ce travail dans la **documentation technique du dépôt**, et non dans la page publique « Guide et modèles ». Celle-ci doit continuer à parler d'usage, de méthodes et de limites, sans lister le code des applications de référence.
