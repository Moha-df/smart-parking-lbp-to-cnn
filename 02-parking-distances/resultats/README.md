# Resultats

Contenu produit par `python build_dataset.py`, `python compare.py`,
`python benchmark.py` et `python figures.py`. Tout ce dossier est regenerable a
l'identique.

## Fichiers de donnees

| Fichier | Contenu |
| ------- | ------- |
| `training.txt` | 200 lignes : les 256 valeurs du descripteur LBP d'une imagette, puis son label (0 = libre, 1 = occupe). |
| `test.txt` | Meme format, sur 200 autres imagettes, disjointes du jeu training. |
| `benchmark.csv` | Un taux de reconnaissance par metrique et par tirage (`metrique,tirage,taux`), soit 70 lignes pour 7 metriques sur 10 tirages. |
| `execution.txt` | Sortie console complete des scripts, commande par commande. |

## Figures

| Figure | Ce qu'elle montre |
| ------ | ----------------- |
| `comparaison-metriques.png` | Pour chaque metrique, le taux moyen sur 10 tirages (point plein), les 10 tirages individuels (points clairs) et leur etendue (trait). Les etendues se recouvrent toutes : l'ecart entre metriques est plus petit que la variation d'une metrique d'un tirage a l'autre. |
| `profils-distances.png` | Pour une meme image test, la distance vers chacune des 200 lignes du training, normalisee sur [0, 1] pour rendre les trois metriques comparables. Le decrochage visible a la ligne 100 correspond au passage des emplacements libres aux emplacements occupes dans le training. Le point bleu marque le voisin retenu : il change d'une metrique a l'autre, mais reste dans la meme moitie du fichier, donc la classe predite est la meme. |

## Resultats

Taux de reconnaissance sur 10 tirages aleatoires independants :

| Metrique | Moyenne | Ecart-type | Min | Max |
| -------- | ------- | ---------- | --- | --- |
| Intersection (OpenCV) | 97,25 % | 1,59 | 94,50 % | 99,50 % |
| L1 (valeurs absolues) | 97,20 % | 1,63 | 94,50 % | 99,50 % |
| Bhattacharyya (OpenCV) | 97,20 % | 1,68 | 94,50 % | 99,50 % |
| Chi-2 (OpenCV) | 97,10 % | 1,93 | 93,50 % | 99,50 % |
| Correlation (OpenCV) | 96,75 % | 1,50 | 93,50 % | 99,00 % |
| L2 (euclidienne) | 96,60 % | 1,11 | 94,00 % | 98,50 % |
| L2 au carre | 96,60 % | 1,11 | 94,00 % | 98,50 % |

Ecart entre la meilleure et la pire metrique : **0,65 point**. Variation d'une
meme metrique d'un tirage a l'autre : **1,51 point** en moyenne. La seconde
valeur etant plus du double de la premiere, le classement ci-dessus n'est pas
interpretable comme une hierarchie entre metriques.

Les deux variantes L2 sont rigoureusement identiques : la racine carree ne
changeant pas l'ordre des distances, elle ne change pas le voisin retenu.
