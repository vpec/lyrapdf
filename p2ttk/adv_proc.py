
'''
Módulo encargado del etiquetado de la extracción de estructuras para
su posterior procesamiento.

Librerias necesarias:
  
        - PDF Miner six:                https://github.com/pdfminer/pdfminer.six
            - Documentación:            https://media.readthedocs.org/pdf/pdfminer-docs/latest/pdfminer-docs.pdf 
            Utilizada para transformar PDF a texto plano a través de la función convert_pdf_to_txt
            > pip install pdfminer.six

        - Smart Pipe Library:           https://pypi.org/project/sspipe/
            Utilizada para simular el funcionamiento de una pipe y simplificar el código escrito

        - Regular Expresions Python:    https://docs.python.org/2/library/re.html 
            Utilizada para el preprocesado del texto

        - StringIO:                     https://docs.python.org/2/library/stringio.html
            Utilizada para etiquetar ficheros, se encarga de etiquetar la salida de los mismos

        - Natural Languaje Tool Kit:    http://www.nltk.org/index.html
            Utilizada para tokenizar frases y creación de bigramas y trigramas.

'''
from io import StringIO

# Simple Smart Pipe library
from sspipe import p

# RegEx library - Expresiones regulares
import re

# Natural lenguaje Tool Kit
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.util import ngrams
from collections import Counter
from unicodedata import normalize
def extraer_bigramas(text):
    print(text)
    # Se eliminan las Stop Words
    stopWords = set(stopwords.words('spanish'))
    texto_filtrado = []  


    # Tokenizar 
    texto_tokenizado = word_tokenize(text)
    for w in texto_tokenizado:
        if w.lower() not in stopWords:
            texto_filtrado.append(w)

    # Generar Bigramas y Trigramas
    bigramas = ngrams(texto_filtrado,2)
    trigramas = ngrams(texto_filtrado,3)

    # Se genera una lista de tuplas
    lista_bigramas= [' '.join(grams) for grams in bigramas]
    counter_bigramas = Counter(lista_bigramas)
  
    lista_trigramas= [' '.join(grams) for grams in trigramas]
    counter_trigramas = Counter(lista_trigramas)
  
    print("Inicio del conteo de Bigramas")
                                            # Muestra el parrafo
    for numero, tupla in enumerate(sorted(counter_bigramas.items(), key=lambda x: x[1], reverse=True)):
        if numero <= 100:
            fichero_text_append('ficheros_salida/salida_ConteoBigramas.txt', "Bigrama: |||| "+ tupla[0] +" |||| numero de veces:" +str(tupla[1])+'\n')   


    for numero, tupla in enumerate(sorted(counter_trigramas.items(), key=lambda x: x[1], reverse=True)):
        if numero <= 100:
            fichero_text_append('ficheros_salida/salida_ConteoTrigramas.txt', "Trigrama: |||| "+ tupla[0] +" |||| numero de veces:" +str(tupla[1])+'\n')    
   
    return True

