# Importacion de librerias
import numpy as np
import operator


def func_distance(v1, v2):
    v1 = np.array(v1)
    v2 = np.array(v2)
    return np.sqrt(np.sum(np.power(v1 - v2, 2)))


##########################################################################
# OrderSeeds
# Le entrega instancias a esta funcion.
# El primer atributo corresponde a un LISTADO de instancias,
# y el segundo corresponde a LA
# Funcion de actualizacion
def update(OrderSeeds, neighbors, CenterObject, indice):
    # Distancia nucleo del objeto en el centro
    c_dist = CenterObject.core_distance
    # Recorrido de los objetos al rededor
    for Object in neighbors:
        # Si alguno de los puntos no ha sido procesado
        if not Object.Processed:
            distancia = func_distance([Object.latitud,
                                       Object.longitud],
                                      [CenterObject.latitud,
                                       CenterObject.longitud])
            # Se elige la mayor distancia
            new_r_dist = max(c_dist, distancia)
            # Si la distancia de alcance es indefinida
            if Object.reachability_distance == 1000000:
                # Se agrega una distancia
                Object.reachability_distance = new_r_dist
                # Se inserta el objeto en la lista, pero de manera ordenada
                OrderSeeds.append(Object)
            # Si ya hay una distancia
            else:
                # Pero esta es mayor al new_r_dist
                if new_r_dist < Object.reachability_distance:
                    # Se modifica
                    Object.reachability_distance = new_r_dist
    # Ordenamiento del listado de instancias en base a la distancia
    OrderSeeds = sorted(OrderSeeds,
                        key=operator.attrgetter('reachability_distance'))
    return OrderSeeds


##################################################
# Analisis en profundidad del punto
# SetOfObjects es una clase que tiene como atributo
# el listado de de instancias, donde cada instancia es un Object.
# Object es una de las muchas instancias pertenecientes a SetOfObjects.
def ExpandClusterOrder(SetOfObjects,
                       Object, epsi=10000, MinPts=2, listadoTuplas=[(), ()]):
    # Listado de instancias de vecinos [instancia01,
    # instancia02, instancia03, ..., instanciaNN]
    neighbors = SetOfObjects.neighbors(Object, epsi)
    # Se marca como chequeado el objeto/punto
    Object.Processed = True
    # Se define con que se puede alcanzar el objeto
    Object.reachability_distance = 1000000
    # Se calcula la "distancia al centro" del punto en estudio
    Object.setCoreDistance(neighbors, epsi, MinPts)
    # En las siguientes dos lineas se escribe el punto en estudio
    listadoTuplas.append((Object.latitud, Object.longitud,
                          Object.reachability_distance, Object.core_distance))
    # Lista vacia que se llenara con instancias y su indice
    OrderSeeds = []
    indice = 0
    # Si el elemento tiene una "core_distance". Si tiene una "core_distance",
    # se procede a recolectar objetos/puntos que son
    # "directly density-reachable"
    if Object.core_distance != 1000000:
        # Le entrega instancias a esta funcion.
        # El primer atributo corresponde a un LISTADO de instancias,
        # y el segundo corresponde a LA instancia. OrderSeeds,
        # lo que hace entonces es generar un LISTADO con los objetos
        # que estan "DIRECTLY DENSITY-REACHABLE" respecto al "Object",
        # ordenados segun "REACHABILITY DISTANCE".
        OrderSeeds = update(OrderSeeds, neighbors, Object, indice)
        # Mientras hallan puntos en la cola
        #while indice < len(OrderSeeds):
        while OrderSeeds != []:
            # La siguiente linea si bien la define
            # el paper esta intrincicamente
            # currentObject = OrderSeeds.next()
            # indice
            currentObject = OrderSeeds[0]
            # los nuevos vecinos
            neighbors = SetOfObjects.neighbors(currentObject, epsi)
            # Se declara como procesado
            currentObject.Processed = True
            # Se calcula la distancia al nucleo
            currentObject.setCoreDistance(neighbors, epsi, MinPts)
            # En las siguientes dos lineas se escribe el punto en estudio
            listadoTuplas.append((currentObject.latitud,
                                  currentObject.longitud,
                                  currentObject.reachability_distance,
                                  currentObject.core_distance))
            # Si el elemento tiene una "core_distance"
            if currentObject.core_distance != 1000000:
                # Actualiza el orden de la cola
                OrderSeeds = update(OrderSeeds,
                                    neighbors, currentObject, indice)
                indice = -1
            # Remueve el elemento ya revisado
            if currentObject in OrderSeeds:
                OrderSeeds.remove(currentObject)
            # Se pasa al siguiente elemento de la lista OrderSeeds
            indice += 1

    return listadoTuplas


