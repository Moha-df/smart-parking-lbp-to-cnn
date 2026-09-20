"""Classification 1 plus proche voisin des descripteurs LBP.

Pour chaque ligne de test.txt, on calcule la somme des differences en valeurs
absolues avec chacune des lignes de training.txt, on retient le label de la
ligne la plus proche et on le compare au label connu de l'image test.
"""

import argparse

import numpy as np

from dataset import read_descriptors


def classify(train, train_labels, test):
    """Label predit pour chaque ligne de test (distance L1, 1-NN)."""
    predictions = np.empty(len(test), dtype=np.int64)
    for i, vecteur in enumerate(test):
        distances = np.abs(train - vecteur).sum(axis=1)
        predictions[i] = train_labels[int(np.argmin(distances))]
    return predictions


def report(predictions, labels):
    correct = int((predictions == labels).sum())
    total = len(labels)
    print("Images test correctement reconnues : %d / %d" % (correct, total))
    print("Taux de reconnaissance             : %.2f %%" % (100.0 * correct / total))
    print()
    print("Matrice de confusion (lignes = verite, colonnes = prediction)")
    print("            libre  occupe")
    for valeur, nom in ((0, "libre "), (1, "occupe")):
        ligne = [int(((labels == valeur) & (predictions == p)).sum()) for p in (0, 1)]
        print("    %s  %5d  %6d" % (nom, ligne[0], ligne[1]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--training", default="resultats/training.txt")
    parser.add_argument("--test", default="resultats/test.txt")
    args = parser.parse_args()

    train, train_labels = read_descriptors(args.training)
    test, test_labels = read_descriptors(args.test)
    report(classify(train, train_labels, test), test_labels)


if __name__ == "__main__":
    main()
