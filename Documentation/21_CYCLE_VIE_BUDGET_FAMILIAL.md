# Cycle de vie et dépenses des ménages — Financial Adviser v0.7

**Date de revue : 30 octobre 2026.** Document de conception et de validation mathématique. L'application reste un simulateur pédagogique. **Il ne s'agit pas d'un calcul officiel du coût de l'enfant ni de droits à pension.**

## 1. La question « combien coûte un enfant jusqu'à l'âge adulte ? »

Un enfant peut entraîner des dépenses pendant **toute la durée de prise en charge**, laquelle n'est pas limitée obligatoirement au dix-huitième anniversaire : les études et l'aide familiale peuvent prolonger la période jusqu'à 25 ans ou au-delà, selon la situation. En revanche, **les montants et leur profil par âge ne sont pas universels**. Il faut prendre en compte la composition du ménage, le revenu disponible, les dépenses mutualisées, la région, le mode de garde et les prestations publiques. Une courbe automatiquement croissante serait aussi contestable qu'un coût constant.

- La **DREES (dossier 108, mars 2023)**, sur l'enquête *Budget de famille 2017*, distingue logement, alimentation, habillement, garde, scolarité et loisirs. Dans certaines familles à revenu donné, la consommation totale varie peu avec l'âge de l'enfant, car le budget est limité par les ressources. L'effet des seuils d'âge diffère fortement selon poste de dépense et situation familiale : https://drees.solidarites-sante.gouv.fr/sites/default/files/2023-03/DD108.pdf .
- L'**Insee** utilise pour comparer des niveaux de vie des unités de consommation (1 pour le premier adulte, 0,5 pour les personnes supplémentaires de 14 ans ou plus, 0,3 pour celles de moins de 14 ans). **Il ne s'agit pas d'un taux de dépense que l'on peut appliquer directement au salaire** : https://www.insee.fr/en/metadonnees/definition/c1802 .
- Le **Haut Conseil de la famille**, *Le coût de l'enfant* (rapport de 2015), discute les coûts directs, indirects, le temps des parents, les conventions et l'incertitude empirique. Les valeurs citées proviennent souvent d'enquêtes antérieures (notamment SRCV 2011), donc **ne sont pas des prix actuels** : https://hcfea.gouv.fr/sites/hcfea/files/2025-12/rapport_cout_de_l_enfant_def_0.pdf .
- L'**IRES**, *Les dépenses de la société pour les enfants* (septembre 2026), décompose le coût en achats des ménages, production domestique non rémunérée, transferts et services publics. Sa moyenne macroéconomique de **37 500 €/an pour la société**, enfant de moins de 20 ans, en 2024 **ne correspond ni au budget privé du foyer ni au coût marginal d'un enfant**. Les dépenses des parents sur le marché et les services publics doivent être traités séparément : https://ires.fr/publications/documents-de-travail-de-lires/n02-2026-les-depenses-de-la-societe-pour-les-enfants-une-estimation-du-cout-direct-des-enfants-et-de-son-evolution-de-2010-a-2024/ .
- La **NSO du Vietnam**, *Vietnam Household Living Standards Survey 2024* (publication mars 2026), distingue alimentation, éducation, santé, logement et composition familiale, avec des différences urbaines/rurales et de niveau de revenu. Les moyennes **par habitant** ou **par élève** ne peuvent pas être automatiquement interprétées comme dépenses marginales pour un enfant d'un ménage particulier : https://www.nso.gov.vn/en/data-and-statistics/2026/03/results-of-the-viet-nam-household-living-standards-survey-2024/ .

## 2. Moteur introduit en v0.7

Chaque enfant est représenté par un âge au début de sa prise en charge, un mois de début, un âge de fin de soutien choisi (**18 ans, 25 ans ou jusqu'à 30 ans**, selon le profil), deux séries de dépenses **mensuelles supplémentaires** (vie courante, garde/éducation) par classe d'âge, et un indicateur *déjà inclus dans les dépenses de base*.

**Tranches de modélisation** : 0–2, 3–5, 6–11, 12–17 et 18–29 ans. Ces tranches ne constituent pas des seuils empiriques certifiés : elles structurent simplement les dépenses saisies. L'âge avance une fois par douze mois à partir du début du profil ; la date de naissance précise n'est pas demandée. À l'âge de fin de soutien, les coûts s'arrêtent (la famille peut choisir jusqu'à 30 ans).

Soit `C(age)` la somme des deux postes à l'âge considéré, dans la devise de la simulation. L'évolution des montants nominaux reprend, **à titre d'hypothèse**, le taux général de croissance des dépenses du scénario, `g`, et non une inflation spécifique vérifiée pour chaque poste.

\[
C_t = C(\operatorname{âge}_t)\,(1+g)^{t/12}.
\]

Si les coûts de cet enfant **ne figurent pas** déjà dans les dépenses mensuelles principales, on ajoute `C_t` à partir du mois de prise en charge. S'ils y figurent déjà, on applique seulement une **variation** par rapport à la somme `C_initial` déjà contenue dans le budget :

\[
\Delta D_t^{enfant}=\begin{cases}
C_t - C_{initial}(1+g)^{t/12}, &\text{enfant présent et déjà inclus}\cr
C_t, & \text{enfant non inclus dans le budget initial.}
\end{cases}
\]

Après l'âge de fin de soutien, `C_t=0` ; si l'enfant était inclus dans les dépenses initiales, la part de référence cesse donc d'être comptabilisée. **Le champ 'dépenses principales' reste une estimation de la dépense totale réelle actuelle, et pas un budget fictif indépendant de l'enfant.** Il faut éviter de saisir à nouveau ces frais dans les événements ponctuels.

Pour un enfant **à naître**, sa prise en charge commence à la date choisie, avec un coût nul auparavant. Le réglage « déjà inclus » n'est pas applicable pour une naissance future.

**Exemples de valeurs initiales :** l'interface peut suggérer des montants à partir de ratios illustratifs du budget déjà saisi. Il s'agit **uniquement de chiffres synthétiques**, à remplacer par des dépenses propres au foyer. Aucun montant n'est considéré comme une moyenne, une médiane, un minimum réglementaire ou une prévision. Les fonctions 
`child_example` et `household_adjustments` sont séparées pour que l'estimation illustrative n'entre jamais dans la formule comme vérité statistique.

## 3. Vie des adultes, salaire et retraite

Le modèle actuel n'a qu'un **revenu net mensuel de ménage**. Les profils adultes permettent de répartir **jusqu'à 100 %** de ce revenu entre plusieurs personnes, sans inventer de salaires. Chaque adulte possède : âge actuel, part du revenu net du foyer, âge de départ à la retraite choisi, hypothèse de remplacement net du salaire par la pension, et dépenses additionnelles par classe d'âge (18–39, 40–59, 60–74, 75 ans et plus). Le revenu non affecté à des adultes continue d'évoluer selon les hypothèses générales.

- Avant la retraite, la fraction du revenu de chaque personne suit la croissance salariale choisie.
- **À la transition**, la fraction du salaire est remplacée par une pension **hypothétique**, calculée comme un pourcentage du dernier salaire net extrapolé. Les mois suivants, la pension évolue selon l'hypothèse d'inflation (simplification **non conforme à une loi nationale de retraite**).
- **Si l'adulte est déjà retraité** au départ, sa fraction de revenu actuel est déjà considérée comme une pension ; le pourcentage de remplacement n'est **pas** appliqué une seconde fois.
- Les charges additionnelles par tranche d'âge sont comparées au montant actuel si elles figurent déjà dans les dépenses de base, de manière analogue aux enfants. Le changement lié au départ en retraite est un champ distinct, signé. Les soins médicaux et la dépendance ne sont pas inférés de l'âge.
- L'âge augmente chaque année. La mortalité et la survie du conjoint ne sont **pas** modélisées. Projeter jusqu'à 120 ans ou au-delà ne constitue pas une prédiction de longévité.

L'**OCDE, *Pensions at a Glance 2025*** publie des indicateurs de taux de remplacement selon les régimes, salaires et carrières. Ceux-ci ne peuvent pas servir de pension individuelle prédite, notamment entre France et Vietnam : https://www.oecd.org/en/publications/pensions-at-a-glance-2025_e40274c1-en/full-report/recent-pension-reforms_146d2687.html .

## 4. Fonctions compatibles et exclusions

Les coûts sont intégrés dans les vecteurs mensuels `income`/`expenses` du moteur. Le bilan nominal, réel, le calcul inverse et les scénarios Monte Carlo en bénéficient sans modifier leur API existante. Les résultats ajoutent des postes identifiables `child_expenses`, `adult_expenses`, `retirement_income_change` (valeurs **signées** par rapport au budget initial, pas des coûts bruts cumulés).

**Exclusions explicites :** (1) prestations CAF, barèmes de bourses, subventions vietnamiennes ; (2) impôt sur le revenu et pension réglementaire ; (3) probabilité d'enfants, de mariage, de décès, de maladie ou de chômage ; (4) logement et immobilier dédiés, assurances et taux de change ; (5) économies d'échelle exactes pour fratries ; (6) inflation propre à l'éducation/soins ; (7) coûts d'opportunité du temps parental non rémunéré.

## 5. Tests à maintenir

- Enfant présent, déjà inclus ou non ; coût initial sans double compte.
- Nouveau-né à l'avenir, aucun coût avant l'arrivée ; début et fin exacts.
- Transition de tranche, arrêt à 18 ou 25 ans, plusieurs enfants, taux de croissance des dépenses.
- Adultes actifs et retraités, parts de revenu total ne dépassant pas 100 %, retraite à date choisie, pension existante non remplacée.
- Sérialisation JSON des profils avec anciens fichiers sans champs `children`/`adults` ; projection déterministe, Monte Carlo et solution inverse.
- Interface français, anglais, vietnamien et mobile ; contrôle du nombre de profils ; validation de signe/montants ; pas de réinitialisation après navigation.

**Statut à la publication initiale :** tests du moteur localement vérifiés ; évaluation sur le site hébergé, étude avec familles réelles et audit par économiste/fiscaliste/actuaire **non encore réalisés**. GitHub Actions reste à déclenchement manuel pour respecter la préférence concernant les notifications.

## 6. Contrainte de cohérence dans le calcul inverse

Si des composantes de coût déjà incluses dans la dépense courante ont été attribuées explicitement aux membres du foyer, leur somme définit un **plancher de dépenses déjà engagées** dans le simulateur. L'option « réduction des dépenses » du calcul inverse ne peut plus réduire la dépense mensuelle initiale sous ce montant sans invalider la ventilation définie par l'utilisateur. Cette condition évite une solution mathématiquement séduisante mais incohérente avec le budget familial décrit. Elle **n'affirme pas** que toutes les dépenses familiales sont économiquement incompressibles : elle respecte simplement la convention d'affectation de dépenses courantes choisie dans ce scénario.

Le moteur refuse également une ventilation « déjà incluse » dont la somme dépasse la dépense mensuelle totale saisie, plutôt que de produire des charges négatives artificielles. Les 24 tests locaux ciblés du modèle familial et des textes FR/EN/VI vérifient ce cas, les transitions d'âge et l'import/export des profils ; un résultat GitHub Actions ou un test de l'URL hébergée ne sont pas revendiqués pour la présente candidate.

## 7. Attention à la durée de projection

La durée de projection peut être **plus courte que la durée de soutien d'un enfant**. Dans ce cas, le modèle ne calcule que les coûts sur les mois couverts, et non le coût complet jusqu'à l'âge de fin de soutien. L'interface le signale et invite à allonger l'horizon ; aucun coût « à vie » n'est inféré au-delà de la période choisie.
