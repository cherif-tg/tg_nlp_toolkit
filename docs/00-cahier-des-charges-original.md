# Cahier des Charges et Étude de Faisabilité
## Kabiyè-Éwé NLP Toolkit — Traduction et Reconnaissance Vocale pour Langues Bas-Ressource

**Auteur** : Cherif
**Établissement** : École Polytechnique de Lomé (EPL) — Licence Intelligence Artificielle et Big Data
**Date** : Août 2026
**Version** : 1.0

---

## 1. Contexte et justification du projet

### 1.1 Contexte général

L'Éwé et le Kabiyè comptent parmi les langues les plus parlées au Togo, avec plusieurs millions de locuteurs combinés à travers le Togo et les pays voisins (Ghana, Bénin pour l'Éwé). Malgré ce poids démographique, ces langues restent quasi absentes des grands corpus et modèles de traitement automatique du langage (TAL/NLP), qui restent dominés par l'anglais, le français et un nombre restreint de langues à fort volume de données numériques.

Cette absence a des conséquences concrètes : impossibilité d'accéder à des services numériques (santé, éducation, administration) dans sa langue maternelle pour une partie significative de la population togolaise, notamment en zone rurale où le français reste une langue seconde peu maîtrisée.

### 1.2 Constat du vide technique

Une revue des ressources existantes (HuggingFace Hub, OPUS, Masakhane, Common Voice) montre :
- Une couverture partielle et fragmentaire de l'Éwé (quelques corpus religieux, peu de corpus conversationnels)
- Une couverture quasi inexistante du Kabiyè
- Aucun outil de reconnaissance vocale (ASR) fonctionnel et accessible publiquement pour ces deux langues
- Des modèles de traduction multilingues (NLLB-200) qui intègrent l'Éwé mais avec des performances non documentées pour un usage réel

### 1.3 Justification du choix du projet

Ce projet s'inscrit dans une double logique :
1. **Impact réel** : produire une ressource réutilisable (corpus, modèles) pour la communauté togolaise et la recherche NLP africaine (écosystème Masakhane)
2. **Positionnement de carrière** : construire une expertise différenciante en NLP bas-ressource africain, alignée avec les besoins d'acteurs comme Umbaji (Yodi), et rarement démontrée dans les portfolios d'étudiants IA

---

## 2. Objectifs du projet

### 2.1 Objectif général

Concevoir un toolkit NLP open-source permettant la traduction automatique français ↔ Éwé et, dans un second temps, la reconnaissance vocale en Éwé, avec une extension possible au Kabiyè selon la disponibilité des ressources.

### 2.2 Objectifs spécifiques

| # | Objectif | Priorité |
|---|----------|----------|
| O1 | Constituer et publier un corpus parallèle français-Éwé nettoyé et documenté | Priorité 1 |
| O2 | Évaluer et fine-tuner un modèle de traduction automatique français ↔ Éwé | Priorité 1 |
| O3 | Publier une démonstration interactive accessible publiquement | Priorité 1 |
| O4 | Constituer un corpus audio et fine-tuner un modèle ASR en Éwé | Priorité 2 |
| O5 | Étendre le corpus et la traduction au Kabiyè | Priorité 3 (optionnelle) |

### 2.3 Non-objectifs (hors périmètre explicite)

- Développement d'une application mobile grand public complète (le projet livre un toolkit et une démo, pas un produit commercial)
- Couverture exhaustive de toutes les variantes dialectales de l'Éwé et du Kabiyè
- Synthèse vocale (text-to-speech) — envisageable comme extension future, non incluse dans ce périmètre

---

## 3. Étude de faisabilité

### 3.1 Faisabilité technique

| Aspect | Évaluation | Commentaire |
|--------|-----------|-------------|
| Disponibilité de modèles de base | Favorable | NLLB-200 couvre nativement l'Éwé (`ewe_Latn`) ; Whisper est fine-tunable pour de nouvelles langues |
| Ressources de calcul | Favorable | Fine-tuning LoRA/PEFT réalisable sur GPU gratuit (Google Colab, Kaggle) |
| Outils et bibliothèques | Favorable | Écosystème HuggingFace mature (Transformers, Datasets, PEFT, Evaluate) |
| Compétences requises | Acquises | Le porteur du projet maîtrise déjà PyTorch, le fine-tuning et les pipelines ML (via projets antérieurs) |

