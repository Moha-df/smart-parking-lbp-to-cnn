"""Genere les figures du dossier resultats/."""

import argparse
import csv
from collections import defaultdict

import numpy as np

from dataset import sample
from figstyle import AXIS, INK_SECOND, MUTED, SERIES, clean, plt
from lbp import lbp_codes
from multiscale import (RAYONS, TAILLE_DESCRIPTEUR, histogramme,
                        histogrammes_blocs, lbp_codes_circulaire, read_gray)


def lire_benchmark(chemin):
    taux = defaultdict(dict)
    with open(chemin, encoding="ascii") as f:
        for ligne in csv.DictReader(f):
            taux[ligne["mode"]][int(ligne["tirage"])] = float(ligne["taux"])
    return {mode: [v for _, v in sorted(tirages.items())]
            for mode, tirages in taux.items()}


def figure_decoupage(root, seed, grille, sortie):
    """L'image decoupee en blocs, un histogramme par bloc, puis la concatenation."""
    chemin, _ = sample(root, 1, seed)[1]
    gris = read_gray(chemin)
    codes = lbp_codes(gris)
    histos = histogrammes_blocs(gris, grille)
    plafond = max(h[1:].max() for h in histos)

    fig = plt.figure(figsize=(9.8, 6.4))
    structure = fig.add_gridspec(2, 2, height_ratios=(2.1, 1),
                                 width_ratios=(1, 1.5), hspace=0.42, wspace=0.18)

    ax = fig.add_subplot(structure[0, 0])
    ax.imshow(gris, cmap="gray", vmin=0, vmax=255)
    hauteur, largeur = gris.shape
    for k in range(1, grille):
        ax.axhline(k * hauteur / grille - 0.5, color=SERIES[1], linewidth=1.5)
        ax.axvline(k * largeur / grille - 0.5, color=SERIES[1], linewidth=1.5)
    for i in range(grille):
        for j in range(grille):
            ax.text((j + 0.5) * largeur / grille, (i + 0.5) * hauteur / grille,
                    "H%d" % (i * grille + j + 1), ha="center", va="center",
                    color=SERIES[1], fontsize=13, fontweight="bold")
    ax.set_title("1. L'image est decoupee en %d x %d blocs" % (grille, grille))
    ax.set_xticks([])
    ax.set_yticks([])
    ax.grid(False)

    cellules = structure[0, 1].subgridspec(grille, grille, hspace=0.35, wspace=0.12)
    for k, histo in enumerate(histos):
        sous = fig.add_subplot(cellules[k // grille, k % grille])
        sous.fill_between(np.arange(256), histo, color=SERIES[0], linewidth=0)
        sous.set_xlim(0, 255)
        sous.set_ylim(0, plafond)
        sous.set_xticks([])
        sous.set_yticks([])
        sous.grid(False)
        for cote in ("top", "right"):
            sous.spines[cote].set_visible(False)
        sous.set_title("H%d" % (k + 1), fontsize=8, pad=2)

    ax = fig.add_subplot(structure[1, :])
    concatene = np.concatenate(histos)
    ax.fill_between(np.arange(len(concatene)), concatene, color=SERIES[0],
                    linewidth=0)
    for k in range(1, len(histos)):
        ax.axvline(k * 256, color=AXIS, linewidth=1)
    for k in range(len(histos)):
        ax.annotate("H%d" % (k + 1), ((k + 0.5) * 256, plafond * 0.92),
                    ha="center", fontsize=8, color=INK_SECOND)
    ax.set_xlim(0, len(concatene))
    ax.set_ylim(0, plafond)
    ax.set_xlabel("position dans le descripteur")
    ax.set_ylabel("occurrences")
    ax.set_title("3. Les %d histogrammes mis bout a bout : le descripteur, "
                 "%d valeurs" % (len(histos), len(concatene)))
    clean(ax)

    fig.suptitle("L'approche multi-echelle spatiale : decouper, decrire, concatener",
                 x=0.02, y=0.99, ha="left", fontsize=12, fontweight="bold")
    fig.text(0.02, 0.935, "Le descripteur global perd la position des motifs ; "
             "en decrivant chaque bloc separement, elle est conservee.",
             ha="left", fontsize=8.5, color=INK_SECOND)
    fig.text(0.47, 0.862, "2. Un histogramme LBP de 256 valeurs par bloc",
             ha="left", fontsize=10, fontweight="bold")
    fig.subplots_adjust(top=0.84, bottom=0.09, left=0.07, right=0.97)
    fig.savefig(sortie)
    plt.close(fig)
    print("figure : %s" % sortie)


def figure_rayons(root, seed, sortie):
    """Effet du rayon du voisinage sur la carte des codes et l'histogramme."""
    chemin, _ = sample(root, 1, seed)[1]
    gris = read_gray(chemin)

    fig, axes = plt.subplots(2, len(RAYONS), figsize=(9.0, 5.0),
                             gridspec_kw={"height_ratios": (1.5, 1)})
    cartes = [lbp_codes_circulaire(gris, rayon) for rayon in RAYONS]
    plafond = max(histogramme(c)[1:].max() for c in cartes)

    for colonne, (rayon, carte) in enumerate(zip(RAYONS, cartes)):
        haut = axes[0, colonne]
        haut.imshow(carte, cmap="gray", vmin=0, vmax=255)
        haut.set_title("rayon R = %d" % rayon)
        haut.set_xticks([])
        haut.set_yticks([])
        haut.grid(False)

        bas = axes[1, colonne]
        bas.fill_between(np.arange(256), histogramme(carte), color=SERIES[0],
                         linewidth=0)
        bas.set_xlim(0, 255)
        bas.set_ylim(0, plafond)
        bas.set_xlabel("code du motif")
        if colonne == 0:
            bas.set_ylabel("occurrences")
        bas.margins(y=0.18)
    clean(bas)

    fig.suptitle("L'approche multi-echelle du voisinage : les 8 voisins sur un "
                 "cercle de rayon R", x=0.02, y=0.99, ha="left", fontsize=12,
                 fontweight="bold")
    fig.text(0.02, 0.935, "Plus le rayon augmente, plus les motifs decrivent des "
             "structures etendues et moins la micro-texture ressort.",
             ha="left", fontsize=8.5, color=INK_SECOND)
    fig.subplots_adjust(top=0.82, bottom=0.10, left=0.07, right=0.97, hspace=0.35)
    fig.savefig(sortie)
    plt.close(fig)
    print("figure : %s" % sortie)


def figure_benchmark(chemin_csv, sortie):
    """Dot plot des modes : moyenne et etendue sur les tirages."""
    taux = lire_benchmark(chemin_csv)
    ordre = sorted(taux, key=lambda mode: np.mean(taux[mode]))
    n_runs = len(next(iter(taux.values())))

    fig, ax = plt.subplots(figsize=(8.8, 3.8))
    for y, mode in enumerate(ordre):
        v = np.array(taux[mode])
        couleur = SERIES[1] if mode == "global" else SERIES[0]
        ax.plot((v.min(), v.max()), (y, y), color=AXIS, linewidth=2,
                solid_capstyle="round", zorder=2)
        ax.scatter(v, np.full_like(v, y), s=14, color=couleur, alpha=0.35,
                   linewidths=0, zorder=3)
        ax.scatter(v.mean(), y, s=90, color=couleur, edgecolors="#fcfcfb",
                   linewidths=2, zorder=4)
        ax.annotate("%.2f %%" % v.mean(), (v.mean(), y), textcoords="offset points",
                    xytext=(0, 11), ha="center", color=couleur,
                    fontsize=8.5, fontweight="bold", zorder=5)

    ax.set_yticks(range(len(ordre)),
                  ["%s\n%d val" % (m, TAILLE_DESCRIPTEUR[m]) for m in ordre])
    ax.set_xlabel("taux de reconnaissance (%)")
    ax.set_title("Toutes les variantes multi-echelle depassent le descripteur "
                 "global, et varient moins", pad=26)
    ax.annotate("point plein = moyenne sur %d tirages   |   trait = min-max   |"
                "   en orange, le descripteur global de reference" % n_runs,
                (0, 1), xycoords="axes fraction", textcoords="offset points",
                xytext=(0, 6), color=INK_SECOND, fontsize=8)
    ax.set_ylim(-0.7, len(ordre) - 0.3)
    clean(ax, grid_axis="x")
    fig.tight_layout()
    fig.savefig(sortie)
    plt.close(fig)
    print("figure : %s" % sortie)


def figure_ecarts(chemin_csv, sortie):
    """Comparaison appariee au mode global, tirage par tirage.

    Les modes etant evalues sur les memes tirages, la difference par tirage est
    plus informative que la comparaison des moyennes : elle elimine la
    difficulte propre a chaque tirage.
    """
    taux = lire_benchmark(chemin_csv)
    reference = np.array(taux["global"])
    modes = [m for m in taux if m != "global"]
    ordre = sorted(modes, key=lambda m: np.mean(np.array(taux[m]) - reference))

    fig, (haut, bas) = plt.subplots(2, 1, figsize=(8.8, 6.6),
                                    gridspec_kw={"height_ratios": (1.25, 1),
                                                 "hspace": 0.55})

    haut.axvline(0, color=SERIES[1], linewidth=1.5, zorder=1)
    for y, mode in enumerate(ordre):
        ecarts = np.array(taux[mode]) - reference
        vus = {}
        for ecart in ecarts:
            rang = vus.get(ecart, 0)
            vus[ecart] = rang + 1
            haut.scatter(ecart, 1.35 * y + 0.16 * rang, s=42, color=SERIES[0],
                         alpha=0.5, linewidths=0, zorder=3)
        haut.scatter(ecarts.mean(), 1.35 * y, s=100, color=SERIES[0],
                     edgecolors="#fcfcfb", linewidths=2, zorder=4)
        haut.annotate("%+.2f" % ecarts.mean(), (ecarts.mean(), 1.35 * y),
                      textcoords="offset points", xytext=(0, -16), ha="center",
                      color=SERIES[0], fontsize=8.5, fontweight="bold", zorder=5)

    haut.set_yticks([1.35 * y for y in range(len(ordre))], ordre)
    haut.set_xlabel("ecart au descripteur global, en points")
    haut.set_title("Le multi-echelle perd rarement, et gagne surtout sur "
                   "quelques tirages", pad=26)
    haut.annotate("un point par tirage, empiles quand ils sont a egalite   |   "
                  "point plein = moyenne   |   trait orange = descripteur global",
                  (0, 1), xycoords="axes fraction", textcoords="offset points",
                  xytext=(0, 6), color=INK_SECOND, fontsize=8)
    haut.set_ylim(-0.75, 1.35 * (len(ordre) - 1) + 0.75)
    clean(haut, grid_axis="x")

    gains = np.array([np.mean([taux[m][t] - reference[t] for m in modes])
                      for t in range(len(reference))])
    correlation = np.corrcoef(reference, gains)[0, 1]

    bas.axhline(0, color=SERIES[1], linewidth=1.5, zorder=1)
    bas.scatter(reference, gains, s=70, color=SERIES[0], alpha=0.7,
                linewidths=0, zorder=3)
    pente, origine = np.polyfit(reference, gains, 1)
    abscisses = np.array((reference.min(), reference.max()))
    bas.plot(abscisses, pente * abscisses + origine, color=MUTED, linewidth=1.5,
             linestyle=(0, (5, 3)), zorder=2)
    for t, (x, y) in enumerate(zip(reference, gains)):
        bas.annotate("t%d" % t, (x, y), textcoords="offset points",
                     xytext=(7, -3), fontsize=7.5, color=INK_SECOND)

    bas.set_xlabel("taux du descripteur global sur le tirage (%)")
    bas.set_ylabel("gain moyen\ndes modes multi-echelle")
    bas.set_title("Plus le tirage est difficile pour le descripteur global, "
                  "plus le multi-echelle aide", pad=26)
    bas.annotate("correlation : %.2f" % correlation, (0, 1),
                 xycoords="axes fraction", textcoords="offset points",
                 xytext=(0, 6), color=INK_SECOND, fontsize=8)
    bas.margins(y=0.18)
    clean(bas)

    fig.tight_layout()
    fig.savefig(sortie)
    plt.close(fig)
    print("figure : %s" % sortie)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train-root", default="../A")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--grille", type=int, default=3)
    parser.add_argument("--out-dir", default="resultats")
    args = parser.parse_args()

    figure_decoupage(args.train_root, args.seed, args.grille,
                     "%s/decoupage-blocs.png" % args.out_dir)
    figure_rayons(args.train_root, args.seed, "%s/rayons.png" % args.out_dir)
    figure_benchmark("%s/benchmark.csv" % args.out_dir,
                     "%s/comparaison-modes.png" % args.out_dir)
    figure_ecarts("%s/benchmark.csv" % args.out_dir,
                  "%s/ecarts-apparies.png" % args.out_dir)


if __name__ == "__main__":
    main()
