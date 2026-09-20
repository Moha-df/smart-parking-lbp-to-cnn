"""Descripteurs LBP multi-echelle.

Le descripteur LBP global compte les occurrences des 256 motifs sur toute
l'image. Ce comptage perd toute information de position : deux images dont les
memes motifs sont repartis differemment donnent le meme descripteur.

L'approche multi-echelle attaque cette limite selon deux axes independants.

Echelle spatiale
    L'image est decoupee en une grille de blocs. Un histogramme LBP H1, H2, ...
    est calcule sur chaque bloc, puis tous sont concatenes bout a bout. Le
    descripteur resultant conserve la position des motifs : une texture dense
    en haut a gauche ne se confond plus avec la meme texture en bas a droite.
    Une grille g x g donne un descripteur de g * g * 256 valeurs.

    Le mode pyramide combine plusieurs grilles (1x1, 2x2 et 4x4) dans un seul
    descripteur, de facon a decrire la scene simultanement en gros et en fin.

Echelle du voisinage
    Au lieu de la fenetre 3x3, les 8 voisins sont pris sur un cercle de rayon R
    autour du pixel central, leur valeur etant obtenue par interpolation
    bilineaire. Un petit rayon capte la micro-texture, un grand rayon des
    structures plus etendues. Le mode multirayon concatene les histogrammes
    obtenus pour R = 1, 2 et 3.

Les blocs utilisent la fenetre 3x3 de `lbp.py` (convention de la premiere
seance) ; les rayons utilisent le voisinage circulaire defini ici.
"""

import cv2
import numpy as np

from lbp import lbp_codes

RAYONS = (1, 2, 3)
GRILLES_PYRAMIDE = (1, 2, 4)

MODES = ("global", "grille2x2", "grille3x3", "grille4x4", "pyramide", "multirayon")

TAILLE_DESCRIPTEUR = {
    "global": 256,
    "grille2x2": 4 * 256,
    "grille3x3": 9 * 256,
    "grille4x4": 16 * 256,
    "pyramide": (1 + 4 + 16) * 256,
    "multirayon": len(RAYONS) * 256,
}


def lbp_codes_circulaire(gray, rayon):
    """Carte des codes LBP a 8 voisins pris sur un cercle de rayon donne.

    Les voisins ne tombent pas sur des pixels entiers des que le rayon depasse
    1 : leur valeur est interpolee bilineairement. Les bits sont ranges dans le
    sens trigonometrique en partant de la droite du pixel central.
    """
    g = gray.astype(np.float64)
    hauteur, largeur = g.shape
    marge = int(np.ceil(rayon))
    if hauteur - 2 * marge < 1 or largeur - 2 * marge < 1:
        raise ValueError("image trop petite pour un rayon de %s" % rayon)

    lignes = np.arange(marge, hauteur - marge)[:, None]
    colonnes = np.arange(marge, largeur - marge)[None, :]
    centre = g[marge:hauteur - marge, marge:largeur - marge]
    codes = np.zeros(centre.shape, dtype=np.uint8)

    for bit in range(8):
        angle = 2.0 * np.pi * bit / 8.0
        y = lignes - rayon * np.sin(angle)
        x = colonnes + rayon * np.cos(angle)

        y0 = np.floor(y).astype(np.intp)
        x0 = np.floor(x).astype(np.intp)
        dy = y - y0
        dx = x - x0
        y1 = np.minimum(y0 + 1, hauteur - 1)
        x1 = np.minimum(x0 + 1, largeur - 1)

        voisin = (g[y0, x0] * (1 - dy) * (1 - dx) + g[y0, x1] * (1 - dy) * dx
                  + g[y1, x0] * dy * (1 - dx) + g[y1, x1] * dy * dx)
        codes |= ((voisin > centre).astype(np.uint8) << bit)

    return codes


def histogramme(codes):
    return np.bincount(codes.ravel(), minlength=256).astype(np.int64)


def blocs(codes, grille):
    """Decoupe la carte des codes en grille x grille blocs, ligne par ligne."""
    for bande in np.array_split(codes, grille, axis=0):
        for bloc in np.array_split(bande, grille, axis=1):
            yield bloc


def histogrammes_blocs(gray, grille):
    """Les grille^2 histogrammes H1, H2, ... dans l'ordre de lecture."""
    codes = lbp_codes(gray)
    return [histogramme(bloc) for bloc in blocs(codes, grille)]


def describe_grille(gray, grille):
    """Descripteur spatial : les histogrammes de blocs mis bout a bout."""
    return np.concatenate(histogrammes_blocs(gray, grille))


def describe_pyramide(gray):
    """Descripteur pyramidal : plusieurs grilles concatenees."""
    codes = lbp_codes(gray)
    morceaux = []
    for grille in GRILLES_PYRAMIDE:
        morceaux.extend(histogramme(bloc) for bloc in blocs(codes, grille))
    return np.concatenate(morceaux)


def describe_multirayon(gray):
    """Descripteur multi-rayon : un histogramme par rayon, concatenes."""
    return np.concatenate([histogramme(lbp_codes_circulaire(gray, rayon))
                           for rayon in RAYONS])


DESCRIPTEURS = {
    "global": lambda gray: histogramme(lbp_codes(gray)),
    "grille2x2": lambda gray: describe_grille(gray, 2),
    "grille3x3": lambda gray: describe_grille(gray, 3),
    "grille4x4": lambda gray: describe_grille(gray, 4),
    "pyramide": describe_pyramide,
    "multirayon": describe_multirayon,
}


def read_gray(path):
    img = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise IOError("image illisible : %s" % path)
    return img


def describe_file(path, mode):
    return DESCRIPTEURS[mode](read_gray(path))
