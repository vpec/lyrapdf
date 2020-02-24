import sys
from pdfppl import extractionPyPDF2 as e1

def run():
    if(len(sys.argv) == 2):
        e1.extract(sys.argv[1])
    else:
        print("Invalid number of arguments")
