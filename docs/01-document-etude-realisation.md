# Document d'Étude et de Réalisation
## Kabiyè-Éwé NLP Toolkit — Traduction et Reconnaissance Vocale pour Langues Bas-Ressource

**Auteur** : Cherif
**Établissement** : École Polytechnique de Lomé (EPL) — Licence Intelligence Artificielle et Big Data
**Date** : 13 août 2026
**Version** : 2.0 (corrigée et enrichie)

> **Base** : Cahier des charges v1.0 (archivé dans `docs/00-cahier-des-charges-original.md`).
> **Objet de la v2.0** : intégration des ajustements issus de la relecture critique — stratégie de licences, lutte contre le biais de registre, évaluation renforcée, attentes ASR réalistes, plan de collecte ciblée, éthique de la donnée.

---

## Historique des révisions

| Version | Date | Changements |
|---|---|---|
| 1.0 | Août 2026 | Cahier des charges initial |
| 2.0 | 13/08/2026 | Matrice de licences par source ; collecte ciblée santé/éducation/administration en priorité 1 ; protocole d'évaluation renforcé (hors-domaine, COMET, revue humaine formalisée) ; attentes WER réalistes pour l'ASR ; back-translation + filtrage ; datasheet ; principes éthiques de collecte ; plan de réalisation détaillé ; structure du dossier de projet |

---

## 1. Contexte et justification

### 1.1 Contexte général

L'Éwé et le Kabiyè comptent parmi les langues les plus parlées au Togo, avec plusieurs millions de locuteurs combinés à travers le Togo et les pays voisins (Ghana, Bénin pour l'Éwé). Malgré ce poids démographique, ces langues restent quasi absentes des grands corpus et modèles de traitement automatique du langage (TAL/NLP), dominés par l'anglais, le français et un petit nombre de langues à fort volume de données.

Conséquence concrète : une partie significative de la population togolaise — notamment en zone rurale où le français reste une langue seconde peu maîtrisée — ne peut pas accéder aux services numériques (santé, éducation, administration) dans sa langue maternelle.

### 1.2 Constat du vide technique

Revue des ressources existantes (HuggingFace Hub, OPUS, Masakhane, Common Voice) :
- Couverture partielle et fragmentaire de l'Éwé (corpus religieux surtout, peu de corpus conversationnels)
- Couverture quasi inexistante du Kabiyè
- Aucun outil de reconnaissance vocale (ASR) fonctionnel et publiquement accessible pour ces deux langues
- NLLB-200 intègre l'Éwé (`ewe_Latn`) mais avec des performances non documentées pour un usage réel

### 1.3 Positionnement stratégique (ajout v2.0)

**Le corpus est l'actif durable du projet ; les modèles sont périssables.** Les modèles de traduction évoluent vite (les LLM frontier traduisent déjà l'éwé décemment), mais un corpus éwé propre, documenté, sous licence claire — cela n'existe pas et personne d'autre ne le construira à notre place. Toute la stratégie du projet est orientée autour de ce principe : **produire la donnée manquante, la publier, et la valoriser**.

---

## 2. Objectifs

### 2.1 Objectif général

Concevoir un toolkit NLP open-source permettant la traduction automatique français ↔ Éwé — avec une attention particulière aux domaines santé, éducation et administration — puis, dans un second temps, la reconnaissance vocale en Éwé, avec une extension possible au Kabiyè selon la disponibilité des ressources.

### 2.2 Objectifs spécifiques

| # | Objectif | Priorité |
|---|----------|----------|
| O1 | Constituer et publier un corpus parallèle français-Éwé nettoyé, documenté et **sous licence claire** | P1 |
| O2 | **Collecte ciblée de 500 à 1000 phrases des domaines santé, éducation et administration**, vérifiées par des locuteurs natifs (correction du biais de registre) | P1 |
| O3 | Évaluer et fine-tuner un modèle de traduction automatique français ↔ Éwé, avec **évaluation renforcée** (hors-domaine, COMET, revue humaine) | P1 |
| O4 | Publier une démonstration interactive accessible publiquement | P1 |
| O5 | **Augmenter le corpus par back-translation + filtrage** à partir de données monolingues éwé | P1 |
| O6 | Constituer un corpus audio et fine-tuner un modèle ASR en Éwé (**attentes WER réalistes, démo en domaine contraint**) | P2 |
| O7 | Étendre le corpus et la traduction au Kabiyè | P3 (optionnelle) |

