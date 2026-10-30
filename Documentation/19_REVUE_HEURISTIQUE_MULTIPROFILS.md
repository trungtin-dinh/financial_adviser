# Audit après refonte v0.5 — critères d'ergonomie et validation honnête
**30 octobre 2026.** Cette évaluation est une inspection des choix UX et du code, complétée par des scénarios synthétiques; ce n'est **pas** une étude auprès de vrais participants ni une revue indépendante.

## Audits ciblés

| Problème de la v0.4 | Risque UX | Correction de la v0.5 | Vérification / limites |
|---|---|---|---|
| Résultats dans un onglet séparé des données | clics aller-retour pour relier une hypothèse au résultat | parcours vertical unique : entrées → résultats → objectif inverse → comparaison | vérifier sur vrai mobile longueur/scroll et tâches |
| Contrôles principaux de pays/langue dans la barre latérale | difficile à découvrir sur mobile | sélecteurs visibles en haut de la page | contrôler reflow et clavier virtuel |
| Mode avancé et hypothèses dans accordéons fermés | paramètres importants « cachés » | tous les champs actuels toujours affichés, en sections titrées | tester que la longueur est tolérable, simplifier au besoin |
| Fiches d'événements sous un accordéon | l'utilisateur peut ignorer la fonction | fiches visibles, bouton d'ajout explicite | vérifier ajout, édition, suppression, validation |
| Coûts ponctuels, variations de revenu et dépenses récurrentes | ambiguïté signe, cumul et durée | résumé net cumulatif en devise de la fiche, hors intérêts/inflation | contrôle analytique à taux nul |
| Modification de données sans actualisation des résultats | décision prise sur des courbes périmées | avertissement visible « résultats de la dernière simulation »; bloque goal seek/comparaison sur anciennes entrées | à confronter à comportement réel sur navigateur |
| Export du scénario après édition | confusion sauvegarde vs brouillon | libellé « dernier scénario calculé »; désactivé avant premier calcul | à tester après saisies non calculées |
| Hypothèses Monte Carlo affichées uniquement après activation | réglages invisibles | chemins/graine visibles, désactivés si Monte Carlo désactivé | vérifier clarté sur mobile |
| Bouton contextuel vers données statistiques causant un changement de page | aller-retour pour lire une aide | infobulle/popover à côté des données essentielles, page dédiée facultative | vérifier focus/accessibilité |
| Graphiques de nominal et réel | mauvaise interprétation possible | libellés localisés et avertissement de résultats périmés | manque encore une explication visuelle simple et contexte de calcul |

## Vérification de cohérence

- **Revue par profil synthétique** : étudiant, parent monoparental, chômage, maladie, proche aidant, achat important, logement/déménagement, foyer France/Vietnam; les calculs à rendement zéro sont exprimés en tests dans `tests/test_personas_synthetiques.py`.
- **Risque social et finance** : [87 facteurs recensés](17_FACTEURS_FINANCIERS_SOCIAUX_ET_RISQUES.md), dont une partie seulement entre dans le moteur. Une catégorie recensée n'est **pas** une variable calibrée.
- **Langues** : la traduction métier est centralisée FR/EN/VI. Les documents sources restent majoritairement en français; contrôles natifs Streamlit éventuellement en anglais.
- **Portée** : app « éducative » uniquement; pas de calcul fiscal FR/VN complet, d'assurances obligatoires, de retraite détaillée ni de probabilités médicales.

## Qualité logicielle et état des preuves

Les workflows automatiques GitHub Actions ont été désactivés à la demande du propriétaire pour éviter des e-mails de notification. Les workflows `Python and UX checks` et `Public Streamlit browser smoke` restent **manuels**. Les tests de cette version ne doivent pas être annoncés comme réussis tant qu'ils ne sont pas réellement exécutés. La prépublication v0.5 est une **candidate**, et non une « version finale validée ».

Les essais sur appareils réels, la revue accessibilité avec lecteur d'écran, les tests auprès de profils socio-économiques réels et les revues fiscaliste/actuaire/développeur externe **n'ont pas été effectués**. Le protocole et les critères sont documentés dans [18_PROTOCOL_EVALUATIONS_HUMAINES.md](18_PROTOCOL_EVALUATIONS_HUMAINES.md).

## Critères de sortie vers une version finale

1. Aucun problème de justesse/calcul ou de perte de saisie critique connu.
2. Tests unitaires et navigateur (local et hébergé) effectivement passés **sur le même commit**.
3. Tâches critiques testées sur mobile et PC avec des participants représentatifs, erreurs recensées puis corrigées.
4. Revue du moteur statistique par spécialiste et revue fiscale par juridiction **avant** toute activation de taxes ou prestations.
5. Documentation FR/EN/VI réellement intelligible et déclarations d'accessibilité fondées sur preuves.

**Le statut « version finale » ne peut pas être revendiqué aujourd'hui.**

## Mise à jour v0.6 — changements vérifiables dans le code

La v0.6 ajoute une proposition d'événement en six modèles éditables et des comparaisons de stress sans écrasement du plan. Le changement de pays et l'exemple demandent confirmation ; la projection se recalcule sans déplacer l'utilisateur vers le haut. Les curseurs des horizons et du choc de rendement sont remplacés par des valeurs numériques saisissables au clavier. Voir [20_REDESIGN_V06.md](20_REDESIGN_V06.md). Les essais utilisateurs réels restent à réaliser ; aucune certification ergonomique n'est revendiquée.
