# Référentiel d'ergonomie logicielle — Financial Adviser

**30 octobre 2026 — Référentiel de travail, pas une certification de conformité ni une étude auprès d'utilisateurs réels.**

## 1. Méthode et sources

Le projet applique une démarche centrée utilisateur, cohérente avec ISO 9241-210: comprendre les utilisateurs, leurs objectifs et leur contexte; spécifier les exigences; concevoir; évaluer; itérer. Le résumé public de la norme est consultable à https://www.iso.org/standard/77520.html et les principes sont présentés par le NIST : https://www.nist.gov/itl/iad/human-centered-technologies/human-factors-human-centered-design . Le texte intégral de la norme n'a pas été reproduit.

Références UX consultées :
- Nielsen Norman Group, **10 heuristiques** (mise à jour 2024) : https://www.nngroup.com/articles/ten-usability-heuristics/ .
- GOV.UK Design System, **validation et messages d'erreur** : https://design-system.service.gov.uk/components/error-message/ .
- GOV.UK, **questions compréhensibles** (actualisé en juin 2026) : https://www.gov.uk/service-manual/design/designing-good-questions .
- UK Parliament Design System, **formulaires par étapes et divulgation progressive** : https://designsystem.parliament.uk/how-tos/designing-forms/ .
- W3C, **WCAG 2.2**, notamment reflow, champs, libellés, navigation au clavier et focus : https://www.w3.org/TR/WCAG22/ ; explication du reflow 320 CSS px : https://w3c.github.io/wcag/understanding/reflow.html .
- GOV.UK, **tests d'utilisabilité modérés** : https://www.gov.uk/service-manual/user-research/using-moderated-usability-testing .

Ces sources fournissent des principes généraux. Les recommandations concrètes ci-dessous sont des **déductions d'ingénierie pour notre produit**, pas des prescriptions attribuées mot à mot aux auteurs.

## 2. Principes non négociables

| Principe | Conséquence vérifiable dans Financial Adviser |
| --- | --- |
| Statut visible | Distinguer « valeurs modifiées », « simulation en cours », « résultat à jour », « résultat périmé » et « source indisponible ». Afficher la date/version des hypothèses de chaque résultat. |
| Langage du public | Préférer « dépenses mensuelles » à « flux sortants »; présenter séparément patrimoine, liquidités et capital investi. Expliquer net/brut, mensualité, inflation réelle/nominale. |
| Contrôle et réversibilité | Ne jamais écraser un scénario ou ses événements sans aperçu et confirmation. Proposer annulation/réinitialisation explicites et export avant fermeture. |
| Cohérence | Une langue FR/EN/VI pour les textes métier, unités visibles cohérentes, les mêmes conventions d'indices calendaires, les mêmes commandes entre pages. |
| Prévention des erreurs | Vérifier horizon, montant et durée d'événement avant lancement; empêcher double comptage du remboursement d'emprunt; expliciter les dépenses déjà incluses. |
| Reconnaissance plutôt que mémoire | Résumer le scénario à côté des graphiques; montrer les hypothèses et leur provenance; conserver les saisies après erreur. |
| Débutant et expert | Chemin court avec paramètres essentiels; sections avancées repliées sans masquer l'accès à la documentation et aux calculs. |
| Minimalisme | Un message principal et une action principale par vue; déplacer les détails fiscaux/mathématiques vers « Guide ». Aides courtes à côté du champ concerné. |
| Erreurs réparables | Dire **quel champ**, **pourquoi** et **comment corriger**; garder les valeurs précédentes; ne pas afficher un simple « Invalid input ». |
| Aide contextuelle | « Pourquoi cette hypothèse ? », « Source », « Voir le modèle » au bon endroit, sans imposer la lecture des documents complets. |

## 3. Parcours de référence

**Débutant :** choisir la langue, le pays, l'objectif, saisir revenu net, dépenses, patrimoine éventuel et horizon; lancer; identifier sur la première vue le résultat **et** ses hypothèses. Un exemple est disponible explicitement, sans application silencieuse.

**Famille / événements :** ajouter une fiche « enfant », « soins », « chômage », « achat »; comprendre si le montant est une dépense unique ou récurrente; dater début et fin; comparer avec/sans événement; supprimer sans perdre les autres événements.

**Expérimenté :** modifier croissance, rendement, inflation, dette et volatilité; inspecter les formules et exporter un scénario reproductible. Un résultat vieux de deux éditions doit être marqué comme périmé.

**Statistique officielle :** identifier clairement **moyenne/médiane**, population, unité, année de mesure et source; ne jamais convertir automatiquement un revenu moyen par habitant en revenu net d'un ménage. Une observation passée n'est pas une prévision.

**Simulation inverse :** partir de l'objectif et expliquer séparément chaque levier (hausse du revenu net, baisse de dépenses, capital externe), sa faisabilité et ses contraintes. Les solutions ne sont pas des recommandations d'investissement.

## 4. Accessibilité et écrans

Cibles de vérification : bureau 1440×900, tablette 834×1112, mobile 390×844 et 360×800; ajouter 320 CSS px et zoom navigateur 200–400 % quand c'est techniquement possible. Aucun contenu critique caché horizontalement, hors composants dont le sens exige le défilement à deux dimensions. Vérifier libellés accessibles, focus visible, navigation au clavier, taille des cibles, contrastes, lecteurs d'écran, et distinction graphique ne reposant pas seulement sur la couleur.

Un passage Playwright avec captures ou absence de débordement **ne prouve pas à lui seul la conformité WCAG**. Prévoir des essais sur appareils physiques, lecteurs d'écran et claviers virtuels.

## 5. Protocole de revue utilisateur

Recruter, avec leur accord, des personnes représentant réellement : utilisateur sans connaissances financières, salarié, parent avec enfants, travailleur indépendant, épargnant confirmé, résident au Vietnam et personnes ayant des besoins d'accessibilité. Adapter les tâches, pas les réponses attendues. Préparer un jeu de **données fictives** pour éviter la collecte de données de santé ou d'épargne personnelles lors des essais publics.

Tâches types, sans donner l'endroit où cliquer :
1. Prévoir les économies de ce ménage dans 15 ans;
2. Ajouter deux ans de frais de garde à partir d'une année choisie;
3. Évaluer l'impact d'un achat ponctuel;
4. Trouver comment atteindre un patrimoine cible;
5. Identifier la source d'une statistique puis revenir au scénario;
6. Exporter et réimporter son scénario.

Recueillir : taux de réussite sans aide, temps par tâche, erreurs critiques (unité, signe, date, confusion de source), abandons, retours qualitatifs et verbalisations. Éviter de créer une mesure de satisfaction avec quelques témoignages isolés. Analyser par profil et appareil, avec citations anonymisées avec consentement. Les **tests de personas fictifs** et les tests automatisés ne remplacent pas ces observations.

## 6. Boucle de qualité

Pour chaque modification : (a) problème détecté avec preuve, (b) gravité et fréquence, (c) hypothèse de correction, (d) critères d'acceptation, (e) tests automatisés et, lorsque possible, retours d'utilisateurs réels, (f) journal des changements. Un rendu joli n'est pas une preuve d'une meilleure compréhension. Ne jamais annoncer « validé par experts » sans véritable revue traçable.
