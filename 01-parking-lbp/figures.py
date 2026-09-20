"""Genere les figures du dossier resultats/."""

import argparse

import cv2
import numpy as np

from classify import classify
from dataset import read_descriptors, sample
from figstyle import INK_SECOND, SERIES, SEQUENTIAL, clean, plt
from lbp import lbp_codes, lbp_histogram

NOMS = ("emplacement libre", "emplacement occupe")


def figure_principe(root, seed, sortie):
    """Image -> carte des codes LBP -> histogramme, pour un exemple de chaque classe."""
    exemples = sample(root, 1, seed)
    fig, axes = plt.subplots(2, 3, figsize=(9.5, 5.2))

    for ligne, (chemin, label) in enumerate(exemples):
        gris = cv2.imread(str(chemin), cv2.IMREAD_GRAYSCALE)
        codes = lbp_codes(gris)
        histogramme = lbp_histogram(gris)

        axes[ligne, 0].imshow(gris, cmap="gray", vmin=0, vmax=255)
        axes[ligne, 0].set_title("1. Image en niveaux de gris\n%s" % NOMS[label])

        axes[ligne, 1].imshow(codes, cmap="gray", vmin=0, vmax=255)
        axes[ligne, 1].set_title("2. Carte des codes LBP\nun code [0-255] par pixel")

        for ax in axes[ligne, :2]:
            ax.set_xticks([])
            ax.set_yticks([])
            ax.grid(False)

        ax = axes[ligne, 2]
        ax.fill_between(np.arange(256), histogramme, color=SERIES[label], linewidth=0)
        ax.set_title("3. Descripteur LBP\n256 valeurs = le vecteur compare")
        ax.set_xlim(0, 255)
        ax.set_xlabel("code du motif")
        ax.set_ylabel("occurrences")
        clean(ax)

    fig.suptitle("Du pixel au descripteur : les trois etapes du LBP",
                 x=0.02, ha="left", fontsize=12, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(sortie)
    plt.close(fig)
    print("figure : %s" % sortie)


def figure_histogrammes_moyens(training_path, sortie):
    """Profil LBP moyen de chaque classe, et ecart entre les deux."""
    descripteurs, labels = read_descriptors(training_path)
    moyennes = [descripteurs[labels == label].mean(axis=0) for label in (0, 1)]
    ecart = moyennes[1] - moyennes[0]
    codes = np.arange(256)

    fig, (haut, bas) = plt.subplots(2, 1, figsize=(9.5, 5.6), sharex=True,
                                    gridspec_kw={"height_ratios": (2, 1.4)})

    for label in (0, 1):
        haut.plot(codes, moyennes[label], color=SERIES[label],
                  linewidth=2, label=NOMS[label])
    haut.set_ylim(0, 1.05 * max(m[1:].max() for m in moyennes))
    haut.set_ylabel("occurrences moyennes")
    haut.set_title("Descripteur LBP moyen des deux classes (jeu training)")
    haut.legend(loc="upper right", ncol=2)
    note = ("le code 0 (zones uniformes) sort du cadre : %d pour libre, %d pour occupe"
            % (moyennes[0][0], moyennes[1][0]))
    haut.annotate(note, (0, haut.get_ylim()[1]), textcoords="offset points",
                  xytext=(8, -14), color=INK_SECOND, fontsize=8)
    clean(haut)

    bas.axhline(0, color="#c3c2b7", linewidth=1)
    bas.fill_between(codes, ecart, where=ecart >= 0, color=SERIES[1], linewidth=0)
    bas.fill_between(codes, ecart, where=ecart < 0, color=SERIES[0], linewidth=0)
    for code in np.argsort(-np.abs(ecart[1:]))[:3] + 1:
        positif = ecart[code] >= 0
        bas.annotate("code %d" % code, (code, ecart[code]),
                     textcoords="offset points", xytext=(4, 4 if positif else -12),
                     color=SERIES[1] if positif else SERIES[0],
                     fontsize=8, fontweight="bold")
    bas.set_xlim(0, 255)
    bas.set_xlabel("code du motif LBP")
    bas.set_ylabel("ecart occupe - libre")
    bas.set_title("Motifs qui separent les deux classes")
    clean(bas)

    fig.tight_layout()
    fig.savefig(sortie)
    plt.close(fig)
    print("figure : %s" % sortie)


def figure_matrice_confusion(training_path, test_path, sortie):
    """Detail des erreurs : ce que le modele predit face a la verite."""
    train, train_labels = read_descriptors(training_path)
    test, test_labels = read_descriptors(test_path)
    predictions = classify(train, train_labels, test)

    matrice = np.array([[int(((test_labels == v) & (predictions == p)).sum())
                         for p in (0, 1)] for v in (0, 1)])
    taux = 100.0 * np.trace(matrice) / matrice.sum()

    fig, ax = plt.subplots(figsize=(4.6, 4.0))
    rampe = plt.matplotlib.colors.LinearSegmentedColormap.from_list("bleu", SEQUENTIAL)
    ax.imshow(matrice, cmap=rampe, vmin=0, vmax=matrice.max())

    for i in range(2):
        for j in range(2):
            fonce = matrice[i, j] > 0.55 * matrice.max()
            ax.text(j, i, matrice[i, j], ha="center", va="center", fontsize=15,
                    fontweight="bold", color="#ffffff" if fonce else "#0b0b0b")

    ax.set_xticks((0, 1), ("libre", "occupe"))
    ax.set_yticks((0, 1), ("libre", "occupe"))
    ax.set_xlabel("classe predite par le modele")
    ax.set_ylabel("classe reelle de l'image")
    ax.set_title("Matrice de confusion\n%.2f %% d'images test bien reconnues" % taux)
    ax.grid(False)
    ax.tick_params(length=0)
    for cote in ax.spines.values():
        cote.set_visible(False)
    fig.savefig(sortie)
    plt.close(fig)
    print("figure : %s" % sortie)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train-root", default="../A")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--out-dir", default="resultats")
    args = parser.parse_args()

    figure_principe(args.train_root, args.seed,
                    "%s/principe-lbp.png" % args.out_dir)
    figure_histogrammes_moyens("%s/training.txt" % args.out_dir,
                               "%s/histogrammes-moyens.png" % args.out_dir)
    figure_matrice_confusion("%s/training.txt" % args.out_dir,
                             "%s/test.txt" % args.out_dir,
                             "%s/matrice-confusion.png" % args.out_dir)


if __name__ == "__main__":
    main()
