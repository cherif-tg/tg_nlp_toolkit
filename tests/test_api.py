#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests de l'API REST sans charger le modele (traduire est simule).

Lancement :
    python tests/test_api.py

Le modele complet (2,4 Go) n'est pas telecharge : le lifespan de l'app
n'est pas execute par TestClient hors contexte, et traduire() est mocke.
"""

import os
import sys
from unittest import mock

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RACINE)

from fastapi.testclient import TestClient  # noqa: E402
from src.api.main import app  # noqa: E402

client = TestClient(app)  # sans "with" : le lifespan (chargement modele) ne tourne pas


def test_health():
    r = client.get("/health")
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "ok", r.text
    print("1. GET /health -> 200 OK :", r.json())


def test_traduction_fr_ewe():
    with mock.patch("src.api.main.traduire", return_value="Efoa, wòle asi nyuie?") as m:
        r = client.post(
            "/translate",
            json={"text": "Bonjour, comment vas-tu ?", "src": "fr", "tgt": "ewe"},
        )
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["traduction"] == "Efoa, wòle asi nyuie?", body
        assert body["src"] == "fr" and body["tgt"] == "ewe", body
        m.assert_called_once_with("Bonjour, comment vas-tu ?", src="fr", tgt="ewe")
        print("2. POST /translate FR->EWE -> 200 OK :", body)


def test_traduction_ewe_fr():
    with mock.patch("src.api.main.traduire", return_value="Bonjour, comment vas-tu ?"):
        r = client.post(
            "/translate",
            json={"text": "Efoa, wòle asi nyuie?", "src": "ewe", "tgt": "fr"},
        )
        assert r.status_code == 200, r.text
        print("3. POST /translate EWE->FR -> 200 OK :", r.json())


def test_langue_inconnue():
    r = client.post("/translate", json={"text": "hello", "src": "en", "tgt": "ewe"})
    assert r.status_code == 400, r.text
    print("4. Langue inconnue (en) -> 400 :", r.json()["detail"])


def test_src_egal_tgt():
    r = client.post("/translate", json={"text": "hello", "src": "fr", "tgt": "fr"})
    assert r.status_code == 400, r.text
    print("5. src == tgt -> 400 :", r.json()["detail"])


def test_texte_vide():
    r = client.post("/translate", json={"text": "", "src": "fr", "tgt": "ewe"})
    assert r.status_code == 422, r.text
    print("6. Text vide -> 422 :", r.status_code)


def test_champ_manquant():
    r = client.post("/translate", json={"src": "fr"})
    assert r.status_code == 422, r.text
    print("7. Champ 'text' manquant -> 422 :", r.status_code)


def test_racine_redirige():
    r = client.get("/", follow_redirects=False)
    assert r.status_code in (302, 307), r.status_code
    assert r.headers["location"] == "/docs", r.headers
    print("8. GET / ->", r.status_code, "vers", r.headers["location"])


def test_docs():
    r = client.get("/docs")
    assert r.status_code == 200, r.status_code
    print("9. GET /docs -> 200 OK (documentation interactive)")


if __name__ == "__main__":
    test_health()
    test_traduction_fr_ewe()
    test_traduction_ewe_fr()
    test_langue_inconnue()
    test_src_egal_tgt()
    test_texte_vide()
    test_champ_manquant()
    test_racine_redirige()
    test_docs()
    print("TOUS LES TESTS PASSENT")
