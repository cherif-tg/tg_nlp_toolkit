# Exploration ASR éwé — Mozilla Data Collective et état des ressources

- **Date** : 2026-08-31
- **Auteur** : Cherif (vérifications web/API du 30-31/08)
- **Branche** : `feature/asr_ewe`
- **Complète** : [09-etude-faisabilite-asr.md](09-etude-faisabilite-asr.md)

## 1. Mozilla Data Collective (MDC)

Mozilla Data Collective est la plateforme Mozilla (lancée en 2025) qui
héberge désormais les corpus de Common Voice (ex. « Common Voice Corpus
22.0 ») et des datasets communautaires tiers (parole, MT, TTS).

### API REST (documentée le 30/08)

- Base URL : `https://mozilladatacollective.com/api`
- Auth : `Authorization: Bearer <CLE_API>` (clé gérée dans le profil web)
- Endpoints documentés :
  - `GET /datasets/:datasetId` : détails (nom, locale, licence, tâche,
    format, taille)
  - `POST /datasets/:datasetId/download` : retourne une URL signée
    (valable 12 h) pointant directement vers le stockage (S3/R2),
    avec checksum sha256
- Contraintes pratiques :
  - **L'accord des conditions d'utilisation se fait uniquement via
    l'interface web** — pas d'endpoint API pour cela. Il faut ouvrir la
    fiche du dataset et accepter les termes avant tout téléchargement.
  - 30 téléchargements/jour/organisation (limite remise à zéro à minuit
    UTC) ; rate limiting en 429 avec en-tête `Retry-After`.
  - **Pas d'endpoint public de listing des datasets** (testé le 30/08 :
    404). La recherche de datasets se fait dans l'UI web, et l'ID du
    dataset se lit dans l'URL de sa fiche.
- Licences hétérogènes selon les datasets (CC0-1.0, CC-BY-SA-4.0,
  MDC DLA-1.0, NOODL-1.0, ...) → vérifier chaque dataset au cas par cas
  et documenter la décision dans `data/licenses/`.

### Clé API (règle de sécurité)

La clé ne doit jamais apparaître dans le dépôt. Convention retenue :

```bash
cp .env.example .env      # puis renseigner MDC_API_KEY dans .env
```

`.env` est déjà ignoré par git (`*.env` dans `.gitignore`). Le code
chargera les variables avec `python-dotenv`.

## 2. Statut de l'éwé côté Common Voice (vérifié le 30/08)

- L'API publique `https://commonvoice.mozilla.org/api/v1/languages`
  liste 443 langues ; l'éwé (`ee`) y figure **comme langue
  contribuable** (`is_contributable = 1`, cible 750 phrases).
- Le changelog du dépôt `common-voice/common-voice` confirme l'ajout de
  variantes éwé et la migration des phrases existantes.
- **Aucun corpus Common Voice publié avec des heures validées n'a été
  trouvé à ce jour pour l'éwé** → Common Voice n'est pas (encore) une
  source de données pour nous ; c'est une piste de contribution
  communautaire.
- À confirmer : recherche « ewe » / « Ewe » / « éwé » dans
  l'UI de MDC (la recherche est côté client, non scriptable sans
  navigateur) ; si des datasets éwé existent, relever leur `datasetId`
  dans l'URL de la fiche.

## 3. Ressources HuggingFace vérifiées (API du 30/08)

### Modèles ASR éwé existants

| Modèle | Base | Licence | Téléch. |
|---|---|---|---|
| `waxal-benchmarking/whisper-small-waxal-ewe` | whisper-small | Apache-2.0 | 39 |
| `waxal-benchmarking/whisper-tiny-waxal-ewe` | whisper-tiny | Apache-2.0 | 31 |
| `abiyo27/whisper-small-ewe` | whisper-small | non renseignée | 125 |
| `abiyo27/whisper-medium-ewe-mix` | whisper-medium | non renseignée | 16 |
| `facebook/mms-1b-all` (adaptateur `ewe`) | MMS-1B | CC-BY-NC-4.0 | ~255 000 |

- **Nouveau par rapport à l'étude 09** : l'adaptateur éwé de MMS est
  confirmé (`adapter.ewe.safetensors` présent dans le dépôt
  `facebook/mms-1b-all`) → **baseline zero-shot sans entraînement**,
  à ajouter au comparatif. Attention : licence non commerciale.
- Les deux modèles `abiyo27` n'ont pas de licence déclarée → utilisables
  comme référence comparative, mais pas comme base de publication sans
  clarification.

### Datasets audio éwé

| Dataset | Licence | Remarques |
|---|---|---|
| `abiyo27/BibleTTS_Ewe-Bible` | **CC-BY-SA-4.0** (confirmée) | la référence de l'étude 09 |
| `analist/bibletts-ewe-16k-public` | à vérifier | 16 kHz, candidat pour fine-tune direct |
| `ghananlpcommunity/ewe-tts-bible-full-audio-text` | à vérifier | volume à inspecter |
| `worldboss/ewe_bible_v2_tts` | à vérifier | |
| `VKAgbesi/Ewe_News_Dataset` | à vérifier | nouvelles en éwé — **hors domaine biblique**, intéressant pour la diversité |

