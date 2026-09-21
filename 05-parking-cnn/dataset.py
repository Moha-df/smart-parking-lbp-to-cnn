"""Selection des imagettes, identique aux TP LBP (01-04).

Copie volontaire de `dataset.py` (memes `list_images`/`sample`) et de la
fonction `tirages` de `build_dataset.py` du TP 4. Avec la meme racine et le
meme schema de graine (`tirage * 2`), un tirage numero N pioche exactement les
memes images que le benchmark LBP multi-echelle : la comparaison CNN / LBP se
fait donc a donnees strictement identiques, tirage par tirage.
"""

import random
from pathlib import Path

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


def tirages(train_root, test_root, n_train, n_test, seed):
    """Jeux training et test disjoints lorsqu'ils viennent du meme dossier."""
    training = sample(train_root, n_train, seed)
    deja_vues = [path for path, _ in training] if test_root == train_root else []
    test = sample(test_root, n_test, seed + 1, exclude=deja_vues)
    return training, test
