""" ."""

# Libreria numpy
import numpy as np


def Neighborhood(conj_puntos, pto, Eps):
    seeds = []

    for qoint in conj_puntos:
        if Distance(qoint.Coords, pto.Coords) <= Eps:
            seeds.append(qoint)

    # Se devuelve el listado con las semillas.
    return seeds


def ExpandCluster(conj_puntos, conj_revisado,
                  point, ClId, Eps, MinPts):
    """conj_puntos esta ordenado de manera creciente respecto a las
    distancias con el punto de referencia"""

    # Se explora el conjunto de puntos alrededor del punto "p". Notese que
    # seeds es un conjunto o listado de puntos.
    seeds = Neighborhood(conj_puntos, point, Eps)

    # No core point
    if len(seeds) < MinPts:
        point.ClusterId = "NOISE"
        conj_revisado.append(point)
        return False
    # all points in seeds are density-reachable from point
    else:
        for qoint in seeds:
            qoint.ClusterId = ClId

        seeds.remove(point)
        #conj_puntos.remove(point)
        if not point in conj_revisado:
            conj_revisado.append(point)

        while seeds != []:
            currentP = seeds[0]
            result = Neighborhood(conj_puntos, currentP, Eps)
            if len(result) >= MinPts:
                for resultP in result:
                    condition_1 = resultP.ClusterId == "UNCLASSIFIED"
                    condition_2 = resultP.ClusterId == "NOISE"
                    if (condition_1 or condition_2):
                        if resultP.ClusterId == "UNCLASSIFIED":
                            seeds.append(resultP)
                        resultP.ClusterId = ClId
            seeds.remove(currentP)
            #conj_puntos.remove(currentP)
            if not currentP in conj_revisado:
                conj_revisado.append(currentP)
        return True


def Distance(punto, pnt_ref):
    """Funcion que calcula la distancia en dos dimenciones"""
    punto = np.array(punto[0:2])
    pnt_ref = np.array(pnt_ref[0:2])
    return np.sqrt(np.sum(np.power(punto - pnt_ref, 2)))


class clase_punto:
    """Clase que genera un punto con sus atributos"""
    def __init__(self, punto, metadata=None):
        try:
            # Metadata
            self.metadata = metadata
            # Se guardan las coordenadas originales
            self.Coords = punto[0:2]
        except:
            pass

        # p.ClusterId = UNCLASSIFIED;
        self.ClusterId = "UNCLASSIFIED"
        # p.NeighborsNo = 1
        self.NeighborsNo = 1
        # p.Border = vacio
        self.Border = []


def DBScan(conj_puntos, eps, MinPts, metadata=None):
    """Esta clase aplica el algoritmo TI-DBScan al conjunto
    de puntos entregados.

    conj_puntos = [[coord1, coord2, ...], ...]:
        Es un listado de tuplas o listas, donde los dos
    primeros elementos de cada lista son las coordenadas y
    el tercero es METAdata."""
    # the number of points cannot be 1.
    MinPts = MinPts if MinPts > 1 else 2

    # D' = empty set of points;
    conj_revisado = []
    # Se transforman los puntos
    try:
        conj_puntos = [clase_punto(
            conj_puntos[indice], metadata=metadata[indice])
            for indice in xrange(len(conj_puntos))]
    except TypeError:
        conj_puntos = [clase_punto(
            conj_puntos[indice])
            for indice in xrange(len(conj_puntos))]

    # ClusterId = label of first cluster;
    i = 1
    ClusterId = "%s" % (i)

    # for each point p in the ordered set D starting from
    # the first point until last point in D do
    #for p in conj_ordenado: (Esta es la linea original)
    #while conj_puntos != []:
    for point in conj_puntos:
        if point.ClusterId == "UNCLASSIFIED":
            # if TI-ExpandCluster(D, D', p, ClusterId, Eps, MinPts) then
            if ExpandCluster(conj_puntos, conj_revisado,
                             point, ClusterId, eps, MinPts):
                # ClusterId = NextId(ClusterId)
                i += 1
                ClusterId = "%s" % (i)

            # endif
        # endfor

    # return D'// D' is a clustered set of points
    return conj_revisado


# La siguiente linea es para el testeo
if __name__ == "__main__":
    conjunto_de_puntos = [[1.00, 1.00], [1.50, 1.00], [2.00, 1.50],
                          [5.00, 5.00], [6.00, 5.50], [5.50, 6.00],
                          [10.00, 11.00], [10.50, 9.50], [10.00, 10.00],
                          [8.00, 1.00], [1.00, 8.00]]

    #conjunto_de_puntos = [[1.00, 1.00], [1.50, 1.00], [2.00, 1.50],
     #                    [5.00, 5.00], [6.00, 5.50], [5.50, 6.00],
      #                   [8.00, 1.00], [1.00, 8.00]]

    #conjunto_de_puntos = [[1.00, 1.00], [1.50, 1.00], [2.00, 1.50],
     #                     [5.00, 5.00], [8.00, 1.00], [1.00, 8.00]]

    #conjunto_de_puntos = [[1.00, 1.00], [1.50, 1.00],
     #                     [8.00, 1.00], [1.00, 8.00]]

    resultado = DBScan(conjunto_de_puntos, 2, 2)

    for elemento in resultado:
        print elemento.ClusterId
        print elemento.Coords
        print ""
