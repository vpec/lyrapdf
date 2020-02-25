import sys
from pdfppl import extractionPyPDF2 as e1
from pdfppl import extractionTabula as e2

def run():
    if(len(sys.argv) == 2):
        e1.extract(sys.argv[1])
        # e2.extract(sys.argv[1])
    else:
        print("Invalid number of arguments")
