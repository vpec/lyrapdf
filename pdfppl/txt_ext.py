from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter, PDFPageAggregator, XMLConverter, HTMLConverter
from pdfminer.layout import LAParams, LTTextBoxHorizontal
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfdevice import TagExtractor
from io import BytesIO as StringIO
#from io import StringIO
from pdfppl import pre_proc #, p2t_constants
import re
import time
from multiprocessing import Process, Manager

import PyPDF2

def countRotated(text):
    return len(re.findall(r'\w\n', text))

def process_without_detect_vertical(interpreter, retstr, page, return_dict):
    t_start = time.process_time()
    interpreter.process_page(page)
    t_elapsed = time.process_time() - t_start
    print("elapsed 2: ", t_elapsed)
    
    return_dict[0] = countRotated(retstr.getvalue().decode("utf-8")) + 1

    
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


    
def convert_pdf_to_txt(path, output_dir, file_name):
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
    _device = HTMLConverter(_rsrcmgr, _retstr, laparams=_laparams)
    _file = open(path, 'rb')

    _interpreter = PDFPageInterpreter(_rsrcmgr, _device)


    _password = '' # Set empty password as default value

    _pagenos=set()  # empty page set
    _rsrcmgr_default = PDFResourceManager()
    _retstr_default = StringIO()
    _laparams_default = LAParams() # detect_vertical=False
    _device_default = HTMLConverter(_rsrcmgr_default, _retstr_default, laparams=_laparams_default)
    _interpreter_default = PDFPageInterpreter(_rsrcmgr_default, _device_default)

    _text = b""

    check_rotated = False


    for number,page in enumerate(PDFPage.get_pages(_file, _pagenos ,password=_password, check_extractable=True)):

        print("Extracting page: ", number)
        #interpreter.process_page(page)

        rotating = False

        t_start = time.process_time()
        # Analyze with detect_vertical
        _interpreter.process_page(page)

        if(check_rotated):
            t_elapsed = time.process_time() - t_start
            print("elapsed 1: ", t_elapsed)
            print("countRotated", countRotated(_retstr.getvalue().decode("utf-8")))
            num_occ = countRotated(_retstr.getvalue().decode("utf-8")) + 1

            # Set timeout based on elapsed time using detect_vertical processing
            _timeout = 5 + t_elapsed * 10
            max_timeout = 60 # seconds
            _timeout = min(max_timeout, _timeout)
            #_timeout = 100000
            print("timeout: ", _timeout)

            # Create shared variable
            manager = Manager()
            return_dict = manager.dict()

            action_process = Process(target=process_without_detect_vertical, args=(_interpreter_default, _retstr_default, page, return_dict,))
            action_process.start()
            action_process.join(timeout=_timeout)
            
            # If thread is still active
            if action_process.is_alive():
                # Terminate
                action_process.terminate()
                action_process.join()
                print("Ran out of time")
                rotating = True
            else:
                # Get number of occurences
                num_occ_default = return_dict[0]
                print("num_occ_default", num_occ_default)
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
            
    
        # Append new text
        _text += _retstr.getvalue()
        
        
        # Clean buffers
        _retstr.truncate(0)
        _retstr.seek(0)
        _retstr_default.truncate(0)
        _retstr_default.seek(0)


    print("finishing")


    _text += b'\n\n'


    _file.close()
    _device.close()
    _retstr.close()
    return _text.decode("utf-8")
    

