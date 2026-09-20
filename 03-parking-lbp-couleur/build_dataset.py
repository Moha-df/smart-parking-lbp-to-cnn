"""Genere les descripteurs LBP couleur du jeu training et du jeu test.

Les fichiers sont ecrits dans out/<mode>/training.txt et out/<mode>/test.txt :
une ligne par image, les valeurs du descripteur puis le label
(0 = libre, 1 = occupe). Les jeux training et test sont disjoints.
"""

import argparse

import cv2

from color import MODES, describe_file, mosaic, read_color
from dataset import sample, write_descriptors


def build(selection, mode, output):
    descriptors = [describe_file(path, mode) for path, _ in selection]
    labels = [label for _, label in selection]
    write_descriptors(output, descriptors, labels)
    print("%s : %d lignes de %d valeurs (%d libres, %d occupes)"
          % (output, len(labels), len(descriptors[0]),
             labels.count(0), labels.count(1)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=MODES, default="mosaic",
                        help="strategie de descripteur couleur")
    parser.add_argument("--train-root", default="../A")
    parser.add_argument("--test-root", default=None,
                        help="dossier de test (par defaut : celui du training)")
    parser.add_argument("--train-per-class", type=int, default=100)
    parser.add_argument("--test-per-class", type=int, default=100)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--out-dir", default="resultats")
    parser.add_argument("--save-mosaic", metavar="FICHIER",
                        help="enregistre la mosaique R|G|B de la premiere image")
    args = parser.parse_args()

    test_root = args.test_root or args.train_root

    training = sample(args.train_root, args.train_per_class, args.seed)
    deja_vues = [path for path, _ in training] if test_root == args.train_root else []
    test = sample(test_root, args.test_per_class, args.seed + 1, exclude=deja_vues)

    if args.save_mosaic:
        cv2.imwrite(args.save_mosaic, mosaic(read_color(training[0][0])))
        print("mosaique enregistree : %s" % args.save_mosaic)

    base = "%s/%s" % (args.out_dir, args.mode)
    build(training, args.mode, "%s/training.txt" % base)
    build(test, args.mode, "%s/test.txt" % base)


if __name__ == "__main__":
    main()
