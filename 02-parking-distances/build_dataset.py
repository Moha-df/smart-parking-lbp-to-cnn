"""Genere out/training.txt et out/test.txt a partir de la base CNRPark.

Chaque ligne contient les 256 valeurs du descripteur LBP de l'image, suivies
du label : 0 = emplacement libre, 1 = emplacement occupe. Les jeux training et
test sont tires aleatoirement et sont disjoints.
"""

import argparse

from dataset import sample, write_descriptors
from lbp import describe_file


def build(selection, output):
    descriptors = [describe_file(path) for path, _ in selection]
    labels = [label for _, label in selection]
    write_descriptors(output, descriptors, labels)
    print("%s : %d lignes (%d libres, %d occupes)"
          % (output, len(labels), labels.count(0), labels.count(1)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train-root", default="../A",
                        help="dossier contenant free/ et busy/ pour le training")
    parser.add_argument("--test-root", default=None,
                        help="dossier de test (par defaut : celui du training)")
    parser.add_argument("--train-per-class", type=int, default=100)
    parser.add_argument("--test-per-class", type=int, default=100)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--out-dir", default="resultats")
    args = parser.parse_args()

    test_root = args.test_root or args.train_root

    training = sample(args.train_root, args.train_per_class, args.seed)
    deja_vues = [path for path, _ in training] if test_root == args.train_root else []
    test = sample(test_root, args.test_per_class, args.seed + 1, exclude=deja_vues)

    build(training, "%s/training.txt" % args.out_dir)
    build(test, "%s/test.txt" % args.out_dir)


if __name__ == "__main__":
    main()
