# Qualité, confidentialité et limites connues

## 1. Principes

Les résultats sont des **illustrations conditionnelles** aux entrées. Ne pas appeler un rendement supposé « attendu du marché » ni une fraction de scénarios Monte Carlo « probabilité réelle » sans calibration justifiée. L'[AMF](https://www.amf-france.org/fr/espace-epargnants/savoir-bien-investir/cadrer-son-projet/les-performances-passees-ne-prejugent-pas-des-performances-futures-pourquoi-cette-mention-0) rappelle que les performances passées ne permettent pas de prédire les performances futures.

## 2. Tests automatisés initiaux

`pytest -q` vérifie : flux nuls, transferts sans double comptage, événements et agrégation, taux effectifs, inflation, prêts nuls/positifs, maturité et dette restante, reproductibilité Monte Carlo, identité déterministe à volatilité zéro, déficit de trésorerie, import/export JSON, rejets d'entrées invalides.

**Non encore testés dans cette étape :** exécution de Streamlit dans un vrai navigateur (Streamlit n'est pas disponible dans l'environnement de validation), mobile/tablette réels, API Banque mondiale en temps réel (réseau indisponible dans l'environnement de tests), tableaux de taxes inexistants.

## 3. Modèle de confiance et données

- Pas de connexion bancaire et pas de base de comptes personnelle dans le code.
- Les entrées sont gardées en mémoire de session du serveur Streamlit et dans le navigateur pendant la session ; les exports sont déclenchés par l'utilisateur.
- Une app publique hébergée n'est pas un stockage local privé : les données saisies sont envoyées au serveur d'hébergement. Pour des données financières réelles, exécution locale recommandée.
- Ne jamais commiter de données financières personnelles, identifiants, tokens ou clés d'API.
- Le système d'import JSON vérifie le schéma et limite la taille, mais n'est pas une sandbox pour fichiers malveillants ; ne pas charger des sources inconnues.
- Dans une version multi-utilisateur persistante, protection des données, consentement, sécurité, suppression et contrôle d'accès devront faire l'objet d'une analyse spécifique (RGPD en UE et règles vietnamiennes applicables).

## 4. Limites mathématiques / économiques

- Modèle à **deux postes d'actif** (cash et investissements) et **une dette** ; pas de portefeuille multi-actifs, de fiscalité ou de taux de change.
- Le moteur laisse la trésorerie devenir négative ; les coûts d'emprunt non autorisé et la faillite financière ne sont pas modélisés.
- Rendements constants en déterministe. Monte Carlo normal IID et clipping à -99 %, sans queues épaisses, taux corrélés ou calibration empirique.
- Dépenses estimées par croissance uniforme, pas par poste de consommation ; salaire déjà net, absence de cotisations/retraite.
- L'inflation ne s'applique qu'au calcul du patrimoine réel ; les dépenses ont leur propre croissance supposée, réglable séparément.
- Les rendements n'intègrent pas d'office frais, spreads, fiscalité des plus-values ou frais de gestion.
- Un prêt est supposé fixe, sans assurance/frais ni remboursement anticipé. Le principal restant est soustrait du patrimoine sans bien immobilier associé.
- Les valeurs en VND peuvent être de plusieurs milliards : des flottants sont employés pour les projections, mais il n'y a pas de calcul bancaire exact au centime. Une future comptabilité monétaire devra utiliser `Decimal`/quantification.
- L'interface FR/EN/VI est partiellement traduite ; certains messages et explications restent en anglais/français.

## 5. Risques UX à corriger

- Différencier le « pays de référence » de la **résidence fiscale** ; le modèle actuel ne traite aucune fiscalité.
- Changer de pays recharge un exemple et **n'effectue aucune conversion** de devise : avertissement obligatoire.
- Les scénarios en cours de saisie doivent être validés par « Run » avant comparaison ; avertissement affiché.
- Les données World Bank restent **historiques** ; l'option de les appliquer à une hypothèse future exige un clic explicite.
- Améliorer accessibilité/contrastes, vues mobiles, validation d'entrées et choix de langue persistant après navigation.

## 6. Exigences avant fonctionnalité réglementaire

1. Source juridique primaire et date d'application validées.
2. Scénarios d'essai officiels et comparaison indépendante.
3. Journal des règles et cas non couverts.
4. Prise en compte des années fiscales / dates historiques et sauvegarde des versions.
5. Revue humaine avant activation. Aucune « mise à jour magique » via IA directement dans le calcul.
