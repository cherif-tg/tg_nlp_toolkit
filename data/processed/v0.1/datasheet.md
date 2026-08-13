# Datasheet — Corpus parallèle FR↔Éwé v0.1 (exploratoire)

- **Version** : 0.1 (exploratoire — non vérifié par locuteur natif)
- **Date de génération** : 2026-08-13
- **Paires** : 18 995 « ok » (train 15 199 / dev 1 898 / test 1 898) + 4 554 candidates « à vérifier »
- **Langues** : français (`fr`) ↔ éwé (`ee`, ISO 639-3 `ewe`, langue gbe du sud Togo/Bénin/Ghana)

## 1. Motivation

Combler le manque de données parallèles publiques français↔éwé (langue parlée par
~3 M de locuteurs ; quasi aucune donnée structurée publiée en 2026). Ce corpus est
la colonne vertébrale d'un toolkit NLP pour le Togo (traduction + ASR conditionnel).

## 2. Composition

| Composante | Volume | Contenu |
|---|---|---|
| `train.tsv` | 15 199 | paires ok, split 80 % stratifié par livre |
| `dev.tsv` | 1 898 | paires ok, 10 % |
| `test.tsv` | 1 898 | paires ok, 10 % (jeu d'évaluation) |
| `candidates-a-verifier.tsv` | 4 554 | versets fusionnés par l'OCR (ratio de longueur hors norme) |

66 livres couverts (Ancien + Nouveau Testament). Longueur moyenne des phrases : voir STATS.md.

## 3. Collecte

- **Côté éwé** : Bible éwé 1913, British and Foreign Bible Society
  (archive.org, **domaine public** — badge Public Domain Mark 1.0 vérifié).
  Texte OCR complet (182 540 lignes) téléchargé et nettoyé.
- **Côté français** : Bible Louis Segond 1910 (**domaine public**), texte p.sfm
  du dépôt GitHub `BibleCorps/FRA-B-LSG1910-PD-UBS`, 31 170 versets.

## 4. Prétraitement

Pipeline complet (scripts dans `src/clean/`, commits référencés dans le README) :
1. Nettoyage OCR : dé-hyphenation, filtrage du bruit (références croisées, en-têtes de page, notes)
2. Normalisation cyrillique : 51 422 homoglyphes cyrilliques corrigés (table de codepoints + corrections mot-à-mot)
3. Localisation des 66 livres (positions des titres dans le scan)
4. Extraction des versets (numérotation OCR, chapitres estimés)
5. Alignement verset-à-verset par programmation dynamique (bande 250) — 23 549 paires, 100 % à numéros identiques
6. Nettoyage fin : retrait des références croisées résiduelles, numéros parasites ; flag qualité par ratio de longueur

## 5. Biais et limitations (à lire avant usage)

- **Registre** : exclusivement biblique/religieux (traduction de 1913). Aucune couverture des domaines modernes (santé, éducation, administration).
- **Orthographe** : éwé de 1913, antérieur aux conventions orthographiques modernes (1984). Les diacritiques (ɛ, ɔ, ŋ, ƒ) sont **partiellement absents** de l'OCR.
- **Erreurs OCR** : texte scanné il y a un siècle ; erreurs résiduelles localisées (versets fusionnés, numéros avalés, références résiduelles).
- **Non vérifié** : l'échantillon de 100 paires est en cours de vérification par un locuteur natif (statut à mettre à jour).
- **Style français** : Segond 1910 = français littéraire ancien, pas le français courant.

## 6. Utilisations recommandées

- Fine-tuning de modèles de traduction (ex. NLLB-200-distilled-600M, langue `ewe_Latn`)
- Évaluation (test set séparé, jamais utilisé en entraînement)
- Combinaison avec le lexique Riebstein 1926 (8 575 paires de mots, `data/processed/`) et les grilles manuelles (10 thèmes, 1 050 phrases) pour le domaine moderne

## 7. Licence

- Sources : **domaine public** (Bible 1913 BFBS ; Segond 1910)
- Corpus dérivé : publiable. Diffusion prévue : HuggingFace (privé → public après vérification)
- Décisions de licence écrites : `data/licenses/decision-bible-ewe.md`, `decision-segond1910.md`, `matrix.csv`

## 8. Maintenance

- Responsables : Cherif (vérification linguistique) + Sukuna (pipeline)
- Prochaine mise à jour : intégration des corrections de l'échantillon de vérification → v0.2
- Reproductibilité : seed 42, scripts versionnés dans `src/clean/`

## 9. Contact

Projet `togo-nlp-toolkit` — cheriftenga (HuggingFace).
