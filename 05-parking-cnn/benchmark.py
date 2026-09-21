"""Evalue le CNN sur plusieurs tirages independants.

Meme protocole que `04-parking-lbp-multiechelle/benchmark.py` : 100 imagettes
libres et 100 occupees pour le training, 100 + 100 disjointes pour le test,
repete sur N tirages independants (10 par defaut). Le schema de graine
(`tirage * 2`) est identique a celui du TP 4 : les tirages piochent exactement
les memes imagettes, ce qui permet une comparaison appariee dans `figures.py`.

Les taux sont enregistres dans resultats/benchmark.csv (meme format que le
TP 4 : colonnes mode, tirage, taux).
"""

import argparse
import csv
import time
from pathlib import Path

import numpy as np

from cnn import IMG, train_and_evaluate
from dataset import tirages


def run(root, n_train, n_test, n_runs, sortie, **kwargs):
    taux = []
    for tirage in range(n_runs):
        training, test = tirages(root, root, n_train, n_test, tirage * 2)
        t0 = time.time()
        valeur, _, _ = train_and_evaluate(training, test, seed=tirage, **kwargs)
        taux.append(valeur)
        print("tirage %d/%d : %.2f %% (%.0f s)"
              % (tirage + 1, n_runs, valeur, time.time() - t0), flush=True)

    Path(sortie).parent.mkdir(parents=True, exist_ok=True)
    with open(sortie, "w", newline="", encoding="ascii") as f:
        writer = csv.writer(f)
        writer.writerow(("mode", "tirage", "taux"))
        for tirage, valeur in enumerate(taux):
            writer.writerow(("cnn", tirage, "%.2f" % valeur))
    return taux


def report(taux, n_runs):
    v = np.array(taux)
    print("\nTaux de reconnaissance du CNN sur %d tirages independants\n" % n_runs)
    print("Moyenne %8.2f %%" % v.mean())
    print("Ecart-t %8.2f" % v.std())
    print("Min     %8.2f %%" % v.min())
    print("Max     %8.2f %%" % v.max())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train-root", default="../A")
    parser.add_argument("--train-per-class", type=int, default=100)
    parser.add_argument("--test-per-class", type=int, default=100)
    parser.add_argument("--runs", type=int, default=10)
    parser.add_argument("--img-size", type=int, default=IMG)
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--patience", type=int, default=5)
    parser.add_argument("--out-dir", default="resultats")
    args = parser.parse_args()

    taux = run(args.train_root, args.train_per_class, args.test_per_class,
              args.runs, "%s/benchmark.csv" % args.out_dir,
              img_size=args.img_size, epochs=args.epochs, patience=args.patience)
    report(taux, args.runs)


if __name__ == "__main__":
    main()
