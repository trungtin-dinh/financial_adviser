# Cahier des charges — v0.1 et vision à long terme

**Date** : 2026-10-29 — **Produit** : `financial_adviser` — **Statut** : exigences initiales et critères vérifiables.

## 1. Vision

Application Streamlit utilisable prioritairement sur ordinateur, avec mise en page adaptable tablette/mobile. Vise les projections financières personnelles transparentes et paramétrables, pour des utilisateurs débutants et experts. France et Vietnam sont les deux premiers pays de référence. D'autres pays doivent être ajoutables sans modifier le moteur transversal.

**À distinguer** : simulation exploratoire, prévision statistique conditionnelle, conseil financier personnalisé, calcul réglementaire opposable. La première version ne couvre que la simulation exploratoire.

## 2. Parcours

**Débutant** : choisit le pays et sa devise; renseigne revenu NET, dépenses, trésorerie, investissements, versements et horizon; lance; lit les courbes et indicateurs; enregistre son scénario JSON.

**Avancé** : modifie les taux de croissance, l'inflation, la volatilité, les dettes, événements ponctuels, la graine et le nombre de trajectoires; compare des hypothèses; exporte les séries mensuelles.

**Expert (futur)** : définit plusieurs classes d'actifs, une matrice de corrélation et des règles d'allocation; choisit les enveloppes fiscales, conventions de change et régimes de retraite; retrace les versions des règles.

## 3. Exigences fonctionnelles

| ID | Priorité | Exigence | v0.1 |
|---|---|---|---|
| F01 | P0 | Saisie FR/EUR ou VN/VND, avec exemple identifié comme fictif | Oui |
| F02 | P0 | Projection mensuelle déterministe et patrimoine net nominal/réel | Oui |
| F03 | P0 | Flux salaires/dépenses/versements sans double comptage | Oui |
| F04 | P0 | Saisie de rendements et inflation supposés | Oui |
| F05 | P0 | Export/import JSON versionné, résultats CSV | Oui |
| F06 | P0 | Visualisation interactive et comparaison de scénarios | Oui (sensibilité de rendement) |
| F07 | P1 | Événements datés et emprunt à annuités constantes | Oui (avancé) |
| F08 | P1 | Monte Carlo reproductible et quantiles | Oui (modèle pédagogique simplifié) |
| F09 | P1 | Source macro officielle et actualisation volontaire | Oui (inflation historique Banque mondiale) |
| F10 | P0 | Prévenir d'une trésorerie négative | Oui |
| F11 | P1 | Documentation et liens de références FR/VN | Oui |
| F12 | P1 | Traductions FR/EN/VI complètes et revues | Partiel (terminologie principale) |
| F13 | P1 | Fiscalité France et Vietnam correcte selon régime, année, situation | Non |
| F14 | P2 | Actifs et dettes multiples, immobilier, retraite, multi-devises | Non |
| F15 | P2 | Scrutation/vérification automatique des textes et versionnement juridique | Non |
| F16 | P2 | Export PDF/rapport, accessibilité mobile auditée | Non |

## 4. Exigences non fonctionnelles

- Calculs indépendants de Streamlit, testables sans navigateur.
- Reproductibilité : même `Plan` + même graine = mêmes quantiles.
- Pas de connexion bancaire, secret ou données utilisateur dans Git.
- Pas de collecte ni stockage persistant par l'application. Les instances hébergées traitent néanmoins les entrées côté serveur.
- Erreurs d'entrée explicites; unités visibles; avertissements de limitations affichés avant les résultats.
- Cache économique à durée limitée, dégradation sans réseau, interdiction d'appliquer silencieusement de nouvelles hypothèses.
- Conserver des exports JSON versionnés et rejeter des schémas incompatibles.

## 5. Critères d'acceptation v0.1

1. À flux et taux nuls, les capitaux restent constants et le patrimoine = trésorerie + investissements − dette.
2. Un virement de 100 vers investissements réduit la trésorerie de 100 et n'augmente pas artificiellement le patrimoine de 100.
3. À taux d'intérêt nul, un crédit de 1 200 sur un an se rembourse avec 12 échéances de 100.
4. Inflation annuelle effective de 12 % sur un capital de 1 000 conservé un an → pouvoir d'achat final `1000/1.12`.
5. Un choc ponctuel intervient au mois demandé; plusieurs événements au même mois s'additionnent.
6. Monte Carlo à volatilité zéro coïncide avec le parcours déterministe (pour les mêmes hypothèses).
7. Un scénario JSON exporté et réimporté donne les mêmes entrées.
8. Échec d'accès à l'API : aucune valeur externe ne remplace un taux sans consentement.
9. Les textes légaux référencés ne sont jamais annoncés comme déjà calculés par l'application.

## 6. Non-objectifs initiaux

Pas de courtage, pas de recommandations de titres, pas de collecte bancaire, pas d'optimisation réglementaire automatisée, pas de conseil fiscal transfrontalier, pas de prévision de cours boursiers, pas de garantie de résultat.
