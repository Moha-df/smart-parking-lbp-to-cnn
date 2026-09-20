"""Descripteurs LBP couleur.

Une image couleur est codee sur 3 canaux (CV_8UC3). Pour appliquer le LBP,
qui est defini sur un canal unique, on separe l'image en ses trois plans R, G
et B, chacun traite comme une image en niveaux de gris.

Trois strategies sont implementees :

  gray        : conversion classique en niveaux de gris (reference)
  mosaic      : les trois plans sont juxtaposes horizontalement en une seule
                image de largeur 3W, sur laquelle un unique LBP est calcule
  perchannel  : un LBP par plan, les trois histogrammes etant concatenes
                (descripteur de 768 valeurs)
"""

import cv2
import numpy as np

from lbp import lbp_histogram

MODES = ("gray", "mosaic", "perchannel")
DESCRIPTOR_SIZE = {"gray": 256, "mosaic": 256, "perchannel": 768}


def read_color(path):
    img = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if img is None:
        raise IOError("image illisible : %s" % path)
    return img


def planes_rgb(bgr):
    """Plans R, G, B de l'image (OpenCV charge les canaux dans l'ordre B, G, R)."""
    b, g, r = cv2.split(bgr)
    return r, g, b


def mosaic(bgr):
    """Image unique de largeur 3W : plans R, G puis B juxtaposes."""
    return cv2.hconcat(list(planes_rgb(bgr)))


def describe_gray(bgr):
    return lbp_histogram(cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY))


def describe_mosaic(bgr):
    # Le LBP est calcule sur la mosaique entiere : les deux colonnes de
    # jonction entre plans produisent des motifs inter-canaux, negligeables
    # devant les W-2 colonnes utiles de chaque plan.
    return lbp_histogram(mosaic(bgr))


def describe_perchannel(bgr):
    return np.concatenate([lbp_histogram(plan) for plan in planes_rgb(bgr)])


DESCRIBERS = {
    "gray": describe_gray,
    "mosaic": describe_mosaic,
    "perchannel": describe_perchannel,
}


def describe_file(path, mode):
    return DESCRIBERS[mode](read_color(path))
