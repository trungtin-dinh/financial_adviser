# Audit UX et architecture — espace de travail, fiches de scénario et personnes à charge

**État : candidate v0.10.0.** Revue de la structure de navigation, de l'ergonomie des cartes, du cycle de vie du foyer et des parcours PC/mobile. Une inspection heuristique n'est pas une étude auprès de vrais participants.

## Constats et corrections

| Constat | Impact | Correction |
| --- | --- | --- |
| La barre latérale était pratiquement vide, hormis la navigation et une mention de confidentialité | Repères insuffisants, écran principal encombré par le choix de langue | La langue est transférée en barre latérale, avec résumé du scénario (pays/devise/horizon, nombres d'enfants/adultes/proches et d'événements) et statut du dernier calcul ; ne pas dupliquer les formulaires |
| Ajouter un élément l'ouvrait immédiatement | Multiplication de formulaires longs | Nouvelle carte repliée par défaut, résumé lisible, flèche explicite |
| La suppression était cachée à l'intérieur du volet | Risque de ne pas découvrir l'action | Croix distincte dans l'en-tête, visible en permanence et accessible au clavier |
| L'intitulé « enfants et personnes à charge » ne couvrait que les enfants | Modèle incomplet | Ajout de personnes à charge autres que les enfants : parent âgé, adulte dépendant, partenaire ou autre proche, avec flux mensuels et période déclarés |
| Deux gros éditeurs foyer/événements étaient empilés même sur grand écran | Longue page et perte de repères | Deux colonnes de largeur équivalente et responsive, séparées du panneau de paramètres essentiels |
| README en anglais, redondant, rempli d'historique et badge DeepWiki cassé | Information difficile à lire, confusion présentation/changelog | README entièrement refondu en français, liens stables vers Streamlit, docs et DeepWiki (sans image de badge cassée) |
| Licence indéfinie | Ambiguïté sur les droits de réutilisation | Licence propriétaire « tous droits réservés » avec autorisation limitée d'évaluation personnelle et interdiction de redistribution |

## Références et inspirations

- **Notion** — barre latérale pour les pages et informations de contexte, panneau principal dédié à la tâche : https://www.notion.com/help/navigate-with-the-sidebar
- **Linear** — hiérarchie visuelle calme ; navigation secondaire atténuée, surface de travail prioritaire : https://linear.app/now/behind-the-latest-design-refresh
- **Figma** — séparation navigation/espace de travail, possibilité de réduire les panneaux : https://help.figma.com/hc/en-us/articles/360039831974-Explore-the-navigation-bar-and-left-sidebar
- **Streamlit** — st.sidebar pour les contrôles persistants, st.columns pour les mises en page adaptatives : https://docs.streamlit.io/develop/concepts/design/layouts-and-containers
- **YNAB** — budgets catégorisés, suivi d'objectifs, rapports patrimoniaux comme dimensions distinctes : https://www.ynab.com/features
- **BCE HFCS** — patrimoine, transferts, dettes, revenus des ménages et transferts familiaux : https://www.ecb.europa.eu/stats/ecb_surveys/hfcs/html/index.en.html

Ces applications servent de références de **structure et de comportement**, pas de preuve d'une étude comparative des notes utilisateurs.

## Modélisation des autres personnes à charge

Un proche aidé n'est pas forcément un enfant et n'est pas nécessairement un adulte du foyer ayant un salaire. Le modèle `DependentBudget` contient : nom, lien familial, premier mois, durée, soutien financier régulier, dépenses d'accompagnement et indication de leur inclusion éventuelle dans les dépenses actuelles. Les coûts s'ajustent selon la croissance des dépenses du scénario. Si le coût est déjà dans le budget initial, seul le changement au cours du temps est comptabilisé.

La présence d'un membre de la famille ne permet **pas** d'inférer un handicap, une maladie, une prestation, ni des probabilités. Le modèle ne calcule pas automatiquement la fiscalité des aidants ni les droits français/vietnamiens. Éviter le double comptage lorsqu'un adulte du foyer et un proche aidé sont une seule et même personne.

## Tests d'acceptation à exécuter

1. Nouveau scénario FR/EN/VI sans résultats visibles ; barre latérale compréhensible et langue modifiable.
2. Ajouter enfant, adulte, événement et autre proche : cartes **repliées** avec flèche et croix visibles, et suppression sans ouverture.
3. Ouvrir une carte, modifier ses montants, la replier : scénario et calcul restent cohérents.
4. Coût de soutien d'un proche : début/fin inclusifs mensuels, coût supplémentaire puis zéro, ou réduction correcte après fin lorsque déjà dans le budget.
5. Export/import JSON v0.9 accepté, avec `dependents=()` implicite ; versions futures acceptent des proches à charge.
6. Largeur PC : foyer et événements voisins ; affichage mobile sans défilement horizontal de page.
7. CI Python et navigateur Chromium local puis contrôle du **site public** après push.
8. GitHub README français et lien DeepWiki sans ressource graphique cassée ; licence visible et lisible.

Les tests automatisés ne remplacent ni audit juridique de la licence, ni entretiens UX, ni vérification des hypothèses par un économiste ou un spécialiste des politiques sociales.

## Correction issue de l'inspection des captures

La première capture mobile montrait le bouton ✕ **sur une deuxième ligne**, à cause de l'empilement automatique de `st.columns`. La version récente de Streamlit (>= 1.62) fournit `wrap=False`, qui permet de conserver la flèche/résumé et la suppression sur la même ligne avec défilement local si nécessaire. Une répartition [8,2] laisse une largeur minimale utile pour la croix sur PC et mobile. Le test navigateur compare les positions verticales du bouton et du titre de carte, et vérifie la largeur du bouton pour éviter les icônes tronquées.
