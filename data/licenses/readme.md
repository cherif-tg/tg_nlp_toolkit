# Matrice des licences — guide d'utilisation

## Pourquoi cette matrice ?

Chaque donnée intégrée au projet a un statut juridique différent. Certaines sources peuvent être **publiées** dans le corpus public, d'autres uniquement servies à **l'entraînement** des modèles, d'autres doivent être écartées. Cette matrice consigne la décision **par source**, prise **avant** toute intégration de données.

## Comment lire la matrice (`matrix.csv`)

| Colonne | Signification |
|---|---|
| `source` | Nom de la source de données |
| `langues` | Langues concernées (`ewe`, `kbp`) |
| `type` | Nature : texte parallèle, texte monolingue, audio, etc. |
| `volume_estime` | Ordre de grandeur attendu |
| `statut_licence` | Ce que dit la licence / les CGU |
| `usage_autorise` | **Décision** : Publier / Entraînement uniquement / Ne pas utiliser |
| `statut_verification` | `Verifie` / `A verifier` / `Planifie` / `Absent` |
| `actions` | Ce qu'il reste à faire pour finaliser la décision |
| `responsable` | Qui porte la vérification |
| `date` | Date de la dernière mise à jour |

## Protocole de vérification (par source)

1. Trouver la **page officielle de licence / CGU** de la source
2. Lire les conditions de **redistribution** (pas juste d'utilisation)
3. Noter les **interdictions** éventuelles
4. Prendre la décision (`usage_autorise`) et la justifier
5. Consigner dans une **fiche de décision** (modèle : `_template-decision.md`)
6. Mettre à jour la matrice (statut + actions)

## Ce qu'il reste à vérifier en ligne (liste pour Cherif)

- [ ] **JW.org** — lire les conditions d'utilisation : <https://www.jw.org/en/terms-of-use/> — la redistribution du contenu est-elle autorisée ? (dans la plupart des cas : non)
- [ ] **OPUS** — ouvrir la page du corpus pour l'éwé : <https://opus.nlpl.eu/> — lister les corpus disponibles pour `ewe` et noter la licence de chacun (JW300, bible-uedin, Tatoeba…)
- [ ] **Bible éwé** — identifier les éditions disponibles (traduction, année, éditeur) et vérifier leur statut (domaine public ? droits réservés ?)
- [ ] **Wikipedia** — licence CC BY-SA confirmée (standard), vérifier seulement le volume d'articles en éwé

## Règles d'or

1. Une source = une décision écrite, **avant** intégration
2. Le corpus **publié** ne contient que des sources publiables
3. Le JW300 sert à l'entraînement, **jamais** dans le dataset public
4. Ne jamais mélanger silencieusement des sources de licences différentes dans un fichier publié

## Constats de la vérification (13/08/2026 — par Cherif)

| Source | Constat | Décision |
|---|---|---|
| JW.org / JW300 | CGU lues : redistribution interdite, scraping interdit | Entraînement uniquement (validé) — passer par OPUS, jamais scraper jw.org |
| OPUS | Aucun corpus éwé trouvé à la navigation | À reconfirmer via l'API OPUS en P1 |
| Bibles éwé (EB14, AL, EWERV) | Toutes sous copyright (sociétés bibliques) | Ne pas publier — entraînement si besoin critique |
| Wikipedia éwé | Quasi vide (page alphabet uniquement) | Indisponible — page alphabet conservée comme référence orthographique |

**Conséquence stratégique** : la collecte ciblée (santé/éducation/admin) devient la **source principale** du corpus publié — volume cible porté à 1000-2000 phrases. Le corpus publié sera 100% hors registre religieux (biais de registre éliminé par construction).
