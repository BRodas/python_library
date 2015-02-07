"""Clustering indexes are covert in this script."""

import numpy as np
import distances as dist


class FormatPoint(object):

    """This class only adapts the given point to a point like DBScan."""

    def __init__(self, Coords, ClusterId):
        self.Coords = Coords
        self.ClusterId = ClusterId


def centroids(DataSet, algorithm=None, eps=800):
    sum_per_centroid = dict()
    points_per_centroid = dict()
    elements_per_cluster = dict()
    list_centroids = []

    if algorithm == 'optics':
        DataSet = np.array(DataSet)
        ClusterId = 0
        new_cluster = True

        for index in range(len(DataSet)):
            if DataSet[index, 2] <= eps:
                if new_cluster is True:
                    new_cluster = False
                    ClusterId += 1
                    sum_per_centroid.setdefault(ClusterId,
                                                DataSet[index - 1, [0, 1]])
                    points_per_centroid.setdefault(ClusterId, 1)
                    elements_per_cluster.setdefault(
                        ClusterId, [FormatPoint(DataSet[index, [0, 1]],
                                                ClusterId)])

                sum_per_centroid[ClusterId] += DataSet[index - 1, [0, 1]]
                points_per_centroid[ClusterId] += 1
                elements_per_cluster[ClusterId].append(
                    FormatPoint(DataSet[index, [0, 1]], ClusterId))

                try:
                    list_centroids.pop(ClusterId - 1)
                    list_centroids.insert(
                        ClusterId - 1,
                        np.true_divide(sum_per_centroid[ClusterId],
                                       points_per_centroid[ClusterId]))
                except IndexError:
                    list_centroids.insert(
                        ClusterId - 1,
                        np.true_divide(sum_per_centroid[ClusterId],
                                       points_per_centroid[ClusterId]))

            elif new_cluster is False:
                new_cluster = True

        return list_centroids, elements_per_cluster

    # if the case is DBScan or TI-DBScan
    else:
        for point in DataSet:
            NotNoise = not point.ClusterId == 'NOISE'
            if NotNoise:
                ID = int(point.ClusterId)
                sum_per_centroid.setdefault(ID, np.array([0, 0]))
                points_per_centroid.setdefault(ID, 0)
                elements_per_cluster.setdefault(ID, [])

                sum_per_centroid[ID] += np.array(point.Coords)
                points_per_centroid[ID] += 1
                elements_per_cluster[ID].append(point)

        list_centroids = [np.true_divide(sum_per_centroid[ID],
                                         points_per_centroid[ID])
                          for ID
                          in sorted(sum_per_centroid.keys())]

        return list_centroids, elements_per_cluster


class DaviesBouldin(object):

    """Class to calculate Davies-Bouldin index."""

    def __init__(self, ListOfObjects, algorithm=None, eps=800):
        """Parameters:
            ListOfObjects
            algorithm

            """

        # first the centroids: A_i
        if algorithm == "optics":
            self.list_centroids, SetOfClusters = centroids(ListOfObjects,
                                                           algorithm,
                                                           eps)
        else:
            self.list_centroids, SetOfClusters = centroids(ListOfObjects)

        # second the S value or internal dispertion of each centroid
        self.S = []
        sum_acumulated = 0
        for key in SetOfClusters.keys():
            for vector in SetOfClusters[key]:
                v1 = vector.Coords
                v2 = self.list_centroids[key - 1]
                result = np.array((v1[0] - v2[0], v1[1] - v2[1]))
                result = np.power(result, 2)
                result = np.sum(result)
                sum_acumulated += result

            self.S.append(
                np.sqrt(
                    np.true_divide(sum_acumulated, len(SetOfClusters[key]))))

        # third the distance beetween every cluster
        NumberOfClusters = len(self.list_centroids)
        self.M = np.zeros([NumberOfClusters, NumberOfClusters])
        for i in range(NumberOfClusters - 1):
            for j in range(i + 1, NumberOfClusters):
                self.M[i, j] = dist.euclidean(self.list_centroids[i],
                                              self.list_centroids[j])

        # fourth the ratio beetween internal dispersion of each centroid and
        # between centroids.
        self.R = np.zeros([NumberOfClusters, NumberOfClusters])
        for i in range(NumberOfClusters - 1):
            for j in range(i + 1, NumberOfClusters):

                self.R[i, j] = np.true_divide(self.S[i] + self.S[j],
                                              self.M[i, j])
                self.R[j, i] = self.R[i, j]

        # the Davies-Bouldien value.
        self.value = 0
        for i in range(NumberOfClusters):
            self.value += np.max(self.R[i, :])
        self.value = np.true_divide(self.value, NumberOfClusters)
