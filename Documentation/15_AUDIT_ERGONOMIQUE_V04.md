# Audit heuristique priorisé — Financial Adviser v0.4

**30 octobre 2026.** Périmètre : structure et libellés présents dans le code GitHub, documentation et captures Playwright du workflow précédent. **Pas** un audit navigateur interactif de l'URL publique, ni une certification RGAA/WCAG, ni un panel de vrais utilisateurs.

### Échelle de gravité
**P0** : risque majeur de mauvaise décision, perte de saisie ou mauvais résultat; **P1** : tâche importante difficile à réaliser; **P2** : gêne récurrente; **P3** : finition cosmétique. Statuts : « constaté dans le code », « à vérifier en usage », « projeté ».

| Priorité | Observation | Décision de conception | Critère de validation |
| --- | --- | --- | --- |
| P0 | Un champ de résultat peut afficher la dernière simulation même si l'utilisateur a modifié les données non soumises | Afficher « résultats basés sur la dernière simulation », puis marquer périmé lorsque l'état courant diverge; bouton de recalcul visible | Aucun résultat présenté comme actuel si un paramètre utilisé a changé |
| P0 | Les hypothèses financières peuvent être prises pour des prévisions officielles | Distinguer « saisie personnelle », « exemple », « observation historique » et « hypothèse future », avec provenance par champ | Tous les paramètres proposés ont une étiquette d'origine; aucune valeur statistique incompatible appliquée |
| P1 | Formulaire de saisie de l'ensemble du plan sur la même page | Offrir un parcours guidé facultatif (profil → flux → événements → résultats) et accès direct expert | Première simulation réalisable sans ouvrir les sections avancées; aucun champ essentiel caché |
| P1 | Sur mobile, la navigation/les réglages dans la barre latérale peuvent être difficiles à découvrir | Mettre le pays, la langue et l'action primaire à portée de l'écran initial; conserver les réglages experts dans la barre latérale | Tests utilisateurs sur 360 px, rotation et clavier virtuel |
| P1 | Une fiche événement implique plusieurs champs monétaires et temporels | Associer le coût ponctuel vs mensuel à un exemple, afficher la durée exacte et un aperçu du coût cumulé | Erreurs de signe et de durée détectées avant calcul |
| P1 | Les messages de validation génériques sont peu actionnables | Messages contextualisés au champ concerné et conservation des autres saisies | L'utilisateur retrouve et corrige la valeur sans réinitialiser |
| P1 | Pas de garantie que l'import/export conserve les paramètres s'ils changent au fil des versions | Sauvegarder version de scénario, règles, hypothèses et dernier calcul | Import d'une ancienne version non silencieux, diagnostics intelligibles |
| P2 | Graphiques parfois nombreux avant les valeurs concrètes | Commencer par 3 résultats utiles avec « valeur nominale/réelle »; développer les graphiques secondaires | L'utilisateur peut expliquer le résultat principal et la différence nominal/réel |
| P2 | Gestion de langue : certains boutons natifs Streamlit demeurent en anglais | Documenter la limite, vérifier contraste et compréhension, éviter une traduction partielle de libellé | Tous les textes contrôlés par notre code respectent FR/EN/VI; exceptions isolées |
| P2 | Sur les références statistiques, la source et la population demandent une lecture attentive | Ajouter un libellé « observation uniquement », un résumé de comparabilité et une source immédiatement visible | Aucune confusion salaire / niveau de vie / revenu par personne |
| P2 | Défauts d'accessibilité non mesurés | Ajouter contrôles 320 px et clavier, puis tests manuels lecteurs d'écran | Tests documentés, anomalies ouvertes plutôt que fausse conformité |

### Tableau de bord qualité proposé

- **Compréhension :** part des participants qui identifient sans aide la différence entre valeur hypothétique et statistique.
- **Exécution :** succès autonome pour projection, événement, simulation inverse, export.
- **Erreurs sensibles :** taux d'erreurs d'unité/signe/date, persistance de saisie et risque de double comptage.
- **Accessibilité :** anomalies critiques bloquantes, comportement à 320 CSS px, clavier et lecteur d'écran.
- **Performance :** temps du premier calcul, temps de recalcul, fréquence des erreurs réseau/source.
- **Transparence :** part des résultats accompagnés de leur date/scénario/version/source.

Ces indicateurs ne sont pas encore mesurés avec un échantillon réel. Un objectif chiffré ne doit être adopté qu'après un premier diagnostic des tâches.

### Dépendances et ordre de correction

1. **Fiabilité des états et résultats**, validation des valeurs et des événements.
2. **Découverte sur mobile**, compréhension des champs et parcours simple.
3. **Visualisation explicable**, sources, provenance et comparaisons.
4. **Accessibilité**, revue plurilingue par locuteurs natifs et tests utilisateurs.
5. Optimisation visuelle seulement après correction des blocages de tâche.

L'audit est fondé sur les principes documentés dans [14_REFERENTIEL_ERGONOMIE.md](14_REFERENTIEL_ERGONOMIE.md). Les constats non reproduits dans le navigateur doivent rester explicitement des hypothèses de test.
