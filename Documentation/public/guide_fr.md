# Guide public — Financial Adviser

Cette présentation détaille les méthodes, les hypothèses, les exemples de lecture et les limites du simulateur. Elle ne constitue pas un conseil financier personnel.

## 1. Objectifs et périmètre

**Financial Adviser** est un outil pédagogique de projection du budget et du patrimoine d'un ménage. Il permet de saisir des revenus, des dépenses, une trésorerie initiale, des investissements, un emprunt éventuel et un objectif patrimonial, puis d'observer leur évolution sur plusieurs années.

Vous pouvez explorer des hypothèses différentes, intégrer des événements de vie et comparer des résultats. Il ne s'agit ni d'un suivi bancaire en temps réel, ni d'une prévision individuelle certaine, ni d'un calcul fiscal officiel.

Les montants sont exprimés dans **une seule devise par scénario**. Choisir la France ou le Vietnam ne convertit pas automatiquement les sommes.

### À quoi sert une projection ?

L'outil répond à des questions conditionnelles : « Si je conserve ce niveau de revenus, ces dépenses et ce rythme d'épargne, que devient mon patrimoine dans dix ans ? », « Que se passe-t-il si je dois aider un proche ? », « Mon objectif est-il atteint sans épuiser la réserve disponible ? ». Il ne détermine pas le **meilleur** placement et ne décide pas à votre place.

**Avant de commencer**, réunissez des ordres de grandeur cohérents : revenu **net mensuel du ménage**, dépenses ordinaires **hors remboursement de l'emprunt saisi séparément**, trésorerie disponible, montant déjà investi et capital restant dû. Une estimation prudente vaut mieux qu'un chiffre précis mais non représentatif. Vous pouvez utiliser exclusivement des données fictives.

**Exemple de lecture :** deux ménages peuvent avoir le même patrimoine net aujourd'hui, mais des situations de liquidité très différentes. Un capital investi ne remplace pas automatiquement l'argent nécessaire pour payer une dépense imprévue. C'est pourquoi le guide distingue toujours **patrimoine**, **trésorerie** et **flux mensuels**.

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

### Comprendre l'ordre des opérations

Au début de chaque mois projeté, les revenus s'ajoutent à la trésorerie ; les dépenses, échéances de crédit et coûts d'événements en sont retranchés. Les entrées ponctuelles l'augmentent. Le virement vers les investissements est ensuite retiré de la trésorerie et ajouté aux placements. Enfin, les deux soldes reçoivent leur rendement mensuel supposé.

Pour un virement mensuel $T$ et des rendements mensuels $r_C$ et $r_A$, les soldes évoluent selon $C_m=(C_{m-1}+F_m-T)(1+r_C)$ et $A_m=(A_{m-1}+T)(1+r_A)$. Un virement de 400 € ne crée donc **pas** 400 € de richesse : il modifie la répartition des avoirs.

**Exemple purement fictif**, sans rendement ni événement : 3 000 € de revenu, 2 000 € de dépenses et 300 € de mensualité d'emprunt donnent 700 € de flux disponible avant virement. Un transfert de 400 € vers les placements laisse 300 € supplémentaires en trésorerie et 400 € supplémentaires en placements ; le remboursement du crédit réduit également la dette, selon la part consacrée au capital.

Les revenus et dépenses de base évoluent selon les taux annuels de croissance choisis. Le taux annuel de rendement et l'inflation sont convertis en équivalents mensuels ; **le taux nominal du prêt**, lui, est divisé par douze pour calculer les intérêts mensuels. Le prêt suit un échéancier à mensualités constantes tant qu'il reste dû.

### Nominal, réel et objectif

Le patrimoine **nominal** est un montant en monnaie courante. Le patrimoine **réel** le ramène au pouvoir d'achat de l'année de départ. Par exemple, avec 2 % d'inflation hypothétique par an, 100 000 € dans dix ans représentent environ 82 035 € de pouvoir d'achat initial : ce n'est pas une prévision d'inflation.

