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
from os.path import exists
from os import mknod
import json
import matplotlib.pylab as plt
from scipy.stats import norm
import numpy as np
import seaborn as sns
from sklearn.cluster import KMeans
from pdfppl.ckmeans import ckmeans

#    fichero_text_append('ficheros_salida/salida_ConteoBigramas.txt', "Fin del top 100 ---") 
def append_text_file(path,text):
    '''
        :param path:    String no vacio relativo a la ruta donde se generará el output
        :param text:    String a guardar en el fichero
        :return:        Añade al final del archivo en la ruta "path" el string "text"
    '''

    file = open(path,'a+')
    file.write(text)
    file.close()
    return 1



def create_json_file(path,text):
    '''
        :param path:    String no vacio relativo a la ruta donde se generará el output
        :param text:    String a guardar en el fichero
        :return:        Genera un fichero de texto en el directorio path cuyo contenido
                         es text
    '''
    file = open(path,'wb+')
    file.write(text)
    file.close()
    return 1


def create_text_file(path,text):
    '''
        :param path:    String no vacio relativo a la ruta donde se generará el output
        :param text:    String a guardar en el fichero
        :return:        Genera un fichero de texto en el directorio path cuyo contenido
                         es text
    '''
    file = open(path,'w+')
    file.write(text)
    file.close()
    return 1






def delete_jumps(text):
    '''
        :param text:        String a procesar.
        :return:            A través de una expresión regular eliminar los saltos de línea
                            la letra final seguida de un salto de linea y 
                            comenzando por otra letra minúscula.     
    '''
    p1 = re.compile(r'((\w|, |\)) *)\n+([a-z]|\(|\¿|\")', re.MULTILINE | re.DOTALL |re.UNICODE)
    text2 = p1.sub(r'\1\3',text)
    return text2






def delete_whitespaces(text):
    '''
        :param text:            String a procesar.
        :return:               	Identifica dos espacios (carácter 32 en ASCII) y
        						sustituyéndolos por uno solo. 
    '''
    p1 = re.compile(r' {2,}',re.UNICODE)
    text2 = p1.sub(r' ',text)
    return text2






def label_ordered_lists(text):
    '''
    ..  note:: 
        Ejemplo de listas ordenadas: 	
            - 1. Texto1
            - 2. Texto2
            - 3. Texto3

    :param text:	String a procesar
    :return:        Identifica un número seguido de punto y el texto consiguiente.
                    Tras ello, busca que exista otra estructura similar en la siguiente
                    línea.
    '''
    p1 = re.compile(r'( *[0-9]+\. .+\n( *[0-9]+\. .+\n)+)\n+(\w)',re.UNICODE)
    text2 = p1.sub(r'<ol>\n\1<\\ol>\n\3',text)

    return text2
 





def label_h1(text):
    '''
    .. note::
	    Título:
		    - 1.		Título de primer nivel
		    - 1.1.	    Título de segundo nivel
		    - 1.1.1.	Título de tercer nivel

    :param text:	String a procesar
    :return:       	Identifica una estructura de título. Tras ello, etiqueta el apartado con
                las etiquetas <h1..n> Título1 <\h1..n>
    '''
    p1 = re.compile(r'(\n[0-9]\. .+\n)', re.MULTILINE|re.UNICODE) 
    text2 = p1.sub(r'\n\n<h1>\1<\\h1>\n\n',text)

    return text2




def label_h2(text):
    p1 = re.compile(r'(\n *[0-9]\.[0-9]\. .+\n)',re.MULTILINE|re.UNICODE) 
    text2 = p1.sub(r'\n\n<h2>\1<\\h2>\n\n',text)

    return text2




def label_h3(text):
    p1 = re.compile(r'(\n *[0-9]\.[0-9]\.[0-9]\. .+\n)',re.MULTILINE|re.UNICODE) 
    text2 = p1.sub(r'\n\n<h3>\1<\\h3>\n\n',text)

    return text2




