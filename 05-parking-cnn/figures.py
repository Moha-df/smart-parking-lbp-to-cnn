"""Genere les figures du dossier resultats/ : synthese des tirages et
comparaison au meilleur descripteur LBP (TP 01-04), tirage par tirage.
"""

import argparse
import csv
from collections import defaultdict

import numpy as np

from figstyle import AXIS, INK_SECOND, SERIES, clean, plt


def lire_benchmark(chemin):
    taux = defaultdict(dict)
    with open(chemin, encoding="ascii") as f:
        for ligne in csv.DictReader(f):
            taux[ligne["mode"]][int(ligne["tirage"])] = float(ligne["taux"])
    return {mode: [v for _, v in sorted(tirages.items())]
            for mode, tirages in taux.items()}


def figure_benchmark(taux, sortie, titre, reference=None, couleurs=None):
    """Dot plot generique : moyenne et etendue de chaque serie sur les tirages."""
    ordre = sorted(taux, key=lambda mode: np.mean(taux[mode]))
    n_runs = len(next(iter(taux.values())))
    couleurs = couleurs or {}

    fig, ax = plt.subplots(figsize=(8.8, 0.85 * len(ordre) + 1.6))
    for y, mode in enumerate(ordre):
        v = np.array(taux[mode])
        couleur = couleurs.get(mode, SERIES[1] if mode == reference else SERIES[0])
        ax.plot((v.min(), v.max()), (y, y), color=AXIS, linewidth=2,
                solid_capstyle="round", zorder=2)
        ax.scatter(v, np.full_like(v, y), s=14, color=couleur, alpha=0.35,
                   linewidths=0, zorder=3)
        ax.scatter(v.mean(), y, s=90, color=couleur, edgecolors="#fcfcfb",
                   linewidths=2, zorder=4)
        ax.annotate("%.2f %%" % v.mean(), (v.mean(), y), textcoords="offset points",
                    xytext=(0, 11), ha="center", color=couleur,
                    fontsize=8.5, fontweight="bold", zorder=5)

    ax.set_yticks(range(len(ordre)), ordre)
    ax.set_xlabel("taux de reconnaissance (%)")
    ax.set_title(titre, pad=26)
    ax.annotate("point plein = moyenne sur %d tirages   |   trait = min-max" % n_runs,
                (0, 1), xycoords="axes fraction", textcoords="offset points",
                xytext=(0, 6), color=INK_SECOND, fontsize=8)
    ax.set_ylim(-0.7, len(ordre) - 0.3)
    clean(ax, grid_axis="x")
    fig.tight_layout()
    fig.savefig(sortie)
    plt.close(fig)
    print("figure : %s" % sortie)


def figure_ecarts_cnn(taux_cnn, taux_reference, nom_reference, sortie):
    """Comparaison appariee : les tirages etant identiques (meme graine), la
    difference tirage par tirage isole l'effet de la methode.
    """
    cnn = np.array(taux_cnn)
    reference = np.array(taux_reference)
    ecarts = cnn - reference

    fig, ax = plt.subplots(figsize=(8.8, 3.4))
    ax.axhline(0, color=SERIES[1], linewidth=1.5, zorder=1)
    ax.bar(np.arange(len(ecarts)), ecarts, color=SERIES[0], alpha=0.75, zorder=3,
          width=0.6)
    ax.axhline(ecarts.mean(), color=SERIES[0], linewidth=1.5,
              linestyle=(0, (5, 3)), zorder=2)
    ax.annotate("moyenne %+.2f point" % ecarts.mean(), (len(ecarts) - 0.5, ecarts.mean()),
               textcoords="offset points", xytext=(4, 4), color=SERIES[0],
               fontsize=8.5, fontweight="bold")

    ax.set_xticks(np.arange(len(ecarts)), ["t%d" % t for t in range(len(ecarts))])
    ax.set_xlabel("tirage (meme graine que le CNN et que %s)" % nom_reference)
    ax.set_ylabel("ecart CNN - %s\n(points)" % nom_reference)
    ax.set_title("Le CNN gagne-t-il ou perd-il, tirage par tirage, face a %s ?"
                 % nom_reference, pad=26)
    clean(ax, grid_axis="y")
    fig.tight_layout()
    fig.savefig(sortie)
    plt.close(fig)
    print("figure : %s" % sortie)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cnn-csv", default="resultats/benchmark.csv")
    parser.add_argument("--lbp-csv",
                        default="../04-parking-lbp-multiechelle/resultats/benchmark.csv")
    parser.add_argument("--lbp-reference", default="global",
                        help="mode du CSV LBP servant de reference (descripteur global)")
    parser.add_argument("--lbp-meilleur", default="pyramide",
                        help="mode du CSV LBP le plus performant du TP 4")
    parser.add_argument("--out-dir", default="resultats")
    args = parser.parse_args()

    taux_cnn = lire_benchmark(args.cnn_csv)
    taux_lbp = lire_benchmark(args.lbp_csv)

    figure_benchmark({"cnn": taux_cnn["cnn"]}, "%s/benchmark-cnn.png" % args.out_dir,
                     "Taux de reconnaissance du CNN sur les tirages independants",
                     couleurs={"cnn": SERIES[0]})

    combine = {
        "cnn": taux_cnn["cnn"],
        "lbp %s" % args.lbp_reference: taux_lbp[args.lbp_reference],
        "lbp %s" % args.lbp_meilleur: taux_lbp[args.lbp_meilleur],
    }
    couleurs = {
        "cnn": SERIES[0],
        "lbp %s" % args.lbp_reference: SERIES[1],
        "lbp %s" % args.lbp_meilleur: SERIES[2],
    }
    figure_benchmark(combine, "%s/comparaison-cnn-lbp.png" % args.out_dir,
                     "CNN face au descripteur LBP (TP 01-04), memes tirages",
                     couleurs=couleurs)

    figure_ecarts_cnn(taux_cnn["cnn"], taux_lbp[args.lbp_reference],
                      "LBP %s" % args.lbp_reference,
                      "%s/ecarts-cnn-vs-lbp.png" % args.out_dir)


if __name__ == "__main__":
    main()
