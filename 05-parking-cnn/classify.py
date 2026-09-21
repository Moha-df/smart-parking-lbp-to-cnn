"""Entraine et evalue le CNN sur un seul tirage (mise en oeuvre en ligne de commande)."""

import argparse

from cnn import IMG, train_and_evaluate
from dataset import tirages


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train-root", default="../A")
    parser.add_argument("--test-root", default=None,
                        help="dossier de test (par defaut : celui du training)")
    parser.add_argument("--train-per-class", type=int, default=100)
    parser.add_argument("--test-per-class", type=int, default=100)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--img-size", type=int, default=IMG)
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--patience", type=int, default=5)
    args = parser.parse_args()

    training, test = tirages(args.train_root, args.test_root or args.train_root,
                             args.train_per_class, args.test_per_class, args.seed)

    taux, historique, _ = train_and_evaluate(
        training, test, seed=args.seed, img_size=args.img_size,
        epochs=args.epochs, patience=args.patience, verbose=2)

    print("\nImages test : %d libres, %d occupees"
          % (args.test_per_class, args.test_per_class))
    print("Epoques effectuees          : %d" % len(historique["loss"]))
    print("Taux de reconnaissance      : %.2f %%" % taux)


if __name__ == "__main__":
    main()
