# Tests du projet

Tests automatises (sans telecharger le modele : la traduction est
simulee). Chaque fichier se lance independamment.

## Lancement

```bash
python tests/test_api.py        # API REST : routes, validation, redirection
python tests/test_cli.py        # CLI batch : CSV, colonnes, erreurs, mode API
python tests/test_demo_api.py   # demo Gradio : payload du mode API
```

Ou tout d'un coup (PowerShell) :

```powershell
python tests/test_api.py; python tests/test_cli.py; python tests/test_demo_api.py
```

## Ce que couvre chaque fichier

| Fichier | Couverture |
|---|---|
| `test_api.py` | /health, /translate (2 sens), langues invalides, src==tgt, texte vide, champ manquant, redirection / -> /docs, /docs accessible |
| `test_cli.py` | traduction d'un CSV, detection auto de colonne, colonne/fichier introuvables, src==tgt, payload du mode API |
| `test_demo_api.py` | mode API de la demo : conversion des libelles (Francais/Ewe) en codes (fr/ewe) |

## Prerequis

- Python 3.11+
- Paquets : `fastapi`, `uvicorn`, `httpx`, `pandas`, `gradio`, `peft`,
  `torch`, `transformers`

## Pourquoi un dossier tests/ ?

- Les tests font partie du projet : versionnes, relancables a tout moment
  apres une modification (regression).
- Le dossier `.openclaw/tmp/` est ignore par git (brouillon local) :
  ce n'est pas un endroit pour du code durable.
- Structure standard : on pourra brancher pytest ou une CI plus tard
  sans rien deplacer.
