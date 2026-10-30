# Plan global d'exécution — Financial Adviser

**Décision : 30 octobre 2026.** Cette feuille de route sert de plan directeur unique plutôt que de proposer des fonctions isolées à chaque échange. Une phase peut rester inachevée lorsqu'elle dépend de validations officielles, d'utilisateurs réels ou d'une capacité d'hébergement.

## Vision / principes non négociables

- Une application de **planification financière pédagogique**, pas un conseiller en investissement réglementé.
- Modes débutant/avancé : les paramètres **personnels essentiels** sont demandés ; les autres sont facultatifs, modifiables et associés à leur origine (illustration/statistique/hypothèse de l'utilisateur).
- Calcul mensuel déterministe et simulations probabilistes explicables : nominal/réel, cashflow, actifs/dettes, événements datés, scénarios inverses.
- France et Vietnam traités par composants juridiques et données séparés, extension internationale possible sans réécrire le moteur.
- Pas de données bancaires/identifiants requis ; aucune valeur personnelle écrasée silencieusement ; pas de « moyenne nationale » déguisée en conseil personnel.
- Interface PC d'abord, lisible sur tablette/mobile, sélection FR/EN/VI cohérente pour l'interface ; provenance et limitations accessibles sans encombrer la saisie.
- Séparer **faits officiels datés**, **hypothèses projetées**, **formules et règles validées**, **résultats et paramètres sauvegardés**.

## Plan ordonné et portes de validation

| Phase | Livrable principal | Dépendances / acceptation | État au 30/10/2026 |
|---|---|---|---|
| 0. Socle | Moteur Python, données de scénarios versionnées, UI Streamlit, CI, docs | Tests déterministes, entrée/sortie claire, reproductibilité | Livré v0.1–0.2 |
| 1. UX fiable | Événements de vie, simulation inverse, interface multilingue et responsive, tests navigateur | Aucun mélange des libellés métier FR/EN/VI, aucun débordement horizontal aux formats cibles | Livré v0.3 ; tests sur appareils physiques et utilisateurs réels encore attendus |
| 2. Références sourcées | Catalogue national, exploration par pays, métadonnées explicites, option de mise à jour des observations, aperçu/consentement à toute application | Pas de confusion médiane/moyenne, salarié/personne/ménage, brut/net, passé/futur ; erreurs réseau sans impact financier | **v0.4 : première implémentation, périmètre limité explicitement** |
| 3. Comptes / bilan complet | Actifs distincts (liquidités, investissements, immobilier), passifs, frais, flux de trésorerie, valeurs réelles, export des hypothèses | Équation bilan et transferts sans double comptage ; tests cas limites | Non implémenté |
| 4. Moteurs nationaux | Régimes fiscaux historiques / applicables FR et VN, comptes d'épargne, retraite, cotisations, crédit, convention FR-VN | Sources officielles à date d'effet, tests d'exemples gouvernementaux, revues juridiques | Non implémenté ; catalogue documentaire seulement |
| 5. Risques | Famille, enfants, aidants, incapacité, santé, perte d'emploi, événements corrélés, scénarios stochastiques | Éviter les probabilités de santé inventées ; calibrage et tests de sensibilité | Coûts déterministes disponibles, probabilités non implémentées |
| 6. Optimisation | Objectifs multiples, leviers combinés, contraintes de trésorerie, fiscalité, allocation et compromis | Comparaison explicable, contraintes vérifiées, limites affichées | Goal seek à un levier disponible ; optimisation multi-leviers non implémentée |
| 7. Données et maintenance | Registre versionné, import officiel, mise à jour avec contrôle, cache, différentiel entre versions, mode hors ligne | Aucune loi activée sans validation, sauvegarde de sources/version lors d'export, erreurs réseau résilientes | Observations ponctuelles World Bank + catalogue versionné ; législation dynamique non implémentée |
| 8. Produit public | Documentation utilisateur complète FR/EN/VI, accessibilité lecteurs d'écran, vrais tests utilisateurs, confidentialité, licence, déploiement | Validation sur appareils physiques et profils variés, revue spécialiste fiscal/financier, hébergement opérationnel | GitHub CI ; déploiement Streamlit non confirmé |

## Conception des données

Entrée scénario > validation des hypothèses et unités > moteurs financiers Python > application optionnelle des règles nationales approuvées > simulations multi-scénarios > représentation + provenance des résultats. Les observations publiques sont une couche séparée : elles n'activent jamais spontanément un champ du plan. Un instantané de la règle et des données utilisées devra accompagner chaque export à terme.

## Décisions de priorisation

1. Traiter intégralement chaque incrément : code, documentation, tests unitaires, tests d'interface, puis push (avec rollback possible).
2. Les statistiques non comparables restent **consultatives** ; ne pas forcer un préremplissage d'un revenu familial à partir d'une moyenne par personne.
3. Une inflation **historique** de la Banque mondiale peut devenir une hypothèse future uniquement après consentement explicite, avec source et année visibles.
4. Les fonctions fiscales ne doivent pas être présentées comme disponibles tant que leur code et leur validation n'existent pas.
5. Des sessions d'utilisateurs réels ne peuvent pas être déclarées réalisées sur la seule base d'audits par profils fictifs ou de tests navigateur automatisés.

## Critères de clôture généraux

Un livrable n'est marqué comme terminé qu'après : liens/documentation et limites mises à jour, tests du moteur + UI verts, contrôles de cohérence des traductions, tests desktop/mobile, vérification d'absence d'écrasement involontaire, commit GitHub identifié. Les étapes dépendantes d'un compte Streamlit, d'une revue de juriste ou de participants humains demeurent signalées comme **non réalisées**.
