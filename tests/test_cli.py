#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests du CLI batch (traduction simulee, sans modele).

Lancement :
    python tests/test_cli.py
"""

import os
import sys
import tempfile
from unittest import mock

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RACINE)

import pandas as pd  # noqa: E402

from src.cli import translate as cli  # noqa: E402

TMP = tempfile.mkdtemp()
ENTREE = os.path.join(TMP, "messages_test.csv")
SORTIE = os.path.join(TMP, "messages_test_out.csv")


def test_traduction_complete():
    pd.DataFrame({"message": ["Bonjour", "Merci beaucoup", ""]}).to_csv(
        ENTREE, index=False, encoding="utf-8"
    )
    with mock.patch("src.api.inference.traduire", return_value="traduit") as m:
        cli.main(["--input", ENTREE, "--output", SORTIE,
                  "--src", "fr", "--tgt", "ewe"])

    df = pd.read_csv(SORTIE, encoding="utf-8", keep_default_na=False)
    assert len(df) == 3, df
    assert list(df.columns) == ["message", "traduction"], df.columns
    assert df["traduction"].iloc[0] == "traduit", df
    assert df["traduction"].iloc[1] == "traduit", df
    assert df["traduction"].iloc[2] == "", df  # ligne vide -> pas d'appel
    print("1. CSV traduit OK - appels traduire :", m.call_count,
          "(attendu 2, la ligne vide ne compte pas)")


def test_detection_auto_colonne():
    pd.DataFrame({"fr": ["Salut"]}).to_csv(ENTREE, index=False, encoding="utf-8")
    with mock.patch("src.api.inference.traduire", return_value="x"):
        cli.main(["--input", ENTREE, "--output", SORTIE])
    df = pd.read_csv(SORTIE, encoding="utf-8")
    assert "traduction" in df.columns, df.columns
    print("2. Detection auto de colonne ('fr') OK")


def test_colonne_inexistante():
    try:
        cli.main(["--input", ENTREE, "--output", SORTIE, "--colonne", "zzz"])
        raise AssertionError("aurait du echouer")
    except SystemExit as e:
        assert "Colonne introuvable" in str(e), e
        print("3. Colonne introuvable ->", e)


def test_fichier_introuvable():
    try:
        cli.main(["--input", "fichier_inexistant.csv", "--output", SORTIE])
        raise AssertionError("aurait du echouer")
    except SystemExit as e:
        assert "Fichier introuvable" in str(e), e
        print("4. Fichier introuvable ->", e)


def test_src_egal_tgt():
    try:
        cli.main(["--input", ENTREE, "--output", SORTIE,
                  "--src", "fr", "--tgt", "fr"])
        raise AssertionError("aurait du echouer")
    except SystemExit as e:
        assert "differents" in str(e), e
        print("5. src == tgt ->", e)


def test_mode_api():
    with mock.patch("httpx.post") as m:
        m.return_value.json.return_value = {"traduction": "via api"}
        m.return_value.raise_for_status = lambda: None
        cli.main(["--input", ENTREE, "--output", SORTIE,
                  "--api", "http://127.0.0.1:8000"])
        payload = m.call_args.kwargs["json"]
        assert payload["src"] == "fr" and payload["tgt"] == "ewe", payload
        print("6. Mode API OK - payload :", payload)


if __name__ == "__main__":
    test_traduction_complete()
    test_detection_auto_colonne()
    test_colonne_inexistante()
    test_fichier_introuvable()
    test_src_egal_tgt()
    test_mode_api()
    print("TOUS LES TESTS DU CLI PASSENT")
