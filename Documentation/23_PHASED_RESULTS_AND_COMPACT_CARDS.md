# v0.9.0 — Audit ergonomique : saisie initiale et fiches repliables

## Motivations et observations

L'interface v0.8.2 montrait le tableau de bord avant toute projection, y compris sans résultats, et allongeait les pages avec les paramètres complets de chaque enfant/adulte/événement. La capture utilisateur montrait en outre des champs d'âge et de date décalés parce que des intitulés de longueurs différentes se répartissaient dans deux colonnes verticales.

## Changements implémentés

**1. Saisie d'abord.** Au démarrage, seul le plan est construit. Quand l'utilisateur déclenche une première projection réussie, Streamlit recalcule la page et active le tableau de bord : entrées à gauche, résultats et comparaisons à droite sur PC ; blocs dans l'ordre vertical sur petit écran. Après modification d'une hypothèse, les résultats antérieurs sont explicitement marqués comme périmés jusqu'à un nouveau calcul.

**2. Cartes compactes.** Un enfant, un adulte ou un événement possède un résumé de sa date, son âge ou ses hypothèses, ainsi qu'un expander à flèche. Le nouvel élément s'ouvre pour saisie immédiate ; les autres sont repliés par défaut au premier affichage. Réduire une fiche ne supprime ni ses données ni son effet financier. L'action Supprimer reste distincte, dans la fiche dépliée.

**3. Réalignement des champs.** L'âge initial et l'âge de fin sont sur une ligne commune; année et mois de début sur la suivante. Les champs financiers des adultes ont des lignes symétriques et ceux des événements ne comportent plus trois colonnes étroites. Les explications détaillées sont disponibles via l'aide des champs au lieu de labels très longs.

**4. Persistance du dépliage.** L'API Streamlit 1.54 n'a pas de paramètre key pour st.expander. Les titres de ces contrôles demeurent donc stables pendant les modifications, tandis que le résumé dynamique est placé à l'extérieur. Les contrôles peuvent être ouverts/fermés par l'utilisateur sans perdre les champs de simulation.

## Contrôles à effectuer après publication

- AppTest FR/EN/VI : aucune section Résultats avant le calcul, mais tous les paramètres utiles accessibles.
- AppTest FR/EN/VI : cartes enfant, adulte et événement présentes et avec leurs champs modifiables.
- Chromium local PC (1440×900) et mobile/tablette (834/390/360 px) : pas de débordement global, cartes à flèche ouvrables et repliables, positions des deux champs d'âge alignées sur PC.
- Après un calcul réel : présence des résultats et disposition PC côte à côte, ou mobile verticale.
- Chromium sur financial-adviser.streamlit.app : numéro de version identique au commit, exemple confirmé, simulation puis résultats.
- Aucun test automatisé ne remplace une étude auprès d'utilisateurs réels ni une revue financière indépendante.

## Références

- [Streamlit 1.54, st.expander](https://docs.streamlit.io/1.54.0/develop/api-reference/layout/st.expander) : corps calculé même replié ; signature sans key.
- [Streamlit, Layouts and containers](https://docs.streamlit.io/develop/concepts/design/layouts-and-containers) : disposition responsive, transparence des sections secondaires.
- [Nielsen Norman Group, Ten usability heuristics](https://www.nngroup.com/articles/ten-usability-heuristics/) : visibilité, cohérence, contrôle et prévention des erreurs.
- [W3C WCAG 2.2, Reflow](https://www.w3.org/TR/WCAG22/#reflow) : éviter les débordements non nécessaires.
