"""Demo Gradio : traduction FR <-> EWE avec NLLB LoRA.

Phase P3 du projet tg-nlp-toolkit.
Le modele est charge depuis HuggingFace : adaptateur LoRA
(cheriftenga/nllb-200-distilled-600M-ewe-lora) sur le modele de base
facebook/nllb-200-distilled-600M.

Lancement local :
    pip install gradio transformers peft torch sentencepiece
    python demo/app.py
    -> ouvre http://127.0.0.1:7860

Deploiement HuggingFace Spaces : voir demo/README.md (fichiers app.py
+ requirements.txt a la racine de l'espace, GPU T4 recommande).
"""

import torch
import gradio as gr
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from peft import PeftModel

BASE = "facebook/nllb-200-distilled-600M"
ADAPTER = "cheriftenga/nllb-200-distilled-600M-ewe-lora"

CODES = {"Francais": "fra_Latn", "Ewe": "ewe_Latn"}


def charger_modele():
    """Charge le tokenizer et le modele (base + adaptateur LoRA)."""
    tokenizer = AutoTokenizer.from_pretrained(ADAPTER)
    base = AutoModelForSeq2SeqLM.from_pretrained(BASE)
    modele = PeftModel.from_pretrained(base, ADAPTER)
    modele.eval()
    return tokenizer, modele


TOKENIZER, MODELE = charger_modele()


def traduire(texte, src, tgt, beams=4):
    """Traduit un texte de la langue src vers la langue tgt."""
    if not texte or not texte.strip():
        return ""
    TOKENIZER.src_lang = CODES[src]
    enc = TOKENIZER(
        texte, return_tensors="pt", truncation=True, max_length=128
    )
    with torch.no_grad():
        gen = MODELE.generate(
            **enc,
            forced_bos_token_id=TOKENIZER.convert_tokens_to_ids(CODES[tgt]),
            max_new_tokens=128,
            num_beams=beams,
        )
    return TOKENIZER.batch_decode(gen, skip_special_tokens=True)[0]


def interface_fr_ewe(fr, beams):
    return traduire(fr, "Francais", "Ewe", beams)


def interface_ewe_fr(ewe, beams):
    return traduire(ewe, "Ewe", "Francais", beams)


with gr.Blocks(title="Traducteur Francais - Ewe (Togo)") as demo:
    gr.Markdown("# Traducteur Francais <-> Ewe")
    gr.Markdown(
        "Modele : NLLB-200-distilled-600M fine-tune LoRA sur le corpus "
        "tg-nlp-toolkit v0.3 (65 640 paires). Projet de toolkit NLP pour "
        "les langues du Togo."
    )
    with gr.Tab("FR -> EWE"):
        fr_in = gr.Textbox(
            label="Francais",
            placeholder="Ecris une phrase en francais...",
            lines=3,
        )
        beams_fr = gr.Slider(1, 8, value=4, step=1,
                             label="Nombre de faisceaux (beam search)")
        fr_out = gr.Textbox(label="Ewe", lines=3)
        fr_btn = gr.Button("Traduire")
        fr_btn.click(interface_fr_ewe, [fr_in, beams_fr], fr_out)
    with gr.Tab("EWE -> FR"):
        ewe_in = gr.Textbox(
            label="Ewe",
            placeholder="Nya aɖeŋlɔ le ewegbe...",
            lines=3,
        )
        beams_ewe = gr.Slider(1, 8, value=4, step=1,
                              label="Nombre de faisceaux (beam search)")
        ewe_out = gr.Textbox(label="Francais", lines=3)
        ewe_btn = gr.Button("Traduire")
        ewe_btn.click(interface_ewe_fr, [ewe_in, beams_ewe], ewe_out)
    gr.Markdown(
        "Note : le modele herite de la licence CC-BY-NC-SA-4.0 de NLLB "
        "(usage non commercial). Plus d'infos sur la page HuggingFace du "
        "modele."
    )


if __name__ == "__main__":
    demo.launch()
