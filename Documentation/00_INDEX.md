# Documentation — Financial Adviser

**État :** socle versionné du projet, au 30 octobre 2026. **Version applicative :** v0.4.0.

Cette documentation distingue systématiquement :

- **Référence officielle observée** : fait réglementaire/statistique avec source et date.
- **Hypothèse de simulation** : valeur modifiable et non garantie.
- **Décision d'ingénierie** : convention adoptée pour assurer un calcul reproductible.
- **Non implémenté** : règle ou fonctionnalité envisagée, dont les résultats ne doivent pas être suggérés à l'utilisateur.

## Index

| Fichier | Utilisation |
|---|---|
| [01_CAHIER_DES_CHARGES.md](01_CAHIER_DES_CHARGES.md) | Utilisateurs, besoins, exigences et critères d'acceptation |
| [02_MODELES_MATHEMATIQUES.md](02_MODELES_MATHEMATIQUES.md) | États, flux, taux, équations et Monte Carlo |
| [03_SOURCES_ET_REGLES.md](03_SOURCES_ET_REGLES.md) | Données FR/VN, sources, dates d'effet et politique de mise à jour |
| [04_ARCHITECTURE.md](04_ARCHITECTURE.md) | Modules, contrats, imports, limites des données |
| [05_BENCHMARK.md](05_BENCHMARK.md) | Applications étudiées, bonnes pratiques et limites de l'étude |
| [06_QUALITE_ET_LIMITES.md](06_QUALITE_ET_LIMITES.md) | Tests, confidentialité, biais et non-fonctionnalités |
| [07_ROADMAP.md](07_ROADMAP.md) | Plan de développement par incréments |
| [08_JOURNAL.md](08_JOURNAL.md) | Journal des décisions et des éléments à revoir |
| [09_FACTEURS_DE_VIE_ET_UX.md](09_FACTEURS_DE_VIE_ET_UX.md) | Événements de vie, calcul inverse, principes UX, revue heuristique de profils simulés |
| [10_ERGONOMIE_RESPONSIVE_ET_LANGUES.md](10_ERGONOMIE_RESPONSIVE_ET_LANGUES.md) | Tests PC/tablette/mobile et internationalisation de l'interface |
| [11_PROFILS_STATISTIQUES.md](11_PROFILS_STATISTIQUES.md) | Proposition de préremplissage statistique et règles de provenance |
| [12_PLAN_GLOBAL.md](12_PLAN_GLOBAL.md) | Plan directeur : architecture, phases, dépendances et critères de validation |
| [13_REFERENCES_STATISTIQUES_V04.md](13_REFERENCES_STATISTIQUES_V04.md) | Sources officielles FR/VN et préremplissage consentant de l'inflation |
| [14_REFERENTIEL_ERGONOMIE.md](14_REFERENTIEL_ERGONOMIE.md) | Principes UX fondés sur ISO, NN/g, GOV.UK et WCAG, parcours et tests utilisateurs |
| [15_AUDIT_ERGONOMIQUE_V04.md](15_AUDIT_ERGONOMIQUE_V04.md) | Risques ergonomiques priorisés, observations vs hypothèses, critères d'acceptation |
| [16_VERIFICATION_APPLICATION_PUBLIQUE.md](16_VERIFICATION_APPLICATION_PUBLIQUE.md) | Contrôles de disponibilité du site Streamlit public après publication |

## Règles de maintenance documentaire

1. Tout nouveau paramètre financier doit recevoir une définition, une unité, une convention de timing, des limites et un test.
2. Toute nouvelle règle nationale doit citer un **texte officiel**, une date d'effet, une version, les exemptions et les tests officiels disponibles. La date d'entrée en vigueur et l'année fiscale d'application sont deux notions distinctes.
3. Une observation économique historique n'est jamais appliquée comme hypothèse future sans choix explicite de l'utilisateur.
4. Le moteur financier et l'interface Streamlit restent séparés.
5. Les révisions de cette documentation et les limites connues doivent être inscrites dans le journal.
6. Pour conserver les résultats antérieurs, enregistrer à terme la version des règles et les hypothèses dans chaque export de simulation.

Le dossier `rules/` contient le **catalogue de références**, non un moteur fiscal actif. Aucun texte réglementaire n'est prétendu exhaustif à la date de ce document.
