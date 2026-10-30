# Vérification de l'application Streamlit publique

**URL déclarée :** https://financial-adviser.streamlit.app/

La publication GitHub et le déploiement Streamlit sont distincts : un workflow de tests locaux réussi ne suffit pas à certifier la version en ligne.

## Ce qui est vérifié

1. **GitHub Actions « Python and UX checks »** : code, tests, simulations et parcours sur Chromium local (bureau, tablette, mobile).
2. **GitHub Actions « Public Streamlit browser smoke »** : après succès des tests locaux (ou déclenchement manuel), ouvre **le site public dans Chromium réel** et exécute avec des données de démonstration : ouverture en français, chargement de l'exemple, projection, accès au résultat; puis ouverture sur un écran mobile en vietnamien avec vérification du reflow. Les captures sont conservées comme artefacts GitHub Actions.

Ce contrôle représente un **test fonctionnel de fumée**, pas un audit exhaustif, un test de charge ou une garantie de cohérence fiscale.

## Pourquoi un navigateur réel ?

Le premier essai en `urllib` a renvoyé une boucle de redirections HTTP 303, sans permettre d'évaluer l'application. Ce comportement des clients non navigateurs sur Streamlit Community Cloud est décrit par l'équipe Streamlit : https://github.com/streamlit/streamlit/issues/15369 . Les clients sans JavaScript ni cookies ne complètent pas toujours le processus de session, y compris pour des applications publiques. L'échec **ne prouvait donc pas une panne de notre code**. Le test a été remplacé par Chromium + Playwright.

## Conditions et limites

- Une application en veille peut afficher un écran de réveil ; le test tente de le prendre en charge.
- Une mise à jour Streamlit peut ne pas être immédiatement disponible lors du lancement du workflow ; le test n'établit pas de correspondance cryptographique entre commit GitHub et version serveur.
- Les tests n'utilisent jamais de données financières personnelles; les valeurs de l'exemple sont fictives.
- Tester sur appareil réel, différents lecteurs d'écran, navigateurs et réseaux reste nécessaire.
- En cas d'échec, consulter les captures GitHub, les journaux d'exécution et les logs de Streamlit Cloud. Ne pas conclure automatiquement que le site public est indisponible.

Sources : https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app et https://github.com/streamlit/streamlit/issues/15369

## Incident constaté en production le 30 octobre 2026

Le premier contrôle Chromium réel a capturé un **KeyError sur `nav_benchmarks`**, pendant l'assemblage du menu `app.py`. Le dictionnaire `ui_i18n.py` versionné sur GitHub contient pourtant cette traduction dans les trois langues. Cela est **compatible avec un module Python périmé encore chargé en mémoire lors d'un redéploiement à chaud**, mais un autre défaut de synchronisation de l'hébergement ne peut être exclu sans accès aux logs internes de Streamlit.

Correctif : recharger explicitement le catalogue de traduction au démarrage de l'entrypoint et toucher le fichier de dépendances pour provoquer une nouvelle installation/reprise de l'environnement; ajouter un test des clés de navigation. Conserver la capture d'écran GitHub Actions comme preuve de régression : https://github.com/trungtin-dinh/financial_adviser/actions/runs/41012291272 .

Ce diagnostic se distingue du premier échec HTTP 303 : cette fois, le **navigateur réel a effectivement chargé l'application et révélé une exception Python**.
