import PyPDF2

def extract(path):
    print("Extracting ", path, " using PyPDF2")
    # pdf file object
    # you can find find the pdf file with complete code in below
    pdfFileObj = open(path, 'rb')# pdf reader object
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)# number of pages in pdf
    print(pdfReader.numPages)# a page object
    pageObj = pdfReader.getPage(15)# extracting text from page.
    # this will print the text you can also save that into String
    print(pageObj.extractText())