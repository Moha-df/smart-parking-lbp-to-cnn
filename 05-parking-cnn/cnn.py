"""Classification par CNN : chargement des images, architecture, entrainement.

Contrairement aux TP 01-04, l'image n'est pas reduite a un descripteur fait
main (LBP) : le reseau apprend directement sur les pixels. Le jeu training
(200 imagettes) est minuscule pour un CNN entraine de zero, d'ou une
architecture volontairement petite, une legere augmentation de donnees et un
arret anticipe sur une validation decoupee dans le training.
"""

import cv2
import numpy as np

IMG = 64  # les imagettes CNRPark (150x150) sont reduites pour l'entrainement


def load_images(selection, img_size=IMG):
    """[(chemin, label)] -> tenseur (N, img_size, img_size, 1) uint8 et labels."""
    x = np.zeros((len(selection), img_size, img_size, 1), dtype=np.uint8)
    y = np.empty(len(selection), dtype=np.int64)
    for i, (path, label) in enumerate(selection):
        img = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise IOError("image illisible : %s" % path)
        x[i, :, :, 0] = cv2.resize(img, (img_size, img_size),
                                    interpolation=cv2.INTER_AREA)
        y[i] = label
    return x, y


def stratified_split(x, y, val_fraction, seed):
    """Decoupe (x, y) en deux sous-ensembles, meme proportion des deux classes."""
    rng = np.random.default_rng(seed)
    idx_train, idx_val = [], []
    for label in np.unique(y):
        idx = np.where(y == label)[0].copy()
        rng.shuffle(idx)
        n_val = max(1, int(round(len(idx) * val_fraction)))
        idx_val.append(idx[:n_val])
        idx_train.append(idx[n_val:])
    idx_train = np.concatenate(idx_train)
    idx_val = np.concatenate(idx_val)
    rng.shuffle(idx_train)
    rng.shuffle(idx_val)
    return (x[idx_train], y[idx_train]), (x[idx_val], y[idx_val])


def build_model(img_size=IMG, augmentation=True, seed=None):
    """Petit CNN binaire : 3 blocs conv, tete dense, sortie sigmoide."""
    import tensorflow as tf
    from tensorflow.keras import Input, Sequential, layers

    if seed is not None:
        tf.keras.utils.set_random_seed(seed)

    modele = Sequential(name="parking_cnn")
    modele.add(Input(shape=(img_size, img_size, 1)))
    modele.add(layers.Rescaling(1.0 / 255))
    if augmentation:
        modele.add(layers.RandomFlip("horizontal"))
        modele.add(layers.RandomTranslation(0.05, 0.05, fill_mode="constant"))
    for filtres in (16, 32, 64):
        modele.add(layers.Conv2D(filtres, 3, activation="relu", padding="same"))
        modele.add(layers.MaxPooling2D(2))
    modele.add(layers.Flatten())
    modele.add(layers.Dense(64, activation="relu"))
    modele.add(layers.Dropout(0.5))
    modele.add(layers.Dense(1, activation="sigmoid"))
    modele.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
    return modele


def train_and_evaluate(training, test, seed, img_size=IMG, epochs=30, patience=5,
                       batch_size=16, val_fraction=0.2, verbose=0):
    """Entraine un CNN sur `training`, evalue sur `test` (jeux disjoints).

    Renvoie (taux de reconnaissance sur test, historique d'entrainement, modele).
    """
    import tensorflow as tf
    from tensorflow.keras.callbacks import EarlyStopping

    tf.keras.backend.clear_session()
    x_train_full, y_train_full = load_images(training, img_size)
    x_test, y_test = load_images(test, img_size)
    (x_train, y_train), (x_val, y_val) = stratified_split(
        x_train_full, y_train_full, val_fraction, seed)

    modele = build_model(img_size, augmentation=True, seed=seed)
    arret = EarlyStopping(monitor="val_loss", patience=patience,
                          restore_best_weights=True)
    historique = modele.fit(x_train, y_train, validation_data=(x_val, y_val),
                            epochs=epochs, batch_size=batch_size,
                            callbacks=[arret], verbose=verbose)

    proba = modele.predict(x_test, batch_size=64, verbose=0).ravel()
    predictions = (proba >= 0.5).astype(np.int64)
    taux = 100.0 * float((predictions == y_test).mean())
    return taux, historique.history, modele
