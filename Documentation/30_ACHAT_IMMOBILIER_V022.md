# Achat immobilier futur — Financial Adviser v0.22.0

**Date : 30 octobre 2026.** Extension pédagogique permettant de simuler **un seul achat immobilier futur**, distinct des biens déjà possédés et du crédit existant au début du scénario.

## 1. Entrées et hypothèses

La personne renseigne explicitement : le **mois d'achat** p (compté à partir de janvier de l'année de départ), le **prix du bien** V strictement positif, l'**apport** a compris entre zéro et V, les **frais d'acquisition** f positifs ou nuls, le **taux annuel nominal** i du nouveau prêt (0 à 100 %) et sa **durée** T (1 à 60 ans). Tous les montants sont dans la devise unique du scénario ; les frais ne sont pas déduits d'un barème légal ou national.

Ce bien futur **ne doit pas être compté dans l'immobilier déjà possédé** au mois initial. L'apport, les frais et les mensualités du nouvel emprunt ne doivent pas non plus être déclarés une seconde fois dans les dépenses courantes ou les flux récurrents.

## 2. Transaction et équité patrimoniale

Le nouveau capital emprunté est L = V − a. Le modèle suppose qu'il finance **directement le vendeur**, sans transiter par la trésorerie du ménage. Pendant le mois d'achat :

- La trésorerie diminue de **a + f** (avant son rendement mensuel).
- L'actif immobilier augmente de **V**, à la date choisie, et non avant.
- La dette totale augmente de **L**.
- Le changement immédiat de patrimoine net lié à la transaction, avant rendement, est **−(a+f) + V − L = −f**.

L'apport est donc une conversion de trésorerie en patrimoine immobilier, et **ne détruit pas du patrimoine** ; les frais sont une perte patrimoniale. Une trésorerie négative reste un **déficit non financé**. Aucun retrait automatique des placements ni nouveau découvert n'est simulé.

## 3. Amortissement du nouveau prêt

Le crédit préexistant et celui lié à l'achat sont deux échéanciers distincts. À la fin du mois p, la nouvelle dette est L mais **la première mensualité intervient au mois p+1**.

Avec r = i/(100×12) et n = 12T, la mensualité théorique est :

- **L/n** pour r = 0 ;
- **Lr / [1 − (1+r)^(−n)]** pour r positif.

Chaque mensualité est limitée au principal restant et aux intérêts du mois, afin de ne pas rembourser davantage que le solde dû. Le bilan affiche la **somme des deux dettes**. Les échéances du prêt antérieur ne sont ni supprimées ni remplacées.

Il n'y a pas de frais bancaires récurrents, assurance emprunteur, taux variable, remboursement anticipé, prêt relais ou droit à l'emprunt automatiquement calculé.

## 4. Valorisation de la propriété

Le bien acheté a une valeur **nulle avant le mois p**, puis V le mois p. Pour chaque mois m supérieur ou égal à p, sa valeur nominale supposée est :

$$
H_{\mathrm{achat},m}=V(1+g_H/100)^{(m-p)/12}.
$$

Ce gain théorique ne se transforme **pas** en revenu disponible. Les biens déjà possédés évoluent depuis le mois initial sous le même taux de revalorisation choisi, tandis que les autres actifs non liquides conservent leur valeur nominale. Dans tous les scénarios :

$$
N_m=C_m+A_m+H_m+O_m-D_m.
$$

En Monte Carlo, les échéances de prêt et la valeur immobilière restent **déterministes** ; seul le rendement des placements est aléatoire. Les résultats ne constituent donc ni une prévision immobilière ni une probabilité réelle de solvabilité.

## 5. Exemple fictif

Un ménage dispose de 100 000 € de trésorerie. Il achète au **mois 3** un bien de **120 000 €**, avec **20 000 € d'apport**, **5 000 € de frais** et **100 000 € d'emprunt** à **0 % sur 20 ans**.

| Période | Trésorerie | Valeur du nouveau bien | Nouvelle dette | Patrimoine net de ces éléments |
|---|---:|---:|---:|---:|
| Mois 2 | 100 000 € | 0 € | 0 € | 100 000 € |
| Mois 3, après achat | 75 000 € | 120 000 € | 100 000 € | 95 000 € |
| Mois 4, après la première mensualité | 74 583,33 € | 120 000 € | 99 583,33 € | 95 000 € |

Cet exemple ignore les autres revenus, charges et rendements. Les **frais de 5 000 €** expliquent la diminution de patrimoine ; à taux nul, le paiement du principal diminue la trésorerie et la dette du **même montant**.

## 6. Expérience utilisateur

La page Planification propose un panneau facultatif fermé par défaut. En activant le projet, l'utilisateur saisit la date d'achat, le prix, l'apport, les frais et le nouveau financement. Les résultats affichent distinctement : sortie initiale de trésorerie, capital emprunté, mensualité et nouveau capital restant dû à l'échéance finale du scénario. Le calendrier de trésorerie réserve une colonne aux coûts d'acquisition. Le graphique de patrimoine peut signaler la date d'achat.

L'interface et les guides présentent les conventions en **français, anglais et vietnamien**. Ne pas confondre ce calcul conditionnel avec une simulation officielle de prêt immobilier.

## 7. Compatibilité, tests et limites

L'export conserve le schéma externe JSON de version 1. Le champ de projet d'achat est **facultatif** : un ancien fichier sans cette donnée garde les mêmes résultats qu'avant. Une date hors horizon, un apport supérieur au prix, une mensualité impossible à construire ou des données non numériques sont refusés.

Les régressions couvrent l'identité actif/dette/trésorerie, la perte immédiate égale aux frais, la coexistence de deux prêts, la première mensualité le mois suivant, la revalorisation après l'achat, les résultats Monte Carlo à volatilité nulle, l'import ancien et l'affichage des trois langues.

**Limites** : achat unique, pas de vente, pas de calcul des loyers, taxes, entretien, prix de marché, coûts de notaire réglementaires, frais de garantie ou assurance de prêt. Tout montant supplémentaire doit être renseigné explicitement par l'utilisateur. **Les tests doivent réussir en CI et la version déployée être contrôlée séparément** avant de qualifier le modèle de stable.