#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Preparation des donnees WAXAL ewe_asr pour l'ASR (tg_nlp_toolkit, v0.1).

Charge les fichiers parquet de la config ``ewe_asr`` du dataset
``google/WaxalNLP``, calcule les metriques par extrait (duree, nombre de
mots, debit de parole), applique les filtres documentes dans
docs/14-asr-ewe-plan-execution-v0.1.md et produit :

- un manifeste CSV : une ligne par extrait, avec la decision
  d'eligibilite a l'entrainement et le statut de comparabilite WAXALNet ;
- un rapport de statistiques Markdown + JSON : heures, durees, locuteurs,
  inventaire orthographique, retention des filtres.

Note technique : la config ``ewe_asr`` declaree dans le YAML du dataset
echoue au chargement (``load_dataset("google/WaxalNLP", "ewe_asr")``) car
les parquet reels contiennent une colonne ``__index_level_0__`` absente du
schema declare. On passe donc par le builder parquet generique, en
resolvant la liste des fichiers via l'API Hugging Face ; la colonne
parasite est ignoree. Les durees sont lues via ``soundfile.info`` sur les
octets bruts (pas de decodage complet de l'audio).

Le script ne modifie jamais la source : il lit, il resume.

Utilisation :
    python src/asr/prep_waxal_ewe.py --split train --max-rows 20 \
        --stream --out-dir data-asr/manifests
    python src/asr/prep_waxal_ewe.py --split all --out-dir data-asr/manifests

En local, preferer --stream avec un petit --max-rows (quelques Mo). Le
telechargement complet des splits etiquetes (~5,7 Go) est prevu sur Colab.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import soundfile as sf

# Constantes documentees dans docs/14 (section 7).
DUREE_MIN = 1.5   # duree minimale acceptee (filtre WAXALNet : >= 1,5 s)
DUREE_MAX = 30.0  # limite d'entree Whisper pour le v0.1 : clips plus longs ecartes
DEBIT_MIN = 4.0   # debit minimal de parole (filtre WAXALNet : >= 4 mots/s)

COLONNES = [
    "id",
    "speaker_id",
    "gender",
    "duration_s",
    "n_mots",
    "debit_mots_s",
    "statut_entrainement",
    "motif_ecart",
    "comparable_waxalnet",
    "transcription",
]

# Inventaire orthographique pertinent pour l'ewe et le style de transcription.
LETTRES_EWE = "ɖɛɔŋƒɣʋ"

MOTIF_FICHIER = re.compile(r"^(?P<langue>[a-z]{3})-(?P<split>[a-z]+)-\d+\.parquet$")


def fichiers_parquet(repo, config, split):
    """Liste triee des parquet d'un split, via l'API Hugging Face.

    ``config`` suit la convention du dataset : ``<langue>_<tache>``
    (ex. ``ewe_asr`` -> ``data/ASR/ewe/ewe-<split>-*.parquet``).
    """
    from huggingface_hub import HfApi

    langue, tache = config.split("_", 1)
    prefixe = f"data/{tache.upper()}/{langue}/"
    api = HfApi()
    noms = [
        f
        for f in api.list_repo_files(repo, repo_type="dataset")
        if f.startswith(prefixe)
        and MOTIF_FICHIER.match(f.split("/")[-1])
    ]
    attends = [
        f for f in noms
        if f.split("/")[-1].startswith(f"{langue}-{split}-")
    ]
    if not attends:
        raise FileNotFoundError(
            f"Aucun parquet pour {repo} / {config} / {split} (prefixe {prefixe})"
        )
    return sorted(attends)


def revision_repo(repo):
    """Revision (sha) courante du depot, pour la reproductibilite."""
    from huggingface_hub import HfApi

    return HfApi().dataset_info(repo).sha


def charger_split(repo, config, split, stream):
    """Charge un split via le builder parquet generique (voir note
    technique en tete de module)."""
    from datasets import load_dataset

    fichiers = fichiers_parquet(repo, config, split)
    urls = [f"hf://datasets/{repo}@main/{f}" for f in fichiers]
    dataset = load_dataset("parquet", data_files=urls, split="train", streaming=stream)
    return dataset


def _duree_secondes(extrait):
    """Duree de l'extrait en secondes, lue dans les octets audio bruts.

    Renvoie None si l'audio est absent ou illisible.
    """
    audio = extrait.get("audio")
    if not isinstance(audio, dict):
        return None
    brut = audio.get("bytes")
    if not brut:
        return None
    try:
        infos = sf.info(io.BytesIO(brut))
    except (sf.LibsndfileError, RuntimeError):
        return None
    if not infos.samplerate:
        return None
    return infos.frames / infos.samplerate


def analyser_extrait(extrait):
    """Calcule les metriques d'un extrait et rend sa ligne de manifeste.

    Renvoie un tuple (ligne, ok) ou ``ligne`` contient les valeurs dans
    l'ordre de COLONNES et ``ok`` vaut True si l'extrait est eligible a
    l'entrainement v0.1.
    """
    transcription = str(extrait.get("transcription") or "").strip()
    duree = _duree_secondes(extrait)

    n_mots = len(transcription.split())
    debit = None
    if duree is not None and duree > 0:
        debit = n_mots / duree

    motifs = []
    if not transcription:
        motifs.append("transcription_vide")
    if duree is None:
        motifs.append("audio_illisible")
    else:
        if duree < DUREE_MIN:
            motifs.append("duree_courte")
        if duree > DUREE_MAX:
            motifs.append("duree_longue")
    if debit is None:
        motifs.append("debit_indetermine")

    ok = not motifs
    comparable = bool(
        duree is not None
        and DUREE_MIN <= duree <= DUREE_MAX
        and debit is not None
        and debit >= DEBIT_MIN
    )

    ligne = [
        extrait.get("id"),
        extrait.get("speaker_id"),
        extrait.get("gender"),
        round(duree, 3) if duree is not None else "",
        n_mots,
        round(debit, 3) if debit is not None else "",
        "ok" if ok else "ecarte",
        ";".join(motifs) if motifs else "",
        "oui" if comparable else "non",
        transcription,
    ]
    return ligne, ok


def collecter_statistiques(lignes_ok):
    """Statistiques globales a partir des lignes de manifeste conservees."""
    stats = {
        "n_extraits_ok": len(lignes_ok),
        "heures_ok": sum(float(l[3]) for l in lignes_ok) / 3600.0,
        "n_mots_total": sum(int(l[4]) for l in lignes_ok),
    }

    durees = sorted(float(l[3]) for l in lignes_ok)
    if durees:
        def percentile(p):
            k = max(0, min(len(durees) - 1, int(round((len(durees) - 1) * p))))
            return round(durees[k], 3)
        stats["duree_s"] = {
            "p05": percentile(0.05),
            "p50": percentile(0.50),
            "p95": percentile(0.95),
            "max": round(durees[-1], 3),
        }
    else:
        stats["duree_s"] = {}

    stats["locuteurs"] = len({l[1] for l in lignes_ok if l[1] not in (None, "")})
    stats["genre"] = dict(
        Counter(str(l[2]) for l in lignes_ok if l[2] not in (None, ""))
    )

    inventaire = Counter()
    transcriptions = []
    for ligne in lignes_ok:
        texte = ligne[9]
        transcriptions.append(texte)
        for c in texte:
            if not c.isspace():
                inventaire[c] += 1

    stats["caracteres"] = {
        "total": sum(inventaire.values()),
        "distincts": len(inventaire),
        "plus_frequents": inventaire.most_common(20),
        "lettres_ewe_presentes": {
            c: inventaire.get(c, 0) for c in LETTRES_EWE if inventaire.get(c, 0)
        },
    }

    n_ponctue = sum(any(c in ".,;:!?" for c in t) for t in transcriptions)
    n_majuscule = sum(any(c.isupper() for c in t) for t in transcriptions)
    stats["style_transcription"] = {
        "part_avec_ponctuation_forte": round(n_ponctue / len(transcriptions), 4),
        "part_avec_majuscules": round(n_majuscule / len(transcriptions), 4),
        "exemples": transcriptions[:3],
    }
    return stats


def rapport_markdown(split, source, revision, stats, retention):
    lignes = [
        f"# Manifeste ewe_asr - {split}",
        "",
        f"- Source : `{source}` (fichiers parquet `data/ASR/ewe/`, revision `{revision}`)",
        f"- Genere le : {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        "- Script : `src/asr/prep_waxal_ewe.py`",
        "",
        "## Retention des filtres",
        "",
        "| Indicateur | Valeur |",
        "|---|---|",
        f"| Extraits lus | {retention['n_lus']} |",
        f"| Extraits ecartes | {retention['n_ecartes']} |",
        f"| Extraits conserves (eligibles v0.1) | {retention['n_ok']} |",
        f"| Heures conservees | {stats['heures_ok']:.2f} h |",
        f"| Comparables WAXALNet (duree >= 1,5 s, debit >= 4 mots/s) | {retention['n_comparables']} |",
        "",
        "## Motifs d'ecart",
        "",
        "| Motif | Nombre |",
        "|---|---|",
    ]
    for motif, n in retention["motifs"].most_common():
        lignes.append(f"| {motif} | {n} |")
    if not retention["motifs"]:
        lignes.append("| (aucun) | 0 |")

    lignes += [
        "",
        "## Statistiques des extraits conserves",
        "",
        f"- Durees (s) : p05 {stats['duree_s'].get('p05')}, p50 {stats['duree_s'].get('p50')}, p95 {stats['duree_s'].get('p95')}, max {stats['duree_s'].get('max')}",
        f"- Locuteurs distincts : {stats['locuteurs']}",
        f"- Genre : {json.dumps(stats['genre'], ensure_ascii=False)}",
        f"- Mots transcrits : {stats['n_mots_total']}",
        "",
        "## Orthographe",
        "",
        f"- Caracteres distincts : {stats['caracteres']['distincts']}",
        f"- Lettres ewe specifiques presentes : {json.dumps(stats['caracteres']['lettres_ewe_presentes'], ensure_ascii=False)}",
        f"- Extrait avec ponctuation forte (.,;:!?) : {stats['style_transcription']['part_avec_ponctuation_forte']:.0%}",
        f"- Extrait avec majuscules : {stats['style_transcription']['part_avec_majuscules']:.0%}",
        "",
        "## Exemples de transcriptions conservees",
        "",
    ]
    for i, exemple in enumerate(stats["style_transcription"]["exemples"], 1):
        lignes.append(f"{i}. {exemple}")
    return "\n".join(lignes) + "\n"


def traiter_split(split, out_dir, repo, config, max_rows, stream, revision):
    """Charge un split, ecrit son manifeste CSV et son rapport, rend un
    dictionnaire de synthese."""
    t0 = time.time()
    print(f"[prep] Chargement {repo} ({config}, {split})"
          + (f", max {max_rows} lignes" if max_rows else "")
          + (" en streaming" if stream else " en mode complet"))

    dataset = charger_split(repo, config, split, stream)
    if max_rows:
        dataset = dataset.take(max_rows)

    lignes = []
    stats_lignes_ok = []
    n_lus = 0
    motifs_counter = Counter()
    n_ok = 0
    n_comparables = 0

    for extrait in dataset:
        n_lus += 1
        ligne, ok = analyser_extrait(extrait)
        if ok:
            n_ok += 1
            stats_lignes_ok.append(ligne)
            if ligne[8] == "oui":
                n_comparables += 1
        else:
            for motif in (ligne[7] or "").split(";"):
                if motif:
                    motifs_counter[motif] += 1
        lignes.append(ligne)
        if n_lus % 500 == 0:
            print(f"[prep] {n_lus} extraits traites en {time.time() - t0:.1f} s")

    out_dir.mkdir(parents=True, exist_ok=True)
    chemin_csv = out_dir / f"ewe_asr_{split}_manifeste.csv"
    with open(chemin_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(COLONNES)
        writer.writerows(lignes)

    if n_ok == 0:
        print(f"[prep] Avertissement : aucun extrait conserve pour {split}.")
        return None

    stats = collecter_statistiques(stats_lignes_ok)
    retention = {
        "n_lus": n_lus,
        "n_ecartes": n_lus - n_ok,
        "n_ok": n_ok,
        "n_comparables": n_comparables,
        "motifs": motifs_counter,
    }

    rapport = rapport_markdown(split, f"{repo}/{config}", revision, stats, retention)
    chemin_rapport = out_dir / f"ewe_asr_{split}_rapport.md"
    chemin_json = out_dir / f"ewe_asr_{split}_stats.json"
    with open(chemin_rapport, "w", encoding="utf-8") as f:
        f.write(rapport)
    with open(chemin_json, "w", encoding="utf-8") as f:
        json.dump(
            {"split": split, "revision": revision, "stats": stats, "retention": retention},
            f, ensure_ascii=False, indent=2,
        )

    print(f"[prep] {split} : {n_lus} lus, {n_ok} conserves, "
          f"{stats['heures_ok']:.2f} h -> {chemin_csv.name}")
    return {"split": split, "revision": revision, "stats": stats, "retention": retention}


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Preparation des donnees WAXAL ewe_asr (manifeste + rapport)."
    )
    parser.add_argument(
        "--split",
        choices=["train", "validation", "test", "all"],
        default="train",
        help="split a preparer, ou 'all' pour les trois (defaut : train)",
    )
    parser.add_argument(
        "--max-rows",
        type=int,
        default=0,
        help="nombre maximal d'extraits a lire (0 = tous) ; utile en local",
    )
    parser.add_argument(
        "--stream",
        action="store_true",
        help="chargement en streaming (recommande en local et pour --max-rows)",
    )
    parser.add_argument(
        "--repo", default="google/WaxalNLP", help="depot Hugging Face source"
    )
    parser.add_argument(
        "--config", default="ewe_asr", help="config du dataset source (<langue>_<tache>)"
    )
    parser.add_argument(
        "--out-dir",
        default="data-asr/manifests",
        help="dossier de sortie des manifestes et rapports",
    )
    args = parser.parse_args(argv)

    splits = ["train", "validation", "test"] if args.split == "all" else [args.split]
    out_dir = Path(args.out_dir)
    revision = revision_repo(args.repo)
    print(f"[prep] Revision du depot : {revision}")

    synthese = {}
    for split in splits:
        resultat = traiter_split(
            split, out_dir, args.repo, args.config, args.max_rows, args.stream, revision
        )
        if resultat:
            synthese[split] = resultat

    chemin_synthese = out_dir / "ewe_asr_synthese.json"
    with open(chemin_synthese, "w", encoding="utf-8") as f:
        json.dump(synthese, f, ensure_ascii=False, indent=2, default=str)
    print(f"[prep] Synthese ecrite dans {chemin_synthese}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
