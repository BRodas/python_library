""" ."""

# Libreria para ordenar instancias en una lista
import operator
from distances import euclidean as Distance


def TI_Forward_Neighborhood(conj_puntos, p, Eps):
    """ ."""
    seeds = []
    forwardThreshold = p.dist + p.radio * Eps
    # Hay que declarar la lista a recorrer.
    # Primero se encuentra el indice donde esta el elemento "p"
    # Se seleccionan los elementos desde el inicio hasta el elemento "p"
    # Y finalmente se da vuelta
    indice = conj_puntos.index(p)
    listado_a_recorrer = conj_puntos[indice + 1:]

    # Se recorre el listado recien calculado
    for q in listado_a_recorrer:
        if q.dist > forwardThreshold:
            break
        if Distance(q.Coords, p.Coords) <= p.radio * Eps:
            seeds.append(q)

    # Se devuelve el listado con las semillas.
    return seeds


def TI_Backward_Neighborhood(conj_puntos, pto, Eps):
    seeds = []
    backwardThreshold = pto.dist - pto.radio * Eps
    # Hay que declarar la lista a recorrer.
    # Primero se encuentra el indice donde esta el elemento "p"
    # Se seleccionan los elementos desde el inicio hasta el elemento "p"
    # Y finalmente se da vuelta
    indice = conj_puntos.index(pto)
    listado_a_recorrer = conj_puntos[:indice]
    listado_a_recorrer.reverse()

    # Se recorre el listado recien calculado
    for q in listado_a_recorrer:
        if q.dist < backwardThreshold:
            break
        if Distance(q.Coords, pto.Coords) <= pto.radio * Eps:
            seeds.append(q)

    # Se devuelve el listado con las semillas.
    return seeds


def TI_Neighborhood(conj_puntos, p, Eps):
    parte_1 = TI_Backward_Neighborhood(conj_puntos, p, Eps)
    parte_2 = TI_Forward_Neighborhood(conj_puntos, p, Eps)
    return parte_1 + parte_2


def TI_ExpandCluster(conj_puntos, conj_revisado,
                     p, ClId, Eps, MinPts):
    """conj_puntos esta ordenado de manera creciente respecto a las
    distancias con el punto de referencia"""

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
        conj_puntos.remove(p)
        conj_revisado.append(p)
        return False

    else:
        # Se asigna la pertenencia al cluster
        p.ClusterId = ClId
        # Se recorren los puntos encontrados en las semillas
        for q in seeds:
            q.ClusterId = ClId
            q.NeighborsNo += 1

        # Ahora para cada punto en el borde de p
        # COMO PROGRAMAR ESTO ESTA COMPLICADO, LO SIGUIENTE ES UNA PROPUESTA.
        # ADEMAS SE PRESENTA EL CODIRO EN EL PAPER:
        #for each point q in p.Border do
        #    D'.q.ClusterId = ClId; //assign cluster id to q in D'
        #endfor
        for q in p.Border:
            # Se identifica que elemento es en el listado conj_revisado, y
            # luego se modifica este.
            conj_revisado[conj_revisado.index(q)].ClusterId = ClId

        # Una vez mas se vacia el conjunto
        p.Border = []
        # Se remueve "p" del conj_puntos hacia conj_revisado
        conj_puntos.remove(p)
        conj_revisado.append(p)
        # Mientras la cantidad de elementos en el listado de las semillas sea
        # mayor a cero, o sea mientras halla UN elemento se debe realizar la
        # siguiente iteracion:
        while seeds:
            # De alguna manera en este while se repite el proceso
            curPoint = seeds[0]
            curSeeds = TI_Neighborhood(conj_puntos, curPoint, Eps)
            curPoint.NeighborsNo += len(curSeeds)
            # i curPoint esta en el borde
            if curPoint.NeighborsNo < MinPts:
                for q in curSeeds:
                    q.NeighborsNo += 1
            # Si curPoint es nucleo
            else:
                while curSeeds:
                    q = curSeeds[0]
                    q.NeighborsNo += 1
                    if q.ClusterId == "UNCLASSIFIED":
                        q.ClusterId = ClId
                        # Se remueve "p" del conj_puntos hacia
                        # conj_revisado
                        curSeeds.remove(q)
                        seeds.append(q)
                    else:
                        curSeeds.remove(q)
                # Se recorren los puntos del borde
                for q in curPoint.Border:
                    # Se identifica que elemento es en el
                    # listado conj_revisado, y luego se modifica este.
                    conj_revisado[conj_revisado.index(q)].ClusterId = ClId

            # Se modifica el contenido de las variables.
            curPoint.Border = []
            conj_puntos.remove(curPoint)
            conj_revisado.append(curPoint)
            seeds.remove(curPoint)

        # Se devuelve el valor logico.
        return True


class clase_punto:
    """Clase que genera un punto con sus atributos"""
    def __init__(self, punto, pnt_ref, metadata=None):
        try:
            # Metadata
            self.metadata = metadata
            # Se guardan las coordenadas originales
            self.Coords = punto[0:2]
            self.radio = punto[2]
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


def VTI_DBScan(conj_puntos, eps, MinPts, metadata=None):
    """Esta clase aplica el algoritmo TI-DBScan al conjunto
    de puntos entregados.

    conj_puntos = [[coord1, coord2, radio], ...]:
        Es un listado de tuplas o listas, donde los dos
    primeros elementos de cada lista son las coordenadas y
    el tercero es el radio que deberia considerar aquel elemento."""
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

    # ClusterId = label of first cluster;
    i = 1
    ClusterId = "%s" % (i)

    # for each point p in the ordered set D starting from
    # the first point until last point in D do
    # Mientras el listado de puntos por revisar no este vacio, se itera
    # infinitamente.
    while conj_puntos:
        #for p in conj_ordenado: (Esta es la linea original)
        p = conj_puntos[0]
        #for p in conj_puntos:
        # if TI-ExpandCluster(D, D', p, ClusterId, Eps, MinPts) then
        if TI_ExpandCluster(conj_puntos, conj_revisado,
                            p, ClusterId, eps, MinPts):
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

    resultado = VTI_DBScan(conjunto_de_puntos, 2, 2)

    for elemento in resultado:
        print elemento.ClusterId
        print elemento.Coords
        print ""
