import tabula

# readinf the PDF file that contain Table Data
# you can find find the pdf file with complete code in below
# read_pdf will save the pdf table into Pandas Dataframe

def extract(path):
    df = tabula.read_pdf(path, pages='45')
    # in order to print first 5 lines of Table
    df.head()