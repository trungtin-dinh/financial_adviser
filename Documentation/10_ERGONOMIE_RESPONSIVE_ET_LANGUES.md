# Ergonomie responsive et internationalisation — v0.3.0

**Statut : mise en œuvre + tests automatiques.** Les tests automatisés et captures d'écran ne remplacent pas une étude avec des utilisateurs réels, ni les essais sur des appareils physiques.

## Problèmes identifiés dans la version 0.2

- Textes anglais et français mélangés à des libellés vietnamien ou français, dans les menus, les messages, les graphiques et le tableau d'événements.
- Saisie des événements de vie dans un tableau à sept colonnes difficilement utilisable sur un petit écran.
- Paramètres de modélisation et texte de documentation parfois très visibles dans le parcours utilisateur principal.
- Gestion imparfaite de la sélection de la langue pour les pages du menu latéral.

## Décisions UI

1. **Une seule langue active** pour les contrôles, graphiques, messages, tableaux de résultat, aides et navigation : français (`fr`), anglais (`en`) ou vietnamien (`vi`). Les noms propres, sigles techniques, unités, symboles monétaires, dates ISO et clés JSON/CSV restent invariants. Les documents Markdown complets restent en français à ce stade ; en anglais et vietnamien, l'application présente un résumé traduit et un lien vers ces documents externes plutôt que de mélanger les textes dans la page.
2. **Traductions centralisées** dans `financial_adviser/ui_i18n.py`, avec vérification de toutes les clés dans les trois langues. Aucune traduction de secours silencieuse vers une autre langue n'est autorisée.
3. **Saisie par fiches** : chaque événement possède type, description, année/mois de début, durée, dépense mensuelle supplémentaire, variation mensuelle du revenu, dépense initiale. Ajouter/supprimer des fiches est indépendant du calcul financier. Les colonnes adaptatives se replient sur les petits écrans.
4. **Dates lisibles** : année et mois calendaires sont présentés à la place de l'indice de mois depuis le début de la projection. Le moteur conserve ses indices mensuels internes, afin de préserver le format de scénario.
5. **Divulgation progressive** : les champs requis restent visibles, les détails techniques et les données ponctuelles avancées sont repliables. Les pages « Guide » et « Sources » restent indépendantes du formulaire de simulation.
6. **Simulation explicite** : modifier un événement ne recalcule pas silencieusement la simulation ; le bouton de projection valide les changements. Les éventuelles sorties reflètent le dernier plan exécuté.
7. **Compatibilité des scénarios** : les catégories d'événements importées depuis la v0.2 en anglais sont reconnues ; les nouveaux scénarios stockent des codes de catégorie indépendants de la langue affichée.

## Plan de validation

Le workflow GitHub Actions exécute :

- Tests unitaires du moteur et de l'exactitude/complétude des traductions.
- Tests de chargement Streamlit pour les trois langues (`streamlit.testing.v1.AppTest`).
- Navigateur Chromium sans interface graphique (`Playwright`) sur les dimensions **1440×900 (PC)**, **834×1112 (tablette)**, **390×844 (mobile)** et **360×800 (petit mobile)**.
- Vérification de l'absence de débordement horizontal au niveau de la page, visibilité de la rubrique Événements, clic sur « Ajouter un événement » et apparition de la première fiche.
- Captures d'écran du formulaire principal et de l'édition d'événement, publiées comme artefact GitHub Actions.

Ce protocole vérifie l'affichage en navigateur et les interactions de base ; il ne peut certifier une compatibilité parfaite avec tous les téléphones, claviers virtuels ou lecteurs d'écran. Les interactions complexes, la qualité des traductions et la pertinence des valeurs nécessitent des retours humains.

## Reste à faire

- Faire tester l'app à de vrais profils débutants, familles, indépendants et investisseurs, ainsi qu'à des personnes francophones, anglophones et vietnamophones ; enregistrer leurs difficultés et la fréquence des erreurs.
- Traduire l'intégralité des neuf documents techniques, après relecture terminologique ; pour l'instant le texte original français n'est pas affiché dans les pages anglaise ou vietnamienne.
- Contrôler le formulaire sur des appareils réels avec VoiceOver/TalkBack, zoom d'accessibilité, clavier virtuel, connexion lente et orientation paysage.
- Ajouter des simulations d'événements composites et de leurs distributions après validation du modèle, et non simplement augmenter le nombre de paramètres.