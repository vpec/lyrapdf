from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument, PDFNoOutlines



def get_outlines_pdfminer(path):

    _file = open(path, 'rb')

    parser = PDFParser(_file)
    document = PDFDocument(parser, "")
    try:
        outlines = document.get_outlines()

        for(level, title, dest, a, se) in outlines:
            print (level, title)
    except PDFNoOutlines:
        print("No outlines")