# Datasheet — Corpus parallèle FR↔Éwé v0.3

- **Version** : 0.3 (exploratoire — vérifié par échantillons)
- **Date** : 2026-08-15
- **Paires** : **65,640** (train 52,512 / dev 6,564 / test 6,564)
- **Colonnes** : `source` (bible | nllb), `fr`, `ewe`

## Composants

| Composant | Paires | Provenance | Variante | Licence |
|---|---|---|---|---|
| Bible 1913 ↔ Segond 1910 | 16,014 | archives (domaine public) | éwé historique (mission de Brême) | CC0-1.0 |
| NLLB filtré v3 | 49,626 | OPUS `NLLB.ee-fr` (allenai/nllb) | éwé moderne + textes minés | **ODC-By** (attribution) |
| Lexique Riebstein v2 | 8 574 (composant séparé) | archive.org (domaine public) | éwé togolais 1926 | Domaine public |

## Qualité mesurée

| Composant | Échantillon vérifié | Qualité |
|---|---|---|
| Bible (v0.2) | 100 paires, locuteur natif | ~66 % (51 ok / 31 corriger / 18 rejeter) |
| NLLB (v2→v3) | 100 paires, locuteur natif | 68 % (v2) → **~72 % estimé (v3** après retrait langues étrangères) |

Le **test de référence (300 paires vérifiées à 100 %)** est en préparation — il
sera la référence officielle d'évaluation (le bruit du corpus d'entraînement
est tolérable, pas celui de l'évaluation).

## Biais connus

1. **Registre** : la composante Bible est biblique ; la composante NLLB est
   hétérogène (web miné, religieux, vie courante) avec ~28 % de bruit résiduel
   (alignements approximatifs).
2. **Orthographe** : éwé historique (1913/1926) vs éwé moderne (NLLB) mélangés
   — chaque paire garde la variante de sa source (politique de variantes du 14/08).
3. **Licence** : ODC-By impose l'attribution (dataset card) ; pas de
   redistribution des sources NLLB brutes non filtrées.

## Pipeline

`src/clean/` (bible) + `scripts/filter_nllb.py` (v3) + `scripts/assemble_v03.py`.
