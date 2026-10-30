# Audit ciblé de Financial Adviser v0.19.1 — exactitude, UX et priorités

**Date : 30 octobre 2026.** **Révision auditée :** `14af64822044284e622adb44fa9fc53899b2b271` (avant les petites corrections de cet audit).

## Périmètre et degré de preuve

Relecture du dépôt courant via GitHub : arbre des fichiers, modèles financiers, nouvelles analyses, interfaces Streamlit, tests, dépendances, documentation et dernières exécutions GitHub Actions. Le clonage et l'exécution locale n'étaient pas possibles dans cet environnement (résolution réseau indisponible). L'ouverture de l'application hébergée n'a pas permis d'obtenir un rendu interactif. **Il ne s'agit donc pas d'un audit exécuté complet ni d'une validation du déploiement.**

**Évaluation :** l'application possède déjà des fonctionnalités avancées (projection mensuelle, événements de vie, profils familiaux, scénarios comparables, Monte Carlo simplifié, calcul inverse, analyse de sensibilité, stress tests, diagnostics de liquidité et calendrier de flux). Les priorités doivent porter sur la **cohérence, la vérifiabilité et la compréhension** plutôt que sur l'ajout immédiat de fonctionnalités complexes.

## Constats et décisions prioritaires

| Priorité | Statut de preuve | Constat | Décision recommandée / critère de vérification |
|---|---|---|---|
| **P0** | **Défaut de contrôle identifié et corrigé** | Dans `pages/planning.py`, la durée minimale du calcul inverse n'incluait pas les périodes de soutien des personnes à charge, alors que les comparaisons les prennent en compte. Un horizon trop court pouvait être proposé puis rejeté par la validation. | Utiliser la même fonction de durée minimale dans les deux parcours ; régression ajoutée. Contrôler en navigateur FR/EN/VI une prise en charge commençant après plusieurs années. |
| **P0** | **Vérification externe incomplète** | Plusieurs workflows récents étaient en attente, annulés ou non terminés ; aucun succès de la dernière révision ne pouvait être certifié. | Exiger une exécution verte de `Python and UX checks` sur la dernière révision, puis du contrôle navigateur public, avant toute affirmation de stabilité. Vérifier les captures desktop/mobile et les trois langues. |
| **P1** | **Risque technique observé dans le code, impact à reproduire** | Le mécanisme de rechargement à chaud de `app.py` énumère des modules fixes ; des modules récents (`cashflow`, plusieurs interfaces `planning_*`) ne sont pas présents. Des sessions Streamlit anciennes peuvent conserver des imports périmés. | Tester le déploiement d'une nouvelle version en gardant un onglet ouvert ; privilégier une stratégie de rechargement centralisée et testable, ou une réinitialisation claire des sessions. |
| **P1** | **Limite explicite du modèle** | Les rendements Monte Carlo varient, mais les revenus, dépenses, dettes et flux de trésorerie restent déterministes. La proportion de trajectoires avec cash négatif ne reflète pas un risque de liquidité calibré. | Ne pas afficher un score de sécurité fondé sur cette proportion. Préférer `part des trajectoires simulées` et réserver toute probabilité « réelle » à un modèle validé. |
| **P1** | **Fonction existante, périmètre limité** | Le calendrier mensuel recompose des flux calculés, mais ne permet pas encore de saisir des récurrences annuelles, trimestrielles ou des échéances variables. | Introduire un seul objet d'échéance datée et périodique avec borne de fin, sans modifier rétroactivement les anciens imports JSON. Tests : mois de prélèvement, changement d'année, devise VND, absence de double comptage. |
| **P1** | **Contrainte scientifique** | La trésorerie peut devenir négative sans mécanisme de financement ; la récurrence du modèle continue ensuite à appliquer le taux de cash à ce solde négatif. | Rendre la convention visible dans les résultats et évaluer un éventuel mode « scénario invalide à partir du premier déficit », distinct du financement automatique. Ne pas inventer un taux de découvert. |
| **P2** | **Déficit de périmètre connu** | L'emprunt ne crée aucun actif immobilier et le patrimoine n'est pas ventilé en classes liquide / illiquide détaillées. | Concevoir un bilan explicite actif/passif, avec valeur immobilière saisie, frais et dette associée, avant d'ajouter des ratios patrimoniaux globaux. |
| **P2** | **Fonction absente** | Le cycle de vie actuel permet une retraite hypothétique mais pas une vraie phase de décumulation contrôlée du capital. | Ajouter une phase de retraits explicite uniquement après définition du financement, de la priorité entre supports, de la réserve et des frais. Tester l'épuisement du capital et les séquences défavorables. |
| **P2** | **Fonction absente** | Les objectifs restent essentiellement centrés sur une cible patrimoniale nominale. | Étudier plusieurs objectifs datés avec enveloppes virtuelles sans création de patrimoine ni double réservation de la même trésorerie. |
| **P2** | **Données et règles** | Les lois fiscales, pensions et prestations françaises/vietnamiennes ne sont pas calculées exhaustivement. | Séparer sources officielles datées, hypothèses de l'utilisateur, règles versionnées et catégories non couvertes avant toute intégration d'une micro-simulation nationale. |
| **P2** | **UX à évaluer** | L'interface dispose d'un grand nombre d'analyses, graphiques et commandes, distribués sur plusieurs panneaux. La complexité peut dépasser le besoin d'un débutant. | Faire une évaluation réelle de 5 tâches courantes sur PC et mobile : premier scénario, interprétation d'un déficit, ajout d'enfant, comparaison, récupération d'une saisie. Mesurer erreurs et temps de réalisation. |
| **P3** | **Recherche exploratoire** | Les approches économiques corrélées, bootstrap historique, GARCH ou optimisation multi-actifs sont étudiées dans la revue précédente, mais non suffisamment calibrées pour une adoption immédiate. | Ne choisir une méthode qu'après sélection d'une question utilisateur, de données pertinentes FR/VN, de paramètres identifiables et d'un protocole de validation. |

