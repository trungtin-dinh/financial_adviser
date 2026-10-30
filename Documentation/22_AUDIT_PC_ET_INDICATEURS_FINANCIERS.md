# Revue scientifique et UX : v0.8.0 (30 octobre 2026)

## Synthèse des problèmes et corrections

**Avant :** le plan, les résultats, la recherche d'objectif et les comparaisons se succédaient verticalement. Le bureau PC n'utilisait pas sa surface de consultation. **Après :** éditeur sur la colonne gauche, résultats et comparaisons sur la droite, disposition à une colonne en dessous du seuil responsive Streamlit. L'utilisateur voit les conséquences de ses hypothèses plus facilement, sans changement de page ni action de navigation cachée.

La mise en page donne la priorité aux champs nécessaires et aux sorties vérifiables. Les paramètres facultatifs du foyer et les événements restent identifiables. Les champs restent modifiables ; les résultats doivent signaler toute modification qui invalide le dernier calcul. Les formes contenant les contraintes de prêt et la saisie ponctuelle restent à auditer avec des personnes réelles.

### Sources ergonomiques

- GOV.UK Design System, Layout : https://design-system.service.gov.uk/styles/layout/
- Streamlit, Layouts and containers : https://docs.streamlit.io/develop/concepts/design/layouts-and-containers
- W3C, WCAG 2.2, redistribution 1.4.10 : https://www.w3.org/TR/WCAG22/#reflow
- Nielsen Norman Group, 10 usability heuristics : https://www.nngroup.com/articles/ten-usability-heuristics/

## Modèle financier : concepts fondamentaux

L'enquête HFCS de la BCE (https://www.ecb.europa.eu/stats/ecb_surveys/hfcs/html/index.en.html) distingue les actifs réels, financiers, dettes, transferts, consommation, emploi et retraites des membres du ménage. L'enquête Insee Budget de famille 2026 (https://www.insee.fr/fr/information/8719834) couvre les structures de dépenses (logement, transport, alimentation, habillement) et leurs différences selon l'âge, le revenu ou le territoire. Ces dimensions éclairent la conception ; elles ne donnent PAS de budget type individuel.

### Indicateurs ajoutés aux résultats

| Variable | Formule | Précaution |
| --- | --- | --- |
| Surplus mensuel courant | Revenu net - dépenses - mensualité de prêt | Avant virement interne vers investissements, sans événements futurs |
| Couverture mensuelle des sorties par le cash | Trésorerie initiale / (dépenses mensuelles + mensualité) | Ratio statique approximatif, ni garantie de résilience ni prévision de faillite |
| Service de crédit relatif | Mensualité du seul prêt simulé / revenu net mensuel | Ne représente ni toutes les dettes, ni un seuil d'octroi bancaire |
| Patrimoine net nominal | Cash + placements - dette modélisée | N'inclut pas les biens immobiliers non modélisés |
| Patrimoine réel | Patrimoine net nominal / facteur d'inflation | Prix futurs hypothétiques et non connus |
| Trésorerie négative | Existence de mois avec cash inférieur à zéro | Avertissement distinct : patrimoine positif n'équivaut pas à liquidité suffisante |

Lorsque le dénominateur est nul, le rapport est indiqué comme non applicable. Il serait trompeur de transformer ces mesures en notation de solvabilité universelle.

### Dimensions socio-économiques non pleinement modélisées

Un foyer se compose d'adultes et d'enfants, de revenus possiblement variables, de dettes, de dépenses contraintes, de transferts publics, d'entraide familiale et de charges qui évoluent avec l'âge. Le module household modélise une partie de cette évolution à partir d'hypothèses modifiables ; il ne modélise pas la fiscalité réelle, les allocations ou les droits réglementaires de retraite. Les risques de chômage, de marché, de santé et d'inflation ne sont généralement pas indépendants. Aucun taux de risque personnel ou coût moyen universel n'est déduit automatiquement.

La différence entre revenus, transferts internes, liquidité et patrimoine total doit demeurer explicite. Les budgets d'enfants déjà inclus dans les dépenses du foyer ne sont pas rajoutés intégralement.

## Critères d'acceptation automatique après push

1. Compilation et tests Python du moteur et de la page dans trois langues.
2. Chromium local aux dimensions 1440x900, 834x1112, 390x844 et 360x800. Sur PC, l'en-tête des résultats doit avoir une abscisse plus grande que celui des paramètres; sur mobile, les blocs doivent suivre l'ordre vertical sans défilement horizontal global.
3. Ajout et modification d'un événement, sans disparition des données.
4. Publication GitHub, puis ouverture Chromium du VRAI domaine public Streamlit, y compris ses cadres intégrés éventuels.
5. Vérifier la version déployée ET le parcours exemple-confirmation-projection-résultats, puis l'affichage vietnamien mobile. Les captures sont jointes aux rapports GitHub Actions.
6. Un test en échec signifie : livraison non vérifiée. Un push réussi n'est pas une preuve de déploiement.

Les deux workflows GitHub Actions sont réactivés à chaque push depuis que l'utilisateur a désactivé les e-mails correspondants dans ses préférences GitHub. Le deuxième workflow démarre uniquement après succès de la CI locale. Un délai de mise à jour du site public est possible; une version périmée est signalée comme telle.

**Limites de la validation :** les scripts ne remplacent ni une étude d'ergonomie avec de vrais participants, ni la revue d'un économiste/actuaire, ni la validation juridique française/vietnamienne. Le code peut passer les tests et le fournisseur d'hébergement encore rencontrer un problème indépendant.

## Incident réel de déploiement et mesures correctrices (v0.8.2)

Le navigateur public a bien trouvé la v0.8.1, mais le parcours « Charger un exemple » puis « Confirmer le remplacement » puis « Lancer la projection » a conduit à l'erreur « Le revenu, les dépenses et l'objectif doivent être renseignés ». Contrairement aux tests de compilation et de l'apparence seule, ce test a détecté une anomalie d'état utilisateur. La v0.8.2 programme une restauration des clés de saisie depuis le Plan enregistré **avant** que les widgets Streamlit soient construits. Le test navigateur attend que le champ revenu soit effectivement rempli avant de déclencher la projection. Cet incident ne concerne pas des probabilités ou hypothèses économiques, mais l'intégrité des saisies de simulation.

## Résolution et vérification publique

Le commit v0.8.2 `64a5873af` a réussi les suites locales Python, PC/tablette/mobile, puis le workflow Playwright [41033538584](https://github.com/trungtin-dinh/financial_adviser/actions/runs/41033538584) sur le vrai site. Messages dans les journaux : version hébergée v0.8.2, parcours FR complet (exemple, calcul, résultats) réussi et chargement VI mobile sans débordement. Ce contrôle corrige une panne d'interaction concrète, et non une simple détection HTTP.

La disponibilité continue, les droits fiscaux FR/VN et une étude avec des personnes réelles restent hors de portée de cette seule validation automatique.
