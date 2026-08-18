# Datasheet - Corpus parallèle FR-éwé v0.3

- **Version** : 0.3 (exploratoire - vérifié par échantillons + référence
  humaine complète)
- **Date** : 2026-08-18 (publication publique)
- **Paires** : **65 640** (train 52 512 / dev 6 564 / test 6 564) +
  **test de référence vérifié : 241 paires** (split `reference`)
- **Colonnes** : `source` (bible | nllb), `fr`, `ewe` (+ `id` pour le
  split `reference`)

## Composants

| Composant | Paires | Provenance | Variante | Licence |
|---|---|---|---|---|
| Bible 1913 - Segond 1910 | 16 014 | archives (domaine public) | éwé historique (mission de Brême) | CC0-1.0 |
| NLLB filtré v3 | 49 626 | OPUS `NLLB.ee-fr` (allenai/nllb) | éwé moderne + textes minés | **ODC-By** (attribution) |
| Test de référence vérifié | 241 | échantillon du split test | double vérification humaine | CC0-1.0 |
| Lexique Riebstein v2 | 8 574 (composant séparé) | archive.org (domaine public) | éwé togolais 1926 | Domaine public |

## Qualité mesurée

| Composant | Échantillon vérifié | Qualité |
|---|---|---|
| Bible (v0.2) | 100 paires, locuteur natif | ~66 % |
| NLLB (v2-v3) | 100 paires, locuteur natif | 68 % (v2) - ~72 % estimé (v3) |
| Test de référence | 300 paires, **double vérification** | 241 validées (80,3 %) |

### Détail de la vérification du test de référence (18/08/2026)

- Protocole : 2 locuteurs natifs indépendants, verdicts par paire
  (ok / corriger / à rejeter), arbitrage final
- Concordance entre vérificateurs : 97 % (après normalisation)
- 238 paires ok/ok + 3 validées à l'arbitrage = **241 paires de référence**
- 59 paires exclues : mauvaise traduction (14), correspondance
  approximative (7), signes/chiffres parasites OCR (8), corriger (26),
  divers (4)
- Archive complète : `test-reference-verifs.csv` dans le repo GitHub
  (`data/processed/v0.3/`), rapport : `rapport-verification-reference.md`

## Biais connus

1. **Registre** : la composante Bible est biblique ; la composante NLLB est
   hétérogène (web miné, religieux, vie courante) avec ~28 % de bruit
   résiduel (alignements approximatifs).
2. **Orthographe** : éwé historique (1913/1926) vs éwé moderne (NLLB)
   mélangés - chaque paire garde la variante de sa source (politique de
   variantes : une source = sa variante documentée).
3. **Variantes régionales** : le vérificateur principal est locuteur de
   l'éwé côtier de Lomé ; la Bible 1913 documente la variante de la
   mission de Brême.
4. **Licence** : ODC-By impose l'attribution (dataset card) ; pas de
   redistribution des sources NLLB brutes non filtrées.

## Recommandations d'usage

- **Entraînement** : splits `train` / `dev` (bruit documenté, acceptable)
- **Évaluation / benchmark** : split `reference` uniquement (241 paires
  vérifiées à 100 %) - ne jamais évaluer sur une quelconque partie du
  `train`
- **JW300** : source connue mais volontairement NON incluse (licence
  restrictive) - entraînement uniquement, jamais publiée

## Historique des versions

| Version | Date | Contenu |
|---|---|---|
| v0.1 | 13/08/2026 | 16 050 paires "ok" (Bible + NLLB v1) |
| v0.2 | 14/08/2026 | Calibrage par échantillon vérifié (100 paires) |
| v0.3 | 15/08/2026 | + NLLB filtré v3 : 65 640 paires |
| v0.3-public | 18/08/2026 | + split `reference` (241 paires vérifiées) - publication publique |
