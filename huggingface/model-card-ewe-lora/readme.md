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

Modele de traduction automatique **francais <-> ewe** (ewe, langue gbe
parlee au Togo et au Ghana), obtenu par **fine-tuning LoRA** de
`facebook/nllb-200-distilled-600M` sur le corpus
`cheriftenga/tg-nlp-toolkit-fr-ewe-v0.3`.

Projet : toolkit NLP pour langues a faibles ressources du Togo (ewe, kabiyè).
Ce modele est la premiere pierre : un traducteur FR <-> EWE adapte a l'ewe
du Togo (littoral de Lome) et au domaine sante/administration (grilles
thematiques en cours de traduction manuelle).

## Resultats

Scores sur le split test du corpus v0.3 (6 564 paires, jamais vues pendant
l'entrainement). **Attention** : ce test set est approxime (alignement
automatique) ; les scores officiels seront recalcules sur un test de
reference verifie par des locuteurs natifs (300 paires, 2 verificateurs).

| Methode | Direction | chrF++ | BLEU |
|---|---|---|---|
| Baseline NLLB zero-shot | FR -> EWE | 34,96 | 11,38 |
| **Fine-tuning LoRA** | **FR -> EWE** | **41,83** | **18,71** |
| Baseline NLLB zero-shot | EWE -> FR | 33,76 | 13,53 |
| Fine-tuning LoRA | EWE -> FR | (en cours de mesure) | - |

Gain FR -> EWE : **+6,87 chrF++** et **+7,33 BLEU** par rapport au
zero-shot — le corpus apporte un gain reel et significatif.

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
- **Test approxime** : les scores cites utilisent un test set auto-aligne,
  pas encore verifie par des locuteurs. Un test de reference (300 paires,
  double verification) est en cours.
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
