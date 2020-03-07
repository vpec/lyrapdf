from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO
from pdfppl import pre_proc #, p2t_constants
import re

def countRotated(text):
    return len(re.findall('\w\n\w', text))


def convert_pdf_to_txt(path, output_dir, file_name, generate_output = True):
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
    _laparams = LAParams(detect_vertical=True)
    #  _device = TextConverter(_rsrcmgr, _retstr, codec=_codec,laparams=_laparams)
    _device = TextConverter(_rsrcmgr, _retstr, laparams=_laparams)
    _file = open(path, 'rb')
    _interpreter = PDFPageInterpreter(_rsrcmgr, _device)
    #pagina = 31           
    _password = ""           # Cambiar en caso de PDF con pass
    # maxpages = pagina       # Máximas páginas a recorrer
    # añadir al for for numero,page in enumerate(PDFPage.get_pages(fp, pagenos, maxpages = maxpages password=password, check_extractable=True)

    _pagenos=set()           # Paginas a extraer separadas por comas
    #lista_paginas = []
    _rsrcmgr_default = PDFResourceManager()
    _retstr_default = StringIO()
    _laparams_default = LAParams() # detect_vertical=False
    _device_default = TextConverter(_rsrcmgr_default, _retstr_default, laparams=_laparams_default)
    _interpreter_default = PDFPageInterpreter(_rsrcmgr_default, _device_default)

    _text = ""


    for number,page in enumerate(PDFPage.get_pages(_file, _pagenos ,password=_password, check_extractable=True)):
        # Descomentar la parte de abajo si se desea una página en concreto
        # añadir "numero al retorno del for"
        # for numero,page in enumerate(PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password, check_extractable=True)
        print("Extracting page: ", number)
        #interpreter.process_page(page)

        # Analyze with detect_vertical
        _interpreter.process_page(page)
        
        print(countRotated(_retstr.getvalue()))
        num_occ = countRotated(_retstr.getvalue()) + 1

        # Analyze without detect_vertical
        _interpreter_default.process_page(page)
        print(countRotated(_retstr_default.getvalue()))
        
        num_occ_default = countRotated(_retstr_default.getvalue()) + 1

        

        if(num_occ_default / num_occ > 5 and num_occ_default > 70):
            print("Rotated")
            # Clean buffer
            _retstr.truncate(0)
            _retstr.seek(0)
            # Rotate page
            page.rotate = (page.rotate+180) % 360
            # Analyze again with detect_vertical
            _interpreter.process_page(page)

        # Append new text
        _text += _retstr.getvalue()
        
        # Clean buffers
        _retstr.truncate(0)
        _retstr.seek(0)
        _retstr_default.truncate(0)
        _retstr_default.seek(0)

        
        '''
            interpreter.process_page(page)
            # Se extrae la pagina y la añadimos a la lista
            lista_paginas.append(retstr.getvalue()+ '\n\n')
            Preprocesado.fichero_text_append('ficheros_salida/salida_ExtraccionTexto.txt',retstr.getvalue())
            # Limpiamos el buffer para la siguiente iteracion
            retstr.truncate(0)
            retstr.seek(0)
        '''

    print("finishing")

    #  _text = _retstr.getvalue() + '\n\n'
    _text += '\n\n'
    if (generate_output) :
        pre_proc.create_text_file(output_dir + "/simple_" + file_name + ".txt", _text) # Insertamos en el fichero el texto extraido

    _file.close()
    _device.close()
    _retstr.close()
    return _text