L'objectif saisi est un **objectif nominal**. Sa comparaison avec le patrimoine final ne signifie pas nécessairement que la trésorerie demeure positive à chaque date. Il faut vérifier ces deux dimensions séparément.

### Calcul inverse : chercher comment atteindre une cible

Dans l'onglet consacré à l'objectif, trois **leviers indépendants** peuvent être estimés : **revenu net mensuel supplémentaire** dès le départ, **réduction des dépenses mensuelles de référence** ou **apport externe de trésorerie initiale**. Le calcul cherche, pour chaque levier pris isolément, un patrimoine final au moins égal à la cible **et une trésorerie non négative à tous les mois**. Il ne combine pas automatiquement les trois solutions.

Une réduction de dépenses ne peut pas supprimer artificiellement les charges familiales que vous avez déjà déclarées comme comprises dans le budget de référence. Un apport initial est un apport **extérieur au patrimoine existant**, non un virement entre vos propres comptes. Un levier déclaré impossible signifie seulement qu'aucune solution admissible n'a été trouvée **dans les hypothèses et contraintes du scénario**, pas que l'objectif serait impossible dans toute situation réelle.

## 3. Sources et fiabilité des informations

L'application distingue **données historiques observées**, **hypothèses de projection** et **règles juridiques**. Une statistique publique ne devient jamais automatiquement votre revenu, votre budget ou votre rendement futur.

Les références privilégiées incluent notamment l'[Insee](https://www.insee.fr/fr/information/8184146) et la [Banque de France](https://www.banque-france.fr/fr), en France, ainsi que la [National Statistics Office du Vietnam](https://www.nso.gov.vn/en/) et les sources réglementaires officielles concernées.

La page « Références statistiques » indique les dates, périmètres et sources des observations disponibles. Les situations fiscales françaises ou vietnamiennes ne sont **pas** calculées automatiquement.

### Comment utiliser les statistiques

Pour chaque référence, vérifiez **l'organisme**, **la date de publication**, **l'année ou période observée**, **la population couverte**, **l'unité** et **la définition exacte de l'indicateur**. Une médiane de revenu individuel n'est pas le revenu net d'un ménage ; un indice général des prix ne décrit pas nécessairement votre panier de consommation.

**France et Vietnam** disposent de sources statistiques et de systèmes sociaux distincts. Un chiffre national n'est pas transférable tel quel entre les deux pays, ni directement à une personne. Les montants que vous saisissez priment sur les valeurs d'exemple ; les références publiques servent à contextualiser les hypothèses, pas à leur donner une garantie.

Une hypothèse de rendement, de pension ou de croissance des salaires doit rester identifiée comme **choix du scénario**, même lorsqu'elle ressemble à un chiffre historique. Consultez la rubrique « Sources et règles » pour distinguer données descriptives et règles qui ne sont pas simulées.

## 4. Fonctionnement général

Le parcours repose sur quatre étapes lisibles : **saisir un scénario**, **ajuster ses hypothèses**, **lancer une projection**, puis **analyser les résultats**.

Les graphiques permettent de suivre le patrimoine net, la trésorerie, les investissements et la dette. Des indicateurs signalent notamment un déficit de trésorerie ou l'atteinte d'un objectif. Plusieurs hypothèses peuvent être comparées sans modifier automatiquement le scénario de référence.

Les données d'un scénario peuvent être importées ou exportées volontairement au format JSON. La comparaison porte sur les résultats financiers, et non sur des transactions bancaires récupérées à votre insu.

### Parcours conseillé

