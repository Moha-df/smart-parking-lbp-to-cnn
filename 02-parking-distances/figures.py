"""Genere les figures du dossier resultats/."""

import argparse
import csv
from collections import defaultdict

import numpy as np

from dataset import read_descriptors
from distances import METRICS
from figstyle import AXIS, INK_SECOND, MUTED, SERIES, clean, plt


def lire_benchmark(chemin):
    taux = defaultdict(list)
    with open(chemin, encoding="ascii") as f:
        for ligne in csv.DictReader(f):
            taux[ligne["metrique"]].append(float(ligne["taux"]))
    return taux


def figure_benchmark(chemin_csv, sortie):
    """Un point par metrique (moyenne) et un trait pour l'etendue des tirages.

    La forme est un dot plot et non un diagramme en barres : les taux sont tous
    proches de 100 %, des barres partant de zero seraient illisibles et un axe
    tronque serait trompeur.
    """
    taux = lire_benchmark(chemin_csv)
    ordre = sorted(taux, key=lambda nom: np.mean(taux[nom]))
    n_runs = len(next(iter(taux.values())))

    fig, ax = plt.subplots(figsize=(8.6, 0.45 * len(ordre) + 2.2))
    for y, nom in enumerate(ordre):
        v = np.array(taux[nom])
        ax.plot((v.min(), v.max()), (y, y), color=AXIS, linewidth=2,
                solid_capstyle="round", zorder=2)
        ax.scatter(v, np.full_like(v, y), s=14, color=SERIES[0], alpha=0.35,
                   linewidths=0, zorder=3)
        ax.scatter(v.mean(), y, s=90, color=SERIES[0], edgecolors="#fcfcfb",
                   linewidths=2, zorder=4)
        ax.annotate("%.2f %%" % v.mean(), (v.mean(), y), textcoords="offset points",
                    xytext=(0, 11), ha="center", color=SERIES[0],
                    fontsize=8.5, fontweight="bold", zorder=5)

    ax.set_yticks(range(len(ordre)), ordre)
    ax.set_xlabel("taux de reconnaissance (%)")
    ax.set_title("Aucune metrique ne se detache : les etendues se recouvrent toutes",
                 pad=26)
    ax.annotate("point plein = moyenne sur %d tirages   |   trait = min-max   |"
                "   points clairs = tirages individuels" % n_runs,
                (0, 1), xycoords="axes fraction", textcoords="offset points",
                xytext=(0, 6), color=INK_SECOND, fontsize=8)
    ax.set_ylim(-0.7, len(ordre) - 0.3)
    clean(ax, grid_axis="x")
    fig.tight_layout()
    fig.savefig(sortie)
    plt.close(fig)
    print("figure : %s" % sortie)


def figure_distances(training_path, test_path, sortie):
    """Distances d'une meme image test vers tout le training, selon la metrique.

    Chaque metrique est tracee sur son echelle normalisee [0, 1] : seule compte
    la position du minimum (ou du maximum), pas la valeur absolue.
    """
    train, train_labels = read_descriptors(training_path)
    test, _ = read_descriptors(test_path)
    vecteur = test[0]
    choisies = ("L1 (valeurs absolues)", "L2 au carre", "Bhattacharyya (OpenCV)")

    fig, axes = plt.subplots(len(choisies), 1, figsize=(9.0, 6.0), sharex=True)
    for ax, nom in zip(axes, choisies):
        fonction, sens = METRICS[nom]
        scores = np.asarray(fonction(train, vecteur), dtype=float)
        normalise = (scores - scores.min()) / (scores.max() - scores.min())
        if sens == "max":
            normalise = 1 - normalise
        meilleur = int(np.argmin(normalise))

        ax.plot(normalise, color=MUTED, linewidth=1)
        ax.scatter(meilleur, normalise[meilleur], s=70, color=SERIES[0],
                   edgecolors="#fcfcfb", linewidths=2, zorder=3)
        ax.annotate("plus proche voisin : ligne %d, classe %s"
                    % (meilleur, "libre" if train_labels[meilleur] == 0 else "occupe"),
                    (0.995, 0.86), xycoords="axes fraction", ha="right",
                    color=SERIES[0], fontsize=8.5, fontweight="bold")
        ax.axvline(100, color=AXIS, linewidth=1, linestyle=(0, (4, 3)))
        ax.set_ylabel("distance\nnormalisee")
        ax.set_title(nom)
        clean(ax)

    axes[0].annotate("lignes 0-99 : training libre", (2, 1.02), fontsize=8,
                     color=INK_SECOND)
    axes[0].annotate("lignes 100-199 : training occupe", (102, 1.02), fontsize=8,
                     color=INK_SECOND)
    axes[-1].set_xlabel("ligne du fichier training.txt")
    axes[-1].set_xlim(0, len(train) - 1)
    fig.suptitle("Une meme image test vue par trois metriques",
                 x=0.02, y=0.985, ha="left", fontsize=12, fontweight="bold")
    fig.text(0.02, 0.928, "Le voisin retenu differe d'une metrique a l'autre, "
             "mais sa classe reste la meme : c'est elle seule qui compte.",
             ha="left", fontsize=8.5, color=INK_SECOND)
    fig.tight_layout(rect=(0, 0, 1, 0.90))
    fig.savefig(sortie)
    plt.close(fig)
    print("figure : %s" % sortie)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", default="resultats")
    args = parser.parse_args()

    figure_benchmark("%s/benchmark.csv" % args.out_dir,
                     "%s/comparaison-metriques.png" % args.out_dir)
    figure_distances("%s/training.txt" % args.out_dir, "%s/test.txt" % args.out_dir,
                     "%s/profils-distances.png" % args.out_dir)


if __name__ == "__main__":
    main()
