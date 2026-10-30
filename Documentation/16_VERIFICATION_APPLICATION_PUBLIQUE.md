# Vérification de l'application Streamlit publique

## 2026-10-30 — Production hot-reload compatibility and live verification

- The old live Playwright workflow (last executed on an older commit) was outdated and could falsely fail to find visible interface content: the browser screenshot showed a loaded app while its selector queried only the top-level page.
- The new smoke test searches all browser frames, checks the **actual deployed version** against the checkout and exercises the **current** French example → confirmation → projection → results flow plus Vietnamese mobile layout. It must run against the **new commit**, not be mistaken for an old successful local test.
- Streamlit's long-lived worker can retain imported modules after a hot deployment. The app now checks its package version against the source on disk and reloads the relevant modules in dependency order when mismatched.
- Existing Streamlit sessions may contain a pre-household Plan object; migration converts it to the v0.7.1 data model, preserving compatible values and invalidating stale projections. If migration fails, it reports an error rather than silently replacing user inputs.
- Local unit tests for this migration and the household engine have passed. **The live URL has not been verified in this session**: do not call the hosted issue resolved solely from these source changes.
- Both GitHub Actions workflows remain manual by request to avoid workflow-run notification email. **Consequently, no automatic production check is performed after every push.** To meet continuous live verification without unwanted notifications requires a connected independent browser-monitoring route or explicit GitHub notification settings change.
- Recommended release procedure: stage changes, run tests, publish, inspect the public app using a real browser, confirm version, test example→projection and mobile. If unable to perform the post-deploy check, mark the release unverified and do not claim production success.


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

## Résultat confirmé : v0.8.2 (30 octobre 2026)

Les tests Python/AppTest et Chromium local du commit `64a5873af433e204fb00c7fe137a816327ccedc1` ont terminé avec succès. Le workflow navigateur du site public [41033538584](https://github.com/trungtin-dinh/financial_adviser/actions/runs/41033538584) a observé la version **v0.8.2** puis a réussi le parcours FR exemple → confirmation → projection → résultats, et le chargement mobile VI sans débordement horizontal.

L'incident découvert sur v0.8.1 (champs obligatoires vides après confirmation de l'exemple) est corrigé par rehydratation explicite des clés de saisie avant création des widgets Streamlit et par un test de non-régression. Les actions GitHub sont de nouveau déclenchées **automatiquement après chaque push**, sans modifier les préférences de notification e-mail du compte utilisateur.

Les captures du navigateur sont jointes comme artefacts du workflow. Cette vérification ponctuelle ne garantit pas la disponibilité continue du fournisseur d'hébergement.