###########################################################################
# Clase creadora de SetOfObjects
# La clase creadora de una Instancia con un conjunto de instancias
class function_objects:
    # Inicialisacion de la clase
    def __init__(self, listadoTuplas=[(), (), ()]):
        # Se hace propia el listado de las tuplas
        self.listadoTuplas = listadoTuplas
        # En esta lista se meteran las mismas tuplas,
        # pero transformadas en instancias
        self.listadoInstancias = [Object(tupla[0], tupla[1])
                                  for tupla in self.listadoTuplas]

    # En esta funcion se genera un listado de las instancias
    # vecinas a la instancia "Object"
    def neighbors(self, Object, epsi):
        # Cero sera el vecino mas cercano en cuanto a distancia
        vecinosDesordenados = []
        # Recorre el listado de instancias de puntos evaluados
        for instancia in self.listadoInstancias:
            # Para que el objeto no se compare consigo mismo
            if not (instancia == Object):
                # Calculo de la distancia entre los puntos
                distancia = func_distance([instancia.latitud,
                                           instancia.longitud],
                                          [Object.latitud,
                                           Object.longitud])
                # Si la distancia con el punto en vista es menor a epsi
                if distancia <= epsi:
                    # Se le agrega un atributo a la instancia
                    instancia.distancia = distancia
                    # Se agrega la instancia evaluada al listado de instancias.
                    # TODAVIA NO ESTAN ORDENADOS
                    vecinosDesordenados.append(instancia)
        # Ordenamiento del listado de instancias en base a la distancia
        vecinosOrdenados = sorted(
            vecinosDesordenados, key=operator.attrgetter('distancia'))

        # Se debuelve el listado de vecinos
        return vecinosOrdenados


###########################################################################
# Clase creadora de instancias Objects
class Object:
    # Se entregan los parametros que crean un objeto
    def __init__(self, latitud, longitud,
                 metadata=None):

        self.latitud = latitud
        self.longitud = longitud
        self.metadata = metadata
        self.distancia = 0
        self.Processed = False
        self.reachability_distance = 1000000
        self.core_distance = 1000000

    # Funcion que calcula la "core distance".
    # neighbors es el listado de instancias correspondientes a puntos
    # vecinos al principal.
    # neighbors VIENE ORDENADO POR DISTANCIAS,
    # EL CERO ES EL VECINO MAS CERCANO.
    def setCoreDistance(self, neighbors, epsi, MinPts):
        # Si hay puntos suficientes, donde al igual que TI-DBScan y DBScan el
        # punto en analisis es un punto mas.
        if (len(neighbors) + 1 >= MinPts) and (not neighbors == []):

            cond = not ((MinPts - 2) < 0)
            vecino = neighbors[int(MinPts) - 2] if cond else neighbors[0]

            # Se calcula la distancia
            distancia = func_distance([vecino.latitud,
                                       vecino.longitud],
                                      [self.latitud,
                                       self.longitud])
            # Se calcula la core_distance, en metros
            self.core_distance = distancia


##################################################
# Algoritmo OPTICS
# SetOfObjects es una clase, que debe tener como atributo un
# listado de instancias, pero tambien los vecinos. epsi es un radio,
# y debe ser en metros. MinPts es un numero natural.
# Destino, corresponde a un directorio donde se escribe el archivo.
def optics(SetOfObjects, epsi, MinPts, metadata=None):
    SetOfObjects = function_objects(SetOfObjects)
    listadoTuplas = []
    # Recorre el conjunto de objetos
    for Object in SetOfObjects.listadoInstancias:
        # Si la instancia NO ha sido procesado
        if not Object.Processed:
            # Si no se ha revisado, lo revisa en profundidad
            listadoTuplas = ExpandClusterOrder(SetOfObjects,
                                               Object, epsi, MinPts,
                                               listadoTuplas)
            # Se continua con los vecinos del punto anterior
            neighbors = SetOfObjects.neighbors(Object, epsi)
            if not neighbors == []:
                for El_neighbor in neighbors:
                    if not El_neighbor.Processed:
                        listadoTuplas = ExpandClusterOrder(
                            SetOfObjects, El_neighbor, epsi, MinPts,
                            listadoTuplas)

    return listadoTuplas


#################################################
# La siguiente linea es para el testeo
if __name__ == "__main__":
    conjunto_de_puntos = [[1.00, 1.00], [1.50, 1.00], [2.00, 1.50],
                          [5.00, 5.00], [6.00, 5.50], [5.50, 6.00],
                          [10.00, 11.00], [10.50, 9.50], [10.00, 10.00],
                          [8.00, 1.00], [1.00, 8.00]]

    #conjunto_de_puntos = [[1.00, 1.00], [1.50, 1.00], [2.00, 1.50],
     #                     [5.00, 5.00], [6.00, 5.50], [5.50, 6.00],
      #                    [8.00, 1.00], [1.00, 8.00]]

    #conjunto_de_puntos = [[1.00, 1.00], [1.50, 1.00], [2.00, 1.50],
     #                     [5.00, 5.00], [8.00, 1.00], [1.00, 8.00]]

    resultado = optics(conjunto_de_puntos, 2, 2)

    for elemento in resultado:
        print elemento
        print ""
