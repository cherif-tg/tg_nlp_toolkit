"""Module d'inference : chargement du modele et traduction.

Ce module est le coeur technique reutilisable du projet :
- l'API REST (src/api/main.py) l'utilise pour repondre aux requetes ;
- la demo Gradio (demo/app.py) peut l'utiliser ;
- le futur CLI (phase P3) l'utilisera aussi.

Principe : le modele (base NLLB + adaptateur LoRA) est charge UNE SEULE
FOIS au demarrage (variable globale _MODELE), pas a chaque traduction.
Charger un modele prend du temps (telechargement + RAM) ; le recharger a
chaque requete rendrait l'API inutilisable.
"""

import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from peft import PeftModel

BASE = "facebook/nllb-200-distilled-600M"
ADAPTER = "cheriftenga/nllb-200-distilled-600M-ewe-lora"

# Codes de langue NLLB : chaque langue a un code interne au modele.
# "fr" -> fra_Latn, "ewe" -> ewe_Latn.
CODES_NLLB = {
    "fr": "fra_Latn",
    "ewe": "ewe_Latn",
}

_TOKENIZER = None
_MODELE = None


def charger_modele():
    """Charge le modele une seule fois (memoire cachee par variable globale)."""
    global _TOKENIZER, _MODELE
    if _MODELE is None:
        _TOKENIZER = AutoTokenizer.from_pretrained(ADAPTER)
        base = AutoModelForSeq2SeqLM.from_pretrained(BASE)
        _MODELE = PeftModel.from_pretrained(base, ADAPTER)
        _MODELE.eval()
    return _TOKENIZER, _MODELE


def traduire(texte, src="fr", tgt="ewe", max_len=128, beams=4):
    """Traduit un texte de la langue src vers la langue tgt.

    src / tgt : "fr" ou "ewe" (voir CODES_NLLB).
    max_len   : longueur maximale (en tokens) de la phrase traitee.
    beams     : taille du faisceau (beam search) ; plus grand = meilleure
                qualite mais plus lent.
    """
    if not texte or not texte.strip():
        return ""
    if src not in CODES_NLLB or tgt not in CODES_NLLB:
        raise ValueError("Langue inconnue. Valeurs acceptees : fr, ewe")
    if src == tgt:
        raise ValueError("src et tgt doivent etre differents")

    tokenizer, modele = charger_modele()

    # Le tokenizer doit connaitre la langue SOURCE pour encoder correctement.
    tokenizer.src_lang = CODES_NLLB[src]
    enc = tokenizer(
        texte, return_tensors="pt", truncation=True, max_length=max_len
    )

    # Generation de la traduction :
    # - forced_bos_token_id : impose la langue CIBLE (le modele commence
    #   obligatoirement par le token de la langue de sortie) ;
    # - num_beams : recherche en faisceau (explore plusieurs hypotheses).
    with torch.no_grad():
        gen = modele.generate(
            **enc,
            forced_bos_token_id=tokenizer.convert_tokens_to_ids(CODES_NLLB[tgt]),
            max_new_tokens=max_len,
            num_beams=beams,
        )
    return tokenizer.batch_decode(gen, skip_special_tokens=True)[0]
