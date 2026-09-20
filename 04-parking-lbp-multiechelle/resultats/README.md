# Resultats

Contenu produit par `python compare_modes.py`, `python benchmark.py` et
`python figures.py`. Tout ce dossier est regenerable a l'identique.

## Fichiers de donnees

| Fichier | Contenu |
| ------- | ------- |
| `global/`, `grille2x2/` | `training.txt` et `test.txt` : une ligne par image, les valeurs du descripteur suivies du label (0 = libre, 1 = occupe), 100 emplacements libres puis 100 occupes. |
| `benchmark.csv` | Un taux de reconnaissance par mode et par tirage (`mode,tirage,taux`), soit 60 lignes pour 6 modes sur 10 tirages. |
| `execution.txt` | Sortie console complete des scripts, commande par commande. |

Les descripteurs des modes `grille3x3`, `grille4x4`, `pyramide`, `multirayon`
et de la variante `croise-camera-B` ne sont pas versionnes : ils representent
plus de 20 Mo pour une information deja resumee par `benchmark.csv` et
`execution.txt`. `python compare_modes.py` les reconstruit. Les deux modes
conserves suffisent a montrer le format des fichiers.

## Figures

| Figure | Ce qu'elle montre |
| ------ | ----------------- |
| `decoupage-blocs.png` | La chaine complete de l'approche spatiale : l'image decoupee en 3 x 3 blocs, l'histogramme LBP calcule sur chacun (H1 a H9), puis les neuf histogrammes mis bout a bout pour former un descripteur de 2 304 valeurs. Les histogrammes sont traces a la meme echelle : H8, qui couvre le capot clair et uniforme du vehicule, se distingue nettement des blocs de feuillage. |
| `rayons.png` | La carte des codes LBP et l'histogramme correspondant pour un voisinage circulaire de rayon 1, 2 et 3. En augmentant le rayon, les motifs cessent de decrire le grain de l'image pour decrire des structures plus larges, et l'histogramme se concentre sur moins de codes. |
| `comparaison-modes.png` | Pour chaque mode, le taux moyen sur 10 tirages (point plein), les tirages individuels (points clairs) et leur etendue (trait). Le descripteur global de reference est en orange. |
| `ecarts-apparies.png` | En haut, l'ecart de chaque mode au descripteur global, tirage par tirage : les modes etant evalues sur les memes tirages, cette difference elimine la difficulte propre a chaque tirage. En bas, le gain moyen du multi-echelle en fonction du taux obtenu par le descripteur global sur le meme tirage. |

## Resultats

Taux de reconnaissance sur 10 tirages aleatoires independants :

| Mode | Descripteur | Moyenne | Ecart-type | Min | Max |
| ---- | ----------- | ------- | ---------- | --- | --- |
| `grille4x4` | 4 096 valeurs | 98,05 % | 0,82 | 96,50 % | 99,00 % |
| `pyramide` | 5 376 valeurs | 98,05 % | 0,79 | 97,00 % | 100,00 % |
| `grille2x2` | 1 024 valeurs | 98,00 % | 0,89 | 96,50 % | 100,00 % |
| `grille3x3` | 2 304 valeurs | 97,75 % | 0,93 | 96,50 % | 99,00 % |
| `multirayon` | 768 valeurs | 97,55 % | 1,21 | 96,00 % | 100,00 % |
| `global` | 256 valeurs | 97,20 % | 1,29 | 95,00 % | 99,00 % |

Les six modes sont classes dans le meme ordre que leur ecart-type decroissant,
et toutes les variantes multi-echelle depassent le descripteur global. L'ecart
entre le meilleur et le pire mode est de 0,85 point, du meme ordre que la
variation d'un mode d'un tirage a l'autre (0,99 point) : pris isolement, ce
classement ne serait pas concluant.

La comparaison appariee leve l'ambiguite. Sur les memes tirages, le gain du
multi-echelle est correle a **-0,81** avec le taux du descripteur global : il
est nul ou legerement negatif sur les tirages faciles, et atteint +2,2 et +2,8
points sur les deux tirages ou le descripteur global tombe a 95,00 %.

Variante ou le jeu test provient de la camera B, beaucoup plus difficile :

| Mode | Taux |
| ---- | ---- |
| `grille4x4` | 67,50 % |
| `grille3x3` | 65,50 % |
| `pyramide` | 63,00 % |
| `grille2x2` | 62,50 % |
| `multirayon` | 62,00 % |
| `global` | 61,50 % |

L'ecart au descripteur global y atteint 6 points, ce qui confirme que l'apport
du multi-echelle croit avec la difficulte de la tache.
