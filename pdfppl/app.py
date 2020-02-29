import sys
from pdfppl import extractionPyPDF2 as e1
from pdfppl import extractionTabula as e2
from os.path import isfile, join, exists, abspath
from os import listdir, makedirs
from pdfppl import txt_ext


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
            
            #  etiquetado.set_path(archivos[i])
            #  etiquetado.set_document(archivos[i].split(".")[0])
            
            print(input_dir + "/output")
            texto_extraido = txt_ext.convert_pdf_to_txt(pdf_path, input_dir + "/output")
            # nombre_archivo = archivos[i]
            
            print("Extracción de : "+ pdf_path + " terminada, iniciando procesado")
            texto_procesado = (      primer_procesado(texto_extraido) | p(segundo_procesado) 
                                )
            texto_total = texto_total + texto_procesado + '\n\n'
            
            i+=1
            
        # mostrar_estadisticas()
        # return texto_total




    else:
        print("Invalid number of arguments")
