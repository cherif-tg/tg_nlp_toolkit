# Décision de licence — OPUS / NLLB fr-ee (corpus éwé)

- **Date** : 2026-08-14 (mise à jour de la décision du 13/08)
- **Responsable** : Cherif + Sukuna
- **URL de la source** : <https://opus.nlpl.eu/NLLB-v1.php> — paquet `NLLB.ee-fr` (format Moses)
- **Vérification API** : `opusapi/?source=fr&target=ee&corpus=JW300` → **vide** (JW300 fr-ee n'existe pas) ; `source=fr&target=ee` → NLLB v1 présent

## Constat du 14/08

| Élément | Valeur |
|---|---|
| Corpus | **NLLB.ee-fr v1** (source : allenai/nllb) |
| Volume | **1 039 385 paires** (~47 Mo éwé + ~56 Mo français) |
| Licence | **ODC-By** (Open Data Commons Attribution) |
| Domaine | Non biblique en majorité : textes minés sur le web (CCMatrix), FLORES, sources religieuses multiples, vie courante |
| Qualité | Corpus **miné** : bonnes paires + bruit (fausses paires, autres langues en éwé : hindi, yoruba…) → **filtrage obligatoire** (scores LASER + ratio + dédoublonnage + échantillon de vérification humaine) |
| Chevauchement | Contient des paires bibliques déjà présentes dans notre corpus (à dédupliquer) |

## Décision

- **Licence ODC-By = licence de données OUVERTE** (attribution requise, usage commercial autorisé) → le sous-ensemble **filtré** est **publiable** (contrairement à JW300).
- **Intégration** : entraînement **et** publication (avec attribution ODC-By + citation NLLB/OPUS).
- **Conditions d'intégration** :
  1. Filtrage automatique (scores de similarité, ratio de longueur, dédoublonnage interne et vs corpus biblique)
  2. **Échantillon de vérification par le locuteur natif** avant publication (comme pour la Bible)
  3. Attribution ODC-By dans la dataset card HuggingFace
- **Statut** : **source validée — pipeline de filtrage à construire (étape en cours)**

## Contexte

La décision du 13/08 prévoyait : « si OPUS vide → collecte ciblée = source unique ». **Ce scénario est invalidé** : OPUS contient une source massive pour le FR↔EWE. La collecte ciblée reste le plan B pour la qualité, mais la diversification (piste 1) a désormais une **source automatique majeure**.
