# Corpus parallèle FR↔Éwé — v0.1 (exploratoire)

**18 995 paires de phrases** (français ↔ éwé) issues de l'alignement verset-à-verset
de la **Bible éwé 1913** (British and Foreign Bible Society, domaine public) avec la
**Bible Louis Segond 1910** (domaine public).

> ⚠️ **Statut : v0.1 exploratoire, non vérifié par un locuteur natif.**
> Un échantillon de 100 paires est en cours de vérification
> (`echantillon-verification-100.csv`). Les textes éwé proviennent d'un OCR
> de 1913 : les diacritiques (ɛ, ɔ, ŋ, ƒ) sont partiellement absents et des
> erreurs résiduelles existent. Voir `DATASHEET.md` pour les limites complètes.

## Fichiers

| Fichier | Paires | Rôle |
|---|---|---|
| `train.tsv` | 15 199 | entraînement (80 %, stratifié par livre) |
| `dev.tsv` | 1 898 | validation (10 %) |
| `test.tsv` | 1 898 | test / évaluation (10 %) — **ne jamais entraîner dessus** |
| `candidates-a-verifier.tsv` | 4 554 | versets fusionnés par l'OCR (hors noyau) |
| `DATASHEET.md` | — | documentation complète (biais, licence, pipeline) |
| `STATS.md` | — | statistiques de génération |

Format (TSV, UTF-8, tabulations) : `livre<TAB>chapitre<TAB>verset<TAB>fr<TAB>ewe`

## Pipeline de génération (reproductible)

| Étape | Script | Commit |
|---|---|---|
| Nettoyage OCR bible éwé | `src/clean/clean_ocr.py` | `4943df4` |
| Normalisation cyrillique (51 422 homoglyphes) | `src/clean/normalise_cyrillique.py` | `3a51ae8` |
| Extraction 66 livres / 25 581 versets | `src/clean/extract_bible.py` | `a0842f4` |
| Parsing Segond 1910 (31 170 versets) | `src/clean/parse_sfm.py` | `b163cb1` |
| Alignement DP (23 549 paires) | `src/clean/align_bible.py` | `c6a3a57` |
| Nettoyage fin + flags qualité | `src/clean/clean_corpus.py` | `d0d2e13` |
| Assemblage splits + seed 42 | `src/clean/assemble_corpus.py` | — |

## Licence

Sources en **domaine public** (Bible 1913 BFBS ; Segond 1910). Corpus dérivé publiable.
Décisions écrites : `data/licenses/decision-bible-ewe.md`, `decision-segond1910.md`, `matrix.csv`.

## Et ensuite

- Intégration des corrections de l'échantillon de vérification → **v0.2**
- Ajout du lexique Riebstein (8 575 paires de mots) et des grilles manuelles (1 050 phrases, 10 thèmes)
- Publication HuggingFace (privé → public) + fine-tuning NLLB-200-distilled-600M