### 2.3 Non-objectifs

- Développement d'une application mobile grand public complète (le projet livre un toolkit et une démo, pas un produit commercial)
- Couverture exhaustive de toutes les variantes dialectales de l'Éwé et du Kabiyè
- Synthèse vocale (text-to-speech) — extension future possible, hors périmètre
- **Surpasser les LLM frontier en traduction** — le projet vise des modèles ouverts, reproductibles et des données durables, pas la compétition avec les modèles propriétaires
- **Packaging d'une bibliothèque Python publique réutilisable** — prévu en phase suivante (après P3), non inclus dans le périmètre initial

---

## 3. Étude de faisabilité

### 3.1 Faisabilité technique

| Aspect | Évaluation | Commentaire |
|--------|-----------|-------------|
| Modèles de base | Favorable | NLLB-200 couvre l'Éwé (`ewe_Latn`) ; Whisper fine-tunable pour de nouvelles langues |
| Ressources de calcul | Favorable | Fine-tuning LoRA/PEFT sur GPU gratuit (Google Colab, Kaggle) |
| Outils | Favorable | HuggingFace (Transformers, Datasets, PEFT, Evaluate), sacrebleu, COMET |
| Compétences | Acquises | PyTorch, fine-tuning et pipelines ML déjà maîtrisés |

**Verdict** : techniquement faisable avec les outils et compétences disponibles.

### 3.2 Faisabilité des données (risque principal — stratégie corrigée)

Le facteur limitant majeur. La v2.0 ajoute deux exigences structurelles : **une décision de licence explicite par source** (avant toute intégration) et **un plan de collecte ciblée** pour corriger le biais de registre.

#### 3.2.1 Matrice des sources et licences