def label_h4(text):
    p1 = re.compile(r'(\n *[0-9]\.[0-9]\.[0-9]\.[0-9]\. .+\n)',re.MULTILINE|re.UNICODE) 
    text2 = p1.sub(r'\n\n<h4>\1<\\h4>\n\n',text)

    return text2



def label_headers(text):
    ''' 
  	    :return: etiqueta todos los niveles de títulos
    '''
    texto_procesado = ( label_h1(text)      | p(label_h2)
                                            | p(label_h3)
                                            | p(label_h4)
    )
    return texto_procesado





def fit_titles(text):
    '''
        :param text:        String a procesar
        :return:            Ajusta títulos
    '''
    p1 = re.compile(r'([^<li>]+) *\n{2,}(<li>.+\n+)',re.UNICODE) 
    text2 = p1.sub(r'\1\n\2',text)

    return text2





def delete_dash(text):
    '''
        :param text:        String a procesar
        :return:            Identifica un los guiones al final de una palabra en línea y lo une 
                            a su continuación de la línea siguiente
    '''
    

    texto = text.replace(chr(10),"<line>")
    p1 = re.compile(r'([a-záéíóú])-(<line>)+(\d+)(<line>)+([a-záéíóú]*)') 
    text2 = p1.sub(r'\1\5 <page n=\3> ',texto)
    p = re.compile(r'([a-z])-(<line>)+([a-z])', re.UNICODE)
    text3 = p.sub(r'\1\3',text2)

        
    text4 = re.sub(r'([a-záéíóú])-(<line>)+([a-záéíó])',r'\1\3',text3,re.UNICODE)
    p = re.compile(r'(<line> *([0-9]*\.)+ *[^<]+)', re.UNICODE)
    text5 = p.sub(r'\n\1',text4)
  
    text6 = text5.replace("<line><line>", chr(10)+chr(10))

    text7 = text6.replace("<line><li>", chr(10)+"<li>")
    text8 = text7.replace("<line>", " ")
    return text8





def delete_false_headers(text):
    '''
        :return:    Elimina caracteres equívocos en headers del texto
    '''
    return text.replace(chr(61602),'\n')





def delete_0C(text):
    '''
        :return:    Elimina el ASCII 0C situado en al final de página para evitar errores
    '''
    texto = text.replace(chr(12),'')
    texto = texto.replace(chr(169),'')
    texto = texto.replace(chr(10),'\n')

    return texto





def delete_CID(text):
    '''
        :return:    Sustituye símbolos no identificados en etiquetado en listas no ordenadas
                    por su etiqueta correspondiente "<li>" además gestiona letras incorrectamente
                    extraidas por la etiqueta de formato CID
    '''
    p1 = re.compile(r'(\(cid:114\) *)') 
    text2 = p1.sub(r'<li>',text)
    p2 = re.compile(r'(\(cid:([0-9]+)\) *)', re.MULTILINE | re.DOTALL |re.UNICODE)
    text3 = p2.sub(lambda m: chr(int(m.group(2))+31),text2)

    # Gestion incorrecta de letras
    text3.replace(chr(229),"a")   
    text3.replace(chr(245),"o") 
    text3.replace(chr(10),"o") 
    text3.replace(chr(245),"o") 
    text3.replace(chr(240),"o") 
    text3.replace(chr(251),"u") 
     
    return text3





def correct_labeling(text):
    '''
    ..note::
        - Inicial:
            <li>
                texto de ejemplo
        - Final:
            <li> texto de ejemplo
    :return:    Corrige una etiqueta <li>\n seguida del texto
    '''
    p2 = re.compile(r'(<li>\s* *.*)\n{1,2}([a-z])', re.MULTILINE | re.DOTALL |re.UNICODE)
    text2 = p2.sub(r'\1 \2',text)
 
    return text2





