# Modèles mathématiques et conventions — v0.1.0

**Statut : modèles implémentés ; unités et hypothèses définies pour la reproductibilité.**

## 1. Repères et unités

- Pas de temps : **1 mois** ; `m = 0` état initial ; `m = 1` premier mois projeté.
- Une seule monnaie par simulation (`EUR` ou `VND`) ; aucun taux de change dans le calcul v0.1.
- Tous les montants mensuels sont exprimés dans la devise du scénario, en unités monétaires courantes.
- Les rendements des actifs et l'inflation annuels sont des **taux effectifs** ; le taux du prêt est un **taux nominal annuel** appliqué mensuellement.
- L'année sur le graphique est `start_year + m/12`, utilisée comme abscisse continue, et non comme date civile exacte.

## 2. État financier

Au mois `m`, on définit `C_m` (trésorerie), `A_m` (investissements), `D_m` (principal d'emprunt restant), `N_m` (patrimoine net) :

$$
N_m=C_m+A_m-D_m.
$$

**Important :** renseigner une dette sans actif correspondant réduit le patrimoine, conformément à l'état explicite. Le modèle ne suppose pas automatiquement que la dette a servi à acheter un bien immobilier.

## 3. Conversion des taux

Pour un taux effectif annuel `R` en décimal, le taux mensuel équivalent est :

$$
r=(1+R)^{1/12}-1.
$$

Cette relation assure `(1+r)^12 = 1+R`. Pour l'emprunt, si `i` désigne le taux nominal annuel, on utilise au contraire `r_{prêt}=i/12`.

## 4. Flux et dates

Pour chaque mois `m=1,…,M`, les revenus et dépenses évoluent selon une croissance annuelle effective supposée :

$$
Y_m=Y_0(1+g_Y)^{(m-1)/12},\qquad
E_m=E_0(1+g_E)^{(m-1)/12}.
$$

Les événements ponctuels `O_m` sont additionnés par mois : `O_m > 0` entrée ; `O_m < 0` sortie.

Après calcul de l'échéance de prêt `L_m`, le flux disponible avant épargne est :

$$
F_m=Y_m-E_m-L_m+O_m.
$$

Avec `T` = **virement mensuel entre trésorerie et investissements** :

$$
\begin{aligned}
C_m&=(C_{m-1}+F_m-T)(1+r_C),\\
A_m&=(A_{m-1}+T)(1+r_A).
\end{aligned}
$$

**Convention temporelle** : revenus, dépenses, échéances, événements et transfert d'investissement interviennent **au début** du mois ; intérêts/performance mensuels ensuite. `T` est une opération interne au patrimoine, pas un revenu. Les valeurs sont des montants hypothétiques et il n'existe pas de frais implicites.

**Trésorerie négative** : autorisée comme indicateur de **déficit non financé**, sans limite de crédit ni frais de découvert. Les valeurs négatives ne démontrent pas la faisabilité du plan.

## 5. Emprunt à échéances constantes

Capital dû `D_0`, durée restante `n` mois, taux mensuel nominal `r_L` :

$$
L = \begin{cases} D_0/n, & r_L=0,\\
D_0r_L/[1-(1+r_L)^{-n}], & r_L>0.
\end{cases}
$$

Chaque mois : intérêt `I_m=r_L D_{m-1}`, échéance effective `L_m=min(L,D_{m-1}+I_m)`, et :

$$
D_m=\max(0,D_{m-1}+I_m-L_m).
$$

Si le prêt est remboursé, les échéances deviennent nulles. Le simulateur modélise un prêt déjà en cours ; les assurances, frais de dossier, renégociations et loyers associés ne sont pas inclus. Si l'utilisateur saisit déjà les échéances dans ses dépenses courantes, il doit les enlever pour éviter un double comptage.

## 6. Inflation et pouvoir d'achat

Pour une inflation annuelle effective supposée `π`, le facteur de prix après `m` mois :

$$
Q_m=(1+\pi)^{m/12},\qquad N_m^{réel}=\frac{N_m}{Q_m}.
$$

`N_m^{réel}` est exprimé en **pouvoir d'achat de la date de départ**. L'inflation future est une hypothèse ; la dernière statistique annuelle publiée n'est pas une prévision.

## 7. Simulation Monte Carlo (simplifiée)

Le modèle probabiliste applique uniquement des rendements aléatoires aux investissements. Pour chaque trajectoire `s` et mois `m` :

$$
r_{A,m}^{(s)}=\max\left(-0.99,\ \mu_m+\sigma_m Z_{m,s}\right),\qquad Z_{m,s}\overset{iid}{\sim}\mathcal N(0,1),
$$

avec `μ_m=(1+R_A)^(1/12)−1` et `σ_m=σ_annuel/√12` (**approximation** de volatilité annualisée). `C_m` et `D_m` suivent les mêmes règles déterministes que précédemment ; inflation fixe. Le moteur stocke les patrimoines de toutes les trajectoires et calcule les percentiles empiriques P10/P50/P90 par mois et la fraction des trajectoires dont le patrimoine final atteint l'objectif **nominal**.

Le risque de trésorerie négative est la fraction des trajectoires ayant `C_m < 0` au moins une fois. Comme la trésorerie et ses flux ne sont pas aléatoires dans v0.1, cette fraction vaut typiquement 0 % ou 100 % : **ce n'est pas un modèle de risque de liquidité calibré**.

**Limites probabilistes :** indépendance des rendements mensuels, normale avec borne -99 %, volatilité annualisée approximée, absence d'autocorrélation, de dépendance avec l'inflation, de frais/taxes, de classes multiples et de risque de change. Les intervalles ne sont pas des bornes garanties. La graine aléatoire fixe la reproductibilité.

## 8. Comparaison de scénarios

L'interface calcule trois versions du même `Plan` : rendement d'investissement initial, rendement abaissé et rendement relevé d'un nombre de **points de pourcentage** choisi. Tous les autres flux et paramètres sont conservés. Il s'agit d'une **sensibilité** et non de scénarios ayant des probabilités connues.

## 9. Extensions attendues

États multi-actifs, taxes et contributions par pays, inflation différenciée, taux de change et covariance, soldes multi-comptes, immobilier, retraite, levier, risque de liquidité et calibration historique. Ces extensions ne doivent pas être assimilées aux fonctionnalités v0.1.


## Extension v0.2 : événements et calcul inverse

Voir [09_FACTEURS_DE_VIE_ET_UX.md](09_FACTEURS_DE_VIE_ET_UX.md) pour les conventions détaillées : modification additive des flux mensuels sur un intervalle, dépense ponctuelle au début, et trois solveurs inverses indépendants sous contraintes `V_T >= G` et `cash_m >= 0`. Ces événements sont des hypothèses et non une distribution de risque calibrée.