**Verdict** : techniquement faisable avec les outils et compétences déjà disponibles.

### 3.2 Faisabilité des données (risque principal)

C'est le facteur limitant majeur du projet, à traiter avec lucidité :

| Source de données | Volume estimé | Fiabilité | Risque |
|---|---|---|---|
| JW.org (traductions Éwé) | Moyen-élevé | Élevée | Restrictions d'usage à vérifier (CGU) |
| OPUS / corpus bible parallèles | Faible-moyen | Élevée | Couverture lexicale limitée à un registre religieux |
| Masakhane (ressources communautaires) | Variable | Élevée | Dépendance à ce que la communauté ait déjà publié |
| Collecte manuelle (locuteurs natifs) | Faible (100-1000 phrases) | Très élevée si supervisée | Chronophage, nécessite des volontaires |
| Corpus audio pour ASR | Très faible initialement | Dépend de la collecte | Risque le plus élevé du projet |

**Stratégie de mitigation** : prioriser l'Éwé (meilleure couverture documentaire que le Kabiyè), traiter le Kabiyè comme extension conditionnelle, et considérer l'ASR comme objectif secondaire activable seulement si une collecte audio minimale (5-10h) est atteignable.

### 3.3 Faisabilité temporelle

Projet dimensionné pour une réalisation en solo, en parallèle d'un cursus universitaire actif :

| Phase | Durée estimée |
|---|---|
| Cadrage et revue de ressources | 1 semaine |
| Constitution et nettoyage du corpus texte | 3-4 semaines |
| Traduction (baseline + fine-tuning + évaluation) | 2-3 semaines |
| ASR (conditionnel) | 2-3 semaines |
| Packaging, démo, documentation | 1-2 semaines |
| **Total (sans ASR)** | **7-9 semaines** |
| **Total (avec ASR)** | **9-12 semaines** |

### 3.4 Faisabilité économique

Coût quasi nul : outils open-source, GPU gratuit (Colab/Kaggle tiers gratuit suffisant pour du fine-tuning LoRA), hébergement gratuit de la démo (HuggingFace Spaces) et du corpus (HuggingFace Datasets).

### 3.5 Synthèse de faisabilité

Le projet est **faisable dans son périmètre priorité 1** (corpus + traduction texte + démo). L'ASR et l'extension Kabiyè sont **conditionnellement faisables**, dépendant de la capacité de collecte de données audio et de ressources écrites supplémentaires — ils sont donc traités comme objectifs secondaires et non comme livrables garantis.

---

## 4. Spécifications fonctionnelles

### 4.1 Fonctionnalités du corpus (F1)

- F1.1 : Agrégation de données parallèles français-Éwé issues de sources multiples
- F1.2 : Nettoyage automatisé (normalisation Unicode des caractères spéciaux ɖ, ƒ, ɔ, ɛ ; déduplication ; filtrage des paires mal alignées)
- F1.3 : Vérification qualité par échantillonnage manuel
- F1.4 : Export et publication au format standard (HuggingFace Datasets, JSON Lines)
- F1.5 : Documentation des sources, licences et limites du corpus

### 4.2 Fonctionnalités de traduction (F2)

- F2.1 : Traduction français → Éwé
- F2.2 : Traduction Éwé → français
- F2.3 : Évaluation quantitative (BLEU, chrF++) sur un jeu de test dédié
- F2.4 : Évaluation qualitative par relecture d'un locuteur natif

### 4.3 Fonctionnalités de reconnaissance vocale (F3 — conditionnel)

- F3.1 : Transcription audio Éwé → texte
- F3.2 : Évaluation via taux d'erreur mot (WER)

### 4.4 Fonctionnalités de démonstration (F4)

- F4.1 : Interface web interactive (saisie de texte, traduction affichée en temps réel)
- F4.2 : Affichage des métriques du modèle pour transparence
- F4.3 : Accès public sans authentification

