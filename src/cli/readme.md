# CLI de traduction batch FR <-> EWE

Traduit un fichier CSV entier (campagnes de messages, questionnaires,
listes de phrases) d'une langue a l'autre, en une commande.

## Usage

```bash
# Mode local : le CLI charge le modele lui-meme
python -m src.cli.translate --input messages.csv --src fr --tgt ewe --output messages_ewe.csv

# Mode API : le CLI appelle l'API REST deja lancee (modele deja charge)
python -m src.cli.translate --input messages.csv --src fr --tgt ewe --output messages_ewe.csv --api http://127.0.0.1:8000
```

Exemple Windows (PowerShell) :

```powershell
python -m src.cli.translate --input messages.csv --src fr --tgt ewe --output messages_ewe.csv --api http://127.0.0.1:8000
```

## Options

| Option | Role | Defaut |
|---|---|---|
| `--input` | Fichier CSV d'entree (obligatoire) | - |
| `--output` | Fichier CSV de sortie (obligatoire) | - |
| `--src` | Langue source : `fr` ou `ewe` | `fr` |
| `--tgt` | Langue cible : `ewe` ou `fr` | `ewe` |
| `--colonne` | Nom de la colonne de texte | auto |
| `--beams` | Taille du faisceau (beam search) | 4 |
| `--api` | URL de l'API REST | mode local |

## Format des fichiers

- Entree : CSV (virgule ou tabulation) avec une colonne de texte.
  La colonne est detectee automatiquement : `text`, `texte`, `fr`,
  `phrase`, `message`, `ewe` — ou la premiere colonne. Sinon,
  `--colonne mon_nom`.
- Sortie : toutes les colonnes d'origine + une colonne `traduction`.
- Les cellules vides restent vides (pas d'appel au modele).
- Les fichiers sont lus/ecrits en UTF-8.

Exemple :

messages.csv

```csv
message
Bonjour, comment vas-tu ?
Ou est le centre de sante ?
```

commande :

```bash
python -m src.cli.translate --input messages.csv --output messages_ewe.csv --api http://127.0.0.1:8000
```

resultat messages_ewe.csv

```csv
message,traduction
Bonjour, comment vas-tu ?,...
Ou est le centre de sante ?,...
```

## Mode local vs mode API

- **Mode local** : le CLI charge le modele (~1 min + 2,4 Go RAM).
  Utile quand l'API ne tourne pas, ou pour un usage ponctuel.
- **Mode API** : le CLI envoie chaque phrase a l'API (recommande si
  l'API tourne deja : un seul modele en memoire, le CLI reste leger).

## Comment ca marche (resume)

1. `argparse` analyse les arguments de la ligne de commande.
2. `lire_csv()` lit le fichier (virgule ou tabulation, UTF-8).
3. `choisir_colonne()` trouve la colonne de texte (auto ou `--colonne`).
4. Boucle : chaque ligne est traduite (`traduire_lot`), avec progression
   affichee toutes les 25 lignes.
5. `df["traduction"]` ajoute les resultats, `to_csv` ecrit la sortie.

## Tests

```bash
python .openclaw/tmp/test_cli.py
```

(6 tests : CSV, detection de colonne, erreurs, mode API — modele simule.)
