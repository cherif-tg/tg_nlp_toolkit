# src/

Architecture du code :

- `collect/` : scripts de collecte (JW300/OPUS via `datasets`/`opustools`, Wikipedia, enregistrements audio)
- `clean/` : normalisation Unicode (ɖ ɸ ɣ ɔ ɛ ŋ), déduplication, filtrage (opusfilter)
- `augment/` : back-translation + filtrage (confiance, round-trip)
- `train/` : fine-tuning LoRA NLLB-200-distilled-600M ; Whisper (conditionnel)
- `evaluate/` : chrF++ (sacrebleu), COMET, BLEU, WER (jiwer), protocole revue humaine

Conventions : Python 3.11+, configs versionnées, données jamais commitées dans `data/raw`.
