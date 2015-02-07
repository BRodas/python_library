import numpy as np


def euclidean(v1, v2):
    v1 = np.array(v1)
    v2 = np.array(v2)
    return np.sqrt(np.sum(np.power(v1 - v2, 2)))


def manhattan(v1, v2):
    v1 = np.array(v1)
    v2 = np.array(v2)
    return (np.sum(np.abs(v1 - v2)))
