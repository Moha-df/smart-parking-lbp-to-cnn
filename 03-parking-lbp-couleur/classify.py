"""Classification 1 plus proche voisin (distance L1) des descripteurs couleur."""

import argparse

import numpy as np

from color import MODES
from dataset import read_descriptors


def classify(train, train_labels, test):
    predictions = np.empty(len(test), dtype=np.int64)
    for i, vecteur in enumerate(test):
        distances = np.abs(train - vecteur).sum(axis=1)
        predictions[i] = train_labels[int(np.argmin(distances))]
    return predictions


def evaluate(training_path, test_path):
    train, train_labels = read_descriptors(training_path)
    test, test_labels = read_descriptors(test_path)
    predictions = classify(train, train_labels, test)
    return int((predictions == test_labels).sum()), len(test_labels), train.shape[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=MODES, default="mosaic")
    parser.add_argument("--out-dir", default="resultats")
    args = parser.parse_args()

    base = "%s/%s" % (args.out_dir, args.mode)
    correct, total, taille = evaluate("%s/training.txt" % base, "%s/test.txt" % base)
    print("mode %s (descripteur de %d valeurs)" % (args.mode, taille))
    print("Images test correctement reconnues : %d / %d" % (correct, total))
    print("Taux de reconnaissance             : %.2f %%" % (100.0 * correct / total))


if __name__ == "__main__":
    main()
