# Étude de faisabilité — ASR éwé (piste 4)

- **Date** : 2026-08-15
- **Auteur** : Sukuna (avec recherches web + API HuggingFace du jour)
- **Objectif** : évaluer comment introduire l'audio (reconnaissance vocale) dans le projet

---

## 1. Bonne nouvelle : l'écosystème ASR éwé existe déjà

Contrairement au corpus de traduction (quasi vide avant notre travail), l'ASR
éwé dispose de **ressources existantes** :

### Datasets audio éwé

| Ressource | Contenu | Licence | Statut |
|---|---|---|---|
| **BibleTTS_Ewe-Bible** (HF, abiyo27) | Audio de la Bible en éwé + transcriptions | **CC-BY-SA-4.0** | Public ✓ |
| **WAXAL** (arXiv 2602.02734) | Corpus parole multilingue africain : 14 langues ASR + 10 TTS (éwé inclus) | À vérifier (Apache-2.0 sur les modèles) | Public ✓ |
| **Dataset Univ. du Ghana** (ICNLSP 2025) | **203 336 échantillons validés (1 130 h), 1 937 locuteurs** + 107 h transcrites | À vérifier (souvent sur demande) | À confirmer |
| **Ewe_News_Dataset** (HF, VKAgbesi) | Nouvelles en éwé | À vérifier | Public |
| **Common Voice (Mozilla)** | L'éwé y est cité comme langue cible (à confirmer la disponibilité) | CC0 | À confirmer |

### Modèles ASR éwé existants (HuggingFace)

| Modèle | Base | Licence | Downloads |
|---|---|---|---|
| `waxal-benchmarking/whisper-small-waxal-ewe` | whisper-small | Apache-2.0 | 39 |
| `waxal-benchmarking/whisper-tiny-waxal-ewe` | whisper-tiny | Apache-2.0 | 47 |
| `abiyo27/whisper-small-ewe` | whisper-small | À vérifier | 112 |
| `abiyo27/whisper-medium-ewe-mix` | whisper-medium | À vérifier | 11 |

**Référence de performance** (papier ICNLSP 2025, fine-tune Whisper sur éwé) :
WER 37 % / CER 12 % — prometteur pour du low-resource, améliorable avec plus
de données.

## 2. Options stratégiques

| Option | Description | Coût | Délai | Risque |
|---|---|---|---|---|
| **A. Utiliser un modèle existant** | Tester `whisper-small-waxal-ewe` sur nos textes lus | Faible | Jours | Qualité limitée par le modèle |
| **B. Fine-tuner Whisper (recommandé)** | Fine-tune `whisper-small` sur BibleTTS (CC-BY-SA) + nos propres enregistrements | Moyen (GPU Colab) | 2-4 semaines | Données nécessaires |
| **C. Collecte communautaire** | Contribuer à Common Voice éwé / enregistrer avec nos locuteurs | Élevé | Mois | Le plus durable |

## 3. 🎯 La synergie avec notre projet (recommandation)

Le point fort : **notre projet produit déjà le texte éwé** (corpus v0.3,
grilles 10 thèmes, lexique Riebstein). Pour l'ASR, il faut de l'**audio
aligné au texte**. Deux voies complémentaires :

1. **BibleTTS_Ewe-Bible** (CC-BY-SA-4.0) : audio biblique éwé déjà aligné →
   fine-tune immédiat (mais le texte diffère de notre Bible 1913 — c'est une
   version moderne ; la licence CC-BY-SA impose le partage dans les mêmes
   conditions → notre dataset ASR dérivé serait CC-BY-SA, à documenter)
2. **Enregistrements maison (la vraie valeur ajoutée)** : pendant la phase E
   (traduction manuelle des grilles), les locuteurs **enregistrent les
   phrases éwé** (téléphone suffit, ~30 min par grille) → dataset
   **audio + texte aligné, licence propre (CC0 avec consentement)**, domaine
   santé/éducation/administration = exactement notre cible fonctionnelle !

## 4. Feuille de route proposée

| Phase | Action | Durée |
|---|---|---|
| 4.1 | Évaluer `whisper-small-waxal-ewe` sur 20 phrases éwé lues (benchmark rapide) | 1 jour |
| 4.2 | Fine-tune `whisper-small` sur BibleTTS_Ewe-Bible (Colab) → modèle de base éwé | 1 semaine |
| 4.3 | Collecte audio maison : locuteurs enregistrent les grilles traduites (avec consentement) | 2-4 semaines (parallèle phase E) |
| 4.4 | Fine-tune final sur audio maison → ASR domaine fonctionnel + TTS possible | 1 semaine |

## 5. Points à vérifier avant engagement

- [ ] Licence et accès effectif du dataset **WAXAL** (éwé inclus ?)
- [ ] Disponibilité du dataset **Univ. du Ghana** (1 130 h) — téléchargeable ?
- [ ] Licence exacte de `abiyo27/whisper-small-ewe` et `BibleTTS_Ewe-Bible` (CC-BY-SA-4.0 confirmé pour le dataset)
- [ ] Présence éwé dans **Common Voice** (à confirmer via l'API)
- [ ] Compatibilité licence : un modèle fine-tuné sur des données CC-BY-SA
      hérite-t-il de la licence ? (Oui pour le dataset dérivé ; le modèle
      entraîné : question à documenter — Apache-2.0 pour les poids si
      re-entraîné sur données libres)

## 6. Conclusion

**Faisable et recommandé.** L'option B (fine-tune Whisper sur BibleTTS +
enregistrements maison) est la voie la plus rapide vers un ASR éwé
fonctionnel, avec une **synergie naturelle avec la phase E** (les locuteurs
enregistrent ce qu'ils traduisent). Coût : ~0 € (Colab gratuit), effort :
2-4 semaines en parallèle du reste.
