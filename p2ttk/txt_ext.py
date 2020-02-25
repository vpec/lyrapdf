from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO
from p2ttk import pre_proc, p2t_constants

def convert_pdf_to_txt(path, generate_output):
    """ 
        PDFMiner:                       https://pypi.org/project/pdfminer/ 
            - Documentación:            https://media.readthedocs.org/pdf/pdfminer-docs/latest/pdfminer-docs.pdf 
        :param path:    String que indica el path hacia el archivo
        :return:        Extrae el texto contenido en un PDF a través del uso de
                        PDFMiner y saca lo extraído al fichero salida_ExtraccionTexto
        """
    _rsrcmgr = PDFResourceManager()
    _retstr = StringIO()
    _codec = 'utf-8'
    _laparams = LAParams()
    _device = TextConverter(_rsrcmgr, _retstr, codec=_codec,laparams=_laparams)
    _file = open(path, 'rb')
    _interpreter = PDFPageInterpreter(_rsrcmgr, _device)
    #pagina = 31           
    _password = ""           # Cambiar en caso de PDF con pass
    # maxpages = pagina       # Máximas páginas a recorrer
    # añadir al for for numero,page in enumerate(PDFPage.get_pages(fp, pagenos, maxpages = maxpages password=password, check_extractable=True)

    _pagenos=set()           # Paginas a extraer separadas por comas
    #lista_paginas = []

    pre_proc.create_text_file(p2t_constants.OUTPUT_DIR + '/salida_ExtraccionTexto.txt','') # Vaciamos el fichero

    for numero,page in enumerate(PDFPage.get_pages(_file, _pagenos ,password=_password, check_extractable=True)):
        # Descomentar la parte de abajo si se desea una página en concreto
        # añadir "numero al retorno del for"
        # for numero,page in enumerate(PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password, check_extractable=True)
        print("Extracting page: ", numero)
        #interpreter.process_page(page)
        _interpreter.process_page(page)
        
        '''
            interpreter.process_page(page)
            # Se extrae la pagina y la añadimos a la lista
            lista_paginas.append(retstr.getvalue()+ '\n\n')
            Preprocesado.fichero_text_append('ficheros_salida/salida_ExtraccionTexto.txt',retstr.getvalue())
            # Limpiamos el buffer para la siguiente iteracion
            retstr.truncate(0)
            retstr.seek(0)
        '''

    _text = _retstr.getvalue() + '\n\n'
    if (generate_output) :
        pre_proc.create_text_file(p2t_constants.OUTPUT_DIR + '/salida_ExtraccionTexto.txt', _text) # Insertamos en el fichero el texto extraido

    _file.close()
    _device.close()
    _retstr.close()
    return _text

