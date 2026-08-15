# Décision de licence — Ressources historiques (archive.org, Lexilogos)

- **Date** : 2026-08-13
- **Responsable** : Cherif (découverte) + Sukuna (vérification badges via API archive.org + lecture de pages)
- **URL vérifiées** :
  - Bible éwé 1913 : <https://archive.org/details/biblia-alo-nonlo-kokoe-la-le-ewegbe-me-1913>
  - Vocabulaire Riebstein 1926 : <https://archive.org/details/vocabulairedelal02rieb>
  - Portail Lexilogos : <https://www.lexilogos.com/ewe_dictionnaire.htm>

## Résultats vérifiés

### 1. Bible éwé 1913 — DOMAINE PUBLIC (publiable)

- Titre : « Biblia alo Nɔnɔlɔ kɔkɔe la le Eʋegbe me 1913 » (autre titre : « Nubabla Yeye la ƒe Agbalẽ, le Eʋegbe me »)
- Éditeur : British and Foreign Bible Society (British kple Duta-Bibliahabɔbɔ), Londres, 1913
- **Badge affiché : « Usage: Public Domain Mark 1.0 »** (confirmé par l'API métadonnées : licenseurl = creativecommons.org/publicdomain/mark/1.0)
- Langue : éwé ; full text + EPUB + PDF téléchargeables
- **Décision : PUBLIER.** C'est la traduction originale de 1913 (antérieure à la révision 2006 sous copyright).
- **Stratégie parallèle** : texte monolingue éwé → alignement **verset par verset** avec une bible française domaine public (ex. Louis Segond, 1910) → corpus parallèle FR↔EWE légitime et publiable.
- **Caveat** : OCR de mauvaise qualité probable (détection de langue « sw » à tort) → évaluer la qualité du full text en P1 avant intégration.

### 2. Vocabulaire de la langue éwé (Riebstein, 1926) — domaine public probable (publiable)

- Titre : « Vocabulaire de la langue éwé : éwé-français » — Émile Riebstein, Rome : Sodalité de St. Pierre Claver, 1926
- **Volume 2 seul disponible** (partie français-éwé, 410 p.) ; le volume 1 (éwé-français) est manquant
- Publication 1926 → **domaine public aux USA** (avant 1930) ; auteur décédé depuis longtemps → domaine public probable au Togo aussi
- Pas de badge « Usage » visible dans l'extraction de la page (contrairement à la bible) → **confirmer visuellement le badge** ; archive.org propose néanmoins le téléchargement libre du full text et du PDF
- **Décision : PUBLIER** (entrées de dictionnaire = paires mot/phrase FR↔EWE ; référence orthographique de premier ordre pour la normalisation ɖ ɸ ɣ ɔ ɛ ŋ)

### 3. Lexilogos — portail (référence, pas une source de données)

- Confirme la bibliographie éwé : Westermann 1905 (éwé-allemand), Riebstein 1926 (éwé-français), Henrici 1891, grammaires Westermann 1907, etc.
- Fournit un **clavier éwé** (caractères spéciaux) et la **DUDH en éwé** — utiles pour le pipeline de nettoyage et les tests
- **Décision : référence bibliographique uniquement**

### 4. Dictionnaire éwé-allemand (Westermann, 1905) — domaine public (1905)

- À localiser sous forme numérisée (archive.org ou bibliothèques numériques) → publiable si trouvé

## Décision globale

La bible 1913 (domaine public confirmé) et le vocabulaire Riebstein 1926 (domaine public probable) deviennent des **sources publiables** — la bible 1913 est même la clé pour construire un **corpus parallèle FR↔EWE** par alignement verset à verset avec une bible française domaine public.

**Statut** : Validé pour la bible 1913 ; confirmation visuelle du badge à faire pour Riebstein 1926 ; Westermann 1905 à localiser.
