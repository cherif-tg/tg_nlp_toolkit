# Décision de licence — Louis Segond 1910 (français, domaine public)

- **Date** : 2026-08-13
- **Responsable** : Sukuna (vérifié), Cherif (validation)
- **Source** : dépôt GitHub `BibleCorps/FRA-B-LSG1910-PD-UBS`
  - URL : https://github.com/BibleCorps/FRA-B-LSG1910-PD-UBS
  - Format : p.sfm (USFM) — 66 livres, `\c` chapitres, `\v` versets, UTF-8
- **Type de contenu** : texte parallèle côté français (registre religieux, pour alignement avec la bible éwé 1913)
- **Licence déclarée** : **Domaine public**
  - Le texte de la Bible Louis Segond (révision 1910) est dans le domaine public : traduction initiale publiée en 1880, révision 1910, auteur décédé depuis plus de 70 ans.
  - Le nom du dépôt contient explicitement « PD » (Public Domain) et « UBS » ; le README précise : « Le texte de cette Bible est la reproduction du texte de la Bible Segond à parallèles en 1910 ».
  - Les notes de bas de page (`\x`) et références (`\r`) sont des ajouts éditoriaux du dépôt (Moon Sun Kim / E. Canales, DBL 2012) mais sont diffusées par ce dépôt sous marquage PD ; on ne conservera de toute façon que le texte des versets (`\v`), pas les notes.
- **Conditions de redistribution** : aucune connue (domaine public)
- **Décision** : **Publier** — alignement verset par verset avec la bible éwé 1913 (domaine public) pour créer un corpus parallèle publiable.
- **Justification** : les deux textes sont dans le domaine public → le corpus dérivé est publiable. C'est la base légale de la colonne vertébrale du corpus v0.1 (≈ 30 000 paires attendues).
- **Statut** : **Validé** (publiable)
- **Livrable technique associé** : `src/clean/parse_sfm.py` — 31 170 versets extraits (13/08/2026)
