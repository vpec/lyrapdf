from io import StringIO
import re
import json


class Paragraph:
    '''
        Clase que se encarga de registrar una clase parrafo con el siguente estándar:
        http://participants-area.bioasq.org/general_information/Task7a/
    '''
    abstractText = ""       # parrafo del articulo
    journal = ""            # Titulo del documento o guia           
    meshMajor = []          # Conjunto de etiquetas asociadas a un articulo
    pmid = 0                # Identificador único

  
    def __init__(self,_abstractText,_journal,_pmid):
        self.abstractText = _abstractText
        self.journal = _journal
        self.meshMajor = []
        self.pmid = _pmid


class ParagraphQualif:
    '''
        Clase encargada de gestionar los parrafos enfocados a la valoración via web.
        Campos:
            id_parrafo: Identificador único de documento. Identificado de la siguiente manera:
                < "nombre_PDF" - "identificador_numerico">
            publication:    Contiene el titulo de la publicacion.
            text:           Contiene el parrafo a evaluar
            is_recommended: Número de personas que lo han recomendado
            topics:         Strings asociados a las etiquetas del parrafo
    '''

    def __init__(self,_id_parrafo, _publication,_text):
        self.id_parrafo = _id_parrafo
        self.publication = _publication
        self.text = _text
        self.is_recommended = 0
        self.total_votes = 0
        self.topics =[]


    def addTopic(self,_topic):
        '''
            Añade un topic a la lista de topics de la clase.
        '''
        self.topics.append(_topic)
    def toJSON(self):
        '''
            Transforma la clase a formato JSON
        '''
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4,ensure_ascii=False)


class Topic:
    ''' 
        Clase encargada de guardar un topic.
        Campos:
            Topic - string que guarda el nombre del topic
            numero - Introduce el numero de veces que se ha elegido ese topic
    '''
    def __init__(self,nombre):
        self.topic = nombre
        self.numero = 0
    

class Document:
    '''
        Clase encargada de generar una etiqueta para 
        el parrafo de aquel documento que se le pasa 
        como parametro en su contructor
    '''
    articles = []

    def __init__(self):
        self.articles = []

    def add_paragraph(self,new_document):
        '''
            Añade un Parrafo a la lista de parrafos de la clase Documento
        '''
        self.articles.append(new_document)
    
    def toJSON(self):
        '''
            Transforma la clase a formato JSON
        '''
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4,ensure_ascii=False)
