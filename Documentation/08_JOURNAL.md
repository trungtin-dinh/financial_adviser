# Journal de décisions et mises à jour

## 2026-10-29 — Création de la base de connaissances et v0.1.0

**Décisions retenues**

- Développer un moteur Python indépendant de Streamlit, avec états et flux mensuels explicites.
- Viser France et Vietnam dans la structure et les références, mais **ne pas inventer de fiscalité légale** dans la première version.
- Présenter toutes les valeurs par défaut comme des hypothèses fictives et non des statistiques officielles.
- Obtenir l'inflation observée via Banque mondiale **en option** ; ne pas remplacer une hypothèse automatiquement.
- Utiliser des exports JSON/CSV, pas de comptes ni de connexions bancaires.
- Favoriser une interface desktop, sans supposer que le mobile est déjà pleinement validé.
- Lire les codes et documentations de MontePlan, MyFinModel et Monte Carlo Retirement pour éclairer la séparation moteur/UI ; réécrire nos propres calculs.
- Tests unitaires de toutes les équations fondamentales avant diffusion.

**Points à revoir**

- Complexité fiscale FR/VN, année fiscale et résidence, intégration des sources juridiques validées.
- Propriétés statistiques du Monte Carlo et leur interprétation (risque de mauvaise confiance).
- Modélisation d'une trésorerie négative, d'une dette sans actif et des arrondis monétaires.
- Audit du parcours mobile et de l'ensemble des traductions.
- Différence de persistance entre exécution locale et Streamlit Cloud.

**Règle d'entretien** : à chaque incrément, ajouter ici les nouveaux changements, sources confirmées, limites corrigées et fichiers concernés. Ne pas remplacer une référence officielle sans conserver la date et le motif de remplacement.