def delete_listCHR(text):
    
    '''
    .. note::
        Ejemplo de texto ordenado con el carácter 1F
            - Texto1
            - Texto2
            - Texto3
    :return:     Elimina los caracteres propios de la inclusión de viñetas
                a la hora de ordenar texto:       
    '''
    texto = text.replace(chr(31),"<li>")
    texto = texto.replace(chr(61613),"<li>")
    texto = texto.replace(chr(61550),"<li>")
    texto = texto.replace(chr(8226),"<li>")
    texto = texto.replace(chr(8212),"<li>")
    texto = texto.replace(chr(61623),"<li>")
    texto = texto.replace(chr(61680),"<li>")

    return texto





def delete_emptyListCHR(text):
    '''
    :return:    Elimina los caracteres de lista no ordenada de un texto y los <li> que se encuentran dentro de palabras
    '''

    p1 = re.compile(r'\n+<li>\s+\n+', re.UNICODE)
    text2 = p1.sub(r'',text)
    p2 = re.compile(r'(\w)<li>(\w)', re.UNICODE)
    text3 = p2.sub(r'\1\2',text2)

    return text3





def delete_list_jumps(text):
    '''
    :return:    Elimina las palabras inacabadas con saltos de línea, juntando
                el final de línea y palabra con su continuación.
    '''
    p1 = re.compile(r'(<li> [^-\n]+)[' '*\n|\-' '*\n]\n+([a-z].+\.)', re.UNICODE)
    text2 = p1.sub(r'\1\2> ',text)

    return text2





def delete_list_doublejumps(text):
    '''
    :return:    Elimina los saltos de línea dobles en guías clínicas
    '''

    p1 = re.compile(r'(<li>\s* *.+)\n\n([a-z])', re.UNICODE)
    text2 = p1.sub(r'\1\2> ',text)
    return text2





def delete_double_jump_start(text):
    '''
    :return:    Elimina los saltos de línea entre la úlima frase antes de una etiqueta <li>
                y la propia etiqueta
    .. note::
        Ejemplo de salto de línea previo a una etiqueta
            - Texto1
            - Texto2
            - Texto3
     
    '''
    p1 = re.compile(r'(.+)\n{2,}( *<li> .+\.)', re.UNICODE)
    text2 = p1.sub(r'\1\n\2> ',text)

    return text2





def delete_double_endline_list(text):

    ''' 
    :return:    Elimina los dobles saltos de línea entre una misma lista
                palabras no ordenadas, y junta cada lista no ordenada con
                su título en la parte superior
    '''
    p1 = re.compile(r'(<li> .+)\n+( *<li>.+)\n+ *', re.UNICODE)
    text1 = p1.sub(r'\1\n\2\n',text)

    p1 = re.compile(r'(<li> .+\n{2,3})(\w)', re.UNICODE)
    text2 = p1.sub(r'\1\n\2',text1)

    p1 = re.compile(r'(.+\.)\n+( *<li>.+)', re.UNICODE)
    text3 = p1.sub(r'\1\n\2',text2)
    return text3





def delete_labels(text):
    '''
        :return:    Texto que se introdujo eliminando las etiquetas <ol> y <h[0-9]>
    '''
    p1 = re.compile(r'<\\*ol>', re.UNICODE)
    text1 = p1.sub(r'',text)

    p2 = re.compile(r'<\\*h[0-9]>', re.UNICODE)
    text2 = p2.sub(r'',text1)
    p3 = re.compile(r'<\\*li>',re.UNICODE)
    text3 = p3.sub(r'',text2)
    return text3




def delete_tabs(text):
    '''
        :return:    Sustituye las tabulaciones por espacios simples
    '''
    p1 = re.compile(r'\t', re.UNICODE)
    text3 = p1.sub(r' ',text)
    return text3




def label_li(text):
    '''
    NO USADA
    :return:    Añade una etiqueta sobre la listas no ordenadas

    '''
    return(re.sub(r'(.+\s+( *<li>.*\s+)+)(.)',r"<full_li>\n\1<\\full_li>\n\3",text,re.UNICODE))




