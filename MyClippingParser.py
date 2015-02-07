#!/usr/bin/python2.7

"""
########################################################################################################################
# MODIFICACIONES
########################################################################################################################
Tue 25 Jun 2013 11:44:49 AM CLT 
1) Se le da fecha a los nombres
2) Se modifica la generacion de archivos
"""

########################################################################################################################
# LIBRERIAS
########################################################################################################################
# Se importa la libreria que permite tratamiento de fechas
from datetime import datetime


########################################################################################################################
# FUNCION QUE LEE EL ARCHIVO
########################################################################################################################
# funcion que lee un archivo y pone cada LINEA DEL ARCHIVO en una 'lista' de python. Cada elemento de la 'lista' es a su vez otra 'lista' con las PALABRAS de cada linea del archivo original
def leer(ubicacion):
	# Abre el archivo
	try:
		f = open(ubicacion, 'r')
	except IOError:
		print("Falta copiar el archivo en el directorio")

	# Lee 'la' linea
	linea = f.readline()
	# La guarda en la lista, posicion 0
	lineaS = [linea]
	# Se lee el resto de las lineas
	while 1:
		linea=f.readline()
		if not linea: break
		lineaS.append(linea)
	f.close()	
	
	return lineaS

########################################################################################################################
# FUNCION QUE ARMA EL DICCIONARIO
########################################################################################################################
def diccionario_libro(documento,separador):

	# Variables auxiliares
	libro = []

	# Diccionario libros
	diccionario_libros = {}
	trozo_documento = []

	# Se leen linea por linea hasta que toca una con "=========="
	for linea in documento:
		# Si no hay un separador		
		if not linea == separador:
			# Agrega la linea
			trozo_documento.append(linea)

		# Si HAY un separador			
		else:
			# Agrega el conjunto de lineas a una parte del diccionario
			diccionario_libros.setdefault(trozo_documento[0],[])
			diccionario_libros[trozo_documento[0]].extend(trozo_documento[1:])
			diccionario_libros[trozo_documento[0]].append('######################################################################'+'\n'+'\n')
			# Vacia el pedazo que se leyo
			trozo_documento = []

	return diccionario_libros


########################################################################################################################
# FUNCION ESCRIBIR ARCHIVO
########################################################################################################################

def escribir(camino,nombreArchivo,modo):
	# Se crea la instancia que lo hace
	try:
		Escribir = open( camino+nombreArchivo, modo)
	# Si hay algun Slash o caracter raro, este se debe sacar
	except IOError:
		nombreArchivo = nombreArchivo.replace("/","-")
		nombreArchivo = nombreArchivo.replace("\\","-")
		Escribir = open( camino+nombreArchivo, modo)

	return Escribir

########################################################################################################################
# EL CODIGO
########################################################################################################################

# Se lee el documento completo
camino = '/home/bernardo/Documents/MyClippings/'
nombre_documento = 'My Clippings.txt'
documento = leer(camino+nombre_documento)

# Se crea el diccionario_libros
# '==========\r\n'
# '==========\n'
diccionario_libro = diccionario_libro(documento,'==========\r\n')

# La fecha
now=datetime.now()

# Ve iterando por cada documento leido
for titulo in diccionario_libro.keys():

	# Nombre del archivo
	# Notese que es "-4" debido a que estoy sacando el "\r\n" al final de los titulos
	nombreArchivo = titulo[:-2]+'.txt'

	Escribir = escribir(camino,nombreArchivo,'a')

	# Se escribe linea por linea el diccionario	
	for linea in diccionario_libro[titulo]:
		Escribir.write(linea)

	Escribir.close()



