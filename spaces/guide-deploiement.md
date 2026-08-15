# Deploiement de la demo sur HuggingFace Spaces

Ce dossier contient tout ce qu'il faut pour publier la demo Gradio
publiquement sur HuggingFace Spaces.

## Fichiers

| Fichier | Role |
|---|---|
| `app.py` | L'interface Gradio (copie de `demo/app.py`, mode local) |
| `requirements.txt` | Dependances installees par le Space |
| `README.md` | Carte du Space (titre, licence, scores) |

## Procedure (2 options)

### Option A - Interface web (la plus simple)

1. Va sur <https://huggingface.co/new-space>
2. Nom du Space : `nllb-ewe-demo` (ou autre)
3. SDK : **Gradio**, Hardware : **T4 small** (GPU gratuit)
4. Clique **Create Space**
5. Onglet **Files** -> **Add file** -> **Upload files** :
   - `app.py`
   - `requirements.txt`
   - `README.md` (remplace le README genere)
6. Le Space se construit automatiquement (quelques minutes :
   installation des paquets puis telechargement du modele au premier
   lancement).

### Option B - Git (si tu preferes la ligne de commande)

```bash
# avec le token Write du compte cheriftenga
git clone https://huggingface.co/spaces/cheriftenga/nllb-ewe-demo
cd nllb-ewe-demo
cp ../tg_nlp_toolkit/spaces/app.py .
cp ../tg_nlp_toolkit/spaces/requirements.txt .
cp ../tg_nlp_toolkit/spaces/README.md .
git add . && git commit -m "demo FR-EWE" && git push
```

## Points d'attention

- **GPU T4 obligatoire** : sans GPU, la traduction est trop lente
  (plusieurs secondes par phrase). Le hardware du Space se regle dans
  Settings -> Hardware (T4 small, gratuit).
- **Premier lancement lent** : le Space telecharge le modele de base
  NLLB (~2,4 Go) au premier demarrage. Les lancements suivants sont
  plus rapides (cache).
- **Mode local** : sur le Space, la demo charge le modele elle-meme
  (pas d'API_URL) -> autonome.
- La licence du README est CC-BY-NC-SA-4.0 (heritee du modele).

## Apres deploiement

L'URL publique ressemblera a :
`https://huggingface.co/spaces/cheriftenga/nllb-ewe-demo`

Partageable dans le portfolio, sur LinkedIn, dans le rapport de stage...
C'est la vitrine publique du projet.
