from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter, PDFPageAggregator, XMLConverter, HTMLConverter
from pdfminer.layout import LAParams, LTTextBoxHorizontal
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfdevice import TagExtractor
from io import StringIO
from pdfppl import pre_proc #, p2t_constants
import re
import time
from multiprocessing import Process, Manager

import PyPDF2




def countRotated(text):
    return len(re.findall('\w\n\w', text))

def process_without_detect_vertical(interpreter, retstr, page, return_dict):
    interpreter.process_page(page)
    return_dict[0] = countRotated(retstr.getvalue()) + 1

def convert_pdf_to_txt_pypdf2(path, output_dir, file_name, generate_output = True):
    _file = open(path, 'rb')
    read_pdf = PyPDF2.PdfFileReader(_file)
    number_of_pages = read_pdf.getNumPages()

    _text = ""
    
    for page_num in range(read_pdf.numPages):
        print("Extracting page: ", page_num)
        try:
            page = read_pdf.getPage(page_num)
            _text += page.extractText()
        except:
            pass

    if (generate_output) :
        pre_proc.create_text_file(output_dir + "/pypdf2_raw_" + file_name + ".txt", _text) # Insertamos en el fichero el texto extraido

    _file.close()



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
    
    '''
    _aggregator = PDFPageAggregator(_rsrcmgr, laparams=_laparams)
    '''
    #_device_html = HTMLConverter(_rsrcmgr, _retstr, laparams=_laparams)
    '''
    _device_xml = XMLConverter(_rsrcmgr, _retstr, laparams=_laparams,
                              imagewriter=None,
                              stripcontrol=False)

    
    _device_tag = TagExtractor(_rsrcmgr, _retstr)
    '''

    _interpreter = PDFPageInterpreter(_rsrcmgr, _device)

    #_interpreter = PDFPageInterpreter(_rsrcmgr, _device_tag)
    #_interpreter = PDFPageInterpreter(_rsrcmgr, _device_html)
    #_interpreter = PDFPageInterpreter(_rsrcmgr, _device_xml)
    #_interpreter = PDFPageInterpreter(_rsrcmgr, _aggregator)

    


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

        rotating = False

        t_start = time.process_time()
        # Analyze with detect_vertical
        _interpreter.process_page(page)
        t_elapsed = time.process_time() - t_start
        print(t_elapsed)
        
        print(countRotated(_retstr.getvalue()))
        num_occ = countRotated(_retstr.getvalue()) + 1

        # Set timeout based on elapsed time using detect_vertical processing
        _timeout = 5 + t_elapsed * 10

        # Create shared variable
        manager = Manager()
        return_dict = manager.dict()

        #action_process = Process(target=_interpreter_default.process_page, args=(page,))
        action_process = Process(target=process_without_detect_vertical, args=(_interpreter_default, _retstr_default, page, return_dict,))
        action_process.start()
        action_process.join(timeout=_timeout)

        # If thread is still active
        if action_process.is_alive():
            # Terminate
            action_process.terminate()
            action_process.join()
            rotating = True
        else:
            # We start the process and we block for 5 seconds.
            print(countRotated(_retstr_default.getvalue()))
            # Get number of occurences
            num_occ_default = return_dict[0]
            # Check if page needs to be rotated
            if(num_occ_default / num_occ > 5 and num_occ_default > 100):
                rotating = True

        if(rotating):
            print("Rotating")
            # Clean buffer
            _retstr.truncate(0)
            _retstr.seek(0)
            # Rotate page
            page.rotate = (page.rotate+90) % 360
            # Analyze again with detect_vertical
            _interpreter.process_page(page)

        '''
        layout = _aggregator.get_result()
        for element in layout:
            if(isinstance(element, LTTextBoxHorizontal)):
                print(element.get_text())
        '''

        # Append new text
        _text += _retstr.getvalue()
        
        # Clean buffers
        _retstr.truncate(0)
        _retstr.seek(0)
        _retstr_default.truncate(0)
        _retstr_default.seek(0)


    print("finishing")

    #  _text = _retstr.getvalue() + '\n\n'
    _text += '\n\n'
    if (generate_output) :
        pre_proc.create_text_file(output_dir + "/raw_" + file_name + ".txt", _text) # Insertamos en el fichero el texto extraido

    _file.close()
    _device.close()
    _retstr.close()
    return _text

