# ASR éwé — état vérifié et plan d'exécution v0.1

Date : 2026-11-16
Projet : tg_nlp_toolkit
Statut : pipeline prête (script de préparation testé ; notebooks prêts pour Colab)
Suite de : `docs/09-etude-faisabilite-asr.md` (2026-08-15) — ce document met à
jour l'état des données (re-vérifié le 2026-11-16) et fixe le plan d'exécution.

---

## 1. Contexte et objectif

Le toolkit couvre aujourd'hui la traduction automatique français <-> éwé
(corpus v0.3, modèle LoRA v2 sur NLLB-200) et prévoyait l'ASR « en étude de
faisabilité » (README). Cette étude conclut : l'ASR éwé est faisable dès
maintenant, avec des données publiques propres et un point de comparaison
publié. L'objectif du v0.1 est un premier modèle ASR éwé entraînable sur un
T4 gratuit (Google Colab), une pipeline reproductible de bout en bout et un
benchmark honnête.

Portée du v0.1 : transcription de parole éwé (lecture et spontanée).
Hors périmètre : pseudo-labeling, collecte de terrain, extension kabiyè
(voir feuille de route, section 9).

---

## 2. Méthode de l'étude

Recherche web effectuée le 2026-11-16 sur les sources publiques (Hugging
Face, arXiv, GitHub, catalogues de corpus). Les affirmations ci-dessous sont
étayées par les sources listées en section 10 ; chaque fait vérifié
directement sur la page source est marqué (vérifié). Les points non
vérifiables sont signalés comme tels, conformément à la culture « datasheet
honnête » du projet.

---

## 3. Paysage des données audio éwé