1. **Définissez votre situation actuelle** : revenu mensuel net après prélèvements, dépenses usuelles, réserves, placements, éventuel prêt et horizon de projection.
2. **Vérifiez le budget initial** : les mensualités du prêt et les sommes transférées vers les placements ne doivent pas figurer une seconde fois dans les dépenses usuelles.
3. **Renseignez les changements connus** : composition du foyer, aide à des proches, retraite hypothétique, événements datés et montants supplémentaires.
4. **Examinez les paramètres avancés** : croissance des revenus et dépenses, inflation, rendements et volatilité ; modifiez les valeurs illustratives si elles ne vous conviennent pas.
5. **Lancez la projection**, puis commencez par la trésorerie minimale, la trajectoire des dettes et le patrimoine en pouvoir d'achat initial, avant de regarder l'objectif.
6. **Changez une seule hypothèse à la fois** pour comprendre son influence, puis comparez éventuellement des situations de stress.

### À quoi correspondent les résultats ?

Le **patrimoine net** additionne trésorerie et placements puis retranche le capital dû. La **réserve de trésorerie** rapporte la trésorerie initiale aux dépenses actuelles et à la mensualité de prêt : c'est un indicateur statique, pas une garantie de sécurité. Le rapport **crédit / revenu net** ne constitue pas un taux d'endettement réglementaire. La variation du patrimoine peut aussi être favorable alors que la trésorerie diminue.

Lorsque vous modifiez des paramètres après un calcul, les résultats affichés peuvent encore correspondre à la **dernière projection lancée**. Relancez-la avant de tirer une conclusion. L'export d'un scénario permet de conserver les hypothèses ; il ne constitue ni un relevé bancaire ni une preuve de résultat futur.

## 5. Positionnement par rapport aux autres outils

Un **outil de budget** décrit surtout les dépenses passées ou en cours ; un **suivi de portefeuille** observe des investissements ; un **simulateur de projection** explore des trajectoires conditionnelles.

Financial Adviser privilégie ce troisième usage, avec des événements de vie et des hypothèses explicites. Il ne prétend pas remplacer les solutions spécialisées de fiscalité, de comptabilité, de retraite ou de conseil réglementé.

La richesse fonctionnelle de produits tiers varie selon les pays et les versions ; aucune équivalence de précision n'est revendiquée.

### Quel usage choisir ?

| Besoin | Utilité principale de cet outil | Ce qu'il ne remplace pas |
|---|---|---|
| Comprendre l'effet d'une hausse de dépenses | Comparaison de projections à hypothèses constantes | Un suivi détaillé de toutes les factures |
| Préparer un déménagement ou une interruption de revenu | Événements datés avec coûts et variations de revenus | Un devis ou un calcul d'indemnisation |
| Étudier l'objectif patrimonial | Trajectoires nominales et contraintes de trésorerie | Un conseil d'investissement personnalisé |
| Anticiper la retraite | Scénario de revenu de retraite **supposé** | Un relevé officiel de droits à pension |
| Explorer une baisse des marchés | Sensibilité et dispersion hypothétique des placements | Une prévision boursière ou une mesure complète du risque |

La comparaison de scénarios éclaire la **sensibilité** des résultats ; elle n'établit pas laquelle des situations surviendra.

## 6. Limites, qualité et confidentialité

Les calculs n'intègrent pas une fiscalité exhaustive, les frais de tous les produits, les prestations sociales, les taux de change ni l'ensemble des actifs immobiliers.

Une **trésorerie négative** signale un besoin de financement non couvert : le simulateur ne suppose pas qu'un découvert ou une vente d'actifs sera accordé. Une trajectoire financière favorable n'est pas une garantie de faisabilité.

L'application ne demande pas de connexion bancaire. Les valeurs saisies sur l'application hébergée sont néanmoins traitées sur son serveur pendant la session. Pour des informations sensibles, utilisez des montants fictifs ou une exécution locale. Les simulations ne constituent pas un conseil personnalisé.

### Questions à se poser devant un résultat

