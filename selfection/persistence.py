import pickle
import os
import errno


def save(obj, filename):
    with open(filename, "wb") as f:
        pickle.dump(obj, f)


def load(filename):
    with open(filename, "rb") as f:
        obj = pickle.load(f)
    return obj


def makedirs(pathname):
    if len(pathname):
        try:
            os.makedirs(pathname)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
