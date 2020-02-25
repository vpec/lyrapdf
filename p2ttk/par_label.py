
from io import StringIO
import re

class ParLabel:
    '''
        Clase encargada de generar una etiqueta para 
        el parrafo de aquel documento que se le pasa 
        como parametro en su contructor
    '''
    _counter = 0
    _name = ''
    _doc_number = 0
    _path = ''

    def __init__(self, p_path, _firstdoc):
        self._counter = 1
        self._doc_number = _firstdoc - 1
        self._path = p_path

    def reset_counter(self):
        self._counter = 0

    def inc_doc_number(self):
        self._doc_number = self._doc_number + 1

    def add(self):
        self._counter = self._counter + 1

    def set_path(self, p_path):
        if self._path != p_path :
            self._path = p_path
            self.inc_doc_number()

    def set_doc_name(self, p_name):
        self._name = p_name

    def get_counter(self):
         return self._counter

    def get_distincID(self):
        return str(self._doc_number).rjust(2,'0') + '-' + str(self._counter).rjust(4,'0')
         
    def get_doc_name(self):
         return self._name

    def get_doc_number(self):
        return self._doc_number        

    def get_header(self, text):
        '''
            Ajusta una cabecera para el archivo que se le pasa como parametro
        '''
        _preheader = '<' + self.get_distincID() + '>\n'
        _postheader = '\n'+'<' + self.get_distincID() + '\>\n'
        return _preheader + text + _postheader

