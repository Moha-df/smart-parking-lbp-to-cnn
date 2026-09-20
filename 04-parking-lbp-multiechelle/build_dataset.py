"""Genere les descripteurs LBP multi-echelle du jeu training et du jeu test.

Les fichiers sont ecrits dans resultats/<mode>/training.txt et
resultats/<mode>/test.txt : une ligne par image, les valeurs du descripteur
puis le label (0 = libre, 1 = occupe). Les jeux training et test sont disjoints.
"""

import argparse

from dataset import sample, write_descriptors
from multiscale import MODES, describe_file


def build(selection, mode, output):
    descriptors = [describe_file(path, mode) for path, _ in selection]
    labels = [label for _, label in selection]
    write_descriptors(output, descriptors, labels)
    print("%s : %d lignes de %d valeurs (%d libres, %d occupes)"
          % (output, len(labels), len(descriptors[0]),
             labels.count(0), labels.count(1)))


def tirages(train_root, test_root, n_train, n_test, seed):
    """Jeux training et test disjoints lorsqu'ils viennent du meme dossier."""
    training = sample(train_root, n_train, seed)
    deja_vues = [path for path, _ in training] if test_root == train_root else []
    test = sample(test_root, n_test, seed + 1, exclude=deja_vues)
    return training, test


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=MODES, default="grille3x3",
                        help="strategie de descripteur multi-echelle")
    parser.add_argument("--train-root", default="../A")
    parser.add_argument("--test-root", default=None,
                        help="dossier de test (par defaut : celui du training)")
    parser.add_argument("--train-per-class", type=int, default=100)
    parser.add_argument("--test-per-class", type=int, default=100)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--out-dir", default="resultats")
    args = parser.parse_args()

    training, test = tirages(args.train_root, args.test_root or args.train_root,
                             args.train_per_class, args.test_per_class, args.seed)

    base = "%s/%s" % (args.out_dir, args.mode)
    build(training, args.mode, "%s/training.txt" % base)
    build(test, args.mode, "%s/test.txt" % base)


if __name__ == "__main__":
    main()
