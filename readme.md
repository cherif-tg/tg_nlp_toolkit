# Kabiyè-Éwé NLP Toolkit

Toolkit NLP open-source : traduction automatique français ↔ éwé (+ ASR conditionnel, extension kabiyè en option).

## Documentation

- `docs/00-cahier-des-charges-original.md` — cahier des charges v1.0
- `docs/01-document-etude-realisation.md` — document d'étude et de réalisation v2.0 (référence)

## Structure

| Dossier | Rôle |
|---|---|
| `docs/` | Documents de projet (cahier des charges, étude/réalisation, datasheet, rapport d'évaluation) |
| `data/raw/` | Sources brutes, jamais modifiées |
| `data/processed/` | Corpus nettoyés (train/dev/test + domaine cible) |
| `data/licenses/` | Matrice des licences + justificatifs par source |
| `src/collect/` | Scripts de collecte |
| `src/clean/` | Nettoyage et normalisation |
| `src/augment/` | Back-translation + filtrage |
| `src/train/` | Fine-tuning (NLLB, Whisper) |
| `src/evaluate/` | Évaluation (chrF++, COMET, BLEU, WER) |
| `notebooks/` | Explorations et analyses |
| `models/` | Artefacts locaux (gitignorés) |
| `demo/` | Application Gradio |
| `tests/` | Tests unitaires |
| `scripts/` | Scripts one-shot (publication HF, etc.) |

## Infos projet

- **HuggingFace** : [cheriftenga](https://huggingface.co/cheriftenga)
- **Locuteurs natifs éwé** : l'utilisateur (éwé) + 1 personne à confirmer
- **Vérifications licences** : en cours par l'utilisateur (JW.org, OPUS, Bible éwé) — 13/08/2026
