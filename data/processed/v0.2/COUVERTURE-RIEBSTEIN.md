# Couverture du vocabulaire Riebstein dans le corpus v0.2

Rapport généré le 2026-08-14 par `scripts/verif_riebstein.py`.

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
| ≥1 mot ÉWÉ présent dans le corpus | 5723 (83 %) |
| Mot FR **et** ÉWÉ présents | 1841 (27 %) |
| Ni FR ni ÉWÉ présents | 941 (14 %) |

## Interprétation

> ⚠️ La couverture **FR** mesure si le *mot* du lexique apparaît dans le
> corpus biblique — mais un verset biblique ne « contient » pas le mot au
> même sens que l'entrée de dictionnaire. La couverture indique donc la
> **proximité lexicale**, pas la traduction du terme.

## Couverture par section alphabétique

| Section | Entrées | FR présent | ÉWÉ présent |
|---|---|---|---|
| A | 687 | 175 (25 %) | 597 (87 %) |
| B | 370 | 98 (26 %) | 273 (74 %) |
| C | 902 | 268 (30 %) | 730 (81 %) |
| D | 523 | 143 (27 %) | 455 (87 %) |
| E | 623 | 132 (21 %) | 523 (84 %) |
| F | 339 | 108 (32 %) | 265 (78 %) |
| G | 223 | 55 (25 %) | 182 (82 %) |
| H | 110 | 16 (15 %) | 94 (85 %) |
| I | 271 | 78 (29 %) | 234 (86 %) |
| K | 4 | 1 (25 %) | 4 (100 %) |
| L | 152 | 57 (38 %) | 127 (84 %) |
| M | 392 | 127 (32 %) | 311 (79 %) |
| N | 114 | 37 (32 %) | 91 (80 %) |
| O | 146 | 61 (42 %) | 125 (86 %) |
| P | 635 | 235 (37 %) | 489 (77 %) |
| Q | 23 | 8 (35 %) | 19 (83 %) |
| R | 489 | 172 (35 %) | 437 (89 %) |
| S | 398 | 151 (38 %) | 334 (84 %) |
| T | 324 | 115 (35 %) | 261 (81 %) |
| U | 21 | 5 (24 %) | 19 (90 %) |
| V | 173 | 68 (39 %) | 142 (82 %) |
| W | 3 | 0 (0 %) | 2 (67 %) |
| Y | 1 | 0 (0 %) | 1 (100 %) |
| Z | 12 | 2 (17 %) | 8 (67 %) |

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
| î | 1289 |
| îe | 235 |
| îo | 165 |
| faire | 125 |
| îu | 84 |
| gâ | 79 |
| être | 72 |
| gblê | 70 |
| un- | 70 |
| avoir | 69 |
| être- | 53 |
| gbâ | 52 |
| mettre | 50 |
| à- | 47 |
| lô | 46 |
| sesê | 44 |
| agbalê | 43 |
| -s | 43 |
| une- | 40 |
| dans | 39 |
| p- | 36 |
| gbegblê | 36 |
| donner | 34 |
| des- | 32 |
| nù | 31 |

## Conclusion

- **Vocabulaire FR** : 30 % des mots Riebstein sont présents
  dans le corpus (4823 absents, ex. « bourdon »).
- **Vocabulaire ÉWÉ** : 83 % des traductions Riebstein ont au
  moins un mot présent (19344 mots absents au total).
- Le corpus est **biblique** : les mots absents sont souvent du vocabulaire
  courant non-biblique (administration, santé, vie quotidienne) — c'est
  exactement la lacune que la diversification (piste 1) doit combler.

## Voir aussi
- Pipeline de nettoyage : `src/clean/`
- Datasheet : `data/processed/v0.2/DATASHEET.md`
