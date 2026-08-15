#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test du mode API de la demo Gradio : le payload envoye doit utiliser
les codes API (fr/ewe), pas les libelles d'interface (Francais/Ewe).

Lancement :
    python tests/test_demo_api.py

Ne charge pas le modele : la fonction traduire() est mockee.
"""

import os
import sys
from unittest import mock

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RACINE)

os.environ["API_URL"] = "http://127.0.0.1:8000"  # active le mode API de la demo

import demo.app as app  # noqa: E402


def test_mode_api_active():
    assert app.API_URL == "http://127.0.0.1:8000", "mode API non active"
    print("1. Mode API active :", app.API_URL)


def test_payload_fr_ewe():
    with mock.patch("demo.app.httpx.post") as m:
        m.return_value.json.return_value = {"traduction": "bonjour en ewe"}
        m.return_value.raise_for_status = lambda: None
        resultat = app.traduire("Bonjour", "Francais", "Ewe", beams=4)
        assert resultat == "bonjour en ewe", resultat
        payload = m.call_args.kwargs["json"]
        print("2. Payload FR->EWE :", payload)
        assert payload["src"] == "fr", payload
        assert payload["tgt"] == "ewe", payload
        assert payload["text"] == "Bonjour", payload


def test_payload_ewe_fr():
    with mock.patch("demo.app.httpx.post") as m:
        m.return_value.json.return_value = {"traduction": "bonjour en fr"}
        m.return_value.raise_for_status = lambda: None
        app.traduire("Efoa", "Ewe", "Francais")
        payload = m.call_args.kwargs["json"]
        print("3. Payload EWE->FR :", payload)
        assert payload["src"] == "ewe" and payload["tgt"] == "fr", payload


if __name__ == "__main__":
    test_mode_api_active()
    test_payload_fr_ewe()
    test_payload_ewe_fr()
    print("TEST MODE API : OK (les codes fr/ewe sont bien envoyes)")
