# API REST de traduction FR <-> EWE

API HTTP pour la traduction automatique francais <-> ewe, basee sur
`cheriftenga/nllb-200-distilled-600M-ewe-lora` (NLLB + LoRA).

## Installation

```bash
pip install fastapi "uvicorn[standard]" httpx transformers peft torch sentencepiece
```

## Lancement

Depuis la racine du projet :

```bash
uvicorn src.api.main:app --reload --port 8000
```

- `src.api.main` = chemin du module (fichier `src/api/main.py`, objet `app`).
- `--reload` : rechargement automatique a chaque modification du code
  (a retirer en production).
- `--port 8000` : port d'ecoute (8000 par defaut).

Au demarrage, le serveur charge le modele (telechargement ~2,4 Go la
premiere fois, puis ~1 min de chargement). Patiente jusqu'au message
"Application startup complete".

## Documentation interactive (generee automatiquement)

- Swagger UI : <http://127.0.0.1:8000/docs>
- ReDoc : <http://127.0.0.1:8000/redoc>

FastAPI genere ces pages a partir du code : schemas, exemples,
bouton "Try it out" pour tester sans ecrire de code.

## Exemples d'utilisation

### 1. Avec curl

```bash
# Traduction FR -> EWE
curl -X POST http://127.0.0.1:8000/translate \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"Bonjour, comment vas-tu ?\", \"src\": \"fr\", \"tgt\": \"ewe\"}"

# Traduction EWE -> FR
curl -X POST http://127.0.0.1:8000/translate \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"Efoa, wòle asi nyuie?\", \"src\": \"ewe\", \"tgt\": \"fr\"}"

# Etat du service
curl http://127.0.0.1:8000/health
```

### 2. Avec Python (requests ou httpx)

```python
import httpx

reponse = httpx.post(
    "http://127.0.0.1:8000/translate",
    json={"text": "Bonjour, comment vas-tu ?", "src": "fr", "tgt": "ewe"},
)
print(reponse.json())
# -> {"text": "...", "src": "fr", "tgt": "ewe", "traduction": "..."}
```

## Schema des requetes / reponses

POST /translate

```json
{
  "text": "Bonjour, comment vas-tu ?",
  "src": "fr",
  "tgt": "ewe"
}
```

Reponse 200 :

```json
{
  "text": "Bonjour, comment vas-tu ?",
  "src": "fr",
  "tgt": "ewe",
  "traduction": "..."
}
```

Erreurs :
- 400 : langue inconnue, ou src == tgt.
- 422 : requete invalide (text vide, champ manquant, type incorrect).
- 500 : erreur interne pendant la traduction.

## Structure du code

| Fichier | Role |
|---|---|
| `src/api/main.py` | Application FastAPI : routes, validation Pydantic, doc auto |
| `src/api/inference.py` | Chargement du modele + fonction `traduire()` (reutilisable) |

## Tests

```bash
python -c "from fastapi.testclient import TestClient; from src.api.main import app; c = TestClient(app); print(c.get('/health').json())"
```

(Le test complet de traduction necessite le modele charge.)

## Production (plus tard)

- Uvicorn sans `--reload`, plusieurs workers (`--workers 4`).
- Conteneur Docker avec le modele pre-charge.
- Authentification (jeton API) si le service est public.
