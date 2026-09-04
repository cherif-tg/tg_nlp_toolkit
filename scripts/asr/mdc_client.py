#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mdc_client.py - Client minimal pour l'API Mozilla Data Collective (MDC).

Documentation API : https://mozilladatacollective.com/api-reference/docs

Usage :
  python scripts/asr/mdc_client.py info <datasetId>
  python scripts/asr/mdc_client.py download <datasetId> [--out DOSSIER]

La cle API est lue dans cet ordre :
  1. Variable d'environnement MDC_API_KEY
  2. Fichier .env a la racine du depot (ligne MDC_API_KEY=xxx),
     fichier jamais commite (voir .env.example).

Contraintes API connues (doc du 30/08/2026) :
  - L'accord des conditions d'utilisation se fait UNIQUEMENT via
    l'interface web (fiche du dataset), jamais par API : en cas de 403,
    ouvrir la fiche du dataset dans le navigateur et accepter les termes.
  - 30 telechargements/jour/organisation, remise a zero a minuit UTC.
  - URL signee valable 12 h, checksum sha256 fourni par l'API.

Dependencies : aucune (bibliotheque standard uniquement).
"""

import argparse
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request

BASE_URL = "https://mozilladatacollective.com/api"


class ErreurAPI(Exception):
    """Erreur avec message oriente utilisateur."""


def charger_cle():
    """Lit la cle API depuis l'environnement ou depuis .env a la racine."""
    cle = os.environ.get("MDC_API_KEY", "").strip()
    if cle:
        return cle
    # .env a la racine du depot (le script vit dans scripts/asr/)
    racine = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    chemin_env = os.path.join(racine, ".env")
    if os.path.isfile(chemin_env):
        with open(chemin_env, encoding="utf-8") as f:
            for ligne in f:
                ligne = ligne.strip()
                if ligne.startswith("MDC_API_KEY=") and not ligne.startswith("#"):
                    cle = ligne.split("=", 1)[1].strip().strip('"').strip("'")
                    if cle:
                        return cle
    raise ErreurAPI(
        "Cle API absente. Definir MDC_API_KEY (environnement) ou creer .env "
        "a la racine du depot : cp .env.example .env puis renseigner la cle."
    )


