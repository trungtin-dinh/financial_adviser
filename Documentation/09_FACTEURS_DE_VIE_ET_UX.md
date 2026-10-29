# Refonte ergonomique, risques de vie et projection inverse — v0.2.0

**Date :** 29 octobre 2026 · **Statut :** v0.2.0, analyse de conception + implémentation initiale. Ce fichier distingue les faits de recherche, les choix d'ingénierie, les limites et les pistes futures. Une revue fondée sur des personas **n'est pas un test avec de vraies personnes**.

## 1. Pourquoi dépasser les paramètres purement financiers ?

Le patrimoine dépend d'événements personnels et professionnels qui modifient les flux futurs : naissance ou charge d'un enfant, études, chômage, arrêt de travail, frais de santé, soutien à des proches, achat important, déménagement ou changement de pays. Il ne faut pas confondre :

- **Événement planifié** : hypothèse de scénario, dont le début, la durée et les coûts sont décidés par l'utilisateur.
- **Aléa** : événement incertain. La v0.2 ne déduit **aucune probabilité statistique** de maladie, accident, maternité ou chômage, ni aucune dépense « moyenne » qui dépendrait du profil sensible de la personne.
- **Risque financier** : dans la v0.2, la possibilité de trésorerie négative est calculée ; les coûts sociaux et sanitaires sont uniquement des scénarios manuels. Monte Carlo n'aléatorise actuellement que les rendements financiers.

**Conception retenue :** événements multiples avec catégorie, description, mois de début, durée en mois, charge mensuelle additionnelle (positive), variation signée de revenu net mensuel, dépense initiale (positive). Aucune donnée médicale individuelle n'est demandée. Une catégorie ne change pas les équations : elle sert à l'organisation et à l'affichage. Les événements n'incluent pas le calcul automatique des prestations sociales ou remboursements de santé FR/VN. Les changements de pays et de fiscalité ne sont pas simulés automatiquement.

**Sources de produits :** ProjectionLab propose des flux de dépenses avec dates de début/fin ou jalons : https://cdn.projectionlab.com/help/adding-expenses-to-your-plan et des objectifs de flux : https://projectionlab.com/help/cash-flow-priorities (consultées 29/10/2026). Ces exemples servent d'inspiration, pas de preuve de précision de leur moteur.

## 2. Modèle des événements et conventions

Pour un mois `m` (1 = premier mois) et l'événement `j` de début `s_j`, durée `d_j`, charge `c_j`, variation de revenu `u_j` et dépense initiale `b_j`, on pose :

- `I_j(m) = 1` si `s_j ≤ m < s_j + d_j`, sinon `0`.
- Revenu effectif `Y(m) = Y_base(m) + ∑_j u_j I_j(m)`.
- Dépenses effectives `D(m) = D_base(m) + ∑_j c_j I_j(m)`.
- Flux ponctuel `E(m) = E_base(m) − ∑_{j:s_j=m} b_j`.

