# Financial Adviser

**Simulateur de planification financière des ménages, pour explorer l'évolution du budget et du patrimoine dans le temps.**

[![Application Streamlit](https://img.shields.io/badge/Application-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://financial-adviser.streamlit.app/)
[![Documentation](https://img.shields.io/badge/Documentation-Technique-blue?logo=readthedocs&logoColor=white)](Documentation/00_INDEX.md)
[![DeepWiki](https://img.shields.io/badge/DeepWiki-Consulter-4A90E2?logo=readthedocs&logoColor=white)](https://deepwiki.com/trungtin-dinh/financial_adviser)

[![Tests Python et ergonomie](https://github.com/trungtin-dinh/financial_adviser/actions/workflows/tests.yml/badge.svg)](https://github.com/trungtin-dinh/financial_adviser/actions/workflows/tests.yml)
[![Vérification sur Streamlit Cloud](https://github.com/trungtin-dinh/financial_adviser/actions/workflows/public-app-check.yml/badge.svg)](https://github.com/trungtin-dinh/financial_adviser/actions/workflows/public-app-check.yml)

## Présentation

Financial Adviser est une application éducative de **simulation financière sur plusieurs années**, développée avec Python et Streamlit. Elle permet de comprendre comment les revenus, les dépenses, les placements, les crédits et les événements de la vie influencent la trésorerie et le patrimoine d'un ménage.

Elle est conçue pour être accessible sans connaissances avancées en finance : les hypothèses sont visibles, les montants sont modifiables et les résultats sont séparés des données saisies. L'interface propose le **français, l'anglais et le vietnamien** ; les scénarios peuvent être exprimés en euros ou en dôngs vietnamiens. Le choix d'un pays ne convertit pas les montants.

## Fonctionnalités

- **Projection du patrimoine** : évolution mensuelle de la trésorerie, des placements, de la dette et du patrimoine net nominal ou corrigé de l'inflation.
- **Budget du foyer** : revenus et dépenses du ménage, enfants avec coûts selon l'âge, profils d'adultes et changements hypothétiques à la retraite, ainsi que soutien à d'autres personnes à charge.
- **Événements de vie** : changements de revenus, dépenses mensuelles supplémentaires et coûts ponctuels avec calendrier et durée.
- **Scénarios de risque** : comparaisons déterministes, notamment en cas d'interruption de revenus ou de dépense imprévue ; les risques ne sont pas appliqués automatiquement à la projection principale.
- **Recherche d'objectif** : estimation d'efforts financiers permettant d'atteindre un patrimoine cible sous les contraintes du modèle.
- **Simulation Monte Carlo simplifiée** : exploration de la sensibilité des placements à des rendements aléatoires, avec quantiles conditionnels aux hypothèses utilisées.
- **Import et export** : sauvegarde locale d'un scénario au format JSON pour le reprendre ou le partager volontairement.
- **Références statistiques** : consultation distincte de données officielles et de leur provenance, sans assimiler ces chiffres à des prédictions personnelles.

## Utilisation

1. Ouvrez l'[application](https://financial-adviser.streamlit.app/) et choisissez la langue et le pays.
2. Renseignez vos revenus, dépenses, avoirs, objectifs et horizon de projection, ou chargez un scénario d'exemple.
3. Si nécessaire, ajoutez des enfants, des adultes, d'autres personnes à charge ou des événements. Vérifiez toujours ce qui est **déjà inclus dans le budget initial**, afin d'éviter le double comptage.
4. Cliquez sur **Lancer la projection** pour calculer les résultats, puis étudiez l'évolution de la trésorerie, du patrimoine, des risques et des objectifs.
5. Enregistrez un scénario JSON lorsque vous souhaitez le retrouver ultérieurement.

Les informations peuvent être fictives. L'application ne nécessite ni connexion bancaire ni compte personnel.

## Exécution locale

Prérequis : **Python 3.11 ou ultérieur**.

```bash
git clone https://github.com/trungtin-dinh/financial_adviser.git
cd financial_adviser
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Sous Windows, activez l'environnement avec `.venv\Scripts\activate`.

L'exécution locale est autorisée **uniquement dans les conditions d'évaluation personnelle** décrites dans la [licence propriétaire](LICENSE). Le dépôt est consultable publiquement, mais **ce n'est pas un projet open source**.

## Précautions et limites

Financial Adviser est un **outil d'étude et d'aide à la compréhension**, pas un conseiller en investissement, un outil de déclaration fiscale, un estimateur officiel de pension ou un service bancaire.

- Les rendements, la croissance des revenus, l'inflation et les coûts des événements sont des **hypothèses**, non des prévisions garanties.
- Les frais, prélèvements, allocations, droits à pension et règles fiscales propres à la France ou au Vietnam ne sont pas intégralement modélisés.
- La simulation Monte Carlo utilise des hypothèses simplifiées : elle ne représente pas la totalité des risques économiques, sociaux, familiaux ou médicaux.
- Une trésorerie négative signifie un **besoin de financement non couvert** ; le moteur ne présume pas l'existence d'un découvert ou la revente automatique des placements.
- Les avoirs immobiliers et les autres actifs non explicitement modélisés ne sont pas implicitement ajoutés au patrimoine.
- Les informations saisies sur la version publique sont traitées sur le serveur de l'hébergeur. Pour des données personnelles sensibles, préférez des montants fictifs ou une exécution locale.

## Documentation

Le répertoire [`Documentation/`](Documentation/00_INDEX.md) réunit les [conventions mathématiques](Documentation/02_MODELES_MATHEMATIQUES.md), les [sources statistiques et économiques](Documentation/03_SOURCES_ET_REGLES.md), le [modèle de cycle de vie du foyer](Documentation/21_CYCLE_VIE_BUDGET_FAMILIAL.md), les [facteurs de risques](Documentation/17_FACTEURS_FINANCIERS_SOCIAUX_ET_RISQUES.md) et les [audits UX et techniques](Documentation/00_INDEX.md).

Les demandes d'évolution, décisions techniques et nouveaux comportements sont consignés dans les notes de version et le [journal du projet](Documentation/08_JOURNAL.md), plutôt que dans cette page de présentation.

## Licence

**© 2026 Trung-Tin Dinh — Tous droits réservés.** Le code et la documentation sont distribués selon une **licence propriétaire**. Leur consultation et une évaluation personnelle limitée sont autorisées ; toute redistribution, mise à disposition publique, exploitation commerciale ou création de dérivés diffusés nécessite une autorisation écrite préalable. Consulter le texte complet : [LICENSE](LICENSE).

Les bibliothèques tierces conservent leurs licences respectives.