def relabel_ol(text):
    '''
    :return:   Asocia a cada lista ordenada su título correspondiente.
    '''

    p1 = re.compile(r'(.+[\.|\:])\s+<ol>(\n(.+\n)+<\\ol>)', re.UNICODE)
    text2 = p1.sub(r'<ol>\n\1\2',text)
    return text2




# Se encarga de etiquetar las listas de elementos en un texto
def label_lists(text):
    '''
        :return:    Etiqueta las listas con <li> y juntando los terminos
                    entre sí y acercándolo a la parte superior
    '''
    texto_procesado = ( delete_listCHR(text)    | p(delete_CID)
                                                | p(delete_emptyListCHR)
                       )
    return texto_procesado



def process_lists(text):
    '''
        :return:    Se encarga de procesar la gestión de las diferentes listas
                    no ordenadas.
    '''
   
    texto_procesado = ( correct_labeling(text)   | p(delete_list_jumps)
                                                    | p(delete_double_endline_list)
                                                    | p(delete_list_doublejumps)
                                                    | p(delete_double_jump_start)
                       )
    return texto_procesado


##########################################################################################

def split_spans(text):
    '''
        :return Keep text and remove miscellaneous elements
    '''

    p1 = re.compile(r'(>)(<span)', re.MULTILINE | re.UNICODE)
    processed_text = p1.sub(r'\1\n\2',text)
    return processed_text

def delete_misc(text):
    '''
        :return Keep text and remove miscellaneous elements
    '''
    
    p1 = re.compile(r'<span style="font-family:.*</span>', re.MULTILINE | re.UNICODE | re.DOTALL)
    match_list = re.findall(p1, text)
    #text2 = p1.sub(r'<ol>\n\1\2',text)
    processed_text = ""
    for match in match_list:
        processed_text += match + '\n'
    return processed_text
    
def delete_dup_greater_than(text):
    p1 = re.compile(r'(<br>)(>)(</)', re.UNICODE)
    processed_text = p1.sub(r'\1\3',text)
    return processed_text

def delete_non_textual_elements(text):
    p1 = re.compile(r'(<div style=)(.*?)(\n<span style=\"font-family)((.|\n)*?)(</span></div>)', re.MULTILINE | re.UNICODE)
    match_list = re.findall(p1, text)
    processed_text = ""
    for match in match_list:
        #print(match)
        processed_text += ''.join(match) + '\n'
    processed_text2 = delete_dup_greater_than(processed_text)
    return processed_text2

def get_page_bounds(text):
    p1 = re.compile(r'<span style=\"position:absolute; border:.*?top:(.*?)px.*?height:(.*?)px.*?></span>\n<div style=\"position:absolute;.*?Page.*?</a></div>', re.UNICODE)
    match_list = re.findall(p1, text)
    # Bound coefficients
    kl = 0.05
    ku = 0.08
    bounds_list = []
    for match in match_list:
        top = int(match[0])
        height = int(match[1])
        lower_bound = top + kl * height
        upper_bound = (top + height) - ku * height
        bounds_list.append((lower_bound, upper_bound))
    return bounds_list


def is_header(bounds_list, position, font_size, i):
    if(font_size >= 18):
        # If text is big, it isn't a header
        return False, i
    else:
        # If text is not big
        found = False
        it_is_header = True
        while(not found):
            if(position >= bounds_list[i][0] and position <= bounds_list[i][1]):
                # OK
                found = True
                it_is_header = False
            elif(position > bounds_list[i][1]):
                # Higher than upper bound
                i += 1
                if(i == len(bounds_list)):
                    # end of the bounds lists
                    found = True
                    # Restore i, maybe there are more headers in the last page
                    i -= 1
            else:
                # Lower than lower bound
                found = True
        # Decrease i, because text might not be in the right order
        i -= 2
        if(i < 0):
            i = 0
        return it_is_header, i

