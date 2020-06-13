from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument, PDFNoOutlines 

def get_outlines_pdfminer(path):
    """Returns outlines if PDFMiner can extract them,
        None otherwise.

    Args:
        path (string): path where pdf is stored.

    Returns:
        [(level, title, dest, a, se)]: list of tuples. None
            if no outlines are detected.
    """


    _file = open(path, 'rb')
    _password = b'' # Set empty password as default value

    parser = PDFParser(_file)
    document = PDFDocument(parser, _password)
    try:
        outlines = document.get_outlines()
        return outlines

        for(level, title, dest, a, se) in outlines:
            print (level, title)
    except PDFNoOutlines:
        print("No outlines")
        return None