import tabula

# readinf the PDF file that contain Table Data
# you can find find the pdf file with complete code in below
# read_pdf will save the pdf table into Pandas Dataframe

def extract(path, output_dir, file_name):
    #df = tabula.read_pdf(path, pages='all')
    # convert PDF into CSV file
    tabula.convert_into(path, output_dir + "/table" + file_name + ".csv", output_format="csv", pages='all')
    # in order to print first 5 lines of Table
    #df.head()