def delete_headers(text, bounds_list):
    p1 = re.compile(r'(<div style=\"position:absolute; border:.*?top:(.*?)px.*?<span style=\"font-family:.*?font-size:(.*?)px.*?</div>)', re.UNICODE | re.DOTALL)
    # Store processed text
    processed_text = ""
    removed_text = ""
    match_list = re.findall(p1, text)
    i = 0 # variable for iterating bounds list
    for match in match_list:
        #print(match)
        matched = match[0]
        position = int(match[1])
        font_size = int(match[2])
        # Check if piece of text is header
        it_is_header, i = is_header(bounds_list, position, font_size, i)
        if(it_is_header):
            # If it's header
            removed_text += matched
        else:
            # If it isn't header
            processed_text += matched
    ### REMOVE LATER, RETURN ONLY PROCESSED_TEXT
    return processed_text


def delete_vertical_text(text):
    
    p1 = re.compile(r'((<div style=\"position:absolute; border:.*?)\n(<span style=\"font-family:.*?>.{1,5}</span>\n){5,}?(.|\n)*?</div>)', re.UNICODE)
    #p1 = re.compile(r'(?!((?:<div style=\"position:absolute; border:.*?)\n(?:<span style=\"font-family:.*?font-size:(?P<size>.+?)px\">.{1,5}</span>\n)((?:<span style=\"font-family:.*?font-size:(?P=size)px\">.{1,5}</span>\n){4,})(?:.|\n)*?</div>))(?:(?:<div style=\"position:absolute; border:.*?)\n(?:<span style=\"font-family:.*?>.{1,5}</span>\n){5,}?(?:.|\n)*?</div>)', re.UNICODE)
    """
    ((<div style=\"position:absolute; border:.*?)\n((?:<span style=\"font-family:.*?font-size:(.+?)px\">.{1,5}</span>\n){5,})(.|\n)*?</div>)
    detect same size text
    ((?:<div style=\"position:absolute; border:.*?)\n(?:<span style=\"font-family:.*?font-size:(?P<size>.+?)px\">.{1,5}</span>\n)((?:<span style=\"font-family:.*?font-size:(?P=size)px\">.{1,5}</span>\n){4,})(?:.|\n)*?</div>)
    Check this out
    (?!((?:<div style=\"position:absolute; border:.*?)\n(?:<span style=\"font-family:.*?font-size:(?P<size>.+?)px\">.{1,5}</span>\n)((?:<span style=\"font-family:.*?font-size:(?P=size)px\">.{1,5}</span>\n){4,})(?:.|\n)*?</div>))((<div style=\"position:absolute; border:.*?)\n(<span style=\"font-family:.*?>.{1,5}</span>\n){5,}?(.|\n)*?</div>)
    Shorter
    ((?:<div style=\"position:absolute; border:.*?)\n(?:<span style=\"font-family:.*?font-size:(?P<size>.+?)px\">.{1,5}</span>\n)(?!((?:<span style=\"font-family:.*?font-size:(?P=size)px\">.{1,5}</span>\n){4,}))(?:.|\n)*?</div>)
    """

    processed_text = p1.sub("", text)
    return processed_text


def kmeans(font_size_list):
    if(font_size_list == []):
        return {}
    k = min(6, len(font_size_list))
    intervals = list(reversed(ckmeans(font_size_list, k)))
    headings_dict = {}
    i = 1
    for sublist in intervals:
        for font_size in sublist:
            headings_dict[font_size] = i
        i += 1
    print(headings_dict)
    return headings_dict


