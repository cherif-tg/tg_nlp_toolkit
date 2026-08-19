# Résultats du fine-tuning v2 (bidirectionnel FR <-> EWE)

**Date** : 19/08/2026
**Modèle de base** : `facebook/nllb-200-distilled-600M`
**Méthode** : LoRA (r=16, alpha=32, q_proj/v_proj), 3 époques, entraînement
**bidirectionnel** (paires inversées)
**Données d'entraînement** : train v0.3 doublé (2 x 52 512 = 105 024 exemples)
+ dev doublé (13 128)
**Jeu de test** : test de référence vérifié (241 paires, double validation
humaine)
**Notebook** : `notebooks/02b-finetune-lora-v2.ipynb`
**Modèle publié** : `cheriftenga/nllb-200-distilled-600M-ewe-lora-v2`

## Scores officiels (test de référence vérifié, 241 paires)

| Direction | Baseline | v1 (unidir.) | v2 (bidir.) |
|---|---|---|---|
| FR -> EWE chrF++ | 37,22 | 47,39 | **47,95** |
| FR -> EWE BLEU | 11,17 | 22,20 | **22,42** |
| EWE -> FR chrF++ | 38,14 | 37,52 | **52,24** |
| EWE -> FR BLEU | 14,92 | 15,15 | **31,83** |

## Analyse

- **Objectif EWE -> FR >= 37 : ATTEINT (52,24, +14,72 vs v1)**. Le
  bidirectionnel a résolu le point faible de la v1 : le modèle sait
  désormais comprendre l'éwé, plus seulement le produire.
- **Objectif FR -> EWE >= 41 : ATTEINT (47,95)**. Le gain de la v1 est
  conservé (légèrement amélioré : +0,56 chrF++).
- Les deux directions sont maintenant au même niveau (~48 et ~52 chrF++),
  ce qui est remarquable pour une langue à faibles ressources.
- Gain total vs baseline : +10,73 chrF++ (FR->EWE) et +14,10 chrF++ (EWE->FR).

## Interprétation

- L'entraînement bidirectionnel est le standard pour un traducteur : chaque
  exemple enseigne à la fois à comprendre et à produire chaque langue.
- La stagnation de la v1 en EWE -> FR venait bien d'un entraînement
  unidirectionnel (labels uniquement en éwé), comme anticipé dans le plan v2.
- Le corpus v0.3 démontre une nouvelle fois son utilité : un gain de
  +14 chrF++ sur la direction inverse est un résultat fort.

## Limites connues

- Même corpus que la v1 : l'éwé 1913 (orthographe ancienne) reste mélangé à
  l'éwé moderne NLLB.
- Domaine principalement religieux/généraliste ; les grilles
  santé/administration sont en cours de traduction manuelle.
- Scores mesurés sur 241 paires (référence vérifiée) : robuste, mais le
  benchmark sur un plus grand volume vérifié renforcerait la confiance.

## Prochaines étapes

1. Benchmark Google Translate sur les 241 paires (comparaison « nous vs
   Google » pour le mémoire).
2. MTPE interne : brouillons de notre modèle -> corrections des locuteurs
   (grilles santé/administration) -> boucle vertueuse.
3. Phase audio (ASR) : enregistrements alignés des phrases traduites.
