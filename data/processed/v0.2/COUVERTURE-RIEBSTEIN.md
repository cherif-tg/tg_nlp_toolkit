# Couverture du vocabulaire Riebstein dans le corpus v0.2

Rapport généré le 2026-08-14 par `scripts/verif_riebstein.py` (lexique v2 nettoyé).

## Question

Le vocabulaire du lexique Riebstein (8 575 entrées FR→ÉWÉ, 1926) est-il
**incorporé** dans le corpus parallèle v0.2 (16 050 paires) ?

## Méthode

- **Côté FR** : le mot principal de chaque entrée Riebstein doit apparaître
  au moins une fois dans les textes français du corpus.
- **Côté ÉWÉ** : au moins un mot de la traduction éwé Riebstein doit
  apparaître dans les textes éwé du corpus.
- Mesure = **couverture lexicale** (présence), pas alignement sémantique.

## Résultats globaux

| Indicateur | Valeur |
|---|---|
| Entrées Riebstein analysées | 6935 |
| Mot FR présent dans le corpus | 2112 (30 %) |
| ≥1 mot ÉWÉ présent dans le corpus | 5119 (74 %) |
| Mot FR **et** ÉWÉ présents | 1679 (24 %) |
| Ni FR ni ÉWÉ présents | 1383 (20 %) |

## Interprétation

> Attention: La couverture **FR** mesure si le *mot* du lexique apparaît dans le
> corpus biblique — mais un verset biblique ne « contient » pas le mot au
> même sens que l'entrée de dictionnaire. La couverture indique donc la
> **proximité lexicale**, pas la traduction du terme.

## Couverture par section alphabétique

| Section | Entrées | FR présent | ÉWÉ présent |
|---|---|---|---|
| A | 687 | 175 (25 %) | 550 (80 %) |
| B | 370 | 98 (26 %) | 244 (66 %) |
| C | 902 | 268 (30 %) | 654 (73 %) |
| D | 523 | 143 (27 %) | 423 (81 %) |
| E | 623 | 132 (21 %) | 481 (77 %) |
| F | 339 | 108 (32 %) | 236 (70 %) |
| G | 223 | 55 (25 %) | 163 (73 %) |
| H | 110 | 16 (15 %) | 82 (75 %) |
| I | 271 | 78 (29 %) | 208 (77 %) |
| K | 4 | 1 (25 %) | 4 (100 %) |
| L | 152 | 57 (38 %) | 105 (69 %) |
| M | 392 | 127 (32 %) | 261 (67 %) |
| N | 114 | 37 (32 %) | 79 (69 %) |
| O | 146 | 61 (42 %) | 112 (77 %) |
| P | 635 | 235 (37 %) | 434 (68 %) |
| Q | 23 | 8 (35 %) | 17 (74 %) |
| R | 489 | 172 (35 %) | 400 (82 %) |
| S | 398 | 151 (38 %) | 293 (74 %) |
| T | 324 | 115 (35 %) | 238 (73 %) |
| U | 21 | 5 (24 %) | 14 (67 %) |
| V | 173 | 68 (39 %) | 112 (65 %) |
| W | 3 | 0 (0 %) | 2 (67 %) |
| Y | 1 | 0 (0 %) | 1 (100 %) |
| Z | 12 | 2 (17 %) | 6 (50 %) |

## Mots FR du Riebstein absents du corpus (top 25)

| Mot | Fréquence dans Riebstein |
|---|---|
| bourdon | 3 |
| d'abord | 2 |
| appâter | 2 |
| bière | 2 |
| boucher | 2 |
| cale | 2 |
| canon | 2 |
| cohue | 2 |
| cousin | 2 |
| dé | 2 |
| déboucher | 2 |
| futur | 2 |
| griller | 2 |
| limon | 2 |
| lustre | 2 |
| manche | 2 |
| mineur | 2 |
| mousse | 2 |
| page | 2 |
| parer | 2 |
| paroissien | 2 |
| pêche | 2 |
| priser | 2 |
| quille | 2 |
| sommer | 2 |

## Mots ÉWÉ du Riebstein absents du corpus (top 25)

| Mot | Fréquence dans Riebstein |
|---|---|
| îe | 130 |
| îo | 93 |
| î | 53 |
| gblê | 49 |
| îu | 45 |
| gâ | 45 |
| gbâ | 38 |
| agbalê | 26 |
| gbegblê | 26 |
| lô | 25 |
| sesê | 23 |
| nù | 17 |
| yâ | 17 |
| mô | 17 |
| hlê | 17 |
| hlâ | 16 |
| nyô | 16 |
| amegâ | 16 |
| srô | 15 |
| atsyô | 14 |
| teîe | 14 |
| mû | 13 |
| miâ | 13 |
| nyâ | 13 |
| mê | 13 |

## Conclusion

- **Vocabulaire FR** : 30 % des mots Riebstein sont présents
  dans le corpus (4823 absents, ex. « bourdon »).
- **Vocabulaire ÉWÉ** : 74 % des traductions Riebstein ont au
  moins un mot présent (7316 mots absents au total).
- Le corpus est **biblique** : les mots absents sont souvent du vocabulaire
  courant non-biblique (administration, santé, vie quotidienne) — c'est
  exactement la lacune que la diversification (piste 1) doit combler.

## Voir aussi
- Pipeline de nettoyage : `src/clean/`
- Datasheet : `data/processed/v0.2/DATASHEET.md`
