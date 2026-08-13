# Grilles de collecte ciblée

Chaque grille est un fichier CSV (séparateur `;`, UTF-8) de phrases françaises prêtes à traduire en éwé par 2 locuteurs natifs indépendants.

## Format

| Colonne | Rôle |
|---|---|
| `ID` | Identifiant unique (ex. PAL-SYM-001) |
| `Sous-thematique` | Sous-catégorie de la grille |
| `Phrase FR` | Phrase française source (à NE PAS modifier) |
| `Trad ewe L1` | Traduction du locuteur 1 |
| `Trad ewe L2` | Traduction du locuteur 2 |
| `Arbitrage` | Version finale si divergence (3e locuteur ou linguiste) |
| `Statut` | A traduire / Traduite / Arbitrée / Validée |

## Circuit de validation

1. Locuteur 1 traduit toutes les phrases (colonne L1)
2. Locuteur 2 traduit **indépendamment** (colonne L2) — sans voir L1
3. Comparaison : si divergence → arbitrage (3e locuteur ou linguiste)
4. Validation orthographique par un linguiste
5. Intégration au corpus (`data/processed/`) avec attribution et consentement

## Règles

- Phrases françaises verrouillées : ne pas reformuler (sauf erreur signalée)
- Traductions en éwé standard écrit (orthographe ɖ ɸ ɣ ɔ ɛ ŋ)
- Une phrase par ligne, pas de retours à la ligne dans les cellules

## Liste des grilles (ordre du plan)

1. `grille-01-paludisme.csv` — 125 phrases (symptômes, prévention, consultation, traitement, signes de gravité, campagnes, femmes enceintes/enfants)
2. `grille-02-vaccination.csv` — à venir
3. `grille-03-consultation-medicale.csv` — à venir
4. `grille-04-pharmacie.csv` — à venir
5. `grille-05-grossesse-nutrition.csv` — à venir
6. `grille-06-scolarisation.csv` — à venir
7. `grille-07-examens-scolaires.csv` — à venir
8. `grille-08-etat-civil.csv` — à venir
9. `grille-09-demarches-administratives.csv` — à venir
10. `grille-10-services-publics.csv` — à venir
