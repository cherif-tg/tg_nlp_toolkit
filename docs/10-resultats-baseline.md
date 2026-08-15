# Resultats de la baseline NLLB (zero-shot)

**Date** : 15/08/2026
**Modele** : `facebook/nllb-200-distilled-600M` (zero-shot, aucun entrainement)
**Jeu de test** : split test du corpus v0.3 (6 564 paires, jamais vues par le modele)
**Notebook** : `notebooks/01-baseline-nllb.ipynb`

## Scores

| Direction | chrF++ | BLEU |
|---|---|---|
| FR -> EWE | 34,96 | 11,38 |
| EWE -> FR | 33,76 | 13,53 |

## Exemples commentes

### FR -> EWE

1. FR : "Ils ont regardé, tout stupéfaits,"
   Ref : "Esi wokpoe la, wofe nu ku, dzidzi fo wo, eye wosi"
   Pred : "Ame siwo katã nɔ afi ma la ƒe mo wɔ yaa eye woƒe mo wɔ yaa."
   -> Sens proche (tous ceux qui etaient la regardaient), formulation differente.

2. FR : "C'est une drôle de question, non ?"
   Ref : "Ðe biabia sia mele vevie ŋutɔ oa?"
   Pred : "Nyabiase ɖedzesi aɖee wònye, alo ɖe?"
   -> Bonne traduction (question etrange, n'est-ce pas).

3. FR : "Les Juifs enterraient leurs morts tout de suite après leur décès..."
   Ref : "Yudatɔwo ɖia woƒe ame kukuwo kaba, zi geɖe le ŋkeke si dzi amea ku le."
   Pred : "Yudatɔwo nɔa woƒe ame kukuwo ɖi ge le woƒe ku megbe enumake, zi geɖe le ŋkeke ma ke dzi."
   -> Tres proche de la reference (sens complet preserve).

### EWE -> FR

1. EWE : "Esi wokpoe la, wofe nu ku, dzidzi fo wo, eye wosi"
   Ref : "Ils ont regardé, tout stupéfaits,"
   Pred : "Mais ils les repoussèrent, et ils se mirent à cracher, à crier..."
   -> Contresens (le modele a mal interprete l'ewe ancien).

2. EWE : "Ðe biabia sia mele vevie ŋutɔ oa?"
   Ref : "C'est une drôle de question, non ?"
   Pred : "Cette question n'est-elle pas très importante ?"
   -> Sens partiellement preserve (question sur l'importance).

3. EWE : "Yudatɔwo ɖia woƒe ame kukuwo kaba, zi geɖe le ŋkeke si dzi amea ku le."
   Ref : "Les Juifs enterraient leurs morts tout de suite après leur décès..."
   Pred : "Et les Juifs ensevelirent les morts selon la coutume d'un jour."
   -> Bonne traduction (sens proche, style different).

## Interpretation

- **chrF++ ~35** : niveau "le modele se debrouille" pour du zero-shot en ewe.
  Il connait le vocabulaire (surtout religieux/ancien) mais fait des erreurs de
  formulation et quelques contresens, surtout sur l'ewe ancien (orthographe 1913).
- **BLEU bas (11-14)** : normal pour une langue a faibles ressources ; BLEU est
  tres strict sur les mots exacts, et l'ewe 1913 differe de l'ewe moderne vu par NLLB.
- Ces scores sont la **reference a battre** : le fine-tuning LoRA (notebook 2,
  sur train v0.3 = 52 512 paires) doit les depasser, surtout en chrF++.
- Objectif raisonnable pour le fine-tuning : **chrF++ 40+** (gain de +5 points
  minimum pour valider l'utilite du corpus).

## Prochaines etapes

1. Fine-tuning LoRA (notebook 2) sur T4 : ~20-40 min pour 3 epoques.
2. Comparaison baseline vs fine-tune sur le **test de reference verifie** (300 paires,
   2 verificateurs) une fois les locuteurs renvoyes leurs fichiers.
3. Publication du modele sur HuggingFace (cheriftenga/nllb-200-distilled-600M-ewe-lora).
