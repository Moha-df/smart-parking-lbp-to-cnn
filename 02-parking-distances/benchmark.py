"""Evalue chaque metrique sur plusieurs tirages aleatoires independants.

Un tirage unique ne suffit pas a departager les metriques : l'ecart entre deux
metriques est du meme ordre que la variation d'une meme metrique d'un tirage a
l'autre. Ce script repete l'experience et reporte moyenne, ecart-type et
etendue. Les taux sont enregistres dans resultats/benchmark.csv.
"""

import argparse
import csv
from pathlib import Path

import numpy as np

from compare import classify
from dataset import sample
from distances import METRICS
from lbp import describe_file


def descriptors(selection):
    x = np.array([describe_file(chemin) for chemin, _ in selection])
    y = np.array([label for _, label in selection])
    return x, y


def run(root, n_train, n_test, n_runs, sortie):
    taux = {nom: [] for nom in METRICS}
    for tirage in range(n_runs):
        training = sample(root, n_train, tirage)
        test = sample(root, n_test, tirage + 1000,
                      exclude=[chemin for chemin, _ in training])
        x_train, y_train = descriptors(training)
        x_test, y_test = descriptors(test)
        for nom, (fonction, sens) in METRICS.items():
            predictions = classify(x_train, y_train, x_test, fonction, sens)
            taux[nom].append(100.0 * (predictions == y_test).mean())
        print("tirage %d/%d termine" % (tirage + 1, n_runs), flush=True)

    Path(sortie).parent.mkdir(parents=True, exist_ok=True)
    with open(sortie, "w", newline="", encoding="ascii") as f:
        writer = csv.writer(f)
        writer.writerow(("metrique", "tirage", "taux"))
        for nom, valeurs in taux.items():
            for tirage, valeur in enumerate(valeurs):
                writer.writerow((nom, tirage, "%.2f" % valeur))
    return taux


def report(taux, n_runs):
    entete = "%-24s %9s %9s %9s %9s" % ("Metrique", "Moyenne", "Ecart-t", "Min", "Max")
    print("\nTaux de reconnaissance sur %d tirages independants\n" % n_runs)
    print(entete)
    print("-" * len(entete))
    for nom, valeurs in sorted(taux.items(), key=lambda kv: -np.mean(kv[1])):
        v = np.array(valeurs)
        print("%-24s %8.2f%% %9.2f %8.2f%% %8.2f%%"
              % (nom, v.mean(), v.std(), v.min(), v.max()))

    etendue = np.mean([np.std(v) for v in taux.values()])
    moyennes = [np.mean(v) for v in taux.values()]
    print("\nEcart entre la meilleure et la pire metrique : %.2f point"
          % (max(moyennes) - min(moyennes)))
    print("Ecart-type moyen d'une metrique d'un tirage a l'autre : %.2f point"
          % etendue)


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
