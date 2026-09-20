"""Compare les trois strategies de descripteur LBP couleur sur le meme tirage."""

import argparse

from build_dataset import build
from classify import evaluate
from color import MODES
from dataset import sample


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train-root", default="../A")
    parser.add_argument("--test-root", default=None)
    parser.add_argument("--train-per-class", type=int, default=100)
    parser.add_argument("--test-per-class", type=int, default=100)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--out-dir", default="resultats")
    args = parser.parse_args()

    test_root = args.test_root or args.train_root
    training = sample(args.train_root, args.train_per_class, args.seed)
    deja_vues = [path for path, _ in training] if test_root == args.train_root else []
    test = sample(test_root, args.test_per_class, args.seed + 1, exclude=deja_vues)

    resultats = []
    for mode in MODES:
        base = "%s/%s" % (args.out_dir, mode)
        build(training, mode, "%s/training.txt" % base)
        build(test, mode, "%s/test.txt" % base)
        resultats.append((mode,) + evaluate("%s/training.txt" % base,
                                            "%s/test.txt" % base))

    entete = "\n%-14s %12s %10s %10s" % ("Mode", "Descripteur", "Correct", "Taux")
    print(entete)
    print("-" * (len(entete) - 1))
    for mode, correct, total, taille in resultats:
        print("%-14s %9d val %5d/%-4d %8.2f %%"
              % (mode, taille, correct, total, 100.0 * correct / total))


if __name__ == "__main__":
    main()