Les flux sont ajoutés à la simulation mensuelle de base avant le rendement du mois. **Les montants par événement sont constants en nominal** pendant leur durée (contrairement à l'évolution paramétrée des dépenses de base). Les montants sont dans l'unique devise du scénario, sans taux de change automatique. Plusieurs événements peuvent se recouvrir et leurs flux s'additionnent. Un événement doit être intégralement compris dans l'horizon de simulation. Ces simplifications sont explicites et révisables.

Exemples sans montant imposé : frais de garde pendant 36 mois ; baisse de revenus 4 mois pour un arrêt de travail ; achat automobile ponctuel ; participation aux frais d'un parent âgé. Les montants doivent être des **hypothèses saisies par l'utilisateur**, pas des tarifs médicaux ou probabilités inférées.

## 3. Projection inverse (goal seeking)

**Problème :** au lieu de seulement calculer la sortie `V_T = F(x)`, fixer un patrimoine nominal souhaité `G` et un horizon `T`, puis chercher des modifications des entrées `x`.

La première version propose **trois solutions distinctes**, calculées séparément :

1. Surcroît de revenu net **mensuel initial**, avec la même hypothèse de croissance annuelle que le revenu de base.
2. Réduction des **dépenses mensuelles de base** initiales, qui conservent ensuite la croissance annuelle des dépenses de base. Impossible de diminuer au-delà de leur montant initial.
3. Apport de **capital liquide externe** au mois zéro, qui suit ensuite le rendement de la trésorerie configuré ; ce n'est ni un transfert interne ni un crédit.

Pour chaque levier `z`, on exige :

`V_T(z) >= G` ET `cash_m(z) >= 0` pour tous les mois `m = 0..T`.

Dans le moteur déterministe actuel, les états sont linéaires en chacun des leviers lorsque les autres paramètres sont fixés :

`V_T(z) = V_T(0) + a_T z` et `cash_m(z) = cash_m(0) + a_m z`.

On calcule les coefficients de sensibilité par différence finie contrôlée, et la plus grande des bornes inférieures sur `z` :

`z >= max{0, (G - V_T(0))/a_T, max_m[-cash_m(0)/a_m si cash_m(0)<0]}`.

Ce calcul n'est admis que pour les sensibilités positives applicables. On revérifie les résultats avec le moteur direct. Pour la réduction de dépenses, on vérifie également `0 <= z <= D_base(0)` et l'option devient « impossible par ce seul levier » sinon.

**Attention :** il ne s'agit PAS de déduire de manière unique une entrée à partir de la sortie. Plusieurs jeux d'entrées peuvent mener au même patrimoine. Il s'agit de trois scénarios explicables, non cumulés, sans garantie de réalisme comportemental. Le calcul ne tient pas compte de la fiscalité, des frais, de l'évolution de la situation socio-familiale induite ou de l'incertitude des rendements. La contrainte de cash est non négative **sans** rendement de découvert ni stratégie de liquidation automatique des investissements.

## 4. Règles de design adoptées

- **Divulgation progressive :** champs essentiels sur l'écran principal ; paramètres techniques optionnels dans le mode avancé. Référence : Nielsen Norman Group, https://www.nngroup.com/articles/progressive-disclosure/.
- **Questions pertinentes uniquement :** revenu net, dépenses, objectif et horizon sont nécessaires au premier calcul ; événements facultatifs. Les champs requis sont vides au premier démarrage, avec possibilité de charger explicitement un jeu d'exemple. Référence : GOV.UK, https://design-system.service.gov.uk/patterns/question-pages/.
- **Séparation des tâches :** les formulaires et résultats de calcul sont distincts des pages « Guide & Models » et « Sources & Regulations », accessibles via la navigation Streamlit `st.navigation`. Référence : https://docs.streamlit.io/develop/concepts/multipage-apps/page-and-navigation.
- **Transparence :** retour « infaisable » pour un levier inverse, affichage de la trésorerie minimale et possibilité d'appliquer explicitement une solution. Les hypothèses de Monte Carlo et les règles non implémentées sont signalées.
- **Reproductibilité :** le moteur est indépendant de Streamlit ; scénarios JSON v1 importés et exportés ; on conserve les événements personnels structurés.
- **Prévention des erreurs :** validation des champs requis, dates, coûts, bornes et détection des résultats de goal-seek périmés. Référence : https://www.nngroup.com/articles/ten-usability-heuristics/.

## 5. Revue critique par profils **simulés**, et non enquête d'utilisateurs

Cette matrice est une **revue heuristique interne par scénarios fictifs**, sans vrais participants ni validation par un conseiller financier. Elle vise à identifier les risques d'utilisation ; elle ne doit pas être présentée comme un résultat de test utilisateur ou d'expertise certifiée.

| Persona fictif / angle d'audit | Tâche | Risque anticipé | Action v0.2 / reste à faire |
|---|---|---|---|
| Étudiant ou salarié débutant, peu d'épargne | Saisir un budget, estimer le patrimoine | Surabondance de taux et hypothèses | Champs requis limités, mode avancé replié ; ajout souhaité de conseils contextuels |
| Parent avec enfants à charge | Projeter garde, études et grosse dépense | Coûts fixes non représentatifs ; confusion récurrent/ponctuel | Événements datés et récurrents, catégorie enfant ; adaptation à l'âge de l'enfant à faire |
| Personne aidante ou avec frais de santé | Simuler charge et perte de revenu | Interprétation comme prédiction médicale ; données sensibles | Saisie de conséquences financières hypothétiques seulement ; pas de dossier médical ni probabilité |
| Indépendant à revenus fluctuants | Tester baisse de chiffre d'affaires | Un revenu mensuel fixe est irréaliste | Variation temporaire du revenu via événements ; profil de revenus variables saisonniers à prévoir |
| Investisseur expérimenté | Atteindre un objectif sans faillite de trésorerie | Confondre rendement, contribution et épargne supplémentaire | Solveur 3 leviers indépendants ; optimisation sous contraintes et fiscalité à développer |
| Personne travaillant entre France/Vietnam | Analyser patrimoine multidevise | Change, fiscalité et protection sociale absents | Limites explicites ; moteur FR/VN et FX à valider avant mise en production |
| Utilisateur mobile, faible familiarité numérique | Ajouter un événement complexe | Table d'édition trop large sur téléphone | Navigation adaptée ; création « une question par étape » sur mobile à ajouter et tester |
| Expert financier / fiscal **simulé** | Auditer les conclusions | Normes, fiscalité, probabilités de risques non étalonnées | Avertissements et références ; audit externe humain indispensable |

**Priorités de revue humaine ultérieure** : 6 à 10 utilisateurs volontaires divers en âge, composition du foyer, budget, littératie financière, FR/VN et appareil utilisé ; 1 à 2 personnes compétentes en fiscalité FR/VN ; 1 spécialiste de planification financière. Obtenir leur consentement et ne collecter que des scénarios fictifs. Mesurer taux de réussite d'une tâche, erreurs, temps, confusion entre « épargne transférée » et « épargne créée », satisfaction et accessibilité. Cette revue humaine **n'a pas été menée**.

## 6. Limites, critères d'acceptation et suites

V0.2 implémente : événements hypothétiques datés, comparaison de leur effet, champs essentiels requis, hypothèses optionnelles, calcul inverse trois leviers, navigation dédiée à la documentation, tests unitaires. Elle ne constitue pas une validation clinique, actuariat, fiscale ni statistique.

À faire : interface événements adaptée au mobile ; scénarios de risque avec probabilités justifiées par des sources publiques non sensibles, sans extrapoler à une personne ; revenus saisonniers ; dépenses par catégories et indexation ; liquidations d'actifs pour combler la trésorerie ; optimisation multicritères (plusieurs leviers combinés et contraintes) ; confrontation avec de vrais utilisateurs et experts ; essais d'interface en navigateur / mobile.
