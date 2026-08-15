---
title: Traducteur Francais - Ewe (Togo)
colorFrom: green
colorTo: blue
sdk: gradio
app_file: app.py
pinned: false
license: cc-by-nc-sa-4.0
short_description: Traduction automatique FR <-> EWE (NLLB + LoRA)
---

# Traducteur Francais <-> Ewe (Togo)

Demo publique du modele `cheriftenga/nllb-200-distilled-600M-ewe-lora`
(NLLB-200-distilled-600M fine-tune LoRA sur le corpus
`cheriftenga/tg-nlp-toolkit-fr-ewe-v0.3`, 65 640 paires).

Projet : toolkit NLP pour les langues a faibles ressources du Togo.

## Utilisation

- Onglet **FR -> EWE** : ecris une phrase en francais, obtiens l'ewe.
- Onglet **EWE -> FR** : l'inverse.
- Le curseur **beam search** regle la qualite/vitesse (4 par defaut).

## Scores (test v0.3)

| Direction | chrF++ | BLEU |
|---|---|---|
| FR -> EWE | 41,83 | 18,71 |
| EWE -> FR | 33,35 | 13,69 |

Scores officiels a venir sur le test de reference verifie par des
locuteurs natifs (300 paires).

## Licence

Modele sous CC-BY-NC-SA-4.0 (herite de NLLB, Meta AI) : usage non
commercial. Donnees : domaine public (Bible 1913, Segond 1910) + ODC-By
(OPUS NLLB).