def analyze_font_size(text):
    p1 = re.compile(r'<span style=\"font-family: (.*?); font-size:(.*?)px\">((?:.|\n)*?)</span>', re.UNICODE)
    match_list = re.findall(p1, text)
    font_size_dict = {}
    summatory = 0
    num_data = 0
    data = []
    for match in match_list:
        font = match[0]
        font_size = int(match[1])
        matched_text_len = len(match[2])
        # Check if key exists in dictionary
        if font_size in font_size_dict:
            # It exists, increase value
            font_size_dict[font_size] = int(font_size_dict[font_size]) + matched_text_len
        else:
            # It doesn't exist, create new pair
            font_size_dict[font_size] = matched_text_len
        summatory += font_size * matched_text_len
        num_data += matched_text_len
        data += [font_size] * matched_text_len

    """
    print(font_size_dict)
    mean = summatory / num_data
    mu, std = norm.fit(data)
    xmin, xmax = plt.xlim()
    x = np.linspace(xmin, xmax, 100)
    p = norm.pdf(x, mu, std)
    plt.plot(x, p, 'k', linewidth=2)

    print("mean", mean)
    # Plot analysis
    lists = sorted(font_size_dict.items())
    x, y = zip(*lists)
    #plt.plot(x, y)
    #plt.bar(font_size_dict.keys(), font_size_dict.values(), color='g')
    """
    plt.hist(data)
    #plt.show()

    if(0 in font_size_dict):
        print("delete element 0")
        del font_size_dict[0]

    percentage = 0.95
    percentage_quote = 0.10
    sorted_font_size_dict = sorted(font_size_dict)
    print(sorted_font_size_dict)
    print(max(font_size_dict, key=font_size_dict.get))

    total = sum(font_size_dict.values())
    percentage_sum = 0
    max_quote = 0
    i = 0 # Keep track of the index
    for key in sorted_font_size_dict:
        percentage_sum += (font_size_dict[key] / total)
        i += 1
        if(percentage_sum <= percentage_quote):
            print("size", key)
            print("quote_sum", percentage_sum)
            i_quote = i
            max_quote = key
        if(percentage_sum >= percentage):
            font_threshold = key
            print("key", key)
            print("percentage_sum", percentage_sum)
            print("percentage_sum old", (percentage_sum - (font_size_dict[key] / total)))
            break
    headings_dict = kmeans(sorted_font_size_dict[i:])
    print("Quote font", max_quote)

    #sns.distplot(data)
    #plt.show()
    # return key with max value (most frequent font size)
    #return max(font_size_dict, key=font_size_dict.get)
    return font_threshold, headings_dict, max_quote

"""
def replace_br(text):
    p1 = re.compile(r'<br>', re.UNICODE)
    p2 = re.compile(r'\n+', re.UNICODE)
    processed_text = p1.sub(r'\n', text)
    processed_text2 = p2.sub(r'\n', processed_text)
    return processed_text2
"""

def remove_small_text(text):
    p1 = re.compile(r'(<div style=\"position:absolute;(?:.|\n)*?<span style=\"font-family: .*?; font-size:(.*?)px\">(?:.|\n)*?</div>)', re.UNICODE)
    match_list = re.findall(p1, text)
    processed_text = ""
    for match in match_list:
        font_size = int(match[1])
        if(font_size >= 7):
            processed_text += match[0]
    return processed_text

def extract_text(text):
    font_threshold, headings_dict, max_quote = analyze_font_size(text)
    p1 = re.compile(r'<span style=\"font-family: (.*?); font-size:(.*?)px\">((?:.|\n)*?)</span>', re.UNICODE)
    match_list = re.findall(p1, text)
    processed_text = ""
    prev_font_size = 0
    text_list = [] # Initialize as empty list
    for match in match_list:
        #print(match)
        font = match[0]
        font_size = int(match[1])
        matched_text = match[2]
        if(len(text_list) == 0):
            # New text element
            text_list.append(matched_text + '\n')
        elif(prev_font_size == font_size):
            # Same text element
            text_list[-1] += matched_text + '\n'
        else:
            if(prev_font_size <= font_threshold + 1 and font_size <= font_threshold + 1):
                # Same text element
                text_list[-1] += matched_text + '\n'
            else:
                # New text element
                text_list.append(matched_text + '\n')
            
        prev_font_size = font_size
        #print(text_list[-1])
    return json.dumps(text_list, ensure_ascii=False).encode('utf8')