- **Liquidité :** la trésorerie devient-elle négative, même brièvement ? Le modèle ne finance pas automatiquement ce déficit en vendant des placements.
- **Cohérence :** les mensualités, dépenses familiales et événements sont-ils comptés une seule fois ?
- **Pouvoir d'achat :** un objectif élevé en valeur nominale reste-t-il pertinent après inflation ?
- **Risque :** le résultat dépend-il surtout d'un rendement supposé élevé ou d'une croissance de revenu optimiste ?
- **Couverture :** manque-t-il une assurance, un impôt, un bien, un frais ou une charge récurrente significative ?

Les rendements sont appliqués selon des hypothèses simplifiées ; les frais, prélèvements et calendriers exacts de nombreux produits ne sont pas représentés. L'emprunt modélisé n'ajoute **aucun actif immobilier** en contrepartie. Saisir le crédit d'un logement sans en représenter la valeur peut donc sous-estimer le patrimoine global réel.

**Confidentialité :** évitez les noms, montants ou situations identifiants si vous utilisez la version publique avec des informations sensibles. L'absence de connexion bancaire ne signifie pas que les saisies ne transitent pas par un service hébergé.

## 7. Évolutions envisagées

Les pistes d'évolution comprennent des scénarios patrimoniaux plus variés, une représentation plus fine des actifs et dettes, une meilleure prise en compte des incertitudes et des références nationales.

L'ajout éventuel de règles fiscales, de pensions ou de prestations nécessiterait une vérification des textes applicables, de leur date d'effet et des cas particuliers.

**Ces pistes ne sont pas des fonctionnalités disponibles ni des engagements de livraison.**

### Comment comprendre les fonctions absentes ?

Les sujets comme fiscalité individualisée, prestations sociales, biens immobiliers valorisés, investissements de plusieurs catégories, devises multiples et retraite réglementaire nécessitent des hypothèses et données supplémentaires. Leur absence n'est **pas** équivalente à une valeur nulle dans votre situation réelle.

En attendant, vous pouvez représenter certains effets financiers par un **montant ponctuel** ou une **variation de revenu ou de dépense**, à condition de connaître vous-même ces montants et de ne pas les présenter comme une estimation officielle. Une future fonctionnalité ne doit jamais être anticipée comme si elle existait déjà.

## 8. Principes de conception

Les choix mis en avant sont la **transparence des hypothèses**, la séparation entre observation historique et projection future, et la distinction entre saisie en cours et scénario réellement calculé.

La confirmation explicite évite d'appliquer silencieusement certains changements importants. Le modèle ne crée ni événements personnels ni risques médicaux ou sociaux à votre place.

L'objectif est de permettre une lecture critique des résultats, plutôt que de présenter un chiffre final comme une vérité.

### Des hypothèses que vous contrôlez

Le scénario de référence reste explicite : les suggestions ne modifient pas votre situation sans action de votre part. Un exemple peut remplacer des saisies existantes après confirmation ; un événement n'est ajouté que lorsque vous le choisissez. Évitez de confondre **valeur proposée pour illustrer** et **valeur observée**.

Pour analyser un résultat, conservez de préférence une version de départ, puis créez une variante où **un seul paramètre** change : horizon, rendement, dépense, naissance, revenu ou date de retraite. Si plusieurs hypothèses évoluent simultanément, leur effet individuel devient plus difficile à attribuer.

La précision des décimales affichées n'est pas une précision prévisionnelle : le résultat est calculé précisément **pour les hypothèses saisies**, pas pour le monde réel.

## 9. Événements de vie et expérience utilisateur

Un événement peut représenter, par exemple, un déménagement, une interruption de revenus, des dépenses de santé ou un achat important. Il est décrit par sa **date de début**, sa **durée**, un éventuel coût initial et les **variations mensuelles** de revenu ou de dépenses.

Ces événements sont volontaires et modifiables. Ils n'ont pas de probabilité automatique et ne doivent pas être comptabilisés deux fois lorsqu'un coût figure déjà dans les dépenses de base.

