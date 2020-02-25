"""
Este módulo corresponde al programa principal del sistema. En él se hacen la diferentes llamadas para
el primer y segundo procesado de los textos que se asocian al mismo.
"""
from sspipe import p
import re
# Se importa la clase asociada al etiquetado
from p2ttk.par_label import *
from os import listdir
from os.path import isfile, join

# Se importan el resto de módulos del programa
import p2ttk.txt_ext,p2ttk.pre_proc,p2ttk.par_proc


dir_entrada = 'ficheros_entrada'         # Directorio a extraer archivos PDF
PDF_path_actual  = ''                    # Path del archivo a procesar   
etiquetado = ParLabel(dir_entrada)

def mostrar_estadisticas():
    '''
        :return:    Muestra por pantalla los 20 mayores párrafos con su respectivo tamaño
    '''
    p2ttk.pre_proc.fichero_text('ficheros_salida/conteopalabras.txt','')
    parrafos = p2ttk.par_proc.get_paragraph()
    for numero,parrafo in enumerate(parrafos) :
            if numero > -1:
                parrafo_proc = "////////////////\nEste parrafo contiene: " + str(Procesado_parrafos.contar_palabras(parrafo)) + " palabras\n"+ parrafo +"\n////////////////\n"       # Muestra el tamaño
                p2ttk.pre_proc.fichero_text_append('ficheros_salida/conteopalabras.txt', parrafo_proc)                                            # Muestra el parrafo

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

    texto_procesado = (p2ttk.par_proc.extraccion_parrafos(text,etiquetado) | p(p2ttk.par_proc.detectar_headers))
    p2ttk.pre_proc.fichero_text('ficheros_salida/salida_segundo_procesado.txt',texto_procesado)  
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
  
    texto_procesado = ( p2ttk.pre_proc.delete_0C(text)            | p(p2ttk.pre_proc.delete_false_headers)
                                                                | p(p2ttk.pre_proc.etiquetar_listas)
                                                                | p(p2ttk.pre_proc.delete_dash)
                                                                | p(p2ttk.pre_proc.delete_tabs)
                                                                | p(p2ttk.pre_proc.delete_whitespaces)
                                                                | p(p2ttk.pre_proc.delete_jumps)
                                                                | p(p2ttk.pre_proc.etiquetar_listasOrdenadas)
                                                                | p(p2ttk.pre_proc.procesar_listas)
                                                                | p(p2ttk.pre_proc.etiquetar_headers)
                                                                | p(p2ttk.pre_proc.re_etiquetar_ol)
                                                                | p(p2ttk.pre_proc.ajustar_titulos)
                       )
                                                
    p2ttk.pre_proc.fichero_text_append('ficheros_salida/salida_primer_procesado.txt',texto_procesado)
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
    p2ttk.pre_proc.fichero_text('ficheros_salida/salida_primer_procesado.txt','')
    texto_extraido = ''
    texto_total = ''
    i = 0

    for PDF_path_actual in lista:
        print('Extrayendo texto de este fichero: ',archivos[i])
        etiquetado.set_path(archivos[i])
        etiquetado.set_document(archivos[i].split(".")[0])
        
        texto_extraido = p2ttk.txt_ext.convert_pdf_to_txt(PDF_path_actual)
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


