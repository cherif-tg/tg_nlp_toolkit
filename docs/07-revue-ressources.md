# Revue des ressources existantes — checklist (P0, point 2)

Objectif : savoir **exactement** ce qui existe déjà pour l'éwé et le kabiyè, pour ne pas réinventer l'existant et pour dimensionner la collecte. À faire après validation de la matrice de licences.

## 1. Corpus parallèles (OPUS)

- [ ] Ouvrir <https://opus.nlpl.eu/> et lister les corpus disponibles pour `ewe` :
  - JW300 (volume réel de paires ?)
  - bible-uedin (bible multilingue alignée)
  - Tatoeba (si présent)
  - Autres
- [ ] Noter pour chacun : volume, licence, qualité supposée (domaine)
- [ ] Vérifier si un corpus parallèle FR↔EWE existe déjà en l'état

## 2. HuggingFace Hub

- [ ] Rechercher `ewe` / `ewe_Latn` / `kabiye` dans les datasets : <https://huggingface.co/datasets?search=ewe>
- [ ] Rechercher les modèles : <https://huggingface.co/models?search=ewe> (traduction ? ASR ?)
- [ ] Noter ce qui est réutilisable (et sous quelle licence)

## 3. Textes monolingues (pour back-translation)

- [ ] Wikipedia éwé : nombre d'articles <https://ew.wikipedia.org/> — volume de texte exploitable ?
- [ ] Wikipedia kabiyè : <https://kbp.wikipedia.org/>
- [ ] Autres sources publiques (blogs, journaux en éwé, pages Facebook publiques) — à lister avec leur licence

## 4. Audio / ASR

- [ ] Common Voice : confirmer l'absence de l'éwé
- [ ] FLEURS / autres jeux multilingues : confirmer l'absence
- [ ] Tout autre jeu audio éwé existant (Masakhane, projets de recherche) ?

## 5. Communauté et projets existants

- [ ] Masakhane : projets passés sur l'éwé (traduction, ASR) — <https://github.com/masakhane-io>
- [ ] NLLB-200 : confirmer la couverture `ewe_Latn` et chercher des rapports de perf éwé
- [ ] Articles de recherche : éwé MT / low-resource (Google Scholar)

## 6. Synthèse attendue

| Catégorie | Existant | Réutilisable | Manquant |
|---|---|---|---|
| Parallèle FR↔EWE | ? | ? | ? |
| Monolingue EWE | ? | ? | ? |
| Audio EWE | ? | ? | ? |
| Modèles MT | ? | ? | ? |
| Modèles ASR | ? | ? | ? |

→ La synthèse détermine le **volume de collecte ciblée** nécessaire (P1).

## 7. Ressources historiques (vérifiées le 13/08/2026)

### Résultats

| Ressource | Année | Statut | Verdict |
|---|---|---|---|
| Bible éwé (British and Foreign Bible Society) | 1913 | **Domaine public** (badge Public Domain Mark 1.0 vérifié) | ✅ Publier — alignement avec bible FR domaine public (Louis Segond) → parallèle FR↔EWE |
| Vocabulaire de la langue éwé (Riebstein) | 1926 | Domaine public probable (vol. 2 français-éwé dispo, vol. 1 manquant) | ✅ Publier (paires lexicales + référence orthographique) — confirmer badge visuellement |
| Dictionnaire éwé-allemand (Westermann) | 1905 | Domaine public | 🔍 À localiser numérisé |
| Lexilogos (portail) | — | n/a | 📖 Bibliographie + clavier éwé + DUDH éwé (référence) |

### Actions restantes

- [ ] Confirmer visuellement le badge de licence de Riebstein 1926 sur archive.org
- [ ] Télécharger le full text de la bible 1913 et évaluer la qualité OCR (P1)
- [ ] Identifier une bible française domaine public (Louis Segond 1910) pour l'alignement verset à verset
- [ ] Chercher la numérisation du Westermann 1905
- [ ] Utiliser la bibliographie Lexilogos (Henrici 1891, Westermann 1907, grammaires) pour la revue de ressources
