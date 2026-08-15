#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
assemble_v03.py — Intégration v0.3 : fusion du corpus biblique (v0.2) et du
corpus NLLB filtré v3.

Composants :
  - Bible (v0.2)      : 16 050 paires (train+dev+test), CC0-1.0
  - NLLB filtré v3    : 49 651 paires, ODC-By (attribution requise)
  - Lexique Riebstein : composant séparé (non mélangé aux paires de phrases)

Traitements :
  1. Déduplication exacte (fr+ewe) : interne NLLB + NLLB vs Bible
  2. Fusion avec colonne de provenance (bible | nllb)
  3. Splits 80/10/10 stratifiés par source (seed 42)
  4. Documentation : DATASHEET.md, STATS.md, README.md
  5. Copie dans huggingface/ (publication)

Sorties : data/processed/v0.3/ (train.tsv, dev.tsv, test.tsv, DATASHEET.md,
STATS.md, README.md) + mise à jour huggingface/

Usage : python scripts/assemble_v03.py
"""

import io
import os
import random
import shutil
import statistics

SEED = 42
SPLITS = {
    "bible": [
        "data/processed/v0.2/train.tsv",
        "data/processed/v0.2/dev.tsv",
        "data/processed/v0.2/test.tsv",
    ],
}
NLLB = ".openclaw/tmp/nllb_filtered.tsv"
SORTIE_DIR = "data/processed/v0.3"
HF_DIR = "huggingface"


def charger_bible():
    paires = []
    for path in SPLITS["bible"]:
        with io.open(path, encoding="utf-8") as f:
            next(f)
            for ln in f:
                p = ln.rstrip("\n").split("\t")
                if len(p) >= 5:
                    paires.append(("bible", p[3], p[4]))
    return paires


def charger_nllb():
    paires = []
    with io.open(NLLB, encoding="utf-8") as f:
        next(f)
        for ln in f:
            p = ln.rstrip("\n").split("\t")
            if len(p) >= 2:
                paires.append(("nllb", p[0], p[1]))
    return paires


def dedupe(paires):
    """Déduplication exacte (fr+ewe) en gardant la Bible prioritaire."""
    vus = set()
    resultat = []
    for source, fr, ewe in paires:
        cle = (fr.strip().lower(), ewe.strip().lower())
        if cle in vus:
            continue
        vus.add(cle)
        resultat.append((source, fr, ewe))
    return resultat


def splits_stratifies(paires, seed=SEED):
    rng = random.Random(seed)
    train, dev, test = [], [], []
    par_source = {}
    for source, fr, ewe in paires:
        par_source.setdefault(source, []).append((source, fr, ewe))
    for source, items in par_source.items():
        rng.shuffle(items)
        n = len(items)
        n_dev = int(round(n * 0.10))
        n_test = int(round(n * 0.10))
        dev.extend(items[:n_dev])
        test.extend(items[n_dev:n_dev + n_test])
        train.extend(items[n_dev + n_test:])
    rng.shuffle(train)
    rng.shuffle(dev)
    rng.shuffle(test)
    return train, dev, test


def ecrire_tsv(path, items):
    with io.open(path, "w", encoding="utf-8") as f:
        f.write("source\tfr\tewe\n")
        for source, fr, ewe in items:
            f.write(f"{source}\t{fr}\t{ewe}\n")


def stats(items):
    lens_fr = [len(fr.split()) for _, fr, _ in items]
    lens_ee = [len(ewe.split()) for _, _, ewe in items]
    n_nllb = sum(1 for s, _, _ in items if s == "nllb")
    return {
        "n": len(items),
        "n_nllb": n_nllb,
        "n_bible": len(items) - n_nllb,
        "moy_fr": statistics.mean(lens_fr),
        "moy_ee": statistics.mean(lens_ee),
    }


def main():
    print("Chargement des composants…")
    bible = charger_bible()
    nllb = charger_nllb()
    print(f"  Bible : {len(bible):,} paires | NLLB v3 : {len(nllb):,} paires")

    print("Déduplication…")
    tous = dedupe(bible + nllb)
    print(f"  Après déduplication : {len(tous):,} paires "
          f"({len(bible) + len(nllb) - len(tous):,} doublons retirés)")

    print("Splits 80/10/10 stratifiés par source…")
    train, dev, test = splits_stratifies(tous)

    os.makedirs(SORTIE_DIR, exist_ok=True)
    ecrire_tsv(os.path.join(SORTIE_DIR, "train.tsv"), train)
    ecrire_tsv(os.path.join(SORTIE_DIR, "dev.tsv"), dev)
    ecrire_tsv(os.path.join(SORTIE_DIR, "test.tsv"), test)

    # candidates a-verifier de la Bible conservés
    src_cand = "data/processed/v0.2/candidates-a-verifier.tsv"
    if os.path.exists(src_cand):
        shutil.copy(src_cand, os.path.join(SORTIE_DIR, "candidates-a-verifier.tsv"))

    s_train = stats(train)
    s_dev = stats(dev)
    s_test = stats(test)
    total = s_train["n"] + s_dev["n"] + s_test["n"]

    # STATS.md
    with io.open(os.path.join(SORTIE_DIR, "STATS.md"), "w", encoding="utf-8") as f:
        f.write(f"""# Statistiques — Corpus v0.3

