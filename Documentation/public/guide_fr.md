# Guide public — Financial Adviser

Cette présentation explique les méthodes, hypothèses et limites du simulateur. Elle ne constitue ni un conseil financier personnel ni une description de son implémentation logicielle.

## 1. Objectifs et périmètre

**Financial Adviser** est un outil pédagogique de projection du budget et du patrimoine d'un ménage. Il permet de saisir des revenus, des dépenses, une trésorerie initiale, des investissements, un emprunt éventuel et un objectif patrimonial, puis d'observer leur évolution sur plusieurs années.

Vous pouvez explorer des hypothèses différentes, intégrer des événements de vie et comparer des résultats. Il ne s'agit ni d'un suivi bancaire en temps réel, ni d'une prévision individuelle certaine, ni d'un calcul fiscal officiel.

Les montants sont exprimés dans **une seule devise par scénario**. Choisir la France ou le Vietnam ne convertit pas automatiquement les sommes.

## 2. Modèles et équations

Le simulateur raisonne par mois. Le patrimoine net nominal correspond aux avoirs diminués de la dette :

$$
N_m = C_m + A_m - D_m
$$

avec $C_m$ la trésorerie, $A_m$ les investissements et $D_m$ le capital restant dû au mois $m$.

Le solde courant avant virement vers les placements résulte des revenus, dépenses, mensualités d'emprunt et flux ponctuels :

$$
F_m = Y_m - E_m - L_m + O_m
$$

Les taux annuels effectifs sont convertis en taux mensuels équivalents :

$$
r_m = (1+R)^{1/12}-1
$$

Le patrimoine réel est exprimé en pouvoir d'achat de la date de départ, pour une inflation annuelle supposée $\pi$ :

$$
N_m^{\mathrm{réel}} = \frac{N_m}{(1+\pi)^{m/12}}
$$

**Conventions importantes :** les entrées et sorties de trésorerie sont prises en compte avant les rendements mensuels ; les virements internes ne sont pas des revenus. Les taux, croissances et flux futurs restent des **hypothèses modifiables**, pas des données prédites.

Les simulations Monte Carlo illustrent une dispersion possible des rendements des placements selon des hypothèses simplifiées. Les quantiles observés ne sont pas des garanties de résultat.

## 3. Sources et fiabilité des informations

L'application distingue **données historiques observées**, **hypothèses de projection** et **règles juridiques**. Une statistique publique ne devient jamais automatiquement votre revenu, votre budget ou votre rendement futur.

Les références privilégiées incluent notamment l'[Insee](https://www.insee.fr/fr/information/8184146) et la [Banque de France](https://www.banque-france.fr/fr), en France, ainsi que la [National Statistics Office du Vietnam](https://www.nso.gov.vn/en/) et les sources réglementaires officielles concernées.

La page « Références statistiques » indique les dates, périmètres et sources des observations disponibles. Les situations fiscales françaises ou vietnamiennes ne sont **pas** calculées automatiquement.

## 4. Fonctionnement général

Le parcours repose sur quatre étapes lisibles : **saisir un scénario**, **ajuster ses hypothèses**, **lancer une projection**, puis **analyser les résultats**.

Les graphiques permettent de suivre le patrimoine net, la trésorerie, les investissements et la dette. Des indicateurs signalent notamment un déficit de trésorerie ou l'atteinte d'un objectif. Plusieurs hypothèses peuvent être comparées sans modifier automatiquement le scénario de référence.

Les données d'un scénario peuvent être importées ou exportées volontairement au format JSON. La comparaison porte sur les résultats financiers, et non sur des transactions bancaires récupérées à votre insu.

## 5. Positionnement par rapport aux autres outils

Un **outil de budget** décrit surtout les dépenses passées ou en cours ; un **suivi de portefeuille** observe des investissements ; un **simulateur de projection** explore des trajectoires conditionnelles.

Financial Adviser privilégie ce troisième usage, avec des événements de vie et des hypothèses explicites. Il ne prétend pas remplacer les solutions spécialisées de fiscalité, de comptabilité, de retraite ou de conseil réglementé.

La richesse fonctionnelle de produits tiers varie selon les pays et les versions ; aucune équivalence de précision n'est revendiquée.

## 6. Limites, qualité et confidentialité

