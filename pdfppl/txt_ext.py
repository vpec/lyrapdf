from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import HTMLConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import BytesIO
import re
import time
from multiprocessing import Process, Manager

import PyPDF2

def countRotated(text):
    """Counts the number of ocurrences of '\w\n' in text.

    Args:
        text (string): text that is going to be processed.

    Returns:
        int: number of ocurrences
    """
    return len(re.findall(r'\w\n', text))

def process_without_detect_vertical(interpreter, retstr, page, return_dict):
    """Processes page and return in shared variable the number of 
        countRotated ocurrences.

    Args:
        interpreter (PDFPageInterpreter): PDFPageInterpreter object.
        retstr (BytesIO): BytesIO object.
        page (PDFPage): PDFPage object.
        return_dict (Manager.dict()): Manager.dict() object.
    """
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

    _file.close()
    return _text

    
def extract_pdf_to_html(path, check_rotated = False):
    """Extracts text from PDF document to HTML format.
        When check_rotated is True, pages are processed a second time
        to ensure they are in the correct orientation. If not, the page
        is rotated 90 degrees clockwise and processed again. This may slow
        down the whole process more than a 100%.

    Args:
        path (string): path where pdf file is stored
        check_rotated (bool, optional): check rotated pages. Defaults to False.

    Returns:
        string: document in html format
    """
    # Declare PDFMiner variables for extraction (with detect_vertical ON)
    _rsrcmgr = PDFResourceManager()
    _retstr = BytesIO()
    _codec = 'utf-8'
    _laparams = LAParams(detect_vertical=True)
    _device = HTMLConverter(_rsrcmgr, _retstr, laparams=_laparams)
    _file = open(path, 'rb')
    _interpreter = PDFPageInterpreter(_rsrcmgr, _device)

    _password = '' # Set empty password as default value
    _pagenos=set()  # empty page set

    # Declare PDFMiner variables for extraction  (with detect_vertical OFF)
    _rsrcmgr_default = PDFResourceManager()
    _retstr_default = BytesIO()
    _laparams_default = LAParams() # detect_vertical=False
    _device_default = HTMLConverter(_rsrcmgr_default, _retstr_default, laparams=_laparams_default)
    _interpreter_default = PDFPageInterpreter(_rsrcmgr_default, _device_default)

    # Variable where text is going to be stored
    _text = b""

    # Iterate through PDF document pages
    for number,page in enumerate(PDFPage.get_pages(_file, _pagenos ,password=_password, check_extractable=True)):
        print("Extracting page: ", number)

        rotating = False

        # If checking page rotation
        if(check_rotated):
            # Start to measure time
            t_start = time.process_time()

        # Analyze with detect_vertical
        _interpreter.process_page(page)

        # If checking page rotation
        if(check_rotated):
            # Elapsed time
            t_elapsed = time.process_time() - t_start
            print("elapsed 1: ", t_elapsed)
            print("countRotated", countRotated(_retstr.getvalue().decode("utf-8")))
            # Number of ocurrences of "rotated characters"
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

            # Re-execute page interpreter in another thread
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

    print("Extraction finished")
    _text += b'\n\n'

    # Close files
    _file.close()
    _device.close()
    _retstr.close()
    return _text.decode("utf-8")
    

