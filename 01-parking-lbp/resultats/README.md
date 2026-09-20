# Resultats

Contenu produit par `python build_dataset.py`, `python classify.py` et
`python figures.py`. Tout ce dossier est regenerable a l'identique.

## Fichiers de donnees

| Fichier | Contenu |
| ------- | ------- |
| `training.txt` | 200 lignes : les 256 valeurs du descripteur LBP d'une imagette, puis son label (0 = libre, 1 = occupe). Les 100 premieres lignes sont des emplacements libres, les 100 suivantes des emplacements occupes. |
| `test.txt` | Meme format, sur 200 autres imagettes, disjointes du jeu training. |
| `croise-camera-B/` | Les memes fichiers pour la variante ou le jeu test provient de la camera B. |
| `execution.txt` | Sortie console complete des scripts, commande par commande. |

## Figures

| Figure | Ce qu'elle montre |
| ------ | ----------------- |
| `principe-lbp.png` | Les trois etapes du calcul, pour un emplacement libre et un emplacement occupe : l'image en niveaux de gris, la carte des codes LBP (un code par pixel), puis l'histogramme des 256 motifs qui constitue le descripteur. La difference entre les deux classes est visible des la carte des codes : le bitume nu produit de larges plages uniformes, le vehicule une texture dense. |
| `matrice-confusion.png` | Repartition des 200 decisions du classifieur. La diagonale compte les bonnes reponses ; les cases hors diagonale, les erreurs. Les 5 erreurs sont toutes des emplacements libres classes occupes ; aucun vehicule n'a ete manque. |
| `histogrammes-moyens.png` | En haut, le descripteur LBP moyen de chaque classe sur le jeu training. En bas, l'ecart entre les deux : les motifs dont la barre s'ecarte le plus de zero sont ceux sur lesquels le classifieur s'appuie. |

## Resultats

| Configuration | Taux de reconnaissance |
| ------------- | ---------------------- |
| Training et test sur la camera A (jeux disjoints) | **97,50 %** (195 / 200) |
| Training sur la camera A, test sur la camera B | 61,50 % (123 / 200) |

L'ecart entre les deux lignes mesure la limite de la methode : le descripteur
LBP caracterise la texture telle qu'elle apparait sous un point de vue donne. En
changeant de camera, l'angle de prise de vue, la distance et l'eclairage
changent, et le modele appris sur la premiere camera ne transfere pas.