Les calculs n'intègrent pas une fiscalité exhaustive, les frais de tous les produits, les prestations sociales, les taux de change ni l'ensemble des actifs immobiliers.

Une **trésorerie négative** signale un besoin de financement non couvert : le simulateur ne suppose pas qu'un découvert ou une vente d'actifs sera accordé. Une trajectoire financière favorable n'est pas une garantie de faisabilité.

L'application ne demande pas de connexion bancaire. Les valeurs saisies sur l'application hébergée sont néanmoins traitées sur son serveur pendant la session. Pour des informations sensibles, utilisez des montants fictifs ou une exécution locale. Les simulations ne constituent pas un conseil personnalisé.

## 7. Évolutions envisagées

Les pistes d'évolution comprennent des scénarios patrimoniaux plus variés, une représentation plus fine des actifs et dettes, une meilleure prise en compte des incertitudes et des références nationales.

L'ajout éventuel de règles fiscales, de pensions ou de prestations nécessiterait une vérification des textes applicables, de leur date d'effet et des cas particuliers.

**Ces pistes ne sont pas des fonctionnalités disponibles ni des engagements de livraison.**

## 8. Principes de conception

Les choix mis en avant sont la **transparence des hypothèses**, la séparation entre observation historique et projection future, et la distinction entre saisie en cours et scénario réellement calculé.

La confirmation explicite évite d'appliquer silencieusement certains changements importants. Le modèle ne crée ni événements personnels ni risques médicaux ou sociaux à votre place.

L'objectif est de permettre une lecture critique des résultats, plutôt que de présenter un chiffre final comme une vérité.

## 9. Événements de vie et expérience utilisateur

Un événement peut représenter, par exemple, un déménagement, une interruption de revenus, des dépenses de santé ou un achat important. Il est décrit par sa **date de début**, sa **durée**, un éventuel coût initial et les **variations mensuelles** de revenu ou de dépenses.

Ces événements sont volontaires et modifiables. Ils n'ont pas de probabilité automatique et ne doivent pas être comptabilisés deux fois lorsqu'un coût figure déjà dans les dépenses de base.

Les paramètres courants sont accessibles en priorité ; les hypothèses plus techniques restent consultables dans un panneau distinct.

## 10. Facteurs financiers, sociaux et risques

Les résultats peuvent dépendre de nombreux facteurs : évolution des revenus, inflation, rendement des placements, emprunts, soutien familial, santé ou événements professionnels.

L'application distingue une **analyse de sensibilité** (modifier une hypothèse), un **scénario de choc** choisi par l'utilisateur et une **simulation probabiliste simplifiée** appliquée aux rendements. Ces approches ne donnent pas une probabilité personnelle de chômage, maladie ou accident.

Les corrélations économiques, la fiscalité et les situations individuelles réelles ne sont pas couvertes exhaustivement.

## 11. Évaluation et validation

La démarche de qualité comprend des vérifications automatisées de calcul, de cohérence des données, de navigation et de présentation dans plusieurs langues.

Ces contrôles ne remplacent pas une évaluation indépendante auprès d'utilisateurs réels, ni une revue officielle par des économistes, fiscalistes ou actuaires. **Une telle validation externe ne doit pas être présumée acquise.**

Les interprétations financières restent donc pédagogiques et limitées aux hypothèses du modèle.

## 12. Cycle de vie et budget familial

Les profils d'**enfants**, d'**adultes** et d'**autres personnes à charge** permettent d'explorer des dépenses supplémentaires ou des changements de revenus au fil du temps.

Pour un enfant, le coût peut varier avec l'âge et la durée de soutien choisie. Pour les adultes, un départ à la retraite peut modifier le revenu selon une **pension purement hypothétique**. Pour les autres proches, l'aide régulière et les frais d'accompagnement peuvent être décrits séparément.

Le réglage « déjà inclus dans les dépenses actuelles » est essentiel : il permet de ne considérer que l'évolution d'une charge déjà comprise dans le budget initial. Les montants proposés par défaut sont **illustratifs**, pas des moyennes nationales ou des prévisions individuelles.

L'horizon de simulation peut s'arrêter avant la fin réelle d'une prise en charge : le résultat ne représente alors qu'une **période partielle**.