Les paramètres courants sont accessibles en priorité ; les hypothèses plus techniques restent consultables dans un panneau distinct.

### Événements ponctuels et récurrents

Une dépense ponctuelle n'agit qu'au mois indiqué : par exemple, un équipement à 2 000 € payé au douzième mois. Une **fiche d'événement de vie** peut combiner un coût initial, une dépense mensuelle et une variation de revenu pendant plusieurs mois.

**Exemple fictif :** un déménagement démarre au mois 7, dure deux mois, coûte 1 500 € au départ et entraîne 200 € de charges supplémentaires par mois. Le scénario représente un coût total direct de 1 900 €, avant tout effet de rendement ou d'inflation. Si le nouveau loyer est déjà intégré aux dépenses de référence, il ne faut pas ajouter ces 200 € une seconde fois.

Une baisse de revenu s'exprime par une **variation négative** ; les dépenses supplémentaires et le coût initial sont saisis positivement. La durée inclut le mois de départ et doit rester dans l'horizon choisi.

Les situations proposées (interruption d'emploi, soins, achat imprévu, garde d'enfant, aide familiale ou déménagement) sont des **exemples fictifs et modifiables**, ajustés à votre budget pour faciliter l'exploration. Elles ne sont ni des statistiques nationales ni des événements automatiquement attendus.

## 10. Facteurs financiers, sociaux et risques

Les résultats peuvent dépendre de nombreux facteurs : évolution des revenus, inflation, rendement des placements, emprunts, soutien familial, santé ou événements professionnels.

L'application distingue une **analyse de sensibilité** (modifier une hypothèse), un **scénario de choc** choisi par l'utilisateur et une **simulation probabiliste simplifiée** appliquée aux rendements. Ces approches ne donnent pas une probabilité personnelle de chômage, maladie ou accident.

Les corrélations économiques, la fiscalité et les situations individuelles réelles ne sont pas couvertes exhaustivement.

### Trois approches distinctes

**Sensibilité :** comparez une hypothèse de rendement central avec une hypothèse plus faible et une plus forte. Une variation de deux points de pourcentage signifie par exemple passer de 5 % à 3 % ou 7 % par an, sans probabilité associée.

**Test de résistance :** appliquez **un choc choisi à la fois** (perte temporaire de revenu, dépense importante, soutien familial…) au scénario de référence. Observez la variation du patrimoine final **et** la trésorerie minimale. Ces chocs ne sont pas cumulés dans la comparaison et ne sont pas intégrés au scénario courant sans action explicite.

**Monte Carlo :** les rendements mensuels des placements varient de façon aléatoire autour d'un rendement moyen, avec la volatilité choisie. Les quantiles **P10, P50 et P90** décrivent la distribution **simulée** du patrimoine nominal à chaque date : par exemple P10 signifie que 10 % des trajectoires calculées sont au-dessous de ce seuil. Ce ne sont ni des bornes garanties ni des prédictions personnelles.

Les rendements simulés sont supposés indépendants et suivent une distribution simplifiée, limitée à une perte mensuelle maximale proche de 99 %. Les revenus, les dépenses, les dettes, la trésorerie rémunérée et l'inflation restent déterministes. **Attention :** la proportion de trajectoires ayant une trésorerie négative peut donc être 0 % ou 100 % ; elle ne mesure pas une probabilité empirique de crise de liquidité.

Ces analyses n'attribuent aucune probabilité personnelle aux accidents, à la maladie, au chômage ou aux changements familiaux.

## 11. Évaluation et validation

La démarche de qualité comprend des vérifications automatisées de calcul, de cohérence des données, de navigation et de présentation dans plusieurs langues.

Ces contrôles ne remplacent pas une évaluation indépendante auprès d'utilisateurs réels, ni une revue officielle par des économistes, fiscalistes ou actuaires. **Une telle validation externe ne doit pas être présumée acquise.**

Les interprétations financières restent donc pédagogiques et limitées aux hypothèses du modèle.

