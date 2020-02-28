from io import StringIO
import par_label, pre_proc, p2t_constants
from par_qual import Paragraph, ParagraphQualif, Document, Topic
import re
import json
import pymongo
from pymongo import *

paragraph_list = []         # Guarda en una lista los párrafos procesados

"""
    Módulo encargado de extraer párrafos desde un documento TXT, y procesarlos.
    * extract_paragraphs(p_text, p_labeling, p_array_qualificate):
"""



def to_JSON(p_json, p_text, p_titulo, p_id_paragraph):
    '''
        Añade un párrafo al documento JSON
    '''
    try:
        _documento = Paragraph(p_text,p_titulo,p_id_paragraph)
        p_json.add_document(_documento)
        return True
    except:
        return False


def count_words(p_cadena):
    '''
        A través del uso de expresiones regulares,
        extrae el número de palabras contenidas en 
        una cadena de texto
    '''
    return len(re.findall(r'\w{2,}', p_cadena))




def extract_paragraphs(p_text, p_labeling, p_array_qualificate):
    '''
        Se encarga de identificar un párrafo definido entre saltos
        de línea y extraerlo
        p_text:       String para trabajar
        p_labeling:   Objeto con los parámetros de etiquetado e identificación del párrafo
        :return:    Devuelve en un único string todos los párrafos
                    procesados etiquetados acorde a la clase etiquetado  
    '''
    to_output = ''
    _result = re.finditer('(?<=\n)(.+\s)+.+(?=\n\n)', p_text, re.UNICODE)
    _document = Document()
    for _res in _result:  
        #print(_res)   
        if count_words(_res.group(0)) >= p2t_constants.MIN_PARAGRAPH_LEN :    # filtramos los párrafos con más de 20 palabras
            _paragraph = Paragraph(pre_proc.delete_labels(_res.group(0)), p_labeling.get_doc_name(), p_labeling.get_distincID())
            _paragraph_qual = ParagraphQualif(p_labeling.get_distincID(), p_labeling.get_doc_name(), pre_proc.delete_labels(_res.group(0)))
            p_array_qualificate.append(_paragraph_qual.toJSON())
            _document.add_paragraph(_paragraph)
            paragraph_list.append(pre_proc.delete_labels(_res.group(0)))
            p_labeling.add() # incrementamos el ID de párrafo
            to_output += p_labeling.get_header(pre_proc.delete_labels(_res.group(0)))   
    
    pre_proc.create_text_file(p2t_constants.OUTPUT_DIR + '/' + p_labeling.get_doc_name()+'.json',_document.toJSON()) # Vaciamos el fichero
    p_labeling.reset_counter()
    
    return to_output
    

def detect_headers(text):
    '''
        NO USADO
        Detecta una cabecera en el texto
    '''
   # return(re.sub(r'(<h[0-5]>\n+.+\n<\\h[0-5]>)',r"\1",text,re.UNICODE))
    return text



def get_ordered_paragraph_list():
    '''
        :return:    Devuelve una cuenta en orden descendente de la cantidad de palabras de todos los párrafos
    '''
    paragraph_list.sort(key=lambda x: count_words(x))
    return paragraph_list