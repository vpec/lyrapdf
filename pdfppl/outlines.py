# pdfminer imports
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument, PDFNoOutlines
# PyPDF2 imports
from PyPDF2 import PdfFileReader




def get_outlines_pypdf2(path):
    _file = open(path, 'rb')
    reader = PdfFileReader(_file)
    print(reader.outlines)


    

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