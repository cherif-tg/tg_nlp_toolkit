# Demo Gradio - Traducteur FR <-> EWE

Interface web de demonstration pour le modele
`cheriftenga/nllb-200-distilled-600M-ewe-lora` (NLLB + LoRA, FR <-> EWE).

## Lancement local

```bash
pip install gradio transformers peft torch sentencepiece
python demo/app.py
```

Ouvre <http://127.0.0.1:7860>.

- Premier lancement : telechargement du modele de base NLLB
  (environ 2,4 Go) + adaptateur LoRA (~20 Mo).
- Sans GPU, la traduction est lente (quelques secondes par phrase).
  Un GPU (T4 ou plus) est recommande.

## Deploiement sur HuggingFace Spaces

1. Cree un Space sur <https://huggingface.co/new-space> (SDK : Gradio,
   Hardware : T4 small - GPU gratuit).
2. Pousse dans le Space les fichiers :
   - `app.py` (copie de `demo/app.py`)
   - `requirements.txt` :

     ```
     gradio
     transformers
     peft
     torch
     sentencepiece
     ```

3. Le Space se construit et se lance automatiquement.
   Le modele et le tokenizer sont charges depuis le Hub.

## Contenu

| Fichier | Role |
|---|---|
| `app.py` | Interface Gradio : onglets FR -> EWE et EWE -> FR, reglage du beam search |
| `README.md` | Ce guide |

## Licence

Le modele herite de la licence CC-BY-NC-SA-4.0 de NLLB (Meta AI) :
usage non commercial. Voir la model card du modele pour le detail.