def extract_text_md(text):
    font_threshold, headings_dict, max_quote = analyze_font_size(text)
    p1 = re.compile(r'<span style=\"font-family: (.*?); font-size:(.*?)px\">((?:.|\n)*?)</span>', re.UNICODE)
    p2 = re.compile(r'\n+', re.UNICODE)
    p3 = re.compile(r'^ *\d+(?: *(?:,|-) *\d+)* *(?:<br>)*$', re.MULTILINE | re.UNICODE)
    match_list = re.findall(p1, text)
    processed_text = ""
    prev_font_size = 0
    for match in match_list:
        #print(match)
        font = match[0]
        font_size = int(match[1])
        matched_text = match[2]
        # Convert matched text \n to <br>
        matched_text = p2.sub(r'<br>', matched_text)
        if(p3.search(matched_text) == None or font_size > max_quote):
            if(prev_font_size <= font_threshold and font_size <= font_threshold):
                processed_text += '\n' + matched_text
            elif(font_size == prev_font_size):
                processed_text += ' ' + matched_text
            elif(font_size > font_threshold):
                processed_text += '\n' + '#' * headings_dict[font_size] + ' ' + matched_text
                #processed_text += '\n### ' + matched_text
            elif(prev_font_size > font_threshold):
                processed_text += '\n' + matched_text
            else:  
                print("font_size", font_size)
                print("prev_font_size", prev_font_size)
                print("most_common_size", font_threshold)
            prev_font_size = font_size

    return processed_text


def detect_quotation_marks(text):
    p1 = re.compile(r'<span style=\"font-family: (.*?); font-size:(.*?)px\">((?:.|\n)*?)</span>', re.UNICODE)

def replace_br(text):
    p1 = re.compile(r'^.*?$', re.UNICODE | re.MULTILINE)
    p2 = re.compile(r'^#+.*?$', re.UNICODE | re.MULTILINE)
    p3 = re.compile(r'(?:<br>)+', re.UNICODE | re.MULTILINE)
    # Initialize processed text string
    processed_text = ""
    match_list = re.findall(p1, text)
    for match in match_list:
        if(p2.search(match) != None):
            # It is a title, so replace <br> with blank space
            processed_match = p3.sub(r' ', match)
        else:
            # It is not a title, so replace <br> with \n
            processed_match = p3.sub(r'\n', match)
        processed_text += processed_match + '\n'
    return processed_text

def remove_blank_lines(text):
    p1 = re.compile(r'^\s+$', re.UNICODE | re.MULTILINE)
    processed_text = p1.sub(r'', text)
    return processed_text

def replace_cid(text):
    # Replace with dashes
    p1 = re.compile(r'(\(cid:(114|131)\) *)') 
    text = p1.sub(r'- ',text)
    # Replace with ó
    p2 = re.compile(r'(\(cid:214\) *)') 
    text = p2.sub(r'ó',text)
    # Replace with cid:1 (blank space)
    p3 = re.compile(r'\(cid:[0-5]\) *', re.MULTILINE | re.DOTALL |re.UNICODE)
    text = p3.sub(r'(cid:1)', text)
    # Replace with ASCII extended chars
    p4 = re.compile(r'(\(cid:(19[0-9])\) *)', re.MULTILINE | re.DOTALL |re.UNICODE)
    text4 = p4.sub(lambda m: chr(int(m.group(2))+27),text)
    p5 = re.compile(r'(\(cid:((21[5-9]|22[0-9]))\) *)', re.MULTILINE | re.DOTALL |re.UNICODE)
    text = p5.sub(lambda m: chr(int(m.group(2))+30),text)
    p6 = re.compile(r'(\(cid:(2[0-9][0-9])\) *)', re.MULTILINE | re.DOTALL |re.UNICODE)
    text = p6.sub(lambda m: chr(int(m.group(2))+28),text)
    # Generic replacing
    p7 = re.compile(r'(\(cid:([0-9]+)\) *)', re.MULTILINE | re.DOTALL |re.UNICODE)
    text = p7.sub(lambda m: chr(int(m.group(2))+31),text)
    return text

