# data/

- `raw/` : sources brutes, **jamais modifiées** (JW300, OPUS, Wikipedia, audio). Si volumineux → stockage externe (HF Hub) + manifeste ici.
- `processed/` : corpus nettoyés — `train.jsonl`, `dev.jsonl`, `test.jsonl`, sous-ensemble `domaine_cible.jsonl`.
- `licenses/` : `matrix.csv` + un fichier de décision par source (extrait CGU, décision, date, responsable).

## Règles

1. Une source = une décision de licence écrite, avant intégration.
2. Le corpus publié ne contient que des sources publiables.
3. Le JW300 est réservé à l'entraînement, jamais dans le dataset public.
