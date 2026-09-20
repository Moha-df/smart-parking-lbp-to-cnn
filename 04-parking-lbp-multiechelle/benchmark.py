"""Evalue les strategies multi-echelle sur plusieurs tirages independants.

Les taux sont enregistres dans resultats/benchmark.csv.
"""

import argparse
import csv
from pathlib import Path

import numpy as np

from build_dataset import tirages
from classify import classify
from multiscale import MODES, TAILLE_DESCRIPTEUR, describe_file


def descriptors(selection, mode):
    x = np.array([describe_file(chemin, mode) for chemin, _ in selection])
    y = np.array([label for _, label in selection])
    return x, y


def run(root, n_train, n_test, n_runs, sortie):
    taux = {mode: [] for mode in MODES}
    for tirage in range(n_runs):
        training, test = tirages(root, root, n_train, n_test, tirage * 2)
        for mode in MODES:
            x_train, y_train = descriptors(training, mode)
            x_test, y_test = descriptors(test, mode)
            predictions = classify(x_train, y_train, x_test)
            taux[mode].append(100.0 * (predictions == y_test).mean())
        print("tirage %d/%d termine" % (tirage + 1, n_runs), flush=True)

    Path(sortie).parent.mkdir(parents=True, exist_ok=True)
    with open(sortie, "w", newline="", encoding="ascii") as f:
        writer = csv.writer(f)
        writer.writerow(("mode", "tirage", "taux"))
        for mode, valeurs in taux.items():
            for tirage, valeur in enumerate(valeurs):
                writer.writerow((mode, tirage, "%.2f" % valeur))
    return taux


def report(taux, n_runs):
    entete = "%-13s %13s %9s %9s %9s %9s" % ("Mode", "Descripteur", "Moyenne",
                                             "Ecart-t", "Min", "Max")
    print("\nTaux de reconnaissance sur %d tirages independants\n" % n_runs)
    print(entete)
    print("-" * len(entete))
    for mode, valeurs in sorted(taux.items(), key=lambda kv: -np.mean(kv[1])):
        v = np.array(valeurs)
        print("%-13s %9d val %8.2f%% %9.2f %8.2f%% %8.2f%%"
              % (mode, TAILLE_DESCRIPTEUR[mode], v.mean(), v.std(),
                 v.min(), v.max()))

    moyennes = [np.mean(v) for v in taux.values()]
    print("\nEcart entre le meilleur et le pire mode : %.2f point"
          % (max(moyennes) - min(moyennes)))
    print("Ecart-type moyen d'un mode d'un tirage a l'autre : %.2f point"
          % np.mean([np.std(v) for v in taux.values()]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train-root", default="../A")
    parser.add_argument("--train-per-class", type=int, default=100)
    parser.add_argument("--test-per-class", type=int, default=100)
    parser.add_argument("--runs", type=int, default=10)
    parser.add_argument("--out-dir", default="resultats")
    args = parser.parse_args()

    taux = run(args.train_root, args.train_per_class, args.test_per_class,
               args.runs, "%s/benchmark.csv" % args.out_dir)
    report(taux, args.runs)


if __name__ == "__main__":
    main()
