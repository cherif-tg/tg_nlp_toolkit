# Plan de Travail Détaillé — togo-nlp-toolkit

Version de travail. Complète le §8 du document d'étude et de réalisation (v2.0).
Chaque phase décrit : objectif, étapes, qui fait quoi, sortie, critère de sortie.

---

## Mode de collaboration

| Tâche | Qui |
|---|---|
| Rédaction docs, scripts, notebooks, gabarits d'évaluation | Sukuna |
| Validation du domaine (contenu santé/éduc/admin, orthographe) | Utilisateur |
| Contacts locuteurs natifs + logistique enregistrements/traductions | Utilisateur |
| Exécution GPU (Colab/Kaggle) | Utilisateur (notebooks fournis) |
| Comptes et publication (GitHub, HuggingFace) | Utilisateur (instructions fournies) |
| Vérification CGU / licences en ligne | Utilisateur (Sukuna assiste dès que la recherche web est de retour) |

**Rythme de travail** : un point à la fois → Sukuna propose (doc/code/gabarit) → utilisateur valide → artefact committé dans le repo.

**Comptes à créer** (gratuits) : GitHub, HuggingFace (token), Google Colab ou Kaggle.

---

## P0 — Cadrage (semaine 1)

**Objectif** : lever tous les risques avant de collecter.

1. **Matrice de licences** (`data/licenses/matrix.csv` + un fichier de décision par source)
   - Colonnes : source, langues, volume estimé, licence, usage autorisé (publier / entraînement seul), statut, date, responsable
   - Sources : JW300 (OPUS), OPUS autres, Wikipedia ew/kbp, bibles domaine public, collecte ciblée, audio
   - Vérification CGU en ligne (JW.org, OPUS) — à faire avec l'utilisateur
2. **Revue des ressources existantes** : inventaire OPUS/HF Hub pour l'éwé, taille Wikipedia ew/kbp, présence dans Common Voice/FLEURS, projets Masakhane
3. **Contacts locuteurs** : l'utilisateur est lui-même locuteur éwé ; 1 locuteur supplémentaire à confirmer (traduction + relecture), 1 contact linguistique (Université de Lomé) si possible, locuteurs kabiyè réservés à la phase optionnelle
4. **Repo GitHub** : `git init`, README, `.gitignore`, branches (main + dev)

**Sortie (jalon J1)** : matrice validée + 2 locuteurs confirmés + repo prêt.

---

## P1 — Corpus (semaines 2-6)

**Objectif** : produire le corpus publié (actif durable du projet).

### 1. Collecte automatique (`src/collect/`)
- JW300 éwé via `opustools` → `data/raw/jw300/` (étiquette : entraînement uniquement)
- Autres corpus OPUS (bibles, etc.) → `data/raw/opus/`
- Wikipedia éwé (+ kabiyè si utile) → `data/raw/wiki/`
- Scripts fournis par Sukuna, exécutés localement ou sur Colab

### 2. Nettoyage (`src/clean/`)
- Normalisation Unicode : ɖ ɸ ɣ ɔ ɛ ŋ, NFC, gestion des tons non marqués
- Déduplication (exacte + floue)
- Filtrage d'alignement (opusfilter : ratio de longueur, paires identiques, langue détectée)
- Stats par source et par registre → `data/processed/` + rapport

### 3. Collecte ciblée santé/éducation/administration (**SOURCE PRINCIPALE** du corpus publié)
- Sukuna prépare **10 grilles de 100-200 phrases françaises** (paludisme, vaccination, consultation, pharmacie, grossesse/nutrition, scolarisation, examens, état civil, démarches, services publics) — 1000-2000 phrases cibles
- Traduction par 2 locuteurs natifs indépendants ; divergence → arbitrage (3e ou linguiste)
- Relecture orthographique par le linguiste
- Compensation symbolique documentée

### 4. Vérification qualité
- Échantillonnage manuel, contrôle des alignements, cohérence des registres

### 5. Publication v1
- Dataset HuggingFace public (train/dev/test + sous-ensemble `domaine_cible`)
- Datasheet préliminaire

**Sortie (jalon J2)** : corpus ≥ 1000 paires vérifiées, ≥ 30% hors registre religieux.

---

## P2 — Traduction (semaines 6-10)

**Objectif** : modèle FR↔Éwé fine-tuné, évalué de façon crédible.

1. **Baseline** : NLLB-200-distilled-600M zero-shot sur train/dev/test → chrF++/COMET de référence
2. **Fine-tuning LoRA** (`src/train/`) : notebook Colab fourni (T4 gratuit, quelques heures), PEFT sur NLLB
3. **Back-translation** (`src/augment/`) — **conditionnel** (Wikipedia éwé quasi vide — constat 13/08) :
   - Collecte éwé monolingue : sources alternatives à identifier (pages Facebook publiques, sites d'actualité, blogs — avec vérification des licences)
   - Traduction vers le français avec le modèle seed
   - Filtrage (confiance + round-trip) → partition synthétique séparée
   - Ré-entraînement avec la partition synthétique
4. **Évaluation renforcée** (`src/evaluate/`) :
   - Automatique : chrF++ (principal), COMET, BLEU ; tests standard + **hors-domaine**
   - Humaine : gabarit 100 phrases × 2 directions, échelle adéquation/fluidité 1-5, 2 annotateurs, 3e en cas de désaccord

**Sortie (jalon J3)** : modèle > baseline sur les deux tests (chrF++), rapport d'évaluation.

---

## P3 — Packaging (semaines 10-12)

**Objectif** : rendre le projet public et reproductible.

1. **Démo Gradio** (`demo/app.py`) : traduction FR↔Éwé, métriques affichées → HF Spaces
2. **API REST** (`src/api/`) : FastAPI, `POST /translate` (text/src/tgt), documentation OpenAPI — le mode d'intégration principal pour les organisations
3. **CLI batch** (`src/cli/`) : `python -m toolkit.translate --input messages.csv --src fr --tgt ewe --output messages_ewe.csv` — pour les campagnes
4. **Datasheet** (`docs/02-datasheet-corpus.md`) : origine, licences, volumes, biais, procédures
5. **Rapport d'évaluation** (`docs/03-rapport-evaluation.md`) : métriques + revue humaine
6. **README complet** + model card + publication GitHub/HF
7. **Article de synthèse** (LinkedIn/blog) : démarche, choix, limites

> **Phase suivante (après P3)** : packaging de la bibliothèque Python réutilisable (`pip install ewe-nlp-toolkit`) — décidée avec l'utilisateur le 13/08/2026.

**Sortie (jalon J4)** : démo publique + repo reproductible.

---

## P4 — ASR (conditionnel, +2-3 semaines)

**Objectif** : démo de transcription éwé en domaine contraint (attentes WER réalistes : 40-70% en parole ouverte avec 5-10h).

1. **Protocole d'enregistrement** : formulaire de consentement (fourni), guide pratique (téléphone, pièce calme, 5-10h visées, équilibre locuteurs/domaines)
2. **Collecte + transcription** : enregistrements → transcription et alignement (outil fourni)
3. **Fine-tuning Whisper (LoRA)** sur Colab
4. **Évaluation WER** + démo domaine contraint (phrases de santé, commandes simples)

**Sortie (jalon J5)** : démo ASR + WER documenté.

---

## Risques de calendrier

- Recherche web en panne → vérifications CGU faites manuellement par l'utilisateur
- Disponibilité des locuteurs → planifier les sessions dès P0
- GPU gratuit saturé (Colab) → bascule Kaggle, ou sessions courtes
- Temps du cursus → chaque phase est publiable indépendamment (J1..J5 autonomes)
