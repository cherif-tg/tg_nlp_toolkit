# Demo Gradio - Traducteur FR <-> EWE

Interface web de demonstration pour le modele
`cheriftenga/nllb-200-distilled-600M-ewe-lora` (NLLB + LoRA, FR <-> EWE).

La demo fonctionne dans **deux modes** :

1. **Mode API (recommande)** : la demo appelle l'API REST (`src/api/main.py`).
   Un seul modele charge en memoire, la demo peut tourner sans GPU.
   ```bash
   # terminal 1 : l'API
   uvicorn src.api.main:app --port 8000
   # terminal 2 : la demo
   API_URL=http://127.0.0.1:8000 python demo/app.py
   ```
2. **Mode local (autonome)** : la demo charge le modele elle-meme.
   ```bash
   python demo/app.py
   ```

## Lancement local

```bash
pip install gradio transformers peft torch sentencepiece httpx
python demo/app.py
```

Ouvre <http://127.0.0.1:7860>.

- Mode local : premier lancement = telechargement du modele de base NLLB
  (environ 2,4 Go) + adaptateur LoRA (~20 Mo). Sans GPU, la traduction est
  lente (quelques secondes par phrase). Un GPU (T4 ou plus) est recommande.
- Mode API : rien a telecharger dans la demo, tout passe par l'API.

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
| `app.py` | Interface Gradio : onglets FR -> EWE et EWE -> FR, reglage du beam search, mode API ou local |
| `README.md` | Ce guide |

## Architecture (lien demo / API)

```
Client web (navigateur)
        |
        v
Demo Gradio (demo/app.py)   <- interface utilisateur
        |
        v
API REST (src/api/main.py)  <- logique + modele (uvicorn, port 8000)
```

En mode API, la demo n'est plus qu'une **interface** : elle envoie le texte
au serveur et affiche la reponse. Avantages : un seul modele en memoire,
demo legere (deployable n'importe ou), modele changeable sans toucher a
l'interface.

## Licence

Le modele herite de la licence CC-BY-NC-SA-4.0 de NLLB (Meta AI) :
usage non commercial. Voir la model card du modele pour le detail.