## Ce qui existe déjà et qu'il serait inutile de dupliquer

- **Comparaison à horizon commun** : `comparisons.py` et `custom_comparison.py`.
- **Sensibilité un paramètre à la fois** : `sensitivity.py`.
- **Chocs déterministes indépendants** : `scenarios.py`.
- **Réserve de trésorerie et dépense imprévue** : `resilience.py`.
- **Explication synthétique des résultats** : `insights.py`.
- **Calendrier des flux calculés** : `cashflow.py`.
- **Tests des invariants comptables et de navigation** : `tests/test_accounting_invariants.py` et `tests/test_navigation.py`.

Toutes ces fonctions doivent être **confirmées par exécution sur la révision courante** avant d'être qualifiées de stables.

## Modifications réellement effectuées lors de cet audit

1. **Recherche d'objectif :** borne minimale d'horizon harmonisée avec les comparaisons pour préserver les obligations datées des personnes à charge (`pages/planning.py`).
2. **Régression :** scénario de personne à charge longue ajouté à `tests/test_comparisons.py`, avec garde du calcul inverse et contrôle de l'utilisation de la fonction commune dans l'interface.
3. **Documentation :** version affichée dans `Documentation/00_INDEX.md` synchronisée avec la version 0.19.1, en précisant que les documents antérieurs restent historiques.

**La publication de ces modifications ne prouve pas leur réussite en CI.** Les derniers résultats ont besoin d'être vérifiés indépendamment.

## Ordre des prochains incréments

1. **Validation et stabilisation** : terminer CI et navigateur public ; couvrir sessions ouvertes pendant un redéploiement ; réparer les régressions observées.
2. **Clarté des résultats** : distinguer probabilité conditionnelle simulée, déficit réel non financé, cible nominale, et pouvoir d'achat. Garder FR/EN/VI synchronisés.
3. **Échéances récurrentes** : alimentation contrôlée du modèle mensuel avec tests de conservation comptable et rétrocompatibilité des scénarios.
4. **Bilan patrimonial** : vrais postes d'actifs/passifs et distinction liquidités/immobilier.
5. **Retraite et objectifs multiples** : décisions conditionnelles et calendrier cohérent.
6. **Incertitudes économiques avancées** : uniquement lorsque les règles et données de calibration sont vérifiables.

## Références internes

- [Revue sélective des projets externes](25_REVUE_SELECTIVE_FINANCE_ECONOMIE_UX.md).
- [Conventions mathématiques](02_MODELES_MATHEMATIQUES.md).
- [Cycle de vie des ménages](21_CYCLE_VIE_BUDGET_FAMILIAL.md).
- [Calendrier de trésorerie](26_CALENDRIER_TRESORERIE.md).
- [Qualité et limites](06_QUALITE_ET_LIMITES.md).

**Règle de conduite :** toute nouvelle fonction financière doit annoncer son unité, sa convention temporelle, ses paramètres, ses limites et les cas de test correspondants ; elle ne doit pas créer silencieusement de nouveaux avoirs, dettes, flux ou probabilités.
