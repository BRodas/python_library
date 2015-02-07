""" ."""

# Libreria para ordenar instancias en una lista
import operator
#import math
from distances import Distance
#from TI_Neighborhood import TI_Forward_Neighborhood


def TI_Forward_Neighborhood(conj_puntos, p, Eps):
    """
    conj_puntos (dict): the key is the order of the instance respect
    with the attribute instance, and the value is the instance.
    p (instance class clase_punto):
    Eps (float): episilon, the parameter given to the algorithm."""
    seeds = {}
    forwardThreshold = p.dist + Eps
    # Hay que declarar la lista a recorrer.
    # Primero se encuentra el indice donde esta el elemento "p"
    # Se seleccionan los elementos desde el inicio hasta el elemento "p"
    # Y finalmente se da vuelta
    try:
        q = conj_puntos[p.following]
    # Se recorre el listado recien calculado
        while q.dist < forwardThreshold:
            if Distance(q.Coords, p.Coords) <= Eps:
                seeds[q] = None
            q = conj_puntos[q.following]

    except KeyError:
        pass
    # Se devuelve el listado con las semillas.
    return seeds


def TI_Backward_Neighborhood(conj_puntos, pto, Eps):
    seeds = {}
    backwardThreshold = pto.dist - Eps
    # Hay que declarar la lista a recorrer.
    # Primero se encuentra el indice donde esta el elemento "p"
    # Se seleccionan los elementos desde el inicio hasta el elemento "p"
    # Y finalmente se da vuelta
    try:
        q = conj_puntos[pto.previous]
        while q.dist > backwardThreshold:
            if Distance(q.Coords, pto.Coords) <= Eps:
                seeds[q] = None
            q = conj_puntos[q.previous]

    except KeyError:
        pass
    # Se devuelve el listado con las semillas.
    return seeds


def TI_Neighborhood(conj_puntos, p, Eps):
    parte_1 = TI_Backward_Neighborhood(conj_puntos, p, Eps)
    parte_2 = TI_Forward_Neighborhood(conj_puntos, p, Eps)
    return dict(parte_1.items() + parte_2.items())


def delete_instance(dict_instances, cursor):
    """re-sort the pointers."""

    prev_pnt = dict_instances[cursor].previous
    try:
        dict_instances[prev_pnt].following = dict_instances[
            cursor].following
    except KeyError:
        dict_instances[cursor].previous = None

    next_pnt = dict_instances[cursor].following
    try:
        dict_instances[next_pnt].previous = dict_instances[
            cursor].previous
    except KeyError:
        dict_instances[cursor].following = None

    del dict_instances[cursor]
    return dict_instances


def TI_ExpandCluster(conj_puntos, conj_revisado,
                     p, ClId, Eps, MinPts, cursor):
    """
    conj_puntos (dict): having the key the order, and the value an instance
    of class clase_punto.
    conj_revisado (list): it has the instances of class clase_punto
    already checked.
    p (instance class clase_punto): the instance of the point under study.
    ClId (int): number of cluster.
    Eps (float): radius, the parameter of TI-DBscan.
    MinPts (int): minimum number of points.
    cursor (instance class obj): it could be any instance,
    but must have the attribute "cursos".

    returns a bolean, it's true if it actually makes up a cluster.
    """

    # Se explora el conjunto de puntos alrededor del punto "p". Notese que
    # seeds es un conjunto o listado de puntos.
    seeds = TI_Neighborhood(conj_puntos, p, Eps)
    # Se cuentan los puntos alrededor de "p", incluyendose a si mismo
    p.NeighborsNo += len(seeds)
    # "p" puede ser ruido o un punto de borde
    if p.NeighborsNo < MinPts:
        # Se declara inicialmente como que es ruido
        p.ClusterId = "NOISE"
        # Se recorre cada punto del conjunto de semillas
        for q in seeds:
            q.Border.append(p)
            q.NeighborsNo += 1

        # Se declara el listado de puntos de borde de "p" como vacio
        p.Border = []
        # Se remueve "p" del conj_puntos hacia conj_revisado
        conj_puntos = delete_instance(conj_puntos, cursor.value)
        while not (cursor.value in conj_puntos):
            if conj_puntos == {}:
                break
            cursor.value += 1
        conj_revisado.append(p)

        return False

    else:
        # Se asigna la pertenencia al cluster
        p.ClusterId = ClId
        # Se recorren los puntos encontrados en las semillas
        for q in seeds:
            q.ClusterId = ClId
            q.NeighborsNo += 1

        #endfor
        for q in p.Border:
            # Se identifica que elemento es en el listado conj_revisado, y
            # luego se modifica este.
            conj_revisado[conj_revisado.index(q)].ClusterId = ClId

        # Una vez mas se vacia el conjunto
        p.Border = []
        # Se remueve "p" del conj_puntos hacia conj_revisado
        conj_puntos = delete_instance(conj_puntos, cursor.value)
        while not (cursor.value in conj_puntos):
            if conj_puntos == {}:
                break
            cursor.value += 1
        conj_revisado.append(p)
        # Mientras la cantidad de elementos en el listado de las semillas sea
        # mayor a cero, o sea mientras halla UN elemento se debe realizar la
        # siguiente iteracion:
        while seeds:
            # De alguna manera en este while se repite el proceso
            curPoint = seeds.keys()[0]
            curSeeds = TI_Neighborhood(conj_puntos, curPoint, Eps)
            curPoint.NeighborsNo += len(curSeeds)
            # i curPoint esta en el borde
            if curPoint.NeighborsNo < MinPts:
                for q in curSeeds:
                    q.NeighborsNo += 1
            # Si curPoint es nucleo
            else:
                while curSeeds:
                    q = curSeeds.keys()[0]
                    q.NeighborsNo += 1
                    if q.ClusterId == "UNCLASSIFIED":
                        q.ClusterId = ClId
                        # Se remueve "p" del conj_puntos hacia
                        # conj_revisado
                        del curSeeds[q]
                        seeds[q] = None
                    else:
                        del curSeeds[q]
                # Se recorren los puntos del borde
                for q in curPoint.Border:
                    # Se identifica que elemento es en el
                    # listado conj_revisado, y luego se modifica este.
                    conj_revisado[conj_revisado.index(q)].ClusterId = ClId

            # Se modifica el contenido de las variables.
            curPoint.Border = []
            conj_puntos = delete_instance(conj_puntos, curPoint.init)
            while not (cursor.value in conj_puntos):
                if conj_puntos == {}:
                    break
                cursor.value += 1
            conj_revisado.append(curPoint)
            del seeds[curPoint]

        # Se devuelve el valor logico.
        return True

