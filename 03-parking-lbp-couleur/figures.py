"""Genere les figures du dossier resultats/."""

import argparse
import csv
from collections import defaultdict

import cv2
import numpy as np

from color import mosaic, planes_rgb, read_color
from dataset import sample
from figstyle import AXIS, INK_SECOND, SERIES, clean, plt
from lbp import lbp_histogram

CANAUX = ("R (rouge)", "G (vert)", "B (bleu)")


def figure_construction(root, seed, sortie):
    """Image couleur -> 3 plans en niveaux de gris -> mosaique de largeur 3W."""
    chemin, _ = sample(root, 1, seed)[1]
    bgr = read_color(chemin)
    plans = planes_rgb(bgr)
    grande = mosaic(bgr)
    largeur = plans[0].shape[1]

    fig = plt.figure(figsize=(9.5, 5.0))
    grille = fig.add_gridspec(2, 4, height_ratios=(1, 0.9), hspace=0.32, wspace=0.12)

    def nu(ax):
        ax.set_xticks([])
        ax.set_yticks([])
        ax.grid(False)
        return ax

    ax = nu(fig.add_subplot(grille[0, 0]))
    ax.imshow(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))
    ax.set_title("1. Image couleur\nCV_8UC3, %d x %d, 3 canaux" % bgr.shape[:2],
                 fontsize=9)

    for i, (plan, nom) in enumerate(zip(plans, CANAUX)):
        ax = nu(fig.add_subplot(grille[0, i + 1]))
        ax.imshow(plan, cmap="gray", vmin=0, vmax=255)
        titre = "2. Separation des plans\n%s" % nom if i == 0 else "\n%s" % nom
        ax.set_title(titre, fontsize=9)

    ax = nu(fig.add_subplot(grille[1, :]))
    ax.imshow(grande, cmap="gray", vmin=0, vmax=255)
    ax.set_title("3. Mosaique R | G | B : une seule image %d x %d sur un canal, "
                 "sur laquelle le LBP est calcule"
                 % (grande.shape[1], grande.shape[0]), fontsize=9)
    for x in (largeur, 2 * largeur):
        ax.axvline(x - 0.5, color=SERIES[1], linewidth=1.5)

    fig.suptitle("Comment une image couleur devient une image exploitable par le LBP",
                 x=0.02, y=0.99, ha="left", fontsize=12, fontweight="bold")
    fig.text(0.02, 0.93, "Les traits orange marquent les deux colonnes de jonction, "
             "seuls endroits ou le LBP compare des pixels de canaux differents.",
             ha="left", fontsize=8.5, color=INK_SECOND)
    fig.subplots_adjust(top=0.80, bottom=0.03, left=0.03, right=0.97)
    fig.savefig(sortie)
    plt.close(fig)
    print("figure : %s" % sortie)


def figure_histogrammes_canaux(root, seed, sortie):
    """Descripteur LBP de chaque plan : ce que la couleur ajoute, ou pas."""
    chemin, _ = sample(root, 1, seed)[1]
    plans = planes_rgb(read_color(chemin))
    histogrammes = [lbp_histogram(plan) for plan in plans]

    fig, ax = plt.subplots(figsize=(9.5, 3.8))
    for histogramme, nom, couleur in zip(histogrammes, CANAUX, SERIES):
        ax.plot(histogramme, color=couleur, linewidth=1.6, label=nom)

    ax.set_xlim(0, 255)
    ax.set_ylim(0, 1.05 * max(h[1:].max() for h in histogrammes))
    ax.set_xlabel("code du motif LBP")
    ax.set_ylabel("occurrences")
    ax.set_title("Descripteur LBP de chacun des trois plans (meme image)", pad=24)
    ax.annotate("les trois profils se superposent presque : sur cette scene, "
                "les trois canaux portent la meme texture",
                (0, 1), xycoords="axes fraction", textcoords="offset points",
                xytext=(0, 6), color=INK_SECOND, fontsize=8)
    ax.legend(loc="upper right", ncol=3)
    clean(ax)
    fig.tight_layout()
    fig.savefig(sortie)
    plt.close(fig)
    print("figure : %s" % sortie)


def figure_benchmark(chemin_csv, sortie):
    """Dot plot des trois modes : moyenne et etendue sur les tirages."""
    taux = defaultdict(list)
    with open(chemin_csv, encoding="ascii") as f:
        for ligne in csv.DictReader(f):
            taux[ligne["mode"]].append(float(ligne["taux"]))
    ordre = sorted(taux, key=lambda mode: np.mean(taux[mode]))
    n_runs = len(next(iter(taux.values())))
    moyennes = [np.mean(taux[mode]) for mode in ordre]

    fig, ax = plt.subplots(figsize=(8.6, 3.2))
    for y, mode in enumerate(ordre):
        v = np.array(taux[mode])
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
    ax.set_title("La couleur n'apporte rien ici : %.2f point separe les trois modes"
                 % (max(moyennes) - min(moyennes)), pad=26)
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train-root", default="../A")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--out-dir", default="resultats")
    args = parser.parse_args()

    figure_construction(args.train_root, args.seed,
                        "%s/construction-mosaique.png" % args.out_dir)
    figure_histogrammes_canaux(args.train_root, args.seed,
                               "%s/histogrammes-canaux.png" % args.out_dir)
    figure_benchmark("%s/benchmark.csv" % args.out_dir,
                     "%s/comparaison-modes.png" % args.out_dir)


if __name__ == "__main__":
    main()