### Vérifications de structure (04/09/2026, API datasets-server + hub)

- `abiyo27/BibleTTS_Ewe-Bible` : config `default`, splits `train` /
  `validation` / `test`, colonnes `audio` (Audio, mp3) + `transcription`
  (texte). ~2,3 Go, public, téléchargeable sans token. **Retenu comme
  source principale du benchmark ASR (notebook 06).**
- `analist/bibletts-ewe-16k-public` : config `default`, splits `train` /
  `test`, colonnes `audio` (Audio, flac) + `text`. ~16,2 Go, 10-100k
  extraits. **Aucune licence déclarée** : à clarifier avant tout usage.
- `VKAgbesi/Ewe_News_Dataset` : **ce ne sont pas des fichiers audio mais
  des images** (colonne `image:Image`, scans d'articles de presse, ~4
  lignes). À retirer des ressources ASR dans l'étude 09.

### Vérifications des modèles ASR (04/09/2026, configs HF)

- `facebook/mms-1b-all` : pattern officiel de la model card confirmé —
  `processor.tokenizer.set_target_lang("ewe")` puis
  `model.load_adapter("ewe")`, `model(**inputs)` en conservant
  l'`attention_mask` (requis en batch), décodage CTC par argmax +
  `processor.decode(ids)`. Adaptateur `adapter.ewe.safetensors` présent.
- `waxal-benchmarking/whisper-small-waxal-ewe` : `generation_config.json`
  embarqué avec `forced_decoder_ids [[1, null], [2, 50359]]` (langue non
  forcée, tâche transcribe) et `alignment_heads` → un simple
  `model.generate(input_features)` suffit.
- `abiyo27/whisper-small-ewe` : pas de `generation_config.json`, mais
  `config.json` porte `forced_decoder_ids [[1, 50325], [2, 50359],
  [3, 50363]]` — **50325 est le token `<|yo|>` (yoruba), utilisé comme
  placeholder de langue ewe** (Whisper standard n'a pas de token ewe).
  Piège à garder en tête pour le fine-tune 4.2.

Rappel licence : un dataset dérivé de CC-BY-SA reste CC-BY-SA (partage
aux mêmes conditions) — à intégrer dans la matrice `data/licenses/`.

## 4. Impact sur la feuille de route (étude 09)

- **4.1 (benchmark modèles existants)** : débloqué immédiatement.
  Comparatif proposé sur 20 phrases éwé lues :
  `whisper-small-waxal-ewe` (Apache-2.0) + `facebook/mms-1b-all`
  adaptateur ewe (zero-shot) + `whisper-small-ewe` (référence).
- **4.2 (fine-tune Whisper sur BibleTTS)** : aucune dépendance externe
  bloquante ; le choix du dataset source (abiyo27 vs alternatives 16
  kHz) se fera après inspection des datasheets.
- **MDC, deux rôles** : (a) source de données si des datasets éwé y
  existent (à confirmer via l'UI), (b) **canal de publication future**
  pour nos enregistrements consentis de la phase 4.3 — la plateforme est
  conçue pour que les communautés publient leurs propres datasets.
- **Common Voice éwé** : contribuable mais sans corpus publié → piste de
  contribution à moyen terme, pas une source aujourd'hui.

## 5. Prochaines actions

1. ~~Cherif : créer `.env`~~ — modèle `.env.example` committé le 04/09 ;
   copier vers `.env` et renseigner `MDC_API_KEY` (jamais committé).
2. **Cherif** : rechercher « ewe » dans l'UI MDC ; communiquer les
   `datasetId`/slugs éventuels ; accepter les conditions d'utilisation
   sur la fiche web de tout dataset qu'on voudra télécharger.
3. ~~Sukuna : écrire `scripts/asr/mdc_client.py`~~ — committé le 04/09.
   Usage : `python scripts/asr/mdc_client.py info <datasetId>` puis
   `download <datasetId> --out data/audio` (checksum sha256 vérifié).
4. **Benchmark 4.1** : notebook `06-benchmark-asr-ewe.ipynb` généré par
   `build_notebooks.py` — évalue `whisper-small-waxal-ewe`,
   `facebook/mms-1b-all` (adaptateur ewe) et `abiyo27/whisper-small-ewe`
   sur 100 extraits de `BibleTTS_Ewe-Bible` (WER/CER via jiwer).
   À exécuter sur Colab T4 ; résultats à consigner dans
   `docs/15-benchmark-asr-existants.md`.

Statut au 04/09 : actions 1 et 3 faites ; benchmark prêt à exécuter.
