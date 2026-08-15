"""Demo Gradio FR <-> EWE - version HuggingFace Spaces.

Compatible avec trois environnements :

1. Space CPU basic (gratuit) : modele sur CPU, traduction lente
   (~5-15 s par phrase) mais fonctionnelle.
2. Space ZeroGPU (GPU partage gratuit) : le GPU est alloue a chaque
   appel via @spaces.GPU. `import spaces` doit etre fait avant tout
   paquet CUDA (torch).
3. Space GPU classique (T4) : modele sur GPU directement.

La detection est automatique : `import spaces` reussi -> mode ZeroGPU,
sinon mode CPU/GPU classique selon torch.cuda.is_available().
"""

try:
    import spaces  # noqa: F401
    # Verifie que c'est bien le SDK ZeroGPU de HuggingFace (et pas un
    # dossier/pacquet homonyme sans attribut GPU).
    ZEROGPU = hasattr(spaces, "GPU")
except ImportError:
    ZEROGPU = False

import os  # noqa: E402
import torch  # noqa: E402
import gradio as gr  # noqa: E402
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM  # noqa: E402
from peft import PeftModel  # noqa: E402

BASE = "facebook/nllb-200-distilled-600M"
ADAPTER = "cheriftenga/nllb-200-distilled-600M-ewe-lora"
CODES_NLLB = {"fr": "fra_Latn", "ewe": "ewe_Latn"}

TOKENIZER = None
MODELE = None


def charger_modele():
    """Charge le modele une seule fois (cache en memoire)."""
    global TOKENIZER, MODELE
    if MODELE is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Chargement du modele sur {device} (patienter)...")
        TOKENIZER = AutoTokenizer.from_pretrained(ADAPTER)
        base = AutoModelForSeq2SeqLM.from_pretrained(BASE).to(device)
        MODELE = PeftModel.from_pretrained(base, ADAPTER)
        MODELE.eval()
        print("Modele pret.")
    return TOKENIZER, MODELE


def _traduire(texte, src, tgt, beams=4):
    """Traduction FR<->EWE. src/tgt : codes 'fr' ou 'ewe'."""
    if not texte or not texte.strip():
        return ""
    tokenizer, modele = charger_modele()
    device = modele.device
    tokenizer.src_lang = CODES_NLLB[src]
    enc = tokenizer(
        texte, return_tensors="pt", truncation=True, max_length=128
    ).to(device)
    with torch.no_grad():
        gen = modele.generate(
            **enc,
            forced_bos_token_id=tokenizer.convert_tokens_to_ids(
                CODES_NLLB[tgt]
            ),
            max_new_tokens=128,
            num_beams=beams,
        )
    return tokenizer.batch_decode(gen, skip_special_tokens=True)[0]


# ZeroGPU : chaque appel de traduction recoit une allocation GPU.
traduire = spaces.GPU(_traduire) if ZEROGPU else _traduire


def interface_fr_ewe(fr, beams):
    return traduire(fr, "fr", "ewe", beams)


def interface_ewe_fr(ewe, beams):
    return traduire(ewe, "ewe", "fr", beams)


NOTE_ENV = (
    "Mode ZeroGPU (GPU partage)" if ZEROGPU else
    "Mode CPU (Space gratuit) - la traduction peut prendre ~5-15 s"
)

with gr.Blocks(title="Traducteur Francais - Ewe (Togo)") as demo:
    gr.Markdown("# Traducteur Francais <-> Ewe")
    gr.Markdown(
        "Modele : NLLB-200-distilled-600M fine-tune LoRA sur le corpus "
        "tg-nlp-toolkit v0.3 (65 640 paires). Projet de toolkit NLP pour "
        "les langues du Togo."
    )
    gr.Markdown(NOTE_ENV)
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
