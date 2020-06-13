from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument

from PyPDF2 import PdfFileReader

def get_metadata_pdfminer(path):
    _file = open(path, 'rb')
    parser = PDFParser(_file)
    doc = PDFDocument(parser)
    print(doc.info)  # The "Info" metadata

def get_metadata_pypdf2(path):
    _file = open(path, 'rb')
    pdf = PdfFileReader(_file)
    info = pdf.getDocumentInfo()
    print(info)  # The "Info" metadata