| Split | Paires | Bible | NLLB | Longueur FR (mots) | Longueur ÉWÉ (mots) |
|---|---|---|---|---|---|
| train | {s_train['n']:,} | {s_train['n_bible']:,} | {s_train['n_nllb']:,} | {s_train['moy_fr']:.1f} | {s_train['moy_ee']:.1f} |
| dev   | {s_dev['n']:,} | {s_dev['n_bible']:,} | {s_dev['n_nllb']:,} | {s_dev['moy_fr']:.1f} | {s_dev['moy_ee']:.1f} |
| test  | {s_test['n']:,} | {s_test['n_bible']:,} | {s_test['n_nllb']:,} | {s_test['moy_fr']:.1f} | {s_test['moy_ee']:.1f} |
| **Total** | **{total:,}** | **{s_train['n_bible']+s_dev['n_bible']+s_test['n_bible']:,}** | **{s_train['n_nllb']+s_dev['n_nllb']+s_test['n_nllb']:,}** | | |

Généré le 2026-08-15 par `scripts/assemble_v03.py` (seed {SEED}).
""")

    # DATASHEET.md
    with io.open(os.path.join(SORTIE_DIR, "DATASHEET.md"), "w", encoding="utf-8") as f:
        f.write(f"""# Datasheet — Corpus parallèle FR↔Éwé v0.3

- **Version** : 0.3 (exploratoire — vérifié par échantillons)
- **Date** : 2026-08-15
- **Paires** : **{total:,}** (train {s_train['n']:,} / dev {s_dev['n']:,} / test {s_test['n']:,})
- **Colonnes** : `source` (bible | nllb), `fr`, `ewe`

## Composants

| Composant | Paires | Provenance | Variante | Licence |
|---|---|---|---|---|
| Bible 1913 ↔ Segond 1910 | {s_train['n_bible']+s_dev['n_bible']+s_test['n_bible']:,} | archives (domaine public) | éwé historique (mission de Brême) | CC0-1.0 |
| NLLB filtré v3 | {s_train['n_nllb']+s_dev['n_nllb']+s_test['n_nllb']:,} | OPUS `NLLB.ee-fr` (allenai/nllb) | éwé moderne + textes minés | **ODC-By** (attribution) |
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
""")

    # README.md du corpus
    with io.open(os.path.join(SORTIE_DIR, "README.md"), "w", encoding="utf-8") as f:
        f.write(f"""# Corpus v0.3 (FR↔Éwé)

{total:,} paires parallèles : Bible éwé 1913 ↔ Segond 1910 (CC0) +
NLLB filtré (ODC-By). Voir [DATASHEET.md](DATASHEET.md) pour la qualité,
les biais et les licences. Splits : train {s_train['n']:,} / dev {s_dev['n']:,} / test {s_test['n']:,}.
""")

    # Copie dans huggingface/
    os.makedirs(HF_DIR, exist_ok=True)
    for nom in ("train.tsv", "dev.tsv", "test.tsv"):
        shutil.copy(os.path.join(SORTIE_DIR, nom), os.path.join(HF_DIR, nom))

    print(f"\n=== V0.3 ASSEMBLÉE ===")
    print(f"Train : {s_train['n']:,} (bible {s_train['n_bible']:,} / nllb {s_train['n_nllb']:,})")
    print(f"Dev   : {s_dev['n']:,} (bible {s_dev['n_bible']:,} / nllb {s_dev['n_nllb']:,})")
    print(f"Test  : {s_test['n']:,} (bible {s_test['n_bible']:,} / nllb {s_test['n_nllb']:,})")
    print(f"Total : {total:,}")
    print(f"-> {SORTIE_DIR}/ et {HF_DIR}/")


if __name__ == "__main__":
    main()
