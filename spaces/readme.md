---
title: Traducteur Francais - Ewe (Togo)
colorFrom: green
colorTo: blue
sdk: gradio
app_file: app.py
pinned: false
license: cc-by-nc-sa-4.0
short_description: Traduction automatique FR <-> EWE (NLLB + LoRA v2)
---

# Traducteur Francais <-> Ewe (Togo)

Demo publique du modele `cheriftenga/nllb-200-distilled-600M-ewe-lora-v2`
(NLLB-200-distilled-600M fine-tune LoRA **v2 bidirectionnel** sur le corpus
`cheriftenga/tg-nlp-toolkit-fr-ewe-v0.3`, 65 640 paires).

Projet : toolkit NLP pour les langues a faibles ressources du Togo.

## Utilisation

- Onglet **FR -> EWE** : ecris une phrase en francais, obtiens l'ewe.
- Onglet **EWE -> FR** : l'inverse.
- Le curseur **beam search** regle la qualite/vitesse (4 par defaut).

## Scores officiels (test de reference verifie, 241 paires)

| Direction | chrF++ | BLEU |
|---|---|---|
| FR -> EWE | 47,95 | 22,42 |
| EWE -> FR | 52,24 | 31,83 |

Scores mesures sur le test de reference verifie a 100 % (241 paires,
double validation par 2 locuteurs natifs independants).

## Licence

Modele sous CC-BY-NC-SA-4.0 (herite de NLLB, Meta AI) : usage non
commercial. Donnees : domaine public (Bible 1913, Segond 1910) + ODC-By
(OPUS NLLB).
