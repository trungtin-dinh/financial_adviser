# Plan de validation multi-profils, revue par les pairs et experts

**État au 30 octobre 2026 : protocole défini, scénarios fictifs et tests synthétiques en cours. AUCUN participant humain indépendant ni expert externe n'a encore rendu d'avis.**

La validation professionnelle d'une application financière ne peut pas être remplacée par une simple critique produite par le développeur ou par une IA. Nous séparons trois niveaux de preuve :

- **V1 — Vérification technique** : tests unitaires, validations de calculs, tests de navigation, snapshots d'interface, cohérence FR/EN/VI; vérifiable sans personne extérieure.
- **V2 — Évaluation simulée et heuristique** : revue systématique de parcours de personnes fictives à revenus, âges et contextes variés; hypothèses de conception, **pas** résultat d'étude sociale.
- **V3 — Validation humaine indépendante** : tests modérés avec de **vrais utilisateurs consentants** et avis signés/datés d'un économiste/actuaire, développeur indépendant et fiscalistes FR/VN. **Non réalisée**. Requis pour déclarer un produit final validé.

Références : NIST (https://www.nist.gov/programs-projects/usability-testing et https://www.nist.gov/itl/iad/human-centered-technologies/human-factors-human-centered-design), ISO 9241-210:2019 (https://www.iso.org/standard/77520.html), Nielsen Norman Group (https://www.nngroup.com/articles/ten-usability-heuristics/), WCAG 2.2 (https://www.w3.org/TR/wcag/). Un test ergonomique est effectué avec des personnes *réelles* sur des tâches représentatives, pas par des personas inventés.

## Profils fictifs de vérification (données purement synthétiques)

| Profil de test | Conditions qui peuvent changer le résultat | Tâche observée | Risque particulier |
|---|---|---|---|
| Étudiant / premier emploi | épargne nulle, revenu limité, horizon court | projeter un achat ponctuel, détecter l'insuffisance de trésorerie | ne pas confondre revenu et transfert |
| Travailleur précaire | période de chômage, faibles liquidités | ajouter une perte de salaire datée, voir un déficit | résultat de solvabilité négatif caché |
| Parent seul avec enfant | coût mensuel de garde, éventuel congé | décrire un événement récurrent et sa durée | erreur de signe ou mois |
| Couple bi-actif | charges communes et revenus de plusieurs adultes | calculer un budget consolidé | modélisation d'un revenu unique à expliquer |
| Aidant familial | dépenses de soins et réduction du travail | combiner coût fixe, récurrence et revenu réduit | double comptage ou durée |
| Indépendant | revenus irréguliers, variations saisonnières | tester baisse de revenu sans inventer un risque chiffré | moyennes trompeuses |
| Retraité / revenus fixes | épargne, inflation, longévité | distinguer nominal / pouvoir d'achat | revenu pension non détaillé |
| Investisseur averti | portefeuille/volatilité, taux négatifs | comprendre P10/P90 et hypothèses de rendement | confondre percentiles avec garanties |
| Faible littératie / petit écran | lecture de champs, scrolling, aide | compléter sans navigation cachée | contrôles invisibles / jargon |
| Situation transfrontalière France/Vietnam | VND/EUR, différents pays | changer de devise sans conversion implicite | incohérence d'unités |
| Personne ayant des besoins d'accessibilité | navigation clavier/zoom/lecteur d'écran | saisir et vérifier un événement | absence d'annonce état modifié |

**Important** : la base actuelle possède un **seul revenu mensuel agrégé, une seule devise et un seul actif « investi »**. Les personas ne doivent pas suggérer qu'elle simule individuellement deux salaires, un régime fiscal ou un portefeuille multi-actifs. Les fonctionnalités non prises en charge deviennent des limites et des exigences ultérieures.

## Tâches d'étude à remettre sans indiquer les clics

1. Déterminer votre patrimoine dans 12 ans pour un jeu de données fictif.
2. Ajouter un achat unique dans deux ans; lire la différence avec et sans événement.
3. Ajouter un enfant qui occasionne une dépense de garde pendant trois ans.
4. Simuler trois mois de perte de revenu, sans connaître de fonctions financières.
5. Changer le pays et vérifier que les anciennes valeurs ne sont **pas** converties automatiquement.
6. Modifier le rendement, observer que le résultat existant est **périmé**, relancer sans perdre les champs.
7. Trouver l'apport supplémentaire nécessaire pour atteindre une cible, sans confondre alternatives indépendantes.
8. Identifier la source et l'année d'une donnée « moyenne nationale », puis refuser de l'appliquer à ses revenus.
9. Exporter/importer un scénario, vérifier intégrité des événements.
10. Expliquer la différence entre patrimoine nominal, réel et trésorerie.

## Mesures et méthode

Pour chaque participant (avec accord préalable) : catégorie large déclarée volontairement, pays/langue, navigateur/appareil, tâche, réussite autonome (oui/non), temps de réalisation, erreurs bloquantes ou non, endroits de confusion, verbatim anonymisés. **Aucun montant réel, historique médical, identifiant personnel ou statut fiscal sensible à collecter.** Enregistrer la gravité : P0 calcul/décision erronée, P1 tâche impossible, P2 difficulté, P3 cosmétique. Proposer une correction, puis faire rejouer la même tâche sur le même profil sans suggérer la réponse.

Un petit panel exploratoire permet de détecter des problèmes mais ne suffit pas à quantifier leur fréquence dans la population. Tout pourcentage de réussite doit préciser n, méthode de recrutement, contexte et biais.

## Revue des experts : axes et preuves attendues

| Expert | Audit demandé | Critère d'acceptation | Statut |
|---|---|---|---|
| Economiste / chercheur finance des ménages | bilan, stocks/flux, hypothèses exogènes, calibration et limites de représentativité | revue écrite des équations, exemples analytiques reproduits | Non sollicitée |
| Actuaire / spécialiste risque | corrélation, trajectoires, séquence des rendements, risques de vie, biais probabilistes | distributions sourcées; limites des probabilités établies | Non sollicitée |
| Fiscaliste droit français | PEA, assurance-vie, PER, retraites, cotisations, année fiscale, dates d'effet | cas officiels reproduits avec sources; pas de code fiscal avant accord | Non sollicitée |
| Fiscaliste droit vietnamien | PIT, assurances obligatoires, aides, conventions internationales | cas officiels, règle/version/applicabilité | Non sollicitée |
| Concepteur UX / chercheur utilisateurs | cohérence des parcours FR/EN/VI, accessibilité, navigation mobile | rapport daté, problèmes observés et priorités | Non sollicitée |
| Développeur Python/Streamlit indépendant | sécurité import, état de session, typage, performance, CI | revue PR reproductible et tests | Non sollicitée |
| Locuteurs FR/EN/VI | terminologie financière, absence de mélange, compréhension des messages | revue linguistique native consignée | Non sollicitée |

**Condition de qualification de « version finale validée »** : V1 et V2 documentées, V3 effectivement réalisées, revue des risques P0/P1 clôturée, sources officielles maintenues et conformité règlementaire présentée avec limites véridiques. Aucune invention de signature, expertise ou résultat d'enquête.

## Livrables préparés pour les relecteurs

- Documentation des équations et conventions : `02_MODELES_MATHEMATIQUES.md`.
- Catalogue des facteurs et limites : `17_FACTEURS_FINANCIERS_SOCIAUX_ET_RISQUES.md`.
- Référentiel UX : `14_REFERENTIEL_ERGONOMIE.md`.
- Audit de risques UX : `15_AUDIT_ERGONOMIQUE_V04.md`.
- Tests synthétiques : `tests/test_personas_synthetiques.py`.
- URL de démonstration (à utiliser **avec données fictives seulement**) : https://financial-adviser.streamlit.app/ .

Le fait que ces supports existent n'est **pas** une preuve de revue humaine.
