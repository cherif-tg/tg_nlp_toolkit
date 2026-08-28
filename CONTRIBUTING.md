# Guide de contribution

Merci de votre intérêt pour le **Kabiyè-Éwé NLP Toolkit** ! Ce document
décrit comment contribuer au projet : signalement de problèmes,
environnement de développement, conventions et règles de licence.

## Périmètre du projet

Le projet fournit un pipeline complet de traduction automatique
**français ↔ éwé** (corpus, fine-tuning, API, démo, CLI), avec une
extension **kabiyè** prévue et une phase ASR conditionnelle. Les
contributions utiles couvrent notamment :

- qualité du corpus (nettoyage, vérification manuelle, nouvelles sources)
- évaluation (benchmarks, analyses d'erreurs)
- code (API, CLI, démo, scripts de nettoyage, notebooks)
- documentation et traduction de l'interface

## Signaler un problème ou proposer une idée

Ouvrez une [issue](https://github.com/cherif-tg/tg_nlp_toolkit/issues) en
précisant :

- pour un bug : étapes de reproduction, comportement attendu vs observé,
  environnement (OS, version de Python, GPU le cas échéant) ;
- pour une suggestion : le besoin visé et le contexte (pas seulement la
  solution technique) ;
- pour une question de données : la source concernée et sa licence.

## Environnement de développement

```bash
git clone https://github.com/cherif-tg/tg_nlp_toolkit.git
cd tg_nlp_toolkit
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate

pip install transformers peft torch sentencepiece
pip install fastapi "uvicorn[standard]" httpx gradio pandas
```

Les notebooks d'entraînement sont conçus pour **Google Colab** (GPU T4)
et chargent les données depuis ce dépôt — pas besoin de GPU en local pour
contribuer au code ou à la documentation.

## Organisation des branches

- `main` : branche stable, toujours fonctionnelle ; les jalons sont marqués
  par des tags (`v0.1.0`, ...).
- `feature/<sujet>` : branches de travail (ex. `feature/mtpe`).
- Une branche par sujet ; rebaser ou merger `main` régulièrement pour
  rester à jour.

## Conventions de commits

Commits courts et descriptifs, en français, éventuellement préfixés par le
module concerné :

```
API : gestion du paramètre src manquant
Notebook 02b : fine-tuning v2 bidirectionnel FR<->EWE
README : benchmark Google Translate ajouté
```

## Pull requests

1. Créez votre branche depuis `main` et travaillez-y.
2. Vérifiez que les tests passent avant de soumettre :

```bash
python tests/test_api.py        # API REST
python tests/test_cli.py        # CLI batch
python tests/test_demo_api.py   # démo (mode API)
```

3. Décrivez dans la PR : le changement, la motivation, et les tests exécutés.
4. Gardez les PR ciblées : une PR = un sujet.
5. Mettez à jour la documentation concernée (README, `docs/`, datasheets)
   si votre changement modifie un comportement documenté.

## Style de code

- Python : suivre la PEP 8, noms explicites en anglais ou en français
  cohérents avec l'existant.
- Pas d'emoji dans le code ni dans les fichiers sources.
- Scripts de nettoyage : privilégier des fonctions testables plutôt que du
  code procédural monolithique.

## Données et licences (important)

Le projet assemble des sources de statuts juridiques différents. Toute
contribution de données doit respecter ces règles :

- **Code** : MIT (ce dépôt).
- **Corpus** : CC0-1.0 (sources du domaine public : bibles 1913 / Segond
  1910) + ODC-By (OPUS NLLB, attribution requise).
- **Modèle** : CC-BY-NC-SA-4.0 (héritée de NLLB, Meta AI — usage non
  commercial).

Concrètement :

- Avant d'ajouter une nouvelle source de données, vérifiez sa licence et
  documentez la décision dans `data/licenses/` (voir
  `_template-decision.md` et `matrix.csv`). Une source sans licence claire
  ne sera pas acceptée.
- Conservez les attributions requises (ODC-By) dans les fichiers de
  données et les datasheets.
- Ne réintroduisez pas de contenu dont la licence est incompatible avec
  la redistribution (voir `data/licenses/readme.md` pour l'état des
  décisions, notamment les sources écartées comme JW300).

## Ressources utiles

- [README](readme.md) : présentation, scores, utilisation
- [Datasheet du corpus v0.3](data/processed/v0.3/DATASHEET.md) : qualité et
  limites documentées
- [Matrice des licences](data/licenses/matrix.csv) : statut juridique par
  source
- [Dataset HuggingFace](https://huggingface.co/datasets/cheriftenga/tg-nlp-toolkit-fr-ewe-v0.3)

## Questions

Ouvrez une issue avec le label `question` ou contactez le mainteneur
([@cherif-tg](https://github.com/cherif-tg)).
