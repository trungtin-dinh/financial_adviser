# Échéances récurrentes — Financial Adviser v0.20.0

**30 octobre 2026.** Extension ciblée du simulateur de budget, sans connexion bancaire ni règle fiscale. À distinguer du calendrier v0.19.x qui présentait uniquement les flux déjà calculés.

## 1. Question et conventions

Pour un ménage, une dépense ponctuelle (achat en janvier) et une dépense périodique (assurance chaque année) n'ont pas les mêmes effets sur la **date de trésorerie minimale**. La moyenne mensuelle masquerait le mois de paiement. L'utilisateur doit donc pouvoir ajouter explicitement un montant et une échéance récurrente.

Une échéance possède :
- **Mois de début** `s`, compté à partir du 1er janvier de l'année de départ (`s=1`).
- **Mois de fin** `e`, inclus ; il doit appartenir à l'horizon du scénario.
- **Intervalle** `k`, égal à **1**, **3** ou **12** mois.
- **Montant signé** `a` dans la devise unique du scénario : **négatif** pour une dépense, **positif** pour une entrée de trésorerie.
- **Description** facultative, sans interprétation économique automatique.

Le mois projeté `m` comprend un flux récurrent :

$$
R_m = \sum_{j=1}^{J} a_j\,\mathbf{1}_{\{s_j\le m\le e_j,\ (m-s_j)\bmod k_j=0\}}.
$$

Les dates sont **inclusives**. Un paiement annuel débutant au mois 2 et finissant au mois 26 a lieu aux mois **2, 14, 26** ; il n'a pas lieu aux autres mois. Une échéance prévue hors de l'horizon est rejetée ; raccourcir l'horizon d'une comparaison n'efface pas silencieusement des engagements datés.

## 2. Relation avec le patrimoine

La variation de trésorerie avant rendement mensuel devient :

$$
F_m = Y_m-E_m-L_m+O_m+R_m-T
$$

et la trésorerie projetée :

$$
C_m=(C_{m-1}+F_m)(1+r_C).
$$

L'investissement suit l'équation déjà définie dans les conventions mathématiques ; un virement interne `T` ne crée pas de patrimoine supplémentaire. Le flux récurrent `R_m` reste affiché **séparément** des mouvements ponctuels `O_m` dans le calendrier mensuel et dans les données de résultat.

**Conventions à ne pas masquer :** le montant `a` reste **constant en valeur nominale** dans le temps ; il n'est ni revalorisé par l'inflation ni multiplié par la croissance des dépenses. Un paiement doit donc être entré **en supplément** des dépenses déjà saisies ; sinon, il est compté deux fois. Aucune dette, liquidation d'investissements ou autorisation de découvert n'est créée automatiquement quand la trésorerie devient négative.

## 3. Exemples pédagogiques

- Assurance annuelle : `début=2`, `fin=26`, `périodicité=12`, `montant=-600 €`. Paiements aux mois 2, 14, 26, trois fois.
- Revenu trimestriel : `début=1`, `fin=12`, `périodicité=3`, `montant=+250 €`. Encaissements aux mois 1, 4, 7, 10.
- Abonnement mensuel : `début=1`, `fin=6`, `périodicité=1`, `montant=-30 €`. Six sorties, total nominal de 180 €.

Si les 600 € d'assurance sont **déjà compris** dans la dépense mensuelle de référence, ne les ajoutez pas une seconde fois au tableau.

## 4. Interface et langues

Dans **Planification**, le panneau « Échéances récurrentes » permet d'ajouter ou de retirer des lignes, de choisir la périodicité et de saisir les mois relatifs au départ. Le contrôle refuse les mois non entiers, les fins antérieures aux débuts, les dates au-delà de l'horizon, les fréquences autres que mensuelle/trimestrielle/annuelle, les nombres non finis et les descriptions excessivement longues. Le nombre de lignes est limité à **100**.

Les libellés et avertissements sont fournis en **FR/EN/VI**. Le tableau « Calendrier de trésorerie mensuel » affiche une colonne supplémentaire pour les flux récurrents. Toute modification exige de relancer la projection avant de lire les résultats recalculés.

## 5. Sauvegarde et compatibilité

La liste optionnelle `recurring_flows` est incluse dans les nouveaux exports de scénario. **Le schéma JSON externe reste à la version 1** : les fichiers anciens dépourvus de cette liste sont chargés avec une liste vide ; les anciens résultats déterministes ne changent pas en l'absence de nouvelle saisie. Une importation invalide est rejetée plutôt que convertie silencieusement.

Le modèle conserve une représentation **signée, explicite et indépendante** des éventuels événements de vie ; il ne tente pas de détecter automatiquement les doublons de dépense avec le budget général.

## 6. Validation prévue et contrôles

Les régressions ajoutées dans le dépôt couvrent :
1. Paiements aux bonnes dates en mensuel, trimestriel et annuel, y compris à travers une frontière d'année.
2. Patrimoine net et conservation des virements internes, séparabilité des dépenses ponctuelles.
3. Accord Monte Carlo à volatilité zéro et projection déterministe.
4. Refus des intervalles ou valeurs invalides et limite du nombre de lignes.
5. Export/import actuel et rétrocompatibilité avec les anciens scénarios JSON.
6. Comparaisons conservant une échéance datée en fin de période et disponibilité des traductions FR/EN/VI.

**Ne pas confondre présence des tests et exécution réussie.** La fonctionnalité ne doit être dite validée qu'après succès de GitHub Actions et vérification des écrans en navigateur sur un exemple FR/EN/VI.

## 7. Limites et prochaines étapes

Cette première version ne gère pas les hausses automatiques d'assurance, les jours fériés, les décalages bancaires, les fréquences hebdomadaires, les taux d'indexation propres à chaque dépense, les comptes multiples, les taxes calculées automatiquement, ni une détection universelle des doublons.

La prochaine amélioration utile serait d'offrir une saisie par **mois civil plutôt que numéro relatif**, en gardant une transformation interne explicite, puis de confirmer le comportement mobile du tableau éditable. Le reste du moteur demeure volontairement simple et auditable.
