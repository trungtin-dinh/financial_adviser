# Plan directeur

Le plan complet et les critères d'acceptation de chaque phase se trouvent dans [12_PLAN_GLOBAL.md](12_PLAN_GLOBAL.md). Ce fichier conserve l'historique de la roadmap initiale.

# Roadmap — Financial Adviser

La progression doit être incrémentale ; chaque jalon se termine par code testable, documentation synchronisée et limites explicites.

## v0.1.0 — Premier socle fonctionnel (livré dans le dépôt)

- Interface Streamlit simple + avancée ; FR/EN/VI partiel.
- Plan cash/investissements/dette, événements, horizon et taux modifiables.
- Projection déterministe / Monte Carlo élémentaire, comparaison de rendements.
- Affichage nominal / réel, cash négatif, objectif, graphiques, tables CSV.
- Sauvegarde JSON, sources officielles FR/VN référencées, inflation historique via API optionnelle.
- Moteur isolé et tests unitaires.

## v0.2 — Solidifier le MVP

- Validation UX en navigateur et tests responsive desktop/tablette/mobile ; captures d'écran et guides FR/EN/VI complets.
- Formulaire d'événements structuré (dates réelles, récurrence, variation de revenu), comparaison de scénarios sauvegardés.
- Import/export de plusieurs scénarios, migration de schéma, provenance et hachage des paramètres, historique reproductible.
- Tests UI, tests de sources simulées, audit accessibilité et perfs sur déploiement.

## v0.3 — Portefeuille, risques et immobilier

- Comptes multiples, classes d'actifs, allocation, contributions propres, coûts/commissions.
- Retours corrélés et modèles alternatifs (bootstrap historique, Student-t), crises et analyses de sensibilité.
- Immobilier avec valeur d'actif, financement, charges, impôts et cash-flow locatif (sans promettre de fiscalité exhaustive).
- Devises multiples, prix d'achat/vente et conversion, origines des taux / historique.

## v0.4 — Cadre juridique et fiscal FR/VN

- Inventaire des règles et exemples officiels, couverture par type de revenu, statut résident/non-résident, années fiscales.
- Modules indépendants France et Vietnam, transparence des calculs et cas non pris en charge.
- Veille sur changements de textes, journal des versions, workflow de validation et alertes **sans mise en production automatique des nouveaux taux**.

## v0.5 — Long terme / retraite / transfrontalier

- Retraite, produits nationaux, fiscalité d'enveloppes, revenus passifs, patrimoine familial.
- Trajectoires de résidence, convention fiscale France–Vietnam, données macro par pays, pouvoir d'achat par devise.
- Rapports et partage contrôlé, financement de projets, capacité de retrait et stress-tests.

## Décisions ouvertes prioritaires

1. Faut-il adopter un modèle de *cashflow ledger* comptable mensuel comme source unique du patrimoine ? (Recommandation : oui en v0.2.)
2. Comment distinguer rendement nominal, frais, prélèvements et taxation à la réalisation des plus-values ?
3. Comment figer un « jeu de règles » fiscal par simulation et migrer les anciens scénarios ?
4. Quelle politique de confidentialité et quels modes d'hébergement pour un futur compte multi-utilisateur ?
5. Quel protocole d'évaluation des modèles stochastiques est acceptable avant affichage de probabilités ?


## Incrément v0.2.0 livré (29 octobre 2026)

- Événements de vie, scénarios adverses explicites ; aucun modèle médical ou actuariel.
- Goal seek inverse (trois leviers, non cumulables), contrainte de trésorerie et retour d'infaisabilité.
- Saisie essentielle requise, paramètres secondaires modifiables, documentation/sources séparées en navigation.
- Revue heuristique par profils simulés ; **aucune revue humaine effectuée**.

**Prochain objectif :** revue UI desktop/mobile, vérification des versions de Streamlit et retours réels de testeurs volontaires ; puis modules de risques probabilistes traçables et fiscalité nationale validée.