#def Distance(punto, pnt_ref):
#    """Funcion que calcula la distancia en dos dimenciones"""
#    return math.sqrt(
#        (punto[0] - pnt_ref[0]) * (punto[0] - pnt_ref[0])
#        + (punto[1] - pnt_ref[1]) * (punto[1] - pnt_ref[1]))


class clase_punto:
    """Clase que genera un punto con sus atributos"""
    def __init__(self, punto, pnt_ref, metadata=None):
        try:
            # Metadata
            self.metadata = metadata
            # Se guardan las coordenadas originales
            self.Coords = punto[0:2]
        except:
            pass

        # p.ClusterId = UNCLASSIFIED;
        self.ClusterId = "UNCLASSIFIED"
        # p.dist = Distance(p,r)
        self.dist = Distance(punto[0:2], pnt_ref[0:2])
        # p.NeighborsNo = 1
        self.NeighborsNo = 1
        # p.Border = vacio
        self.Border = []
        # Cursor
        self.previous = None
        self.following = None
        self.init = None


def TI_DBScan(conj_puntos, eps, MinPts, metadata=None):
    """Esta clase aplica el algoritmo TI-DBScan al conjunto
    de puntos entregados.

    conj_puntos = [[coord1, coord2, ...], ...]:
        Es un listado de tuplas o listas, donde los dos
    primeros elementos de cada lista son las coordenadas y
    el tercero es METAdata."""
    try:
        # /* assert: r denotes a reference point */
        pnt_ref = conj_puntos[0]
    except IndexError:
        pass
    # the number of points cannot be 1.
    MinPts = MinPts if MinPts > 1 else 2
    # D' = empty set of points;
    conj_revisado = []
    # Se transforman los puntos
    try:
        conj_puntos = [clase_punto(
            conj_puntos[indice], pnt_ref, metadata=metadata[indice])
            for indice in xrange(len(conj_puntos))]
    except TypeError:
        conj_puntos = [clase_punto(
            conj_puntos[indice], pnt_ref)
            for indice in xrange(len(conj_puntos))]

        # sort all points in D non-decreasingly w.r.t. field dist;
        #conj_ordenado = sorted(conj_puntos, key=operator.attrgetter('dist'))
    conj_puntos = sorted(conj_puntos, key=operator.attrgetter('dist'))

    # dictionary with cursor
    set_D = {}
    for i in xrange(len(conj_puntos)):
        set_D[i] = conj_puntos[i]
        # seting the before one
        set_D[i].previous = i - 1 if i != 0 else None
        # seting the after one
        set_D[i].following = i + 1 if i != len(conj_puntos) - 1 else None
        # seting the initial position
        set_D[i].init = i

    # ClusterId = label of first cluster;
    i = 1
    ClusterId = "%s" % (i)

    # for each point p in the ordered set D starting from
    # the first point until last point in D do
    # Mientras el listado de puntos por revisar no este vacio, se itera
    # infinitamente.
    class cursor(object):
        def __init__(self, value=0):
            self.value = value
    cursor = cursor(0)

    while set_D:
        #for p in conj_puntos:
        # if TI-ExpandCluster(D, D', p, ClusterId, Eps, MinPts) then
        if TI_ExpandCluster(set_D, conj_revisado,
                            set_D[cursor.value], ClusterId,
                            eps, MinPts, cursor):
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

    resultado = TI_DBScan(conjunto_de_puntos, 2, 2)

    for elemento in resultado:
        print elemento.ClusterId
        print elemento.Coords
        print ""
