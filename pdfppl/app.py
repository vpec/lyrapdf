import sys
from pdfppl import extractionPyPDF2 as e1
from pdfppl import extractionTabula as e2
from os.path import isfile, join, exists, abspath
from os import listdir, makedirs
from pdfppl import txt_ext
from sspipe import p
from pdfppl import pre_proc
from pdfppl import outlines
from pdfppl import metadata
import ntpath


def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

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

def primer_procesado(text, output_dir, file_name):
    '''
        - Elimina dashes(guiones de texto) y caracteres raros en el texto
        - Espacios en blanco dobles
        - Saltos de linea en palabras inacabadas y lineas del mismo parrafo
          elimina carácteres no identificados 


        :param text:    String a realizar el procesado
        :return:        String con el tratamiento del texto y saca un fichero "salida_primer_procesado" en
                        "ficheros_entrada"
    '''
    
    texto_procesado = ( pre_proc.delete_0C(text)            | p(pre_proc.delete_false_headers)
                                                                | p(pre_proc.label_lists)
                                                                | p(pre_proc.delete_dash)
                                                                | p(pre_proc.delete_tabs)
                                                                | p(pre_proc.delete_whitespaces)
                                                                | p(pre_proc.delete_jumps)
                                                                | p(pre_proc.label_ordered_lists)
                                                                | p(pre_proc.process_lists)
                                                                | p(pre_proc.label_headers)
                                                                | p(pre_proc.relabel_ol)
                                                                | p(pre_proc.fit_titles)
                       )
    
                                                
    pre_proc.create_text_file(output_dir + "/" + file_name + ".txt", texto_procesado)
    return texto_procesado+'\n'  

def get_listPDF(input_dir):
    '''
    :return: Returns list of file paths inside input_dir
    '''

    path_archivos = [input_dir +'/' + f for f in listdir(input_dir) if isfile(join(input_dir, f)) ]
    archivos = [f for f in listdir(input_dir) if isfile(join(input_dir, f)) ]

    return path_archivos,archivos

def run():
    if(len(sys.argv) == 2):
        # e1.extract(sys.argv[1])
        # e2.extract(sys.argv[1])
        input_dir = abspath(sys.argv[1]) # Directory where are stored pdfs to be processed
        # etiquetado = ParLabel(dir_entrada, "GPC_465_Insomnio_Lain_Entr_compl.pdf")

        pdf_list, archivos = get_listPDF(input_dir)
        #p2ttk.pre_proc.fichero_text('ficheros_salida/salida_primer_procesado.txt','')
        texto_extraido = ''
        texto_total = ''
        i = 0
        output_dir = input_dir + "/output"
        if not exists(output_dir):
            makedirs(output_dir)

        for pdf_path in pdf_list:
            print('Extracting text from: ', pdf_path)

            #e2.extract(pdf_path, input_dir + "/output", path_leaf(pdf_path))
            
            
            #  etiquetado.set_path(archivos[i])
            #  etiquetado.set_document(archivos[i].split(".")[0])
            
            # metadata.get_metadata_pypdf2(pdf_path)
            #txt_ext.convert_pdf_to_txt_pypdf2(pdf_path, input_dir + "/output", path_leaf(pdf_path))
            
            
            outlines.get_outlines_pypdf2(pdf_path)

            
            '''
            print(input_dir + "/output")
            texto_extraido = txt_ext.convert_pdf_to_txt(pdf_path, input_dir + "/output", path_leaf(pdf_path))
            # nombre_archivo = archivos[i]
            
            print("Extracción de : "+ pdf_path + " terminada, iniciando procesado")
            #texto_procesado = primer_procesado(texto_extraido, input_dir + "/output", path_leaf(pdf_path))
            
            #texto_procesado = (      primer_procesado(texto_extraido) | p(segundo_procesado) 
            #                    )
            
            #texto_total = texto_total + texto_procesado + '\n\n'
            
            i+=1
            '''
            
            
            
            
            
        # mostrar_estadisticas()
        # return texto_total




    else:
        print("Invalid number of arguments")
