"""
Este módulo corresponde al programa principal del sistema. En él se hacen la diferentes llamadas para
el primer y segundo procesado de los textos que se asocian al mismo.
"""
from sspipe import p
import re
# Se importa la clase asociada al etiquetado
from Etiquetado_parrafos import *
from os import listdir
from os.path import isfile, join

# Se importan el resto de módulos del programa
import Extraccion_textos,Preprocesado,Procesado_parrafos


dir_entrada = 'ficheros_entrada'         # Directorio a extraer archivos PDF
PDF_path_actual  = ''                    # Path del archivo a procesar   
etiquetado = Etiquetado_parrafos(dir_entrada)

def mostrar_estadisticas():
    '''
        :return:    Muestra por pantalla los 20 mayores párrafos con su respectivo tamaño
    '''
    Preprocesado.fichero_text('ficheros_salida/conteopalabras.txt','')
    parrafos = Procesado_parrafos.get_paragraph()
    for numero,parrafo in enumerate(parrafos) :
            if numero > -1:
                parrafo_proc = "////////////////\nEste parrafo contiene: " + str(Procesado_parrafos.contar_palabras(parrafo)) + " palabras\n"+ parrafo +"\n////////////////\n"       # Muestra el tamaño
                Preprocesado.fichero_text_append('ficheros_salida/conteopalabras.txt', parrafo_proc)                                            # Muestra el parrafo

    return True

def segundo_procesado(text):
    '''
        Se encarga de la gestionar los parrafos, extraerlos y añadirles una cabecera y una cola
        para identificarlos teniendo la siguiente estructura:
        ..  note::
            Ejemplo de output del segundo procesado:

            <idParrafo><NombreDocumento>
            TEXTOTEXTOTEXTO
            <idParrafo><NombreDocumento\>
        :return:    Un string con todos los párrafos etiquetados y además saca la salida al fichero
                    "salida_segundo_procesado" en la carpeta "ficheros_salida"

    '''

    texto_procesado = (Procesado_parrafos.extraccion_parrafos(text,etiquetado) | p(Procesado_parrafos.detectar_headers))
    Preprocesado.fichero_text('ficheros_salida/salida_segundo_procesado.txt',texto_procesado)  
    return texto_procesado

def primer_procesado(text):
    '''
        - Elimina dashes(guiones de texto) y caracteres raros en el texto
        - Espacios en blanco dobles
        - Saltos de linea en palabras inacabadas y lineas del mismo parrafo
          elimina carácteres no identificados 


        :param text:    String a realizar el procesado
        :return:        String con el tratamiento del texto y saca un fichero "salida_primer_procesado" en
                        "ficheros_entrada"
    '''
  
    texto_procesado = ( Preprocesado.delete_0C(text)            | p(Preprocesado.delete_false_headers)
                                                                | p(Preprocesado.etiquetar_listas)
                                                                | p(Preprocesado.delete_dash)
                                                                | p(Preprocesado.delete_tabs)
                                                                | p(Preprocesado.delete_whitespaces)
                                                                | p(Preprocesado.delete_jumps)
                                                                | p(Preprocesado.etiquetar_listasOrdenadas)
                                                                | p(Preprocesado.procesar_listas)
                                                                | p(Preprocesado.etiquetar_headers)
                                                                | p(Preprocesado.re_etiquetar_ol)
                                                                | p(Preprocesado.ajustar_titulos)
                       )
                                                
    Preprocesado.fichero_text_append('ficheros_salida/salida_primer_procesado.txt',texto_procesado)
    return texto_procesado+'\n'  


def get_listPDF():
    '''
    :return: Obtiene la lista de archivos en un directorio
    '''

    path_archivos = [dir_entrada +'/' + f for f in listdir(dir_entrada) if isfile(join(dir_entrada, f)) ]
    archivos = [f for f in listdir(dir_entrada) if isfile(join(dir_entrada, f)) ]

    return path_archivos,archivos

def gestion_procesado():

    '''
    :return:    Devuelve el procesado de todos los ficheros localizados en la carpeta
                ficheros_entrada a través del uso de las funciones primer y segundo 
                procesado
    '''

    lista,archivos = get_listPDF()
    Preprocesado.fichero_text('ficheros_salida/salida_primer_procesado.txt','')
    texto_extraido = ''
    texto_total = ''
    i = 0

    for PDF_path_actual in lista:
        print('Extrayendo texto de este fichero: ',archivos[i])
        etiquetado.set_path(archivos[i])
        etiquetado.set_document(archivos[i].split(".")[0])
        
        texto_extraido = Extraccion_textos.convert_pdf_to_txt(PDF_path_actual)
        nombre_archivo = archivos[i]
        
        print("Extracción de : "+ archivos[i] + " terminada, iniciando procesado")
        texto_procesado = (      primer_procesado(texto_extraido) | p(segundo_procesado) 
                            )
        texto_total = texto_total + texto_procesado + '\n\n'
        
        i+=1
    mostrar_estadisticas()
    return texto_total


# ---------- MAIN -----------------------------------------------
# Extracción de texto y guardado del mismo

texto_procesado = gestion_procesado()


