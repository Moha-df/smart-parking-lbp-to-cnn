"""Compare toutes les strategies multi-echelle sur un meme tirage."""

import argparse

from build_dataset import build, tirages
from classify import evaluate
from multiscale import MODES


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train-root", default="../A")
    parser.add_argument("--test-root", default=None)
    parser.add_argument("--train-per-class", type=int, default=100)
    parser.add_argument("--test-per-class", type=int, default=100)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--out-dir", default="resultats")
    args = parser.parse_args()

    training, test = tirages(args.train_root, args.test_root or args.train_root,
                             args.train_per_class, args.test_per_class, args.seed)

    resultats = []
    for mode in MODES:
        base = "%s/%s" % (args.out_dir, mode)
        build(training, mode, "%s/training.txt" % base)
        build(test, mode, "%s/test.txt" % base)
        resultats.append((mode,) + evaluate("%s/training.txt" % base,
                                            "%s/test.txt" % base))

    entete = "\n%-13s %13s %10s %10s" % ("Mode", "Descripteur", "Correct", "Taux")
    print(entete)
    print("-" * (len(entete) - 1))
    for mode, correct, total, taille in resultats:
        print("%-13s %9d val %5d/%-4d %8.2f %%"
              % (mode, taille, correct, total, 100.0 * correct / total))


if __name__ == "__main__":
    main()
