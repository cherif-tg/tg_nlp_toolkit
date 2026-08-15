# Plan v2 du fine-tuning - bidirectionnel FR <-> EWE

**Statut** : planifie (implementation non lancee)
**Date du plan** : 15/08/2026
**Motif** : la v1 (unidirectionnelle FR -> EWE) a fait progresser FR -> EWE
(+6,87 chrF++) mais pas EWE -> FR (-0,41 chrF++).

## 1. Contexte et objectif

Scores v1 (notebook 2, LoRA r=16, 3 epoques, train 52 512 paires) :

| Direction | Baseline | v1 fine-tune | Gain v1 |
|---|---|---|---|
| FR -> EWE | 34,96 | 41,83 | +6,87 |
| EWE -> FR | 33,76 | 33,35 | -0,41 |

**Objectif v2** :
- EWE -> FR : viser **>= 37-38 chrF++** (gain >= +4 par rapport a la baseline)
- FR -> EWE : **ne pas perdre le gain** (garder >= 41)

**Explication du probleme v1** : le fine-tuning a appris au modele a
PRODUIRE de l'ewe (les labels d'entrainement etaient en ewe). La
comprehension de l'ewe (direction inverse) n'a pas progresse.

## 2. Approche retenue : entrainement bidirectionnel

Doubler le jeu d'entrainement en **inversant les paires** :

```
exemple 1 : fr  -> ewe   (source = francais, labels = ewe)
exemple 2 : ewe -> fr    (source = ewe, labels = francais)   <- inverse
```

- Train : 2 x 52 512 = **105 024 paires**
- Dev : 2 x 6 564 = 13 128 paires (meme principe, pour suivre la loss
  des deux directions)
- Test : inchange (6 564 paires) ; on mesure les DEUX directions avec
  les cellules d'evaluation deja presentes dans le notebook 2.

**Pourquoi ca marche** : le modele apprend a la fois a comprendre et a
produire chaque langue. C'est le standard pour un traducteur
bidirectionnel (NLLB lui-meme est entraine sur des paires orientees
dans les deux sens).

## 3. Technique : tokenisation par exemple

Contrainte technique : NLLB encode la langue via `tokenizer.src_lang`,
qui doit etre la langue SOURCE de chaque exemple. En v1, la fonction
`tokeniser(sources, cibles)` fixait une seule direction. En v2, chaque
exemple porte sa direction :

```python
def tokeniser_exemple(source, cible, code_src, code_tgt):
    tokenizer.src_lang = code_src
    enc = tokenizer(source, max_length=128, truncation=True,
                    return_tensors="pt")
    tokenizer.src_lang = code_tgt
    labels = tokenizer(cible, max_length=128, truncation=True,
                       return_tensors="pt")
    enc["labels"] = labels["input_ids"].clone()
    enc["labels"][enc["labels"] == tokenizer.pad_token_id] = -100
    return {k: v.numpy() for k, v in enc.items()}
```

Construction du Dataset (les deux directions melangees) :

```python
paires = []
for fr, ee in zip(train["fr"], train["ewe"]):
    paires.append(("fra_Latn", "ewe_Latn", fr, ee))   # fr -> ewe
    paires.append(("ewe_Latn", "fra_Latn", ee, fr))   # ewe -> fr
train_ds = Dataset.from_list(
    [tokeniser_exemple(s, c, a, b) for a, b, s, c in paires]
)
```

## 4. Hyperparametres (reprise de la v1)

| Parametre | Valeur | Note |
|---|---|---|
| LoRA r | 16 | identique v1 |
| lora_alpha | 32 | identique v1 |
| lora_dropout | 0.05 | identique v1 |
| target_modules | q_proj, v_proj | identique v1 |
| epoques | 3 | temps double (~1 h sur T4) |
| batch | 8 | identique v1 |
| lr | 3e-4 | identique v1 |
| warmup | 200 | identique v1 |
| fp16 | oui | identique v1 |
| beam search eval | 4 | identique v1 |

Temps estime sur T4 : **60-90 min** (105 k paires au lieu de 52 k).

## 5. Protocole d'evaluation (comparaison complete)

Apres l'entrainement, mesurer et comparer les 4 chiffres :

| | Baseline | v1 | v2 (attendu) |
|---|---|---|---|
| FR -> EWE chrF++ | 34,96 | 41,83 | >= 41 |
| FR -> EWE BLEU | 11,38 | 18,71 | >= 18 |
| EWE -> FR chrF++ | 33,76 | 33,35 | >= 37 |
| EWE -> FR BLEU | 13,53 | 13,69 | >= 16 |

Tableau a jour dans `docs/11-resultats-finetune-lora.md` (section v2
a ajouter).

## 6. Risques et parades

| Risque | Parade |
|---|---|
| FR -> EWE regresse (oubli du gain v1) | Si chrF++ < 41 : revenir a unidirectionnel ou augmenter la proportion de paires fr->ewe (ex. 2/3 - 1/3) |
| Temps d'entrainement trop long sur T4 (session Colab qui expire) | Segmenter : sauvegarder le checkpoint par epoque (deja actif via save_strategy="epoch") et reprendre si besoin |
| Perte de qualite sur l'ewe 1913 | Inchange par rapport a v1 (meme corpus) |

## 7. Ordre des taches

1. [ ] Creer `notebooks/02b-finetune-lora-v2.ipynb` (nouveau notebook,
       on GARDE le 02 v1 intact pour reproductibilite)
2. [ ] Tokenisation bidirectionnelle + Dataset double
3. [ ] Entrainement sur Colab (T4) : ~60-90 min
4. [ ] Evaluation des 2 directions + comparaison des 4 scores
5. [ ] Publier le modele v2 : `cheriftenga/nllb-200-distilled-600M-ewe-lora-v2`
6. [ ] Mettre a jour la model card (scores v2) et les docs de resultats
7. [ ] (Plus tard) Scores officiels sur le test de reference 300 paires

## 8. Decisions a confirmer

- [ ] Nom du modele v2 : `nllb-200-distilled-600M-ewe-lora-v2` (propose)
- [ ] Notebook separe 02b (propose) vs modification du 02
- [ ] Si le gain EWE->FR est faible malgre le bidirectionnel : piste
      alternative = ajouter des donnees monolingues ewe (denoising) -
      a evaluer apres les resultats v2
