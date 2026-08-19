# Benchmark : notre modèle vs Google Translate

**Date** : 19/08/2026
**Jeu de test** : test de référence vérifié (241 paires, double validation
humaine, 97 % de concordance)
**Méthode** : traduction des 241 paires via Google Translate (bibliothèque
`deep-translator`, code éwé `ee`), métriques chrF++ / BLEU (sacrebleu),
même protocole que pour nos modèles.

## Résultats

| Direction | Modèle | chrF++ | BLEU |
|---|---|---|---|
| FR -> EWE | Baseline (zero-shot) | 37,22 | 11,17 |
| FR -> EWE | LoRA v1 | 47,39 | 22,20 |
| FR -> EWE | **LoRA v2** | **47,95** | **22,42** |
| FR -> EWE | Google Translate | 38,62 | 11,40 |
| EWE -> FR | Baseline (zero-shot) | 38,14 | 14,92 |
| EWE -> FR | LoRA v1 | 37,52 | 15,15 |
| EWE -> FR | **LoRA v2** | **52,24** | **31,83** |
| EWE -> FR | Google Translate | 49,86 | 26,61 |

## Conclusion

**Notre modèle v2 surpasse Google Translate dans les deux directions :**

- **FR -> EWE : +9,33 chrF++** d'avance (47,95 vs 38,62). Avance large :
  Google Translate est faible pour PRODUIRE de l'éwé, surtout l'éwé
  historique 1913 que notre corpus couvre.
- **EWE -> FR : +2,38 chrF++** d'avance (52,24 vs 49,86). Avance plus
  serrée : Google comprend bien l'éwé moderne (données massives), mais
  notre modèle reste devant.

## Lecture honnête (limites du benchmark)

1. **Biais de domaine** : la référence est à ~50 % de l'éwé biblique 1913
   (orthographe ancienne) + NLLB miné. C'est « notre terrain » : le
   benchmark mesure notre force sur le domaine que nous ciblons (éwé du
   Togo), pas une comparaison tous-domaines.
2. **Google est un généraliste** : sa valeur = couverture mondiale et éwé
   moderne. Notre valeur = open-source, hors-ligne, adapté à l'éwé du
   Togo (littoral de Lomé), et le kabiyè (que Google ne couvre pas).
3. **Méthode d'accès à Google** : `deep-translator` (accès non officiel à
   l'API web). Pour une publication académique stricte, une confirmation
   via l'API officielle Google Cloud serait plus rigoureuse.

## Piège documenté (à ne pas reproduire)

Le premier benchmark utilisait `googletrans`, qui **ne supporte pas
l'éwé** : le code `ee` est confondu avec l'estonien (`et`), produisant
des traductions en estonien et un BLEU ~0 (artefact). Corrigé en passant
à `deep-translator`, qui gère `ee` correctement.

## Argument pour le mémoire

« Un modèle fine-tuné sur un corpus open-source de 65 640 paires surpasse
Google Translate sur l'éwé du Togo (+9,33 chrF++ en production FR->EWE),
grâce à l'adaptation au registre biblique 1913 et au domaine ciblé. »
