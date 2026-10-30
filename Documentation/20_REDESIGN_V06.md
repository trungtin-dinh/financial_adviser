# Financial Adviser v0.6 — audit, priorisation et limites

**30 octobre 2026.** Statut : livraison candidate, et non certification finale. Les évaluations humaines et la revue indépendante d'experts ne sont pas encore réalisées.

## Références de conception

- GOV.UK, *Structuring forms* : https://www.gov.uk/service-manual/design/form-structure — chaque champ doit justifier son rôle ; les informations essentielles ne doivent pas être rendues difficiles à trouver.
- GOV.UK, *Designing good questions* : https://www.gov.uk/service-manual/design/designing-good-questions — intitulés explicites, validation tolérante, erreurs réparables, aide courte.
- W3C, WCAG 2.2 : https://www.w3.org/TR/WCAG22/ — contrôles prévisibles, prévention des erreurs, cibles accessibles.
- BCE, *Household Finance and Consumption Survey* : https://www.ecb.europa.eu/stats/ecb_surveys/hfcs/html/index.en.html — bilan, dettes, liquidité, revenus, vulnérabilité aux chocs, composition du foyer.
- CFPB, *Emergency fund* : https://www.consumerfinance.gov/an-essential-guide-to-building-an-emergency-fund/ — distinction entre dépenses imprévues, liquidité disponible et objectifs d'épargne.
- OCDE, *More Effective Social Protection for Stronger Economic Growth* : https://www.oecd.org/en/publications/more-effective-social-protection-for-stronger-economic-growth_3947946a-en.html — catégories de risques sociaux et économiques. Les préoccupations déclarées ne sont **pas** des probabilités individuelles.

## Brainstorming structuré et arbitrages

| Priorité | Problème ou opportunité | Décision v0.6 | Limite |
|---|---|---|---|
| P0 | Changer le pays efface les entrées précédentes | Confirmation explicite, annulation possible | Pas de conversion EUR/VND automatique |
| P0 | Charger un exemple peut écraser la saisie | Confirmation d'écrasement | Scénario d'exemple fictif uniquement |
| P0 | La projection redémarre Streamlit et remonte la page | Calcul et résultats dans le même parcours sans rerun | Les actions exceptionnelles de chargement/objectif peuvent encore relancer la page |
| P0 | Lire des résultats périmés comme actuels | Contrôles de statut déjà ajoutés v0.5, maintien de l'invalidation dans v0.6 | Tous les chemins de modification seront à confirmer sur appareils réels |
| P1 | Créer manuellement des événements coûte du temps | Bibliothèque de 6 événements pré-remplis, éditables avant simulation | Valeurs **illustratives** calculées en proportions du budget, aucune statistique prétendue |
| P1 | Risques absents de la comparaison | Simulation de résistance séparée du plan de référence ; effets sur patrimoine, liquidité minimale | Comparaison déterministe, pas d'estimation de probabilité |
| P1 | Paramètres moins visibles dans sidebar | Import, exemple et export regroupés dans une section clairement libellée sur la page principale | Contrôle natif de chargement en anglais selon version Streamlit |
| P1 | Événements ajoutés réinitialisent la page | Ajout dans la même exécution de rendu | Suppression exige encore une exécution Streamlit pour nettoyer les widgets |
| P2 | Paramètres longs sur mobile | Sections visibles et groupées par thème (déjà v0.5) | À revoir avec de vrais usagers : longueur peut rester excessive |
| P2 | Horizon via curseur peu accessible | Passage envisagé vers entrée numérique + tests de clavier | À valider sur navigateurs mobiles |
| P2 | Risque de double comptage des dépenses | Avertissement avant ajout des scénarios suggérés | Détection automatique impossible sans budget détaillé |
| P3 | Paramètres macro et fiscaux incomplets | Documenter les limites, pas de faux contrôles | Moteurs fiscal, social et multi-actifs reportés |

## Définition des scénarios pré-configurés

Chaque événement est une **proposition**, jamais ajouté au scénario principal sans action de l'utilisateur. La date est éditable, la durée et les montants peuvent être modifiés dans la fiche après ajout. Les valeurs ne sont ni médianes, ni recommandations, ni taux de fréquence.

| Modèle | Durée proposée | Hypothèse budgétaire (base = montants saisis) |
|---|---|---|
| Interruption d'emploi | 3 mois | -100 % du revenu mensuel initial |
| Santé et soins | 2 mois | +25 % des dépenses, -30 % du revenu, frais initiaux = 50 % des dépenses |
| Dépense imprévue | 1 mois | coût ponctuel = deux mois de dépenses |
| Garde d'enfant | 36 mois | +20 % des dépenses, coût initial = 50 % des dépenses |
| Soutien familial | 12 mois | +15 % des dépenses |
| Déménagement | 1 mois | coût initial = 1,5 mois de dépenses |

Les pourcentages sont des **exemples modifiables**, sans prétention empirique. Les frais de garde/soins/chômage déjà comptés dans les dépenses/revenus doivent être exclus de l'ajout pour éviter le double comptage. Un changement du revenu salarial en année future n'est qu'approximé ici par le niveau de revenu initial : l'évolution salariale n'est pas compensée exactement pendant la période de chômage.

## Tests attendus et qualité

- Pour six scénarios, `Plan.validate()` et comparaison sans mutation du plan ; les coûts ponctuels et durées extrêmes sont vérifiés.
- Montants exprimés dans la devise sélectionnée, sans conversion cachée.
- Pays changé ou exemple demandé : confirmation avant remplacement.
- Simulation de stress = scénario comparatif séparé, jamais fusionné au scénario de référence.
- Langues FR/EN/VI complètes pour tous les nouveaux contrôles ; aucune traduction de secours cachée.
- Vérification sur ordinateur/mobile et hébergement public avant qualification de « stable ». **GitHub Actions reste manuel** à la demande de l'utilisateur.

## Ce qui n'est pas une revue humaine

Les tests de calcul, audits heuristiques et scénarios fictifs **ne remplacent pas** des évaluations avec des utilisateurs réels de catégories socio-économiques diverses ni des avis de fiscalistes, économistes, actuaires et ergonomes indépendants. La procédure de recrutement et les tâches sont dans `18_PROTOCOL_EVALUATIONS_HUMAINES.md`. Il serait inexact de dire que la version a été relue/validée par de tels participants.
