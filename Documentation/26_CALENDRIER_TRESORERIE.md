# Calendrier de trésorerie mensuel — convention et contrôles

**30 octobre 2026 — Fonctionnalité d'affichage, sans changement du moteur.**

## Pourquoi

La revue sélective [25](25_REVUE_SELECTIVE_FINANCE_ECONOMIE_UX.md) a identifié un besoin prioritaire : rendre explicites les mois de tension, à l'image de la lisibilité des échéances d'Actual Budget. Le premier incrément réutilise les flux déjà produits par Financial Adviser. **Il ne crée pas encore de règles de récurrence (trimestrielle, annuelle, etc.) ni de nouvelles hypothèses financières.**

## Grandeurs, temporalité et convention

Pour chaque mois projeté `m` (à partir de 1), tous les montants sont **nominaux** et exprimés dans la devise unique du scénario :

- `income[m]` : revenu net mensuel total tel que projeté, y compris les changements liés au foyer et aux événements ;
- `expenses[m]` : dépenses du mois, y compris les coûts supplémentaires du foyer et des événements ;
- `loan_payment[m]` : échéance de dette versée ce mois ;
- `one_off[m]` : flux ponctuel **signé** : positif pour une entrée, négatif pour une sortie, comprenant les coûts initiaux d'événements de vie ;
- `monthly_investment` : transfert régulier du compte de trésorerie vers les placements.

Le flux de trésorerie **avant rendements** est :

```text
F_m = income_m - expenses_m - loan_payment_m + one_off_m - monthly_investment
```

Le solde de trésorerie présenté vient directement du résultat du moteur :

```text
cash_m = (cash_(m-1) + F_m) * (1 + r_cash_mensuel)
```

Cela signifie que la variation de trésorerie ne correspond pas exactement à `F_m` quand le rendement du compte n'est pas nul. La contribution aux placements n'est **pas** une dépense qui réduit le patrimoine net, mais un transfert interne. Les rendements de placements ne sont pas compris dans `F_m` et ne doivent pas être interprétés comme un flux d'entrée de trésorerie.

## Parcours utilisateur

Dans **Résultats**, ouvrir « Calendrier de trésorerie mensuel », puis choisir une année. Le tableau présente les douze mois de l'année, avec revenus, dépenses, échéances, flux ponctuels, transfert, flux net et solde de trésorerie. Trois indicateurs résument le flux net cumulé avant rendement, la trésorerie minimale du sous-ensemble annuel et le nombre de mois à solde négatif. La période totale dépend de l'horizon du scénario déjà calculé.

L'affichage utilise **uniquement le dernier scénario enregistré et calculé**, même si la fiche de saisie a été modifiée depuis. La sélection d'année est isolée par un `st.fragment` ; elle n'appelle ni `project` ni `monte_carlo`.

## Limites et vérification

- Une trésorerie négative est un **déficit non financé** : aucun découvert, emprunt ou rachat de titres n'est ajouté implicitement.
- Il ne faut pas déduire une saisonnalité ou un calendrier de prélèvements récurrents **non saisis**.
- Les hypothèses fiscales, de pension ou de frais absentes du scénario demeurent absentes du tableau.
- Les tests ajoutés vérifient conservation des transferts, identité `cash + investments - loan_balance = net_worth`, montant et date des événements, passage d'année, valeurs VND, taux de dette nul et schémas manquants.
- La présence de ces tests dans le dépôt **n'est pas une preuve de succès CI** ; la validation doit confirmer `compileall`, `pytest` et le parcours navigateur desktop/mobile, notamment en FR, EN et VI.

## Mise à jour v0.20.0 (30 octobre 2026)

Les limites mentionnées pour le **premier incrément** ci-dessus décrivent la version précédente. La version v0.20.0 ajoute désormais la saisie d'échéances mensuelles, trimestrielles et annuelles ainsi qu'une colonne de flux périodiques dans le calendrier, selon les [conventions détaillées](28_ECHEANCES_RECURRENTES_V020.md). Les flux sont saisis explicitement, sans indexation automatique. Le texte précédent reste comme historique des décisions.

## Étapes suivantes

1. Valider la refactorisation et ce calendrier par CI/navigateur.
2. Ajouter des échéances **saisies explicitement** avec périodicités et horizon, en conservant le format des anciens scénarios JSON.
3. Tester l'absence de double comptage et la conservation des capitaux avant d'introduire des objectifs multiples.
4. Étudier séparément la décumulation/retraite puis les scénarios macroéconomiques stochastiques, avec conventions et données traçables.
