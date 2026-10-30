# Premier bilan patrimonial explicite — Financial Adviser v0.21.0

**30 octobre 2026.** Extension du bilan aux biens immobiliers **déclarés** et aux autres actifs difficilement liquides, en conservant les conventions de flux mensuels, l'absence de financement implicite et la rétrocompatibilité des scénarios.

## Objectif

Jusqu'à la v0.20, le patrimoine net projeté additionnait trésorerie et placements, puis retranchait la dette. Cette convention est exacte pour les composantes **modélisées**, mais elle peut sous-estimer le patrimoine global d'un propriétaire qui renseigne une dette immobilière sans la valeur de son logement. Inversement, déduire automatiquement la valeur d'un bien d'un montant emprunté créerait artificiellement des actifs.

La v0.21 permet de renseigner explicitement :
- `initial_property_value` : valeur nominale actuelle **déjà possédée** de l'immobilier du ménage ;
- `initial_other_assets` : valeur nominale actuelle des autres actifs non liquides, supposée constante dans ce premier modèle ;
- `property_growth_pct` : taux annuel effectif **hypothétique** de variation de valeur immobilière (positif ou négatif).

Ces montants ne sont **pas** de l'argent disponible à dépenser. L'application ne simule ni achat immobilier, ni loyers, ni frais, ni taxes, ni vente, ni emprunt supplémentaire pour constituer ces actifs. Elle ne suppose **pas** que la dette restante est intégralement adossée à l'immobilier déclaré.

## Grandeurs et calculs

Au mois initial `m=0`, la valeur de l'immobilier est `H_0`, celle des autres actifs non liquides est `O_0`. Le nombre `m` désigne les mois écoulés.

La valeur immobilière nominale suit l'hypothèse composée :

$$
H_m = H_0\left(1+\frac{g_H}{100}\right)^{m/12}.
$$

Les autres actifs non liquides restent à `O_m=O_0` en valeur nominale dans cette version.

Avec `C_m` la trésorerie **signée**, `A_m` les placements et `D_m` le capital restant dû :

$$
N_m = C_m + A_m + H_m + O_m - D_m.
$$

L'indicateur de somme des composantes d'actif `G_m=C_m+A_m+H_m+O_m` est présenté **avant dette**. Si la trésorerie devient négative, elle reste signée : l'indicateur `G_m` ne doit alors **pas** être interprété comme une mesure comptable réglementaire des seuls actifs positifs.

La version en pouvoir d'achat initial, sous l'hypothèse d'inflation annuelle `\pi`, demeure :

$$
N_m^{\mathrm{réel}} = \frac{N_m}{(1+\pi/100)^{m/12}}.
$$

La composante immobilière est ajoutée aux **trajectoires nominales** de Monte Carlo avec une évolution déterministe (conditionnelle à `g_H`). L'aléa de marché porte toujours sur les placements ; aucune volatilité spécifique, corrélation ou aléa de prix immobilier n'est introduit. Le montant de l'immobilier reste disponible dans les résultats, mais ne change **jamais** la trésorerie mensuelle dans cette version.

## Exemple chiffré

Ménage fictif : 12 000 € de trésorerie, 8 000 € de placements, logement évalué explicitement à 160 000 €, autres biens à 5 000 €, et dette restante de 100 000 €.

À la date initiale, le patrimoine net **modélisé** vaut :

`12 000 + 8 000 + 160 000 + 5 000 − 100 000 = 85 000 €`.

Sans déclaration immobilière, le patrimoine affiché aurait été de `−80 000 €`, ce qui ne constitue **pas** une erreur du calcul précédent : il manquait un actif dans les hypothèses. Si la valeur du logement augmente hypothétiquement de 3 % sur l'année, l'augmentation est **une variation de valorisation**, pas un encaissement de 4 800 € utilisable pour payer une facture.

## Interface

Dans les **paramètres avancés**, le panneau « Biens et patrimoine non liquide » propose la valeur immobilière, les autres actifs et le taux annuel choisi. Les valeurs sont à **zéro** par défaut ; aucune hypothèse de propriété n'est imposée.

Quand au moins un bien est déclaré, le panneau de résultats présente un détail : trésorerie, placements, valeur immobilière, autres actifs, dette et patrimoine net. Les deux nouvelles composantes peuvent être sélectionnées dans les courbes de patrimoine. Les comparaisons personnalisées permettent de les modifier indépendamment.

Les trois langues **FR/EN/VI** distinguent explicitement la valeur patrimoniale et la trésorerie.

## Compatibilité et validation

Le schéma JSON de scénario reste `schema_version=1`. Les fichiers antérieurs dépourvus des nouvelles clés sont chargés avec `0` pour chacune ; ils doivent produire les mêmes résultats que précédemment. Les nouvelles clés sont sauvegardées à l'export. Des valeurs négatives de biens, des taux extrêmes hors des limites du scénario et les montants non finis sont refusés.

Contrôles ajoutés :
1. Identité `cash + investments + property_value + other_assets - loan_balance = net_worth`.
2. Absence de création de logement par simple présence d'une dette.
3. Absence d'effet d'une revalorisation immobilière sur la trésorerie ou les placements.
4. Cohérence Monte Carlo à volatilité financière nulle.
5. Import rétrocompatible et rejet des hypothèses non valides.
6. Comparaison personnalisée et libellés graphiques FR/EN/VI.
7. Affichage du scénario sauvegardé dans l'interface.

**Les tests présents dans le dépôt ne sont pas une preuve d'exécution réussie** : attendre un CI vert et la vérification navigateur avant d'annoncer la stabilité publique de cette version.

## Ce qui est volontairement exclu

- Achat, vente, location, plus-value nette, frais de transaction, impôts, assurance, entretien et amortissement comptable des biens.
- Financement immobilier avec apport, capital débloqué, échéancier spécifique par prêt et refinancement.
- Plusieurs propriétés avec revenus, dépenses, hypothèses de marché et devise distinctes.
- Valorisation indépendante et évolutive des autres actifs.
- Liquidation d'une propriété ou de placements en cas de trésorerie négative.
- Probabilité de défaut immobilier, indice régional calibré ou répartition aléatoire du prix de marché.

**Prochain incrément à étudier :** distinguer les propriétés **déjà possédées** de tout futur projet d'achat, avec des flux d'apport, coûts, financement et dates réalistes, avant d'envisager une valorisation plus complexe. Un tel modèle serait une fonctionnalité distincte et exigerait ses propres tests.
