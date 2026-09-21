# Resultats

Contenu produit par `parking_cnn.ipynb` (execute de bout en bout), ou par
`python benchmark.py && python figures.py`. Tout ce dossier est regenerable
a l'identique : les graines de tirage sont fixees, et identiques a celles du
benchmark LBP multi-echelle (`04-parking-lbp-multiechelle/resultats/benchmark.csv`).

## Fichiers

| Fichier | Contenu |
| ------- | ------- |
| `benchmark.csv` | Taux de reconnaissance du CNN par tirage (`mode,tirage,taux`), 10 lignes : 95,50 % a 99,50 %, moyenne 97,65 %. |
| `courbes-demo.png` | Courbes accuracy/loss (entrainement et validation) du tirage de demonstration (graine 0). |
| `matrice-confusion-demo.png` | Matrice de confusion du meme tirage : 99,00 % (198 / 200). |
| `benchmark-cnn.png` | Synthese des 10 tirages : moyenne, min, max. |
| `comparaison-cnn-lbp.png` | CNN (97,65 %) face au LBP global (97,20 %, TP 01) et au meilleur mode multi-echelle (pyramide, 98,05 %, TP 04), memes tirages. |
| `ecarts-cnn-vs-lbp.png` | Ecart CNN - LBP global, tirage par tirage (comparaison appariee) : moyenne +0,45 point, de -2,00 a +4,00 selon le tirage. |
| `conclusion.txt` | Synthese chiffree generee automatiquement par le notebook. |

Execute sur CPU (pas de GPU disponible nativement sous Windows avec
TensorFlow >= 2.11) : quelques secondes par tirage, arret anticipe
generalement avant la 20e epoque sur 30 au maximum.
