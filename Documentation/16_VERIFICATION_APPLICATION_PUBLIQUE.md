# Vérifier le déploiement public Streamlit

**URL déclarée par le propriétaire :** https://financial-adviser.streamlit.app/

La publication GitHub et l'hébergement Streamlit sont deux étapes distinctes. Un commit réussi et des tests sur le serveur local **ne prouvent pas que la version en ligne s'est actualisée**.

## Deux niveaux de contrôle

1. **Application locale / CI de code** : GitHub Actions « Python checks » installe, compile, exécute les tests Python, Streamlit AppTest et Playwright sur PC/tablette/mobile. Vérifie les fonctionnalités contrôlées dans le dépôt, sans intervenir sur le site public.
2. **Site public / transport** : le workflow « Public Streamlit availability » vérifie en HTTPS l'URL publiée et le statut de santé avec des tentatives espacées. C'est un signal de disponibilité, **pas** une preuve de l'absence d'erreur au chargement des widgets, de la justesse des calculs ou de la version déployée.

Le workflow de disponibilité peut échouer temporairement parce que le site est en veille (Streamlit Community Cloud suspend les applications inactives), en redémarrage ou pendant une mise à jour. Une erreur doit conduire à examiner l'état et les journaux Streamlit avant d'imputer le problème au code.

## Vérification fonctionnelle recommandée après publication

- Ouvrir https://financial-adviser.streamlit.app/ dans un vrai navigateur sur PC et sur mobile.
- Contrôler la version de l'app et tester le changement FR/EN/VI sans perte des champs.
- Avec **données fictives**, saisir les revenus/dépenses/objectifs, lancer la projection et consulter le résultat.
- Ajouter puis modifier/supprimer un événement de vie; vérifier qu'il intervient au mois voulu.
- Tester un objectif inverse, exporter puis réimporter un scénario.
- Ouvrir les références FR/VN et vérifier l'origine des chiffres. Vérifier qu'une source indisponible n'altère pas les valeurs.
- Vérifier les messages d'erreur avec une saisie incomplète et l'absence de débordement horizontal à 320 CSS px.
- Pour une vraie validation, utiliser clavier, lecteur d'écran et appareils physiques; documenter anomalie, captures, navigateur et date.

### Limitations de cette intervention

L'accès HTTP automatisé au site public peut être limité depuis les environnements de recherche. Ne pas transformer un échec d'accès de l'outil en conclusion de panne du service. Ne jamais présenter un simple HTTP 200 comme une revue fonctionnelle complète.

Référence Streamlit : https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app