def replace_with_dash(text):
    p1 = re.compile(r'(•|–)')
    text = p1.sub(r'-',text)
    return text

def replace_with_fi(text):
    p1 = re.compile(r'([a-z])(%|#)(\D)')
    text = p1.sub(r'\1fi\3',text)
    p2 = re.compile(r'(\D)(%|#)([a-z])')
    text = p2.sub(r'\1fi\3',text)
    return text

def replace_with_fl(text):
    p1 = re.compile(r'([a-z])(\+)(\D)')
    text = p1.sub(r'\1fl\3',text)
    p2 = re.compile(r'(\D)(\+)([a-z])')
    text = p2.sub(r'\1fl\3',text)
    return text

def join_lines(text):
    #p1 = re.compile(r'(?:\w|,|-|\"|“|\)) *?\n+ *?(?:\w|\(|\"|\.|“|,)', re.MULTILINE | re.UNICODE)
    #(^ *#+.*$)*(\n+^ *[^#].*$)*

    processed_text = ""
    p1 = re.compile(r'^.*$', re.MULTILINE | re.UNICODE)
    p2 = re.compile(r'^ *#.*$', re.MULTILINE | re.UNICODE)
    p3 = re.compile(r'((?:\w|,|-|\"|“|\(|\)|;|%|€|≥|≤|«|»|/|=|®|©|±|∆) *?)\n+( *?(?:\w|\(|\)|\"|\.|“|,|€|≥|≤|«|»|&|;|:|/|=|®|©|±|∆))', re.MULTILINE | re.UNICODE)
    #p3 = re.compile(r'((?:[^\.\n:]) *?)\n+( *?(?:.))', re.MULTILINE | re.UNICODE)
    
    processed_match = ""
    match_list = re.findall(p1, text)
    for match in match_list:
        if(p2.search(match) != None):
            # It is a title
            # Process previous standard text
            processed_match = p3.sub(r'\1 \2',processed_match)
            processed_text += processed_match
            processed_match = ""
            # Append title text
            processed_text += match + '\n'
        else:
            # It is not a title
            processed_match += match + '\n'
    # Process previous standard text
    processed_match = p3.sub(r'\1 \2',processed_match)
    processed_text += processed_match
    return processed_text
    

def join_words(text):
    p1 = re.compile(r'(\w) *- *\n+ *(\w)', re.MULTILINE | re.UNICODE)
    #p2 = re.compile(r'([a-z]) *(?:\n+ *)?- *\n+ *([a-z])', re.MULTILINE | re.UNICODE)
    processed_text = p1.sub(r'\1\2', text)
    #processed_text = p2.sub(r'\1\2', processed_text)
    return processed_text

def remove_duplicated_whitespaces(text):
    p1 = re.compile(r' +', re.MULTILINE | re.UNICODE)
    p2 = re.compile(r'^ +', re.MULTILINE | re.UNICODE)
    processed_text = p1.sub(r' ', text)
    processed_text = p2.sub(r'', processed_text)
    return processed_text
    
def join_et_al(text):
    p1 = re.compile(r'(et +al *\.) *\n+ *(.)', re.UNICODE)
    processed_text = p1.sub(r'\1 \2', text)
    return processed_text

def join_beta(text):
    p1 = re.compile(r'(β) *\n+ *(-)', re.UNICODE)
    processed_text = p1.sub(r'\1\2', text)
    return processed_text

def join_vs(text):
    p1 = re.compile(r'(vs) *\. *\n+ *(.)', re.UNICODE)
    processed_text = p1.sub(r'\1. \2', text)
    return processed_text

def fix_enye(text):
    p1 = re.compile(r'˜ *n', re.UNICODE)
    processed_text = p1.sub(r'ñ', text)
    return processed_text