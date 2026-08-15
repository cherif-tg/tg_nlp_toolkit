# Resultats du fine-tuning LoRA (comparaison avec la baseline)

**Date** : 15/08/2026
**Modele de base** : `facebook/nllb-200-distilled-600M`
**Methode** : LoRA (rang 16, alpha 32, projections q_proj/v_proj), 3 epoques
**Donnees d'entrainement** : train v0.3 (52 512 paires) + dev v0.3 (6 564 paires)
**Jeu de test** : split test du corpus v0.3 (6 564 paires, jamais vues)
**Notebook** : `notebooks/02-finetune-lora.ipynb`

## Comparaison des scores (FR -> EWE)

| Methode | chrF++ | BLEU |
|---|---|---|
| Baseline NLLB zero-shot | 34,96 | 11,38 |
| **Fine-tuning LoRA** | **41,83** | **18,71** |
| **Gain** | **+6,87** | **+7,33** |

Le gain de +6,87 en chrF++ depasse l'objectif fixe (+5 points minimum pour
valider l'utilite du corpus). Le BLEU progresse encore plus (+7,33), ce qui
signifie que les traductions fines sont beaucoup plus proches des references.

## Exemples commentes (FR -> EWE, apres fine-tuning)

1. FR : "Ils ont regardé, tout stupéfaits,"
   Ref : "Esi wokpoe la, wofe nu ku, dzidzi fo wo, eye wosi"
   Pred : "Wo- kpoe, eye wofe mo wu wo, eye wofe mo wu wo"
   -> Sens correct ("ils le virent, leur visage changea"), mais redondance
   (meme groupe repete deux fois) et artefact de tokenisation "Wo- ".
   La version zero-shot etait plus eloignee du sens.

2. FR : "C'est une drôle de question, non ?"
   Ref : "Ðe biabia sia mele vevie ŋutɔ oa?"
   Pred : "Ðe biabia sia mewɔ nuku ŋutɔ oa?"
   -> Traduction quasi parfaite : "Cette question est vraiment drole, non ?"
   La tournure est idiomatique, la structure interrogative est correcte.

3. FR : "Les Juifs enterraient leurs morts tout de suite après leur décès..."
   Ref : "Yudatɔwo ɖia woƒe ame kukuwo kaba, zi geɖe le ŋkeke si dzi amea ku le."
   Pred : "Yudatɔwo ɖia woƒe ame kukuwo enumake le woƒe ku megbe, zi geɖe le ŋkeke ma ke dzi."
   -> Tres proche de la reference : paraphrase presque exacte avec le bon
   vocabulaire (enumake = immediatement, ku megbe = apres leur mort).

## Interpretation

- Le corpus v0.3 apporte un **gain reel et significatif** : le fine-tuning
  adapte NLLB a notre ewe (mariage ewe 1913 + NLLB moderne) et au style Segond.
- Les exemples montrent une amelioration qualitative : tournures idiomatiques,
  vocabulaire plus juste, structure syntaxique plus naturelle.
- Il reste des defauts connus : redondances occasionnelles, artefacts de
  tokenisation (tirets) — a surveiller mais non bloquants.

## Limites connues

- **Scores sur le test v0.3 (approx.)** : le test set n'est pas encore verifie
  par des locuteurs natifs. Les scores finaux officiels seront calcules sur le
  **test de reference verifie** (300 paires, 2 verificateurs, en cours).
- Direction EWE -> FR : a mesurer apres fine-tuning (cellule ajoutee au
  notebook 2).

## Prochaines etapes

1. Publier le modele sur HuggingFace : `cheriftenga/nllb-200-distilled-600M-ewe-lora`
   (voir cellule 12 du notebook 2 : notebook_login puis push_to_hub).
2. Calculer les scores officiels sur le test de reference 300 paires (apres
   retour des verificateurs).
3. Passer le dataset v0.3 en public une fois la reference verifiee.
4. Demo Gradio + API REST (phase P3).