| Source | Volume éwé | Licence | Statut pour v0.1 |
|---|---|---|---|
| WAXAL ASR (`google/WaxalNLP`, config `ewe_asr`) | 15 054 extraits train / 1 916 val / 1 891 test transcrits (~5,7 Go) + 183 920 non transcrits (56 Go) (vérifié) | CC-BY-4.0 selon le papier ; métadonnées HF mentionnent aussi CC-BY-SA-4.0 (voir 6) | **Source retenue** |
| WAXAL TTS (`ewe_tts`) | voix studio, lecture de scripts phonétiquement équilibrés | idem | v0.2 (données de lecture propres pour renforcer l'entraînement) |
| Modèle de référence WAXALNet (`waxal-benchmarking/whisper-small-waxal-ewe`) | Whisper small fine-tuné sur WAXAL éwé ; WER 32,3 / CER 10,6 sur le test filtré (vérifié sur la model card) | apache-2.0 | **Baseline de comparaison** |
| MMS Meta (`facebook/mms-1b-all`) | adaptateur `ee` (éwé) présent dans la liste des langues supportées (vérifié) ; modèle 1 B paramètres | cc-by-nc-4.0 | Baseline zero-shot uniquement (licence non commerciale) |
| FLEURS (`google/fleurs`) | **aucun subset éwé** dans les 103 configs (vérifié) | cc-by-4.0 | Non utilisable |
| Common Voice (v27.0, 295 langues scripted) | présence éwé **non confirmée** (catalogue Mozilla Data Collective non lisible intégralement à la vérification, datasets HF gated) | cc0 | À re-vérifier périodiquement |
| `Professor/ewe-speech-data` (~103,1 h) | provenance non documentée, viewer cassé (webdataset), 1 like, « AfroNet » | cc-by-4.0 | v0.2 après audit |
| Audio Bible éwé (Faith Comes By Hearing, Lumo) | enregistrements alignés sur la Bible éwé | licences de diffusion, pas de réutilisation ML claire | Non utilisable pour l'entraînement |

Conclusion : WAXAL est la seule source publique à la fois volumineuse,
transcrite par des locuteurs experts et licenciée pour l'entraînement. C'est
la source du v0.1.

---

## 4. La source retenue : WAXAL

WAXAL (arXiv 2602.02734, Google Research + University of Ghana + Digital
Umuganda + Makerere + Media Trust) : ~1 250 h transcrites sur 24 langues
subsahariennes, collecte 2021-2024.

Caractéristiques de l'éwé (config `ewe_asr`) :

- **Méthode** : parole spontanée « image-prompted » (description d'images
  couvrant au moins 50 thèmes), enregistrée dans l'environnement naturel du
  locuteur, durée minimale 15 s par clip, transcription par des experts
  linguistiques locaux rémunérés, contrôle qualité (clarté, pertinence,
  PII retirées). Seulement 10 % de l'audio collecté est transcrit ; le
  reste est livré dans le split `unlabeled`.
- **Schéma** (vérifié sur la métadonnée du dataset puis sur un échantillon
  réel) : `id`, `speaker_id`, `transcription`, `language`, `gender`,
  `audio`. Pas de champ région ni âge malgré la mention de l'âge dans le
  papier ; sur l'échantillon testé, le champ `gender` est vide.

### Contrôles effectués sur un échantillon (2026-11-16, script de préparation)

Échantillon de 18 extraits (12 train, 6 test) traité par
  `src/asr/prep_waxal_ewe.py` en streaming :

- **Audio** : MP3 embarqué dans les parquet. Durée p50 ≈ 19 s, max observé
  27 s (le papier annonce un minimum de 15 s).
- **Transcriptions** : orthographe éwé authentique (ɖ, ɛ, ɔ, ŋ, ƒ, ʋ
  présents), texte **casé et ponctué** (92 % des extraits avec ponctuation
  forte, 100 % avec majuscules sur l'échantillon) -> directement adapté à
  Whisper, et utilisable en entrée du modèle MT.
- **Débit de parole réel** : ~1,7 à 2 mots/s. Le filtre « speech rate
  >= 4 mots/s » publié sur la model card WAXALNet exclurait la quasi
  totalité des extraits publics ; voir section 7.
- **Piège technique** : `load_dataset("google/WaxalNLP", "ewe_asr")`
  échoue (CastError) car les parquet réels contiennent une colonne
  `__index_level_0__` absente du schéma déclaré dans le YAML. Les scripts
  et notebooks du projet contournent cela en lisant les parquet avec le
  builder générique (`data/ASR/ewe/*.parquet`).
- **Limites assumées** :
  - les partenaires de collecte sont nationaux (University of Ghana pour
    les langues du Ghana). La répartition exacte langue/partenaire n'est
    pas visible dans la version consultée du papier : il est **probable**
    que les locuteurs éwé soient ghanéens, donc la variante ghanéienne de
    l'éwé (continuum Anlo-Gu-Mina). L'écart avec l'éwé du Togo n'est pas
    mesuré ; c'est le risque principal pour l'usage togolais du modèle
    (mitigation : section 9, v0.2) ;
  - un seul annotateur par enregistrement (pas de double validation,
    contrairement au split reference du corpus MT du projet) ;
  - parole spontanée + environnements bruyants : réaliste mais difficile.

---

## 5. Choix du modèle

**Décision v0.1 : fine-tuning complet de `openai/whisper-small` (244 M) sur
le train `ewe_asr`.**

Arguments :

1. **Comparabilité** : c'est exactement le protocole de WAXALNet
   (arXiv 2606.02375). Même base, même données, même test -> notre score
   WER/CER se compare directement à leur WER 32,3 / CER 10,6, ce qui donne
   un barème public immédiat, comme le benchmark Google Translate pour le
   MT.
2. **Sortie utilisable** : Whisper produit un texte casé et ponctué,
   directement injectable dans le modèle MT FR<->ÉWÉ pour une cascade
   audio -> traduction. Le WAXALNet (et a fortiori MMS en CTC) est un
   concurrent, pas une raison de ne pas le faire : le toolkit ne possède
   pas de modèle ASR éwé à lui, et la pipeline (données, évaluation,
   licences) est le vrai livrable du v0.1.
3. **Contraintes matérielles** : 244 M passent sur T4 16 Go en fp16 avec
   gradient checkpointing. Les hyperparamètres publiés par WAXALNet
   (lr 1e-4, warmup 500 pas, batch 32, 30 époques) sont le point de
   départ ; on vise 3-5 époques avec arrêt précoce sur le WER de
   validation pour rester dans un budget Colab.
4. **Licence** : base Whisper MIT + données WAXAL -> le modèle résultant
   peut être publié sous licence libre (attribution), contrairement à la
   branche MT (NLLB, NC).

Alternatives étudiées et écartées pour le v0.1 :

- **MMS-1B + adaptateur `ee`** : probablement meilleur WER zero-shot, et le
  fine-tuning d'adaptateurs est efficace. Écarté pour v0.1 : licence
  CC-BY-NC-4.0 (non commercial), sortie CTC sans ponctuation ni casse,
  1 B plus lourd sur T4. Gardé comme baseline, et candidat comparatif en
  v0.2.
- **XLS-R 300 M** : base historique solide, mais pas de support éwé natif
  et pas de référence publique sur WAXAL -> moins lisible comme premier
  modèle.
- **whisper-tiny** : plan B si small s'avère trop lent sur T4.

---

## 6. Licences et attribution

- **Données** : le papier WAXAL annonce CC-BY-4.0 ; les métadonnées HF
  mentionnent `cc-by-sa-4.0` en plus de `cc-by-4.0` (vérifié sur le YAML).
  Écart non résolu au moment de la rédaction : il peut s'agir d'une licence
  mixte par config ou d'une erreur de métadonnée. Le notebook 06 vérifie
  les métadonnées de licence au chargement. Posture par défaut : attribution
  à WAXAL (et à ses partenaires) dans tous les livrables, et publication du
  modèle sous CC-BY-4.0 **ou** CC-BY-SA-4.0 selon ce que confirme l'audit.
- **Baselines** : MMS est CC-BY-NC-4.0 -> usage limité à l'évaluation, aucun
  poids de MMS ne doit entrer dans un modèle publié. Le modèle WAXALNet est
  apache-2.0 -> utilisable librement comme référence.
- **Notre modèle** : base Whisper (MIT) fine-tunée sur WAXAL -> distribution
  sous licence libre avec attribution ; pas de clause non commerciale
  héritée (contrairement au MT). C'est un avantage à mettre en avant dans
  la communication.

Attribution type pour un modèle publié :

> Ce modèle est un fine-tuning de whisper-small sur le corpus WAXAL
> (WaxalNLP, Google Research et partenaires, CC-BY-4.0).

---

## 7. Protocole d'évaluation

- **Métriques** : WER et CER (jiwer), normalisation standard Whisper
  (minuscules, ponctuation retirée, espaces normalisés). La normalisation
  exacte de WAXALNet n'étant pas publiée, la comparaison est indicative ;
  la nôtre est documentée et reproductible.
- **Deux variantes du test** :
  - test complet (1 891 extraits) : la comparaison principale ;
  - variante « filtre WAXALNet » (durée >= 1,5 s et débit >= 4 mots/s) :
    le débit réel observé (~1,7-2 mots/s) rend ce filtre non reproductible
    sur les données publiques — leur sous-ensemble nettoyé n'est pas
    publié (« datasets : none public » sur leur organisation HF au
    2026-11-16). Le manifeste continue de porter le drapeau
    `comparable_waxalnet` pour mémoire, mais la comparaison retenue se
    fait sur le test complet, et le WER 32,3 de WAXALNet est cité comme
    indicatif (protocole de filtrage non reproduisible).
- **Baselines chiffrées avant entraînement** (notebook 06) :
  1. MMS-1B zero-shot, adaptateur `ee` ;
  2. `waxal-benchmarking/whisper-small-waxal-ewe` (WER 32,3 de référence).
- **Analyse qualitative** : les 20 pires erreurs du test (WER par extrait)
  sont exportées pour relecture par un locuteur, dans l'esprit de la double
  validation humaine du projet.

---

## 8. Risques et parades

| Risque | Impact | Parade |
|---|---|---|
| Variante ghanéienne des locuteurs WAXAL | modèle moins fidèle à l'éwé du Togo | documenté comme limite ; test togolais en v0.2 pour mesurer l'écart réel |
| Style des transcriptions inconnu (ponctuation, casse, diacritiques ɖ/ɔ/ɛ, graphies) | décisions de normalisation arbitraires | inventaire orthographique systématique dans le notebook 06 avant entraînement |
| Clips > 30 s (limite d'entrée Whisper) | perte de données | comptage exact, filtrage documenté en v0.1 ; découpage en v0.2 |
| Budget Colab T4 | entraînement interrompu | checkpoints réguliers + reprise ; fallback whisper-tiny |
| Licence HF mixte (BY vs BY-SA) | publication du modèle | audit licence au chargement ; modèle publié sous la licence la plus contraignante documentée |
| Comparaison WAXALNet imparfaite (normalisation non publiée) | surestimation | comparaison présentée comme indicative, protocole nôtre documenté |

---

## 9. Feuille de route

- **v0.1 (ce document + notebooks 06/07)** : pipeline reproductible,
  baselines MMS/WAXALNet, whisper-small fine-tuné sur WAXAL éwé, WER/CER
  sur test complet et filtré, export d'erreurs.
- **v0.2** :
  - test togolais : un petit lot de phrases (ex. les grilles de collecte du
    projet) lues par des locuteurs togolais, transcrites en double
    validation -> mesure de l'écart dialectal ;
  - pseudo-labeling des 183 920 extraits non transcrits (56 Go) avec le
    modèle v0.1, puis self-training ;
  - essai comparatif MMS-adapters et éventuel fine-tune XLS-R ;
  - audit de `Professor/ewe-speech-data` et re-vérification Common Voice.
- **v0.3** :
  - cascade ASR -> MT : audio éwé -> texte français (via le modèle MT v2) ;
  - extension kabiyè conditionnée à des données (Common Voice, collecte) ;
  - intégration au toolkit : endpoint API `/transcribe`, CLI batch audio,
    démo Gradio.

---

## 10. Guide d'exécution

### Fichiers

| Fichier | Rôle |
|---|---|
| `docs/14-asr-ewe-plan-execution-v0.1.md` | Le présent document : état vérifié, décisions, protocole |
| `src/asr/prep_waxal_ewe.py` | Préparation des données : manifeste CSV + rapport de statistiques (filtres documentés) |
| `notebooks/06-asr-ewe-baseline.ipynb` | Corpus complet + baselines (MMS-1B zero-shot, WAXALNet) sur le test |
| `notebooks/07-asr-ewe-finetune-whisper.ipynb` | Fine-tuning whisper-small + évaluation finale + export des pires erreurs |

### Préparation locale (échantillon, streaming)

```bash
pip install datasets soundfile
python src/asr/prep_waxal_ewe.py --split train --max-rows 20 --stream \
    --out-dir data-asr/manifests
```

### Exécution complète (Colab T4)

1. `notebooks/06-asr-ewe-baseline.ipynb` (~1 h 30) : statistiques + baselines.
   Télécharger `resultats/` à la fin.
2. `notebooks/07-asr-ewe-finetune-whisper.ipynb` (~3-4 h) : fine-tuning,
   évaluation, comparaison avec les baselines du notebook 06.

## 11. Pièges connus (vérifiés le 2026-11-16)

- `load_dataset("google/WaxalNLP", "ewe_asr")` échoue (CastError) : les
  parquet réels contiennent une colonne `__index_level_0__` absente du
  schéma déclaré. Lire les fichiers `data/ASR/ewe/ewe-*.parquet` avec le
  builder parquet générique (fait dans le script et les notebooks).
- Audio : MP3 44,1 kHz stéréo. Décoder, moyenner en mono, rééchantillonner
  à 16 kHz (`charger_audio_16k` dans le script et les notebooks).
- Le champ `gender` est vide sur les extraits échantillonnés.

## 12. Résultats

À remplir après exécution sur Colab :

| Modèle | WER | CER | Jeu |
|---|---|---|---|
| MMS-1B zero-shot (adaptateur `ewe`) | à mesurer | à mesurer | test complet |
| WAXALNet `whisper-small-waxal-ewe` | à mesurer | à mesurer | test complet |
| **whisper-small fine-tuné WAXAL éwé (v0.1)** | à mesurer | à mesurer | test complet |
| WAXALNet (chiffre annoncé, sous-ensemble privé filtré) | 32,3 | 10,6 | non reproductible |

## 13. Références (toutes consultées le 2026-11-16)

1. WAXAL dataset card et métadonnées :
   https://huggingface.co/datasets/google/WaxalNLP
   (tailles des splits vérifiées via l'API datasets-server).
2. WAXAL paper : arXiv 2602.02734 « WAXAL: ... speech dataset for 24
   Sub-Saharan African languages », v3 du 2026-03-02.
3. WAXAL ASR Benchmark : arXiv 2606.02375 (juin 2026) ; model card
   `waxal-benchmarking/whisper-small-waxal-ewe` (WER/CER de référence,
   hyperparamètres, filtre de test).
4. MMS : https://huggingface.co/facebook/mms-1b-all (liste des langues,
   licence) et paper arXiv 2305.13516.
5. FLEURS : https://huggingface.co/datasets/google/fleurs (liste des 103
   subsets, sans éwé).
6. Common Voice : https://github.com/common-voice/cv-dataset (v27.0,
   295 langues scripted, septembre 2026).
7. `Professor/ewe-speech-data` : https://huggingface.co/datasets/Professor/ewe-speech-data
