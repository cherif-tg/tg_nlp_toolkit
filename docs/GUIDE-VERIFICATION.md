# Guide de vérification — Test de référence (300 paires)

## Objectif

Ce jeu de **300 paires** (150 Bible + 150 NLLB) est la
**référence officielle d'évaluation** du projet : il doit être vérifié à
**100 %** par **au moins 2 locuteurs natifs indépendants** (double
validation). Les paires rejetées seront exclues ; seules les paires validées
par les deux vérificateurs resteront dans la référence finale.

## Consignes

Pour chaque ligne du fichier `test-reference-300.csv` :

1. Lis la phrase **française** (colonne `fr`).
2. Lis la traduction **éwé** (colonne `ewe`).
3. Évalue la qualité de la correspondance :
   - **ok** : traduction correcte, sens fidèle (les petites différences de
     formulation sont acceptables si le sens est bon)
   - **corriger** : la traduction est éwé correct mais la correspondance est
     approximative / il y a des résidus / une partie manque
   - **à-rejeter** : la traduction est fausse, incomplète, dans une autre
     langue, ou ne correspond pas du tout

4. Écris ta décision dans TA colonne (`verif1` pour le 1er locuteur,
   `verif2` pour le 2e). N'écris jamais dans la colonne de l'autre.
5. Optionnel : mets une note dans `commentaire` (ex. « manque la fin »,
   « orthographe ancienne mais correct »).

## Exemples de cas

| Cas | Décision |
|---|---|
| « Le médicament doit être pris matin et soir » → `Atike la wòle be woano ŋdi kple fiẽ` | ok |
| « Je vais à l'école » → traduction correcte mais parle d'autre chose | à-rejeter |
| Éwé correct mais phrase française tronquée | corriger |
| Texte en anglais ou autre langue | à-rejeter |

## Rappel (politique de variantes)

- La composante **Bible** est en éwé historique (1913) : l'orthographe peut
  différer de l'éwé moderne — jugez le SENS, pas l'orthographe.
- La composante **NLLB** est en éwé moderne (parfois approximatif).

## Après la vérification

Renvoyez le fichier rempli au coordinateur (Cherif). Les deux colonnes seront
croisées : désaccords → arbitrage ; consensus ok → référence finale.
