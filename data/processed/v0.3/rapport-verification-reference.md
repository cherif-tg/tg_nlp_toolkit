# Rapport de verification du test de reference (300 paires)

**Date** : 18/08/2026
**Fichier source** : `test-reference-300.csv` (300 paires : 150 bible, 150 nllb)
**Verificateurs** : locuteur 1 (verif1) + Cherif TENGA (verif2, locuteur ewe cotier de Lome)
**Protocole** : double verification independante, verdicts par paire
(ok / corriger / a rejeter), arbitrage final par Cherif.

## 1. Retour des verifications

- 299 lignes retournees sur 300 : la paire `id 141` (bible) etait absente
  du fichier retourne.
- Verdicts detailles avec commentaires des deux cotes.
- Normalisation appliquee : `ok(...)`, `ok` -> ok ; `a corriger`,
  `coriiger(...)`, corrections proposees -> corriger ; `a rejeter`,
  `a-rejeter(...)` -> rejeter.

## 2. Croisement des verdicts

| verif1 x verif2 | Nombre |
|---|---|
| ok x ok | 238 |
| corriger x corriger | 26 |
| rejeter x rejeter | 26 |
| ok x corriger | 3 |
| corriger x ok | 1 |
| corriger x rejeter | 1 |
| autre x rejeter | 1 |
| corriger x autre | 1 |
| ok x vide | 2 |

Concordance des deux verificateurs : 290/299 paires avec verdict identique
apres normalisation (97 %). Seulement 4 desaccords ok vs non-ok.

## 3. Arbitrage (decisions de Cherif, 18/08)

| id | Source | Situation | Decision |
|---|---|---|---|
| 33 | nllb | ok / corriger (correspondance a revoir) | exclue |
| 44 | bible | ok / corriger (parasites `ela- EKEM A.`) | exclue |
| 48 | bible | chiffres parasites (`9, 29 10, 22`) | exclue |
| 97 | nllb | corriger / ok | validee |
| 181 | nllb | ok / sans reponse | validee |
| 264 | bible | ok / sans reponse | validee |
| 140 | bible | colonnes decalees, texte FR/EWE incoherent | exclue |
| 188 | bible | partie ewe sans equivalent FR (alignement decale) | a corriger |
| 141 | bible | paire manquante du retour | exclue |

## 4. Reference finale

**`test-reference-final.csv` : 241 paires validees** (124 bible, 117 nllb).

Regle appliquee :
- ok/ok (238) + arbitrage favorable (97, 181, 264) -> validees
- corriger ou rejeter par au moins un verificateur -> exclues
- l'id 188 est gardee de cote en attente de correction manuelle
  (elle reintegrera la reference apres correction).

Les textes de la reference finale reprennent les colonnes ORIGINALES du
repo (trois cellules ewe du fichier de retour avaient ete modifiees
accidentellement pendant la verification : ids 139, 140, 181 ; parmi
celles-ci seule la 181 est validee, avec le texte original propre).

## 5. Motifs d'exclusion (59 paires)

| Motif | Nombre |
|---|---|
| Non precise / corriger generique | 28 |
| Mauvaise traduction | 14 |
| Correspondance approximative | 7 |
| Signes ou caracteres parasites | 4 |
| Chiffres ou nombres parasites | 4 |

## 6. Diagnostic pour la boucle d'affinage

L'analyse des chiffres arabes asymetriques (presents d'un cote seulement)
dans les splits v0.3 donne :

| Split | Paires avec chiffres asymetriques |
|---|---|
| train.tsv | 2 700 / 47 852 (5,64 %) |
| dev.tsv | 322 / 5 918 (5,44 %) |
| test.tsv | 320 / 5 987 (5,34 %) |

Causes identifiees :
- OCR de la Bible 1913 : confusion de caracteres (`le` -> `1e`,
  `la` -> `1a`, `Eye woawo 1a`), references de versets residuelles
  (`Ve J 14, 7.`).
- Corpus NLLB : nombres du FR non traduits (ou traduits en lettres)
  dans un cote seulement (`28 Ils n'auront...` vs ewe sans nombre ;
  `famille de 8 personnes` vs `ame enyi`).
- Un cas de corruption de ligne dans les donnees NLLB brutes
  (tabulations dans le champ texte).

### Actions recommandees (filtre v4, a appliquer au train uniquement)

1. Exclure ou corriger les paires avec chiffres asymetriques DANS LE
   TRAIN (environ 2 700 paires concernees ; commencer par un nettoyage
   cible OCR : `1e`, `1a`, `1i` en position de lettre).
2. Ne PAS modifier dev/test avant d'avoir decide d'une regenese complete
   v0.4 (sinon les scores v0.3 ne sont plus comparables).
3. Les paires exclus de la reference finale (59) restent utiles :
   motif `mauvaise traduction` -> diagnostic du filtre NLLB ;
   motif `chiffres/parasites` -> tests du futur nettoyage.

## 7. Etapes suivantes

1. Scores officiels (baseline + fine-tune v1) sur les 241 paires de la
   reference finale.
2. Benchmark Google Translate sur les memes 241 paires (comparaison).
3. Correction manuelle de l'id 188 puis reintegration.
4. Decision sur le filtre v4 (nettoyage chiffres asymetriques du train)
   avant le fine-tuning v2.

## 8. Fichiers produits

- `test-reference-final.csv` : la reference officielle (241 paires).
- `test-reference-verifs.csv` : archive complete des verifications
  (verdicts bruts, verdicts normalises, statut final par paire).
- Ce rapport.