| Source | Langues | Volume estimé | Statut de licence | Usage autorisé |
|---|---|---|---|---|
| JW300 (via OPUS) | Éwé | À confirmer (page éwé introuvable sur OPUS à la navigation — vérification API en P1) | CGU JW vérifiées le 13/08 (redistribution interdite, scraping interdit) | **Entraînement uniquement** — ne pas publier tel quel |
| OPUS (autres corpus) | Éwé | Faible-moyen | Variables (souvent libres) | Publier si licence vérifiée |
| Wikipedia (ew, kbp) | Éwé, Kabiyè | Quasi vide (vérifié 13/08 : pas d'articles en éwé) | CC BY-SA | Indisponible — la page « alphabet éwé » est conservée comme référence orthographique |
| Bibles éwé (EB14, AL, EWERV) | Éwé | Moyen | Toutes sous copyright (Bible Society of Togo, Biblica, Bible Society of Ghana) | **Ne pas publier** — entraînement uniquement si besoin critique |
| **Collecte ciblée santé/éducation/admin** | Éwé (puis Kabiyè) | 500-1000 phrases | Propriété du projet, publiée sous licence ouverte (CC-BY-4.0) | Publier |
| Enregistrements audio (locuteurs) | Éwé | 5-10h visées | Consentement écrit explicite, anonymisation | Publier uniquement avec consentement |

**Constats de la vérification du 13/08/2026** : OPUS sans corpus éwé trouvé à la navigation (à confirmer via API en P1) ; Bibles éwé toutes sous copyright ; Wikipedia éwé quasi vide. Conséquence : la collecte ciblée devient la **source principale** du corpus publié (volume cible porté à 1000-2000 phrases).

**Règles d'or** :
1. **Une source = une décision de licence écrite**, consignée dans `data/licenses/` avant intégration.
2. Le corpus **publié** ne contient que des sources publiables. Le JW300 reste utilisable pour l'entraînement des modèles, mais n'entre jamais dans le dataset public.
3. Ne jamais mélanger silencieusement des sources de licences différentes dans un même fichier publié.

#### 3.2.2 Correction du biais de registre (nouveau)

Le risque identifié : un corpus dominé par le texte religieux (JW, Bible) produira un modèle performant sur le registre religieux et médiocre sur les domaines d'impact visés (santé, éducation, administration).

**Mitigation structurée** : la collecte ciblée (O2) devient une priorité 1 à part entière, avec protocole dédié (§ 6.3). Critère de succès associé : au moins **30% du corpus publié hors registre religieux**, idéalement dans les domaines cibles.

#### 3.2.3 Attentes ASR réalistes (ajustement)

Avec 5-10h d'audio, le WER en parole ouverte sera probablement de **40 à 70%** — utilisable en démonstration, pas en production. Deux décisions :
- Cadrer la démo ASR sur un **domaine contraint** (phrases de santé, commandes simples : oui/non, chiffres, demandes courantes) ;
- Ne pas promettre un WER « production » dans les livrables.

### 3.3 Faisabilité temporelle (ajustée)

| Phase | Durée estimée | Contenu |
|---|---|---|
| P0 — Cadrage | 1 semaine | Matrice de licences validée, revue des ressources, contacts locuteurs natifs, partenariat linguistique |
| P1 — Corpus | 4-5 semaines | Collecte multi-sources + nettoyage + **collecte ciblée** santé/éducation/admin + vérification |
| P2 — Traduction | 3-4 semaines | Baseline NLLB, fine-tuning LoRA, back-translation, évaluation renforcée |
| P3 — Packaging | 1-2 semaines | Démo, API REST, CLI batch, datasheet, documentation, publication |
| P4 — ASR (conditionnel) | 2-3 semaines | Collecte audio, fine-tuning Whisper, évaluation WER |
| **Total sans ASR** | **9-12 semaines** | |
| **Total avec ASR** | **11-15 semaines** | |

### 3.4 Faisabilité économique

Coût quasi nul : outils open-source, GPU gratuit (Colab/Kaggle), hébergement gratuit (HuggingFace Spaces / Datasets). **Poste à prévoir** : compensation symbolique des locuteurs natifs (traduction, annotation, enregistrement) — quelques dizaines de milliers de FCFA, à budgéter dès le départ.

### 3.5 Synthèse

Le périmètre P1 est **faisable** avec les ajustements ci-dessus. L'ASR est **conditionnellement faisable** avec des attentes WER réalistes et un domaine contraint. L'extension Kabiyè est **optionnelle**, dépendante des ressources écrites disponibles.

---

## 4. Spécifications fonctionnelles

### 4.1 Corpus (F1)

- F1.1 : Agrégation de données parallèles français-Éwé issues de sources multiples
- F1.2 : Nettoyage automatisé (normalisation Unicode : ɖ, ɸ, ɣ, ɔ, ɛ, ŋ ; déduplication ; filtrage des paires mal alignées — pipeline opusfilter)
- F1.3 : Vérification qualité par échantillonnage manuel + validation orthographique par un linguiste
- F1.4 : Export et publication au format standard (HuggingFace Datasets, JSON Lines)
- F1.5 : Documentation des sources, **licences** et limites du corpus
- **F1.6 (nouveau)** : Datasheet / carte de données complète (contenu § 6.5)
- **F1.7 (nouveau)** : Matrice de licences publiée dans le dépôt (`data/licenses/`)
- **F1.8 (nouveau)** : Sous-ensemble « domaine cible » (santé/éducation/admin) identifié et documenté

### 4.2 Traduction (F2)

- F2.1 : Traduction français → Éwé
- F2.2 : Traduction Éwé → français
- F2.3 : Évaluation automatique **chrF++ (principal) + COMET (secondaire) + BLEU (référence)**
- **F2.4 (renforcé)** : Évaluation sur **jeu de test hors-domaine** (conversationnel / administratif), en plus du test standard
- **F2.5 (renforcé)** : Évaluation humaine formalisée — 2 annotateurs locuteurs natifs, échelle adéquation/fluidité 1-5, échantillon défini, désaccord → 3e annotateur

### 4.3 Reconnaissance vocale (F3 — conditionnel)

- F3.1 : Transcription audio Éwé → texte
- F3.2 : Évaluation WER, avec **attentes documentées** (40-70% en parole ouverte attendus avec 5-10h)
- **F3.3 (nouveau)** : Démo ASR en **domaine contraint** (phrases de santé, commandes simples)

### 4.4 Démonstration (F4)

- F4.1 : Interface web interactive (saisie texte, traduction en temps réel)
- F4.2 : Affichage des métriques du modèle pour transparence
- F4.3 : Accès public sans authentification

### 4.5 API REST et traitement par lot (F5-F6 — livrables du périmètre)

- F5.1 : API REST `POST /translate` (text, src, tgt) → traduction ; `POST /transcribe` (audio, conditionnel ASR)
- F5.2 : API déployable localement (FastAPI), documentée (OpenAPI)
- F6.1 : CLI de traduction par lot (fichier CSV → fichier traduit), pour les campagnes de masse (SMS, sensibilisation)
- F6.2 : CLI testé sur un cas d'usage réel (ex. campagne de 1000+ messages)
- Note : la bibliothèque Python réutilisable (`import ewe_nlp_toolkit`) est prévue en **phase suivante**, hors périmètre initial

---

## 5. Spécifications techniques

### 5.1 Architecture générale (mise à jour)

```
Collecte multi-sources (JW300, OPUS, Wikipedia, domaine public)
        │  + décision de licence par source (data/licenses/)
        ▼
Corpus parallèle FR-Éwé (HuggingFace Datasets)
        │
        ├──► Collecte ciblée santé/éducation/admin (500-1000 phrases vérifiées)
        │            │
        │            ▼
        │      Corpus « domaine cible » (publication prioritaire)
        │
        ├──► Baseline NLLB-200 zero-shot → fine-tuning LoRA
        │            │
        │            ▼
        │      Évaluation renforcée (chrF++, COMET, hors-domaine, revue humaine)
        │            │
        │            ▼
        │      Back-translation (éwé monolingue) → filtrage → 2e itération
        │            │
        │            ▼
        │      Démo Gradio / HuggingFace Spaces
        │
        └──► (Conditionnel) Corpus audio → Whisper fine-tuné (LoRA) → WER → démo domaine contraint
```

### 5.2 Stack technique

| Composant | Technologie |
|---|---|
| Langage | Python 3.11+ |
| Traduction de base | NLLB-200-distilled-600M |
| ASR de base (conditionnel) | Whisper small/base |
| Fine-tuning efficient | PEFT (LoRA) |
| Traitement de données | HuggingFace Datasets, pandas, opusfilter |
| Évaluation | sacrebleu (chrF++, BLEU), COMET (unbabel), evaluate, jiwer (WER) |
| Interface | Gradio |
| API / CLI | FastAPI + uvicorn (API REST), typer (CLI batch) |
| Hébergement | HuggingFace Hub (datasets, models, Spaces) |
| Versionnement | Git / GitHub |

### 5.3 Environnement d'exécution

- Développement et fine-tuning : Google Colab / Kaggle Notebooks (GPU gratuit)
- Stockage : HuggingFace Hub (gratuit pour projets publics)
- Déploiement démo : HuggingFace Spaces (tier gratuit)

---

## 6. Livrables

| # | Livrable | Format |
|---|---|---|
| L1 | Corpus parallèle français-Éwé nettoyé et documenté | Dataset HuggingFace public + datasheet |
| L2 | Modèle de traduction fine-tuné + rapport d'évaluation | Modèle HuggingFace + document de résultats |
| L3 | Démonstration interactive déployée | HuggingFace Spaces (Gradio) |
| L4 | **API REST** (`POST /translate`, OpenAPI) | Déployable localement, docs OpenAPI |
| L5 | **CLI de traitement par lot** (CSV → CSV) | Package CLI documenté et testé |
| L6 | Dépôt GitHub complet (code, README, méthodologie) | Repository public |
| L7 | Article de synthèse sur la démarche | Article LinkedIn/blog |
| L8 (conditionnel) | Corpus audio + modèle ASR + évaluation WER | Dataset et modèle HuggingFace |
| L9 (optionnel) | Extension Kabiyè | Selon disponibilité des ressources |
| L10 (phase suivante) | Bibliothèque Python réutilisable (`pip install ewe-nlp-toolkit`) | Package PyPI/GitHub |

## 7. Stratégie de données

### 6.1 Principes

1. **Le corpus est l'actif durable** — tout le projet s'y ramène
2. **Licences d'abord** — aucune donnée intégrée sans décision écrite
3. **Domaine d'abord** — la couverture santé/éducation/admin prime sur le volume
4. **Éthique** — consentement et compensation des locuteurs, transparence

### 6.2 Matrice des sources et licences

Voir § 3.2.1. Livrable formel : `data/licenses/matrix.csv` + un fichier par source (extrait des CGU, décision, date).

### 6.3 Protocole de collecte ciblée (santé/éducation/admin)

- **Thématiques** (10) : paludisme, vaccination, consultation médicale, pharmacie, grossesse/nutrition, scolarisation, examens scolaires, état civil, démarches administratives, services publics
- **Gabarit** : ~100-200 phrases par thématique = 1000-2000 phrases cibles (**source principale** du corpus publié — constat P0 du 13/08)
- **Évolutivité** : les domaines sont extensibles — la V1 couvre santé/éducation/administration ; les versions suivantes ajouteront d'autres domaines (agriculture, commerce, actualités, conversation) pour généraliser le corpus (stratégie validée le 13/08)
- **Traduction** : chaque phrase traduite par 2 locuteurs natifs indépendants ; divergence → arbitrage (3e locuteur ou linguiste)
- **Validation** : relecture orthographique par un linguiste (partenariat Université de Lomé)
- **Compensation** : rémunération symbolique documentée (budget § 3.4)
- **Licence** : CC-BY-4.0 (attribution aux traducteurs, consentement écrit)

### 6.4 Augmentation du corpus (back-translation)

1. Entraîner un modèle seed FR↔Éwé sur le corpus nettoyé
2. Collecter de l'éwé monolingue (Wikipedia, réseaux sociaux publics, blogs — en respectant les licences)
3. Traduire l'éwé monolingue vers le français avec le modèle seed
4. **Filtrer** : scores de confiance, round-trip (retraduire et comparer), filtres de longueur/duplication
5. N'injecter que les paires de haute confiance dans une **partition séparée** (jamais mélangée aux données vérifiées par des humains)

### 6.5 Carte de données (datasheet) — contenu obligatoire

- Objectif et origine du corpus
- Sources et licences (lien vers la matrice)
- Volumes par source et par registre
- Répartition train/dev/test (documentée, non chevauchante)
- Biais connus (registre, dialectes, style)
- Procédure de collecte et de validation humaine
- Consentement et compensation des contributeurs
- Restrictions d'usage

---

## 8. Plan de réalisation

| Phase | Durée | Tâches | Jalons / critères de sortie |
|---|---|---|---|
| P0 — Cadrage | 1 sem. | Matrice de licences ; revue des ressources ; contacts locuteurs ; partenariat linguistique | J1 : matrice validée + 2 locuteurs confirmés |
| P1 — Corpus | 4-5 sem. | Collecte multi-sources ; nettoyage ; collecte ciblée ; vérification | J2 : corpus publié ≥ 1000 paires vérifiées, dont ≥ 30% hors registre religieux |
| P2 — Traduction | 3-4 sem. | Baseline ; fine-tuning LoRA ; back-translation ; évaluation renforcée | J3 : modèle > baseline sur test standard **et** hors-domaine (chrF++) |
| P3 — Packaging | 1-2 sem. | Démo Gradio ; API REST ; CLI batch ; datasheet ; docs ; publication HF | J4 : démo + API + CLI publics + repo reproductible |
| P4 — ASR (cond.) | 2-3 sem. | Collecte audio 5-10h ; fine-tuning Whisper ; WER | J5 : démo ASR domaine contraint + WER documenté |

**Chaque livrable intermédiaire est publiable indépendamment** (sécurité en cas de contrainte de temps).

---

## 9. Évaluation

### 8.1 Automatique

- **Principal** : chrF++ (robuste pour les langues à faible ressource, insensible aux variations morphologiques)
- **Secondaire** : COMET (aligné sur le jugement humain)
- **Référence** : BLEU (comparabilité avec la littérature)

### 8.2 Jeux de données

- Split train/dev/test documenté, non chevauchant, par source (pas de fuite entre sources)
- **Jeu de test hors-domaine** : phrases conversationnelles/administratives non vues à l'entraînement

### 8.3 Évaluation humaine

- 2 annotateurs locuteurs natifs
- Échelle adéquation/fluidité (1-5) sur un échantillon défini (~100 phrases par direction)
- Désaccord → 3e annotateur
- Rapport d'évaluation publié (`docs/03-rapport-evaluation.md`)

### 8.4 Critères de succès (mis à jour)

- Corpus publié ≥ 1000 paires vérifiées, **dont ≥ 30% hors registre religieux** (santé/éduc/admin)
- Collecte ciblée : ≥ 1000 phrases du domaine cible, double-traduites et validées
- Modèle fine-tuné > baseline NLLB zero-shot sur le test standard **et** le test hors-domaine
- COMET et revue humaine documentés (pas seulement BLEU/chrF++)
- Démo publique fonctionnelle, métriques affichées
- Datasheet + matrice de licences publiées
- Documentation reproductible par un tiers

---

## 10. Risques et plan de mitigation (mis à jour)

| Risque | Probabilité | Impact | Mitigation |
|---|---|---|---|
| **Licences JW.org incompatibles avec publication** | Élevée | Élevé | Matrice de licences dès P0 ; corpus publié = sources libres uniquement ; JW300 réservé à l'entraînement |
| **Biais de registre (corpus religieux)** | Élevée | Élevé | Collecte ciblée en P1 ; critère ≥ 30% hors religieux ; test hors-domaine |
| Volume texte insuffisant | Moyenne | Élevé | Multi-sources ; back-translation + filtrage ; priorité qualité |
| Absence de données audio exploitables | Élevée | Moyen | ASR conditionnel ; démo domaine contraint ; attentes WER documentées |
| WER élevé (40-70%) | Élevée | Moyen | Promesse ajustée ; domaine contraint ; transparence |
| Contraintes de temps (cursus) | Moyenne | Moyen | Phasage strict ; livrables publiables indépendamment |
| Restrictions de licence non détectées | Faible-moyenne | Moyen | Revue systématique des CGU avant intégration ; trace écrite |
| Performance modèle insuffisante | Moyenne | Faible | Documentation honnête ; la valeur réside dans le corpus et la méthodologie |

---

## 11. Valorisation et positionnement

- **Actif principal** : le corpus éwé (et sa carte de données) — réutilisable par les startups locales, institutions et la recherche
- **Communauté** : contribution à l'écosystème Masakhane (normes, relecture, diffusion)
- **Carrière** : expertise NLP bas-ressource africain, alignée avec les besoins d'acteurs comme Umbaji (Yodi)
- **Narration** : « la donnée manquante » — un projet qui construit l'infrastructure de données, pas seulement un modèle de plus
- **Retombées académiques possibles** : mémoire/paper sur la méthodologie de collecte bas-ressource

---

## 12. Structure du dossier de projet

```
togo-nlp-toolkit/
├── README.md                  # vue d'ensemble, badges, liens HF, guide de démarrage
├── docs/
│   ├── 00-cahier-des-charges-original.md   # v1.0 archivée
│   ├── 01-document-etude-realisation.md    # ce document (v2.0)
│   ├── 02-datasheet-corpus.md              # carte de données (à rédiger)
│   └── 03-rapport-evaluation.md            # résultats, métriques, revue humaine
├── data/
│   ├── raw/                   # sources brutes, jamais modifiées (hors git si volumineux)
│   ├── processed/             # corpus nettoyés : train/dev/test + domaine cible
│   ├── licenses/              # matrice des licences + justificatifs par source
│   └── README.md              # description des données, conventions
├── src/
│   ├── collect/               # scripts de collecte (JW300, OPUS, Wikipedia, audio)
│   ├── clean/                 # normalisation Unicode, dédup, filtrage (opusfilter)
│   ├── augment/               # back-translation + filtrage
│   ├── train/                 # fine-tuning LoRA (NLLB, Whisper)
│   ├── evaluate/              # chrF++, COMET, BLEU, WER, revue humaine
│   └── README.md              # architecture du code, conventions
├── notebooks/                 # explorations (EDA corpus, qualité, analyses)
├── models/                    # artefacts locaux (gitignorés ; configs versionnées)
├── demo/                      # app Gradio (traduction + ASR conditionnel)
├── tests/                     # tests unitaires des scripts (collecte, nettoyage)
├── scripts/                   # scripts one-shot (soumission HF, publication)
└── .gitignore                 # data/raw, models/, .env, caches
```
