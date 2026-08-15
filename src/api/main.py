"""API REST de traduction FR <-> EWE (phase P3).

Endpoints :
- GET  /health    -> etat du service ({"status": "ok"})
- POST /translate -> traduction, corps JSON :
    {"text": "...", "src": "fr", "tgt": "ewe"}
    src/tgt acceptent "fr" ou "ewe".

Lancement (depuis la racine du projet) :
    uvicorn src.api.main:app --reload --port 8000

Documentation interactive automatique :
- Swagger UI : http://127.0.0.1:8000/docs
- ReDoc      : http://127.0.0.1:8000/redoc

Comment ca marche (resume) :
1. uvicorn importe `app` depuis ce fichier et lance un serveur HTTP.
2. FastAPI fait correspondre chaque URL a une fonction Python (route).
3. Les donnees JSON recues sont validees par Pydantic (schemas
   TraductionRequest / TraductionResponse) : type, champs obligatoires,
   longueur min/max.
4. La fonction `translate()` appelle `traduire()` (src/api/inference.py)
   qui charge le modele (au demarrage, via lifespan) et traduit.
5. FastAPI renvoie la reponse en JSON et genere la doc OpenAPI
   automatiquement a partir des types declares.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.api.inference import CODES_NLLB, charger_modele, traduire


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Code execute au demarrage du serveur (avant la 1ere requete).

    On charge le modele ici pour que la premiere requete soit repondue
    immediatement (le chargement prend ~1 min : telechargement + RAM).
    """
    charger_modele()
    yield


app = FastAPI(
    title="API Traduction FR <-> EWE",
    description=(
        "Traduction automatique francais <-> ewe. "
        "Modele : NLLB-200-distilled-600M + adaptateur LoRA "
        "(cheriftenga/nllb-200-distilled-600M-ewe-lora)."
    ),
    version="0.1.0",
    lifespan=lifespan,
)


class TraductionRequest(BaseModel):
    """Corps de la requete POST /translate (valide par Pydantic)."""

    text: str = Field(
        ..., description="Texte a traduire", min_length=1, max_length=1000
    )
    src: str = Field("fr", description="Langue source : 'fr' ou 'ewe'")
    tgt: str = Field("ewe", description="Langue cible : 'ewe' ou 'fr'")


class TraductionResponse(BaseModel):
    """Corps de la reponse JSON."""

    text: str
    src: str
    tgt: str
    traduction: str


@app.get("/health")
def health():
    """Point de controle : verifie que le service repond."""
    return {"status": "ok", "modele": "nllb-200-distilled-600M-ewe-lora"}


@app.post("/translate", response_model=TraductionResponse)
def translate(req: TraductionRequest):
    """Traduit le texte recu. Retourne la traduction en JSON."""
    if req.src not in CODES_NLLB or req.tgt not in CODES_NLLB:
        raise HTTPException(
            status_code=400,
            detail="Langue inconnue. Valeurs acceptees : fr, ewe",
        )
    if req.src == req.tgt:
        raise HTTPException(
            status_code=400,
            detail="src et tgt doivent etre differents",
        )
    try:
        resultat = traduire(req.text, src=req.src, tgt=req.tgt)
    except HTTPException:
        raise
    except Exception as e:  # erreur inattendue -> reponse 500 lisible
        raise HTTPException(status_code=500, detail=f"Erreur interne : {e}")
    return TraductionResponse(
        text=req.text, src=req.src, tgt=req.tgt, traduction=resultat
    )
