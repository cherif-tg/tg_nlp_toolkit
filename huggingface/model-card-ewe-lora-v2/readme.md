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
- bidirectional
datasets:
- cheriftenga/tg-nlp-toolkit-fr-ewe-v0.3
base_model: facebook/nllb-200-distilled-600M
pipeline_tag: translation
library_name: peft
---

# NLLB-200-distilled-600M fine-tune LoRA v2 FR <-> EWE (bidirectionnel)

Modèle de traduction automatique **français <-> éwé** (ewe, langue gbe
parlée au Togo et au Ghana), obtenu par **fine-tuning LoRA bidirectionnel**
de `facebook/nllb-200-distilled-600M` sur le corpus
`cheriftenga/tg-nlp-toolkit-fr-ewe-v0.3`.

**Version v2** : contrairement à la v1 (unidirectionnelle FR -> EWE), ce
modèle a été entraîné dans les **deux sens** (paires inversées). Il excelle
dans les deux directions, et corrige le point faible de la v1
(la compréhension de l'éwé, sens EWE -> FR).

Projet : toolkit NLP pour langues à faibles ressources du Togo (ewe, kabiyè).
Ce modèle est la version recommandée du traducteur FR <-> EWE adapté à
l'éwé du Togo (littoral de Lomé).

## Résultats

### Scores officiels (test de référence vérifié, 241 paires)

Scores mesurés sur le **test de référence vérifié à 100 %** (241 paires,
double validation par 2 locuteurs natifs indépendants, 97 % de concordance) :

| Direction | Baseline zero-shot | v1 (unidir.) | **v2 (bidir.)** |
|---|---|---|---|
| FR -> EWE chrF++ / BLEU | 37,22 / 11,17 | 47,39 / 22,20 | **47,95 / 22,42** |
| EWE -> FR chrF++ / BLEU | 38,14 / 14,92 | 37,52 / 15,15 | **52,24 / 31,83** |

**Gains v2 vs baseline** :
- FR -> EWE : **+10,73 chrF++** / +11,25 BLEU
- EWE -> FR : **+14,10 chrF++** / +16,91 BLEU

**Gain majeur de la v2** : le sens EWE -> FR passe de 37,52 (v1, stagnation)
à **52,24 chrF++** — le bidirectionnel a appris au modèle à comprendre
l'éwé en plus de le produire. Les deux directions sont désormais au même
niveau (~48 et ~52 chrF++).

### Sur le split test auto-aligné (6 564 paires, pour comparaison)

| Direction | Baseline | v1 | v2 |
|---|---|---|---|
| FR -> EWE chrF++ | 34,96 | 41,83 | (voir officiels) |
| EWE -> FR chrF++ | 33,76 | 33,35 | (voir officiels) |

### Benchmark Google Translate (241 paires)

La v2 surpasse Google Translate dans les deux directions :

| Direction | LoRA v2 | Google Translate | Avance |
|---|---|---|---|
| FR -> EWE chrF++ | 47,95 | 38,62 | +9,33 |
| EWE -> FR chrF++ | 52,24 | 49,86 | +2,38 |

Détail : [benchmark](https://github.com/cherif-tg/tg_nlp_toolkit/blob/main/docs/13-benchmark-google-translate.md).

## Utilisation

Le modèle publié est l'**adaptateur LoRA** uniquement : il doit être chargé
sur le modèle de base avec `peft`.

```python
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from peft import PeftModel

REPO = "cheriftenga/nllb-200-distilled-600M-ewe-lora-v2"

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

print(traduire("Comment vas-tu ?"))  # FR -> EWE
print(traduire("Nukae nye nyatefe?", src="ewe_Latn", tgt="fra_Latn"))  # EWE -> FR
```

Codes NLLB : `fra_Latn` (français), `ewe_Latn` (ewe).

## Données d'entraînement

Corpus `cheriftenga/tg-nlp-toolkit-fr-ewe-v0.3`, **doublé par inversion des
paires** (bidirectionnel) :

- Train : 2 x 52 512 = **105 024 exemples** (fr->ewe + ewe->fr)
- Dev : 2 x 6 564 = 13 128 exemples
- Hyperparamètres LoRA identiques à la v1 : r=16, alpha=32, dropout 0.05,
  target q_proj/v_proj, 3 époques, lr 3e-4.

| Source | Paires (avant inversion) | Licence |
|---|---|---|
| Bible ewe 1913 + Segond 1910 (alignement verset à verset) | ~16 000 | domaine public |
| OPUS NLLB ee-fr v1 (filtre qualité) | ~49 600 | ODC-By (attribution requise) |

## Limitations

- **Éwé ancien vs moderne** : une partie des données vient de la Bible 1913
  (orthographe ancienne). Le modèle hérite de ce mélange ; la cible long
  terme est l'éwé parlé actuel (Lomé).
- **Défauts connus** : redondances occasionnelles, artefacts de tokenisation.
- **Domaine** : principalement religieux/généraliste ; les domaines
  santé/administration seront couverts par la traduction manuelle des
  grilles thématiques (en cours).
- **Évaluation** : les scores officiels sont mesurés sur le split
  `reference` vérifié (241 paires) du dataset, pas sur le split auto-aligné.

## Licence et attribution

- **Modèle** : `cc-by-nc-sa-4.0` - licence héritée du modèle de base
  NLLB-200 (Meta AI, CC-BY-NC-SA-4.0). Usage **non commercial** sans
  accord distinct.
- **Données** : domaine public (Bible 1913, Segond 1910) + ODC-By
  (OPUS/NLLB - attribution : <https://opus.nlpl.eu/>).

## Auteurs

- TENGA Cherif Abdel Azize (Ingénieur IA)

## Citation

```bibtex
@misc{tengue2026ewelorav2,
  title={NLLB-200-distilled-600M fine-tune LoRA v2 FR-EWE (bidirectionnel)},
  author={Tengue, Cherif},
  year={2026},
  howpublished={\url{https://huggingface.co/cheriftenga/nllb-200-distilled-600M-ewe-lora-v2}}
}
```
