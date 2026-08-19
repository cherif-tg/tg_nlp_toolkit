---
language:
- fr
- ewe
license: cc-by-nc-sa-4.0
tags:
- translation
- nllb
- lora
- peft
- ewe
- low-resource
- seq2seq
- africa
datasets:
- cheriftenga/tg-nlp-toolkit-fr-ewe-v0.3
base_model: facebook/nllb-200-distilled-600M
pipeline_tag: translation
library_name: peft
---

# NLLB-200-distilled-600M fine-tune LoRA FR <-> EWE

> **Note** : une version **v2 bidirectionnelle** est disponible et recommandee :
> [cheriftenga/nllb-200-distilled-600M-ewe-lora-v2](https://huggingface.co/cheriftenga/nllb-200-distilled-600M-ewe-lora-v2).
> Elle ameliore fortement le sens EWE -> FR (52,24 chrF++ contre 37,52).

Modele de traduction automatique **francais <-> ewe** (ewe, langue gbe
parlee au Togo et au Ghana), obtenu par **fine-tuning LoRA** de
`facebook/nllb-200-distilled-600M` sur le corpus
`cheriftenga/tg-nlp-toolkit-fr-ewe-v0.3`.

Projet : toolkit NLP pour langues a faibles ressources du Togo (ewe, kabiyè).
Ce modele est la premiere pierre : un traducteur FR <-> EWE adapte a l'ewe
du Togo (littoral de Lome) et au domaine sante/administration (grilles
thematiques en cours de traduction manuelle).

## Resultats

### Scores officiels (test de reference verifie, 241 paires)

Scores mesures sur le **test de reference verifie a 100 %** (241 paires,
double validation par 2 locuteurs natifs independants, 97 % de concordance
entre verificateurs, arbitrage final) :

| Methode | Direction | chrF++ | BLEU |
|---|---|---|---|
| Baseline NLLB zero-shot | FR -> EWE | 37,22 | 11,17 |
| **Fine-tuning LoRA** | **FR -> EWE** | **47,39** | **22,20** |
| Baseline NLLB zero-shot | EWE -> FR | 38,14 | 14,92 |
| Fine-tuning LoRA | EWE -> FR | 37,52 | 15,15 |

**Gain FR -> EWE : +10,17 chrF++ et +11,03 BLEU** par rapport au zero-shot :
le corpus apporte un gain reel, fort et significatif.

**EWE -> FR** : le modele v1 n'a ete entraine que dans le sens FR -> EWE ;
le sens inverse ne progresse donc pas (leger recul en chrF++, +0,23 BLEU).
Le fine-tuning v2 (bidirectionnel, paires inversees) vise a corriger ce
point faible.

### Scores sur le split test auto-aligne (6 564 paires, pour comparaison)

| Methode | Direction | chrF++ | BLEU |
|---|---|---|---|
| Baseline NLLB zero-shot | FR -> EWE | 34,96 | 11,38 |
| Fine-tuning LoRA | FR -> EWE | 41,83 | 18,71 |
| Baseline NLLB zero-shot | EWE -> FR | 33,76 | 13,53 |
| Fine-tuning LoRA | EWE -> FR | 33,35 | 13,69 |

### Exemples (FR -> EWE, apres fine-tuning)

| Francais | Reference | Prediction |
|---|---|---|
| C'est une drôle de question, non ? | Ðe biabia sia mele vevie ŋutɔ oa? | Ðe biabia sia mewɔ nuku ŋutɔ oa? |
| Les Juifs enterraient leurs morts tout de suite après leur décès, en général dans la journée même. | Yudatɔwo ɖia woƒe ame kukuwo kaba, zi geɖe le ŋkeke si dzi amea ku le. | Yudatɔwo ɖia woƒe ame kukuwo enumake le woƒe ku megbe, zi geɖe le ŋkeke ma ke dzi. |

## Utilisation

Le modele publie est l'**adaptateur LoRA** uniquement : il doit etre charge
sur le modele de base avec `peft`.

```python
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from peft import PeftModel

REPO = "cheriftenga/nllb-200-distilled-600M-ewe-lora"

tokenizer = AutoTokenizer.from_pretrained(REPO)
base = AutoModelForSeq2SeqLM.from_pretrained("facebook/nllb-200-distilled-600M")
model = PeftModel.from_pretrained(base, REPO)
model.eval()

def traduire(texte, src="fra_Latn", tgt="ewe_Latn"):
    tokenizer.src_lang = src
    enc = tokenizer(texte, return_tensors="pt", truncation=True, max_length=128)
    gen = model.generate(
        **enc,
        forced_bos_token_id=tokenizer.convert_tokens_to_ids(tgt),
        max_new_tokens=128,
        num_beams=4,
    )
    return tokenizer.batch_decode(gen, skip_special_tokens=True)[0]

print(traduire("Comment vas-tu ?"))
```

Codes NLLB : `fra_Latn` (francais), `ewe_Latn` (ewe).

## Donnees d'entrainement

Corpus `cheriftenga/tg-nlp-toolkit-fr-ewe-v0.3` (65 640 paires :
train 52 512 / dev 6 564 / test 6 564), assemble depuis :

| Source | Paires | Licence |
|---|---|---|
| Bible ewe 1913 + Segond 1910 (alignement verset a verset) | ~16 000 | domaine public |
| OPUS NLLB ee-fr v1 (filtre qualite : ewe-ness, liste noire) | ~49 600 | ODC-By (attribution requise) |

## Limitations

- **Ewe ancien vs moderne** : une partie des donnees vient de la Bible
  1913 (orthographe ancienne). Le modele herite de ce melange ; la cible
  long terme est l'ewe parle actuel (Lome).
- **Direction EWE -> FR** : le modele v1 est unidirectionnel (entraine
  uniquement FR -> EWE) ; le sens inverse ne progresse pas (leger recul en
  chrF++). Le fine-tuning v2 (bidirectionnel) vise a le corriger.
- **Defauts connus** : redondances occasionnelles, artefacts de tokenisation
  (ex. "Wo- kpoe").
- **Domaine** : principalement religieux/generaliste ; les domaines
  sante/administration seront couverts par la traduction manuelle des
  grilles thematiques (en cours).

## Licence et attribution

- **Modele** : `cc-by-nc-sa-4.0` — licence heritee du modele de base
  NLLB-200 (Meta AI, CC-BY-NC-SA-4.0). Usage **non commercial** sans
  accord distinct.
- **Donnees** : domaine public (Bible 1913, Segond 1910) + ODC-By
  (OPUS/NLLB — attribution : <https://opus.nlpl.eu/>).

## Auteurs

- TENGA Cherif Abdel Azize (Ingenieur IA)

## Citation

```bibtex
@misc{tengue2026ewelora,
  title={NLLB-200-distilled-600M fine-tune LoRA FR-EWE},
  author={Tengue, Cherif},
  year={2026},
  howpublished={\url{https://huggingface.co/cheriftenga/nllb-200-distilled-600M-ewe-lora}}
}
```