### Ce qui est vérifié — et ce qui ne l'est pas

Des contrôles de cohérence portent notamment sur les valeurs saisies, les échéances, la conservation des transferts internes et la présentation des résultats. Ils réduisent le risque d'erreurs évidentes mais **ne prouvent ni la pertinence de vos hypothèses ni l'exactitude d'une prévision**.

Une évaluation complète exigerait aussi des retours d'utilisateurs, des comparaisons avec des cas réels documentés et une revue indépendante des modèles financiers et des règles nationales. Cette validation externe n'est pas revendiquée.

Pour interpréter une anomalie apparente, commencez par retrouver : la devise, l'année de départ, l'horizon, les charges déjà comprises dans le budget, la date des événements et le dernier scénario effectivement calculé.

## 12. Cycle de vie et budget familial

Les profils d'**enfants**, d'**adultes** et d'**autres personnes à charge** permettent d'explorer des dépenses supplémentaires ou des changements de revenus au fil du temps.

Pour un enfant, le coût peut varier avec l'âge et la durée de soutien choisie. Pour les adultes, un départ à la retraite peut modifier le revenu selon une **pension purement hypothétique**. Pour les autres proches, l'aide régulière et les frais d'accompagnement peuvent être décrits séparément.

Le réglage « déjà inclus dans les dépenses actuelles » est essentiel : il permet de ne considérer que l'évolution d'une charge déjà comprise dans le budget initial. Les montants proposés par défaut sont **illustratifs**, pas des moyennes nationales ou des prévisions individuelles.

L'horizon de simulation peut s'arrêter avant la fin réelle d'une prise en charge : le résultat ne représente alors qu'une **période partielle**.

### Enfants : suivre des postes distincts

Pour chaque enfant, distinguez les **dépenses courantes** et les dépenses de **garde ou d'éducation**, selon cinq tranches d'âge : **0–2 ans, 3–5 ans, 6–11 ans, 12–17 ans, 18–29 ans**. Choisissez l'âge initial, la date de prise en charge et l'âge d'arrêt de soutien (au plus 30 ans). Ces tranches sont des conventions pratiques et non des barèmes officiels.

**Exemple fictif :** un enfant déjà présent représente 350 € par mois **déjà inclus** dans les 2 000 € de dépenses du foyer. Si la tranche suivante est estimée à 450 €, la variation prise en compte est la **différence** de 100 € (avant l'effet du taux de croissance choisi), et non l'ajout de 450 € aux 2 000 €. Pour un enfant attendu plus tard, la dépense commence à la date choisie ; elle ne peut pas avoir été incluse dans le budget actuel.

### Adultes et retraite hypothétique

Vous pouvez répartir jusqu'à **100 % du revenu net du ménage** entre les adultes décrits. Chaque personne a un âge, une part de revenu, un âge de retraite choisi, un taux **hypothétique** de remplacement du salaire par la pension et des dépenses selon quatre tranches : 18–39, 40–59, 60–74 et 75 ans et plus. Une personne déjà retraitée conserve la part de revenu actuel comme pension de départ : elle n'est pas réduite une seconde fois. Après un départ en retraite simulé, la pension est supposée évoluer selon l'inflation, et non selon une réglementation réelle.

### Autres proches et précautions

Une aide à un parent ou autre proche peut combiner soutien financier et frais d'accompagnement, avec début et durée. Si une dépense figure déjà dans le budget actuel, indiquez-le pour ne comptabiliser que **sa variation** ; sa disparition en fin de période peut alors réduire les charges de référence.

Vérifiez que le total déclaré « déjà inclus » reste compatible avec les dépenses de base. L'outil ne déduit ni les droits sociaux, ni les frais médicaux de l'âge, ni une date de décès. Si l'horizon s'arrête avant la fin du soutien, les montants cumulés ne concernent **que la période simulée**. Les suggestions de coûts sont entièrement fictives.

