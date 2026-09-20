"""Selection des imagettes et ecriture des fichiers de descripteurs."""

import random
from pathlib import Path

import numpy as np

EXTENSIONS = (".jpg", ".jpeg", ".png", ".bmp", ".pgm")
LABELS = (("free", 0), ("busy", 1))


def list_images(directory):
    return sorted(p for p in Path(directory).iterdir()
                  if p.suffix.lower() in EXTENSIONS)


def sample(root, n_per_class, seed, exclude=()):
    """Renvoie [(chemin, label)] : n images 'free' (0) puis n images 'busy' (1).

    Les chemins presents dans `exclude` sont ecartes, ce qui garantit des jeux
    training et test disjoints lorsqu'ils proviennent du meme dossier.
    """
    rng = random.Random(seed)
    exclude = set(exclude)
    selection = []
    for nom, label in LABELS:
        images = [p for p in list_images(Path(root) / nom) if p not in exclude]
        if len(images) < n_per_class:
            raise ValueError("%s : %d images disponibles, %d demandees"
                             % (nom, len(images), n_per_class))
        for path in rng.sample(images, n_per_class):
            selection.append((path, label))
    return selection


def write_descriptors(path, descriptors, labels):
    """Une ligne par image : 256 valeurs LBP puis le label (0 ou 1)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="ascii") as f:
        for descriptor, label in zip(descriptors, labels):
            f.write(" ".join(str(int(v)) for v in descriptor))
            f.write(" %d\n" % label)


def read_descriptors(path):
    """Relit un fichier ecrit par write_descriptors -> (descripteurs, labels)."""
    data = np.loadtxt(path, dtype=np.int64, ndmin=2)
    return data[:, :-1], data[:, -1]
