# Datasheet — Corpus parallèle FR↔Éwé v0.2 (exploratoire, calibré)

- **Version** : 0.2 (exploratoire — partiellement vérifié par locuteur natif)
- **Date** : 2026-08-14
- **Paires** : 16 050 « ok » (train 12 844 / dev 1 603 / test 1 603) + 7 499 candidates « à vérifier »
- **Langues** : français (`fr`) ↔ éwé (`ee` / `ewe`)

## Langues et variantes (14/08 — à compléter par les locuteurs)

> ⚠️ Les variantes dialectales n'étaient pas précisées : corrigé le 14/08.
> L'éwé fait partie du continuum **gbe** ; les variantes écrites et parlées
> diffèrent (orthographe, tons, lexique).

| Composant | Variante / statut |
|---|---|
| **Bible éwé 1913** | Éwé écrit standardisé par la mission de Brême au Togoland allemand (traducteur autochtone : Ludwig Adzaklo), orthographe de 1913 — **révisée depuis** (Bible Society of Ghana, v. révisée 2006) |
| **Riebstein 1926** | Vocabulaire FR→ÉWÉ du Togo colonial — éwé togolais de l'époque (à confirmer : variante côtière ?) |
| **Segond 1910** | Français standard du début XXe |
| **Locuteur natif (vérification)** | Variante à préciser par Cherif (anlo, waci/watchi, côtière, autre ?) |
| **NLLB (cible modèle)** | Éwé standard moderne écrit (`ewe_Latn`) |

**Décision à acter** : la variante **cible** du projet = éwé standard togolais
contemporain (recommandé pour l'usage public) ; les sources historiques sont
conservées telles quelles, avec leur orthographe, et documentées comme
« éwé historique ».

**POLITIQUE DE VARIANTES (actée le 14/08 avec Cherif, locuteur éwé)** :

1. **Chaque source documente SA variante** (ex. Bible 1913 = éwé écrit
   historique de la mission de Brême ; Riebstein 1926 = éwé togolais de
   l'époque). À chaque intégration de source, sa variante est précisée.
2. **Le corpus hérite de la variante de ses sources** — pas de mélange
   silencieux.
3. **Variante du vérificateur** : Cherif parle l'éwé **côtier de Lomé**
   (utilisé pour la vérification humaine, sans en faire la norme du corpus).
4. **Cible long terme (non engagée)** : se rapprocher de l'éwé **parlé
   actuellement** (standard togolais moderne) — décision de spécialisation à
   prendre plus tard.
5. Le **kabiyè** est une langue distincte (famille gur), pas une variante de
   l'éwé — extension séparée du projet.

**Biais connu** : écart orthographique éwé 1913/1926 ↔ éwé moderne (tons,
digraphies) — à quantifier et à réduire par normalisation orthographique en
v1.x.

## Changements v0.1 → v0.2

1. **Calibrage sur l'échantillon de vérification** (100 paires vérifiées par
   Cherif, locuteur natif) : seuils de ratio resserrés
   (ok : 0,6 ≤ |ewe|/|fr| ≤ 1,8 au lieu de 0,5–2,5). Le locuteur a montré que
   les versets fusionnés par l'OCR (ratio médian 2,6) sont la principale
   source d'erreur.
2. **Nettoyage renforcé** : guillemets allemands, symboles résiduels,
   caractères non-latins, abréviations supplémentaires (Mem, RE…), fragments
   de notes (« > ,28. »).

## Qualité mesurée (échantillon de 100 paires, locuteur natif)

| Statut locuteur | v0.1 flag ok | v0.2 flag ok |
|---|---|---|
| ok | 45/70 (64 %) | 37/56 (66 %) |
| corriger | 14 | 11 |
| à rejeter | 11 | 8 |

**Interprétation** : ~2/3 des paires du noyau sont correctes. Les erreurs
restantes sont principalement des **fausses paires** (verset éwé aligné avec
le mauvais verset français — indétectable par la longueur seule) et des
résidus résiduels. Ce taux est **documenté honnêtement** : le corpus est un
outil d'entraînement (le modèle tolère ~30 % de bruit), mais **le test set
doit être vérifié par un locuteur avant toute publication de scores**.

## Recommandation (prochaine étape)

- **train/dev** : utilisables en l'état (bruit toléré par l'entraînement)
- **test** : à vérifier intégralement par le locuteur (~1 600 paires, ou un
  sous-ensemble de référence de 300 paires) avant de publier des scores —
  sinon les métriques sous-estiment la vraie qualité du modèle.

## 3-9. (inchangé par rapport à v0.1, voir `../v0.1/DATASHEET.md`)

- **Collecte** : Bible éwé 1913 (BFBS, domaine public) + Segond 1910 (domaine public)
- **Prétraitement** : pipeline `src/clean/` (normalisation cyrillique, extraction 66 livres, alignement DP)
- **Biais** : registre biblique uniquement, orthographe 1913, diacritiques partiels
- **Licence** : domaine public — publiable ; diffusion prévue HuggingFace (cheriftenga)
- **Maintenance** : Cherif (linguistique) + Sukuna (pipeline) ; seed 42
