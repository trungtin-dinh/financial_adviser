# Connaissances, sources et règles nationales — FR / VN

**Dernière vérification documentaire : 29 octobre 2026.** Une règle issue d'une source officielle n'est pas automatiquement un modèle fiscal exhaustif. Les dates de publication, d'entrée en vigueur et de période fiscale doivent être distinguées.

## 1. Typologie des informations

| Type | Exemple | Source privilégiée | Traitement logiciel souhaité |
|---|---|---|---|
| Statistique historique | Inflation passée, taux directeur | Banque centrale, institut public, Banque mondiale | Récupération, datation, cache, unité, source |
| Hypothèse future | Inflation de 2 % pendant 20 ans | Choix utilisateur | Versionnée avec le scénario, jamais imposée par la source |
| Règle fiscale | Barème de l'impôt, prélèvements, exonérations | Texte officiel consolidé | Revue juridique, version d'application, tests avant activation |
| Produit financier | PEA, Livret A, dépôts vietnamiens | Régulateur/texte applicable | Conditions d'éligibilité, plafonds, rendement, frais, fiscalité |
| Documentation | Signification de volatilité, TRI, inflation | Sources pédagogiques reconnues | Explications avec date et références |

## 2. France — registre initial

- [Service Public : revenus d'épargne et de placement](https://www.service-public.gouv.fr/particuliers/vosdroits/F2613) : la fiscalité diffère par enveloppe, année et nature du produit ; ne pas appliquer un seul taux à tous les investissements.
- [Banque de France, Livret A / LEP, juillet 2026](https://www.banque-france.fr/fr/actualites/livrets-depargne-reglementee-leur-remuneration-change) et [Bercy](https://www.economie.gouv.fr/particuliers/gerer-mon-argent/gerer-mon-budget-et-mon-epargne/livret-comment-ca-marche) : Livret A à **1,7 % à partir du 1er août 2026**, LEP à **2,5 %**, calcul du Livret A par quinzaine et capitalisation annuelle. **Documenté, non intégré aux rendements futurs.**
- [Légifrance](https://www.legifrance.gouv.fr/) : lois, codes, décrets, dates d'effet, versions consolidées et API via PISTE selon les accès.
- [BOFiP](https://bofip.impots.gouv.fr/) et [DGFiP](https://www.impots.gouv.fr/) : doctrine et règles fiscales, barèmes par année, régimes particuliers.
- [Urssaf : brut/net](https://mon-entreprise.urssaf.fr/simulateurs/salaire-brut-net) : piste pour salaire net, cotisations et cas particuliers ; **non reproduit** en v0.1.
- [Insee — API statistiques](https://www.insee.fr/fr/information/8184146) : données françaises, inflation et indicateurs ; statut d'API/droits d'accès à vérifier pour chaque flux.
- [AMF — limite des performances passées](https://www.amf-france.org/fr/espace-epargnants/savoir-bien-investir/cadrer-son-projet/les-performances-passees-ne-prejugent-pas-des-performances-futures-pourquoi-cette-mention-0) : simulation non prédictive.

**À étudier avant toute implémentation :** résidence fiscale et quotient familial, types de gains imposables et réalisation des plus-values, PEA/PEA-PME, CTO, assurance-vie, PER, livrets, frais immobiliers, crédit, retraite, prélèvements sociaux et cas des non-résidents. Une règle peut varier selon l'année du revenu, la date de versement ou la date d'ouverture d'un produit.

## 3. Vietnam — registre initial

- [Loi n° 109/2025/QH15 — Thuế thu nhập cá nhân](https://vanban.chinhphu.vn/?docid=216495&pageid=27160) : texte promulgué le **10 décembre 2025**, applicable au **1er juillet 2026** ; certaines dispositions sur les revenus salariaux et professionnels des résidents s'appliquent dès **l'année fiscale 2026** selon [la présentation gouvernementale](https://xaydungchinhsach.chinhphu.vn/gioi-thieu-luat-thue-thu-nhap-ca-nhan-so-109-2025-qh15-119260123145437408.htm).
- [Base nationale de textes juridiques](https://vbpl.moj.gov.vn/) : vérifier les versions et textes d'application consolidés.
- [General Department of Taxation](https://www.gdt.gov.vn/) : fiches et guides fiscaux.
- [State Bank of Vietnam](https://www.sbv.gov.vn/) : politique monétaire, référence des taux et monnaies.
- [National Statistics Office](https://www.nso.gov.vn/en/) : statistiques économiques nationales.

**À étudier avant tout calcul fiscal VN :** résidence fiscale ; revenus salariaux et autres revenus ; barème, assiette, abattements, personnes à charge ; assurances sociales et maladie, chômage et plafonds ; titres, dépôts à terme, immobilier, produits d'épargne et exceptions ; dispositions transitoires. Les pourcentages sans leur assiette ne suffisent pas à produire un impôt exact.

## 4. Activités transfrontalières

Source à examiner : [convention fiscale France–Vietnam (impots.gouv.fr, rubrique conventions internationales)](https://www.impots.gouv.fr/les-conventions-internationales). Elle ne se traduit pas par une simple moyenne des taux : localisation du revenu, résidence fiscale, conventions et élimination de la double imposition doivent être traitées selon les articles applicables. **Aucun cas transfrontalier n'est calculé dans v0.1.**

## 5. API macro implémentée

**Banque mondiale — Indicators API v2** : [documentation](https://datahelpdesk.worldbank.org/knowledgebase/articles/889392), indicateur `FP.CPI.TOTL.ZG` = inflation annuelle observée des prix à la consommation. Requêtes aux pays `FRA` et `VNM`, sans clé API, délai d'attente de 7 secondes, premier point annuel récent avec valeur numérique. La réponse affiche : valeur, année d'observation, date de consultation, URL utilisée.

- 24 heures de cache avec `st.cache_data(ttl=...)` ; bouton d'actualisation manuelle.
- Opt-in pour afficher une statistique ; aucune modification automatique du scénario.
- L'utilisateur peut **explicitement** choisir de recopier cette observation dans son hypothèse d'inflation ; le résultat précédent est alors invalidé.
- Une API indisponible n'interrompt pas les simulations locales.
- **Attention :** la Banque mondiale publie des observations parfois avec retard ; l'année de la donnée est distincte de l'année de récupération.

## 6. Politique d'actualisation cible (futur module)

1. **Registre des sources** : organisme, URL exacte, pays, domaine, fréquence, authentification, conditions de réutilisation.
2. **Collecte technique** : formats JSON/XML, version TLS, timeout, cache, validation de contenu et de schéma, journal d'échec.
3. **Différence** : comparer le contenu à la dernière version, distinguer changements HTML cosmétiques et changements matériels des règles.
4. **Analyse réglementaire** : vérifier le texte consolidé, la date d'effet, l'année de revenu et les conditions particulières. Les changements ne sont pas activés automatiquement.
5. **Activation contrôlée** : tests de référence, revue humaine et nouveau manifeste `rules/` avec identifiant de version.
6. **Historisation** : chaque simulation sauvegarde les versions précises de règles, sources et paramètres. Pas d'écrasement silencieux d'un historique.
7. **Défaillance et hors-ligne** : utiliser la dernière version explicitement validée et afficher son ancienneté. En l'absence de validation, afficher **non calculé**, jamais des données supposées juridiques.

Le fichier [`../rules/catalogue.json`](../rules/catalogue.json) implémente **uniquement un registre documentaire initial**, non un système de surveillance des textes ni un moteur fiscal.

## 7. Contrôle qualité des sources

Préférer les textes primaires et autorités publiques, puis guides institutionnels, articles pédagogiques et forums. Un README open source ou un témoignage Reddit ne peut pas justifier une règle fiscale. Indiquer le niveau de confiance, la date, les changements historiques et les validations encore nécessaires. Aucune extrapolation légale à partir du code américain de MontePlan n'est autorisée.
