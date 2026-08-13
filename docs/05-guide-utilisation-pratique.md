# Guide d'Utilisation Pratique — comment le toolkit s'utilise

## 1. Positionnement : un moteur, pas une application

Le toolkit n'est **pas** une app que l'utilisateur final installe. C'est le **moteur IA** (corpus + modèles + API) sur lequel des applications sont construites : bots WhatsApp, services SMS, outils des ONG, plateformes du gouvernement.

```
┌─────────────────────────────────────────────────────────┐
│  APPLICATIONS (produits finaux)                         │
│  Bot WhatsApp santé · campagnes SMS · portail admin ·   │
│  assistant vocal · outils éducatifs                     │
├─────────────────────────────────────────────────────────┤
│  API du toolkit (REST / bibliothèque Python)  ← LIVRÉ  │
├─────────────────────────────────────────────────────────┤
│  MODÈLES : traduction FR↔Éwé (NLLB fine-tuné)           │
│           ASR Éwé (Whisper, conditionnel)               │
├─────────────────────────────────────────────────────────┤
│  DONNÉES : corpus parallèle publié (l'actif durable)    │
└─────────────────────────────────────────────────────────┘
```

## 2. Les 5 modes d'utilisation

### Mode 1 — Bibliothèque Python (pour développeurs)
Un développeur installe le package et l'appelle dans son code :

```python
from ewe_nlp_toolkit import Translator

tr = Translator()
fr_vers_ewe = tr.translate("Prends ce médicament deux fois par jour", src="fr", tgt="ewe")
ewe_vers_fr = tr.translate("Meɖe kpe ɖe ŋutsu sia ŋu", src="ewe", tgt="fr")
```

Usage réel : un développeur d'une startup santé intègre la traduction dans son app sans se soucier du modèle.

### Mode 2 — API REST (pour les systèmes distants)
Le modèle est exposé comme service web (FastAPI ou HuggingFace Spaces) :

```bash
curl -X POST http://localhost:8000/translate \
  -H "Content-Type: application/json" \
  -d '{"text": "Le centre de santé est ouvert de 8h à 17h", "src": "fr", "tgt": "ewe"}'
```

Réponse : `{"translation": "..."}`. C'est le mode le plus demandé par les organisations — elles appellent l'API depuis n'importe quel système (SMS gateway, site web, bot).

### Mode 3 — Traitement par lot (campagnes)
Traduire des milliers de messages d'un coup — cas typique : campagne de sensibilisation :

```bash
python -m toolkit.translate --input messages.csv --src fr --tgt ewe --output messages_ewe.csv
```

Usage réel : le Programme National de Lutte contre le Paludisme (PNLP) ou une ONG veut envoyer 5000 SMS de prévention **en éwé**. On traduit le lot en une commande, puis le prestataire SMS diffuse.

### Mode 4 — Pipeline voix (pour les non-lettrés)
Audio éwé → transcription (Whisper) → éventuellement traduction vers le français :

```python
from ewe_nlp_toolkit import SpeechRecognizer

asr = SpeechRecognizer()
texte = asr.transcribe("audio_agent_sante.wav")   # → texte éwé
```

Usage réel : un agent de santé communautaire envoie une note vocale en éwé ; elle est transcrite et traduite pour le dossier médical. C'est le chemin d'accès aux populations qui ne lisent pas.

### Mode 5 — Démo interactive (vitrine + évaluation)
La démo Gradio sur HuggingFace Spaces : saisie de texte, traduction en temps réel, métriques affichées. Pour démontrer, évaluer, et pour ton portfolio.

## 3. Cas d'intégration typique : un bot WhatsApp santé

```
Utilisateur (éwé) ──► WhatsApp ──► Bot ──► API toolkit (éwé→français)
                                          │
                                          ▼
                                   Moteur de réponse (français)
                                          │
                                          ▼
Utilisateur (éwé) ◄── WhatsApp ◄── Bot ◄── API toolkit (français→éwé)
```

L'utilisateur écrit ou parle en éwé, le système comprend en français, répond en éwé. **Le toolkit est l'étage de traduction au milieu** — il ne fait pas le dialogue, il rend le dialogue accessible en langue locale.

## 4. Contraintes techniques honnêtes

| Contrainte | Réalité |
|---|---|
| Vitesse | Modèle 600M : ~1-3 s/phrase sur CPU, <1 s sur GPU. Acceptable pour chat, pas pour du temps réel massif |
| Production | Quantization (int8), éventuellement distillation pour baisser la charge serveur |
| ASR | WER 40-70% en parole ouverte avec 5-10h → démo en domaine contraint |
| Mobile | Pas de version embarquée sur téléphone (modèle trop lourd) — l'accès passe par API |
| Coût | API sur serveur modeste (ou HF Inference Endpoints) ; la démo tient sur le tier gratuit |

## 5. Livré vs à construire (projets suivants)

**Livré par ce projet** : corpus public, modèles, API REST, CLI de batch, démo Gradio, documentation d'intégration.
**Phase suivante (décidée le 13/08/2026)** : bibliothèque Python réutilisable (`pip install ewe-nlp-toolkit`) — le mode 1 deviendra alors un livrable.

**À construire ensuite (hors périmètre)** : bot WhatsApp complet, app mobile, intégration avec les SMS gateways des opérateurs, plateformes ministérielles. Chaque produit = un projet de plus, qui s'appuie sur ce toolkit.

## 6. Publics consommateurs

1. **Développeurs** (startups type Umbaji/Yodi, freelances) → bibliothèque + API
2. **Organisations** (PNLP, ONG, ministères) → batch + API
3. **Chercheurs** (Masakhane, universités) → corpus + model cards
4. **Toi** → portfolio, expertise, et démonstration de bout en bout
