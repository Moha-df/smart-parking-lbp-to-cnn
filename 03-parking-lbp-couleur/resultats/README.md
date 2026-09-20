# Resultats

Contenu produit par `python compare_modes.py`, `python benchmark.py` et
`python figures.py`. Tout ce dossier est regenerable a l'identique.

## Fichiers de donnees

| Fichier | Contenu |
| ------- | ------- |
| `gray/`, `mosaic/` | `training.txt` et `test.txt` : 200 lignes de 256 valeurs LBP suivies du label (0 = libre, 1 = occupe). |
| `perchannel/` | Meme structure, mais 768 valeurs par ligne : les trois histogrammes concatenes. |
| `mosaique.png` | Export brut de la mosaique R \| G \| B d'une imagette, 450 x 150, produit par `--save-mosaic`. |
| `benchmark.csv` | Un taux de reconnaissance par mode et par tirage (`mode,tirage,taux`), soit 30 lignes pour 3 modes sur 10 tirages. |
| `execution.txt` | Sortie console complete des scripts, commande par commande. |

## Figures

| Figure | Ce qu'elle montre |
| ------ | ----------------- |
| `construction-mosaique.png` | La chaine complete : l'image couleur d'origine, ses trois plans R, G et B affiches comme trois images en niveaux de gris, puis la mosaique 450 x 150 obtenue en les juxtaposant. Les traits orange marquent les deux colonnes de jonction. Sur cet exemple le vehicule est bleu, ce qui rend les plans nettement differents : la carrosserie est sombre dans le plan rouge et claire dans le plan bleu. |
| `histogrammes-canaux.png` | Le descripteur LBP calcule separement sur chacun des trois plans de la meme image. Les trois courbes se superposent presque : meme quand les plans different en luminosite, leur texture locale est la meme, et c'est uniquement la texture que le LBP mesure. C'est l'explication du resultat ci-dessous. |
| `comparaison-modes.png` | Pour chaque mode, le taux moyen sur 10 tirages (point plein), les tirages individuels (points clairs) et leur etendue (trait). |

## Resultats

Taux de reconnaissance sur 10 tirages aleatoires independants :

| Mode | Descripteur | Moyenne | Ecart-type | Min | Max |
| ---- | ----------- | ------- | ---------- | --- | --- |
| `perchannel` | 768 valeurs | 97,30 % | 1,52 | 94,50 % | 99,50 % |
| `mosaic` | 256 valeurs | 97,25 % | 1,72 | 94,00 % | 100,00 % |
| `gray` | 256 valeurs | 97,20 % | 1,63 | 94,50 % | 99,50 % |

Ecart entre le meilleur et le pire mode : **0,10 point**. Variation d'un meme
mode d'un tirage a l'autre : **1,62 point** en moyenne. Le passage a la couleur
n'ameliore donc pas la reconnaissance sur ce jeu de donnees, alors qu'il
triple la taille du descripteur dans le cas `perchannel`.