def requete(url, cle, methode="GET", corps=None):
    """Requete authentifiee avec gestion explicite des erreurs documentees."""
    donnees = json.dumps(corps).encode("utf-8") if corps is not None else None
    req = urllib.request.Request(url, data=donnees, method=methode)
    req.add_header("Authorization", "Bearer " + cle)
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=60) as reponse:
            return json.loads(reponse.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 401:
            raise ErreurAPI("401 : cle API absente ou invalide (verifier MDC_API_KEY).")
        if e.code == 403:
            raise ErreurAPI(
                "403 : acces refuse. Cause la plus frequentes : conditions "
                "d'utilisation du dataset non acceptees. Ouvrir la fiche du "
                "dataset dans le navigateur et accepter les termes (obligatoire, "
                "pas d'endpoint API pour cela)."
            )
        if e.code == 429:
            retry = e.headers.get("Retry-After", "60") if e.headers else "60"
            raise ErreurAPI(
                "429 : limite de taux atteinte. Reessayer dans " + retry + " s. "
                "Rappel : 30 telechargements/jour/organisation, remise a zero a minuit UTC."
            )
        if e.code == 404:
            raise ErreurAPI("404 : dataset introuvable (verifier le datasetId).")
        corps_erreur = ""
        try:
            corps_erreur = e.read().decode("utf-8", "replace")[:300]
        except Exception:
            pass
        raise ErreurAPI("HTTP " + str(e.code) + " : " + corps_erreur)


def afficher_infos(dataset_id, cle):
    """GET /datasets/:id - affiche les details utiles au choix du dataset."""
    donnees = requete(BASE_URL + "/datasets/" + dataset_id, cle)
    print("Nom         :", donnees.get("name"))
    print("Slug        :", donnees.get("slug"))
    print("Locale      :", donnees.get("locale"))
    print("Licence     :", donnees.get("license"))
    print("Tache       :", donnees.get("task"))
    print("Format      :", donnees.get("format"))
    taille = donnees.get("sizeBytes")
    if taille:
        try:
            go = int(taille) / 1e9
            print("Taille      : " + str(round(go, 2)) + " Go")
        except ValueError:
            print("Taille      :", taille)
    print("Fiche web   :", donnees.get("datasetUrl"))
    print("Organisation:", (donnees.get("organization") or {}).get("name"))
    description = donnees.get("longDescription") or donnees.get("shortDescription") or ""
    if description:
        print("Description :", description[:400])
    # Rappel licence : a documenter dans data/licenses/ avant tout usage
    print()
    print("Rappel : documenter la decision de licence dans data/licenses/")
    print("(voir _template-decision.md) avant d'utiliser ces donnees.")


def _verifier_sha256(chemin, checksum_api):
    """Compare le checksum sha256 fourni par l'API (format sha256:hex)."""
    attendu = checksum_api.split(":", 1)[1].strip().lower() if checksum_api else ""
    if not attendu:
        print("Checksum absent de la reponse API : verification impossible.")
        return
    sha = hashlib.sha256()
    with open(chemin, "rb") as f:
        for bloc in iter(lambda: f.read(1024 * 1024), b""):
            sha.update(bloc)
    obtenu = sha.hexdigest()
    if obtenu == attendu:
        print("Checksum sha256 OK :", obtenu[:16] + "...")
    else:
        print("ALERTE checksum : obtenu " + obtenu[:16] + "... attendu " + attendu[:16] + "...")
        print("Fichier corrompu ou modifie : supprimer et retélécharger.")


def telecharger(dataset_id, cle, dossier):
    """POST /datasets/:id/download puis telechargement direct depuis le stockage."""
    print("Creation de la session de telechargement...")
    donnees = requete(BASE_URL + "/datasets/" + dataset_id, cle, methode="POST", corps={})
    url = donnees.get("downloadUrl")
    if not url:
        raise ErreurAPI("Reponse sans downloadUrl : " + json.dumps(donnees)[:300])
    nom = donnees.get("filename") or (dataset_id + ".tar.gz")
    os.makedirs(dossier, exist_ok=True)
    chemin = os.path.join(dossier, nom)
    print("Telechargement de", nom, "vers", dossier)
    debut = time.time()
    telecharges = 0
    with urllib.request.urlopen(urllib.request.Request(url), timeout=120) as reponse, \
            open(chemin, "wb") as f:
        total = reponse.headers.get("Content-Length")
        total = int(total) if total else None
        while True:
            bloc = reponse.read(1024 * 1024)
            if not bloc:
                break
            f.write(bloc)
            telecharges += len(bloc)
            if total:
                pct = 100.0 * telecharges / total
                print("\r  " + str(round(pct, 1)) + "% (" + str(round(telecharges / 1e6, 1)) + " Mo)",
                      end="", flush=True)
    duree = time.time() - debut
    print("\nTermine : " + str(round(telecharges / 1e6, 1)) + " Mo en " + str(round(duree)) + " s")
    _verifier_sha256(chemin, donnees.get("checksum", ""))
    print("Fichier :", chemin)
    return chemin


def main():
    parser = argparse.ArgumentParser(description="Client API Mozilla Data Collective")
    sous = parser.add_subparsers(dest="commande", required=True)

    p_info = sous.add_parser("info", help="Details d'un dataset")
    p_info.add_argument("dataset_id")

    p_dl = sous.add_parser("download", help="Telecharger un dataset (conditions a accepter sur le web)")
    p_dl.add_argument("dataset_id")
    p_dl.add_argument("--out", default="data/audio", help="Dossier de destination (defaut: data/audio)")

    args = parser.parse_args()
    try:
        cle = charger_cle()
        if args.commande == "info":
            afficher_infos(args.dataset_id, cle)
        elif args.commande == "download":
            afficher_infos(args.dataset_id, cle)
            telecharger(args.dataset_id, cle, args.out)
    except ErreurAPI as e:
        print("ERREUR :", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