---

## 5. Spécifications techniques

### 5.1 Architecture générale

```
Collecte & nettoyage corpus
        │
        ▼
Corpus parallèle FR-Éwé (HuggingFace Datasets)
        │
        ├──► Modèle de traduction (NLLB-200 baseline → fine-tuning LoRA)
        │            │
        │            ▼
        │      Évaluation (chrF++, BLEU, revue humaine)
        │            │
        │            ▼
        │      Démo Gradio / HuggingFace Spaces
        │
        └──► (Conditionnel) Corpus audio → Whisper fine-tuné (LoRA) → Évaluation WER
```

### 5.2 Stack technique

| Composant | Technologie |
|---|---|
| Langage | Python 3.11+ |
| Modèle de traduction de base | NLLB-200-distilled-600M |
| Modèle ASR de base (conditionnel) | Whisper small/base |
| Fine-tuning efficient | PEFT (LoRA) |
| Traitement de données | HuggingFace Datasets, pandas |
| Évaluation | sacrebleu, evaluate (HuggingFace) |
| Interface de démonstration | Gradio |
| Hébergement | HuggingFace Hub (modèles, datasets, Spaces) |
| Versionnement | Git / GitHub |

### 5.3 Environnement d'exécution

- Développement et fine-tuning : Google Colab / Kaggle Notebooks (GPU gratuit, T4/P100)
- Stockage : HuggingFace Hub (gratuit pour projets publics)
- Déploiement démo : HuggingFace Spaces (tier gratuit)

---

## 6. Livrables

| # | Livrable | Format |
|---|---|---|
| L1 | Corpus parallèle français-Éwé nettoyé et documenté | Dataset HuggingFace public |
| L2 | Modèle de traduction fine-tuné + rapport d'évaluation | Modèle HuggingFace + document de résultats |
| L3 | Démonstration interactive déployée | HuggingFace Spaces (Gradio) |
| L4 | Dépôt GitHub complet (code, README, méthodologie) | Repository public |
| L5 | Article de synthèse sur la démarche (collecte, choix méthodologiques, limites) | Article LinkedIn/blog |
| L6 (conditionnel) | Corpus audio + modèle ASR + évaluation WER | Dataset et modèle HuggingFace |
| L7 (optionnel) | Extension Kabiyè | Selon disponibilité des ressources |

---

## 7. Critères de succès

- Le corpus français-Éwé publié compte au minimum 1000 paires de phrases vérifiées
- Le modèle de traduction fine-tuné surpasse la baseline NLLB-200 zero-shot sur le jeu de test (chrF++)
- La démonstration est accessible publiquement et fonctionnelle sans intervention manuelle
- La documentation permet à un tiers de reproduire la démarche

---

## 8. Risques et plan de mitigation

| Risque | Probabilité | Impact | Mitigation |
|---|---|---|---|
| Corpus texte insuffisant en volume/qualité | Moyenne | Élevé | Multiplier les sources, prioriser qualité sur quantité, être transparent sur les limites |
| Absence de données audio exploitables | Élevée | Moyen | Traiter l'ASR comme objectif secondaire non garanti |
| Contraintes de temps liées au cursus universitaire | Moyenne | Moyen | Phasage strict avec priorités claires (P1/P2/P3), livrables intermédiaires publiables indépendamment |
| Restrictions de licence sur les sources de données | Faible-moyenne | Moyen | Vérification systématique des CGU avant intégration au corpus public |
| Performance insuffisante du modèle fine-tuné | Moyenne | Faible | Documenter honnêtement les limites plutôt que de survendre les résultats ; la valeur du projet réside aussi dans le corpus et la méthodologie |

---

## 9. Positionnement et valorisation

Ce projet s'inscrit dans l'écosystème NLP africain bas-ressource (communauté Masakhane) et complète un portfolio technique construit autour de projets ancrés dans les réalités togolaises. Il constitue une contribution potentiellement réutilisable par des acteurs locaux (startups, institutions) travaillant sur l'accessibilité numérique en langues africaines, tels qu'Umbaji (produit Yodi).
