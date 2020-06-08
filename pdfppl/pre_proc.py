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
#from unicodedata import normalize
from os.path import exists
from os import mknod
import json
import matplotlib.pylab as plt
from scipy.stats import norm
import numpy as np
import seaborn as sns
#from sklearn.cluster import KMeans
from pdfppl.ckmeans import ckmeans
import sys
from unicodedata import category




def create_binary_file(path, text):
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


def create_text_file(path, text):
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

	max_quote = max(max_quote, font_threshold * 0.8)

	print("New Quote font", max_quote)

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

def sort_html(text):
	p1 = re.compile(r'(<div style=\"position:absolute; border:(?:.|\n)*?left:(.*?)px; top:(.*?)px(?:.|\n)*?height:(.*?)px(?:.|\n)*?<span style=\"font-family:(?:.|\n)*?font-size:(.*?)px(?:.|\n)*?</div>)', re.UNICODE)
	
	match_list = re.findall(p1, text)

	n = len(match_list)
	i = 0
	top = 0
	prev_top = 0
	print("n", n)
	while(i < n):
		top = int(match_list[i][2])
		if(top >= prev_top):
			prev_top = top
			i += 1
		else:
			element = match_list[i]
			bad_i = i
			#print(i)
			while(top < int(match_list[i-1][2]) and i > 0):
				i -= 1
			del match_list[bad_i]
			match_list.insert(i, element)
			prev_top = top
	
	
	
	# Check sorting
	top = 0
	prev_top = 0
	for match in match_list:
		top = int(match[2])
		if(top < prev_top):
			print("BAD SORTING")
		prev_top = top       


	processed_text = ""
	for match in match_list:
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
	p4 = re.compile(r'(^|<br>)( *#)', re.MULTILINE | re.UNICODE)
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

		matched_text = p4.sub(r'\1\\\2', matched_text)

		if((p3.search(matched_text) == None or font_size > max_quote) and font_size > 0):
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
	p1 = re.compile(r'(•|–|·|—|−|―|▪)')
	text = p1.sub(r'-',text)
	text = text.replace(chr(61623), "-")
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
	#p3 = re.compile(r'((?:\w|,|-|\"|“|”|’|\(|\)|;|%|€|≥|≤|«|»|/|=|®|©|±|∆|\[|\]) *?)\n+( *?(?:\w|\(|\)|\"|\.|“|”|’|,|€|≥|≤|«|»|&|;|:|/|=|®|©|±|∆|\[|\]))', re.MULTILINE | re.UNICODE)
	p3 = re.compile(r'([^\.\n: \+\*\?¿√] *?)\n+( *?[^\-\n \+\*\?¿√])', re.MULTILINE | re.UNICODE)
	
	# caution:  
	
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
	

def join_by_hyphen(text):
	p1 = re.compile(r'(\w) *(?:-|\u00AD) *\n+ *(\w)', re.MULTILINE | re.UNICODE)
	#\n- *\n* *[a-z]
	#p2 = re.compile(r'([a-z]) *(?:\n+ *)?- *\n+ *([a-z])', re.MULTILINE | re.UNICODE)
	processed_text = p1.sub(r'\1\2', text)

	
	p2 = re.compile(r'^.*$', re.MULTILINE | re.UNICODE)
	p3 = re.compile(r'^#', re.MULTILINE | re.UNICODE)
	p4 = re.compile(r'^(#+[^\-\u00AD\n]*[a-zA-Z])(?:\-|\u00AD) +([a-zA-Z])', re.MULTILINE | re.UNICODE)
	
	match_list = re.findall(p2, processed_text)
	processed_text2 = ""

	for match in match_list:
		if(p3.search(match) == None):
			# Standard text
			processed_text2 += match + '\n'
		else:
			# Title text
			while(p4.search(match) != None):
				# Contains a hyphen
				match = p4.sub(r'\1\2', match)
			processed_text2 += match + '\n'
	
	return processed_text2

def remove_duplicated_whitespaces(text):
	p1 = re.compile(r'\t+', re.MULTILINE | re.UNICODE)
	p2 = re.compile(r' +', re.MULTILINE | re.UNICODE)
	p3 = re.compile(r'^ +', re.MULTILINE | re.UNICODE)
	p4 = re.compile(r' +$', re.MULTILINE | re.UNICODE)
	processed_text = p1.sub(r' ', text)
	processed_text = p2.sub(r' ', processed_text)
	processed_text = p3.sub(r'', processed_text)
	processed_text = p4.sub(r'', processed_text)
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

def remove_non_printable(text):
	return text
	return text.replace(chr(61623), "-")



	return bytes(text, 'utf-8').decode('utf-8', 'ignore')
	return text.strip().decode('utf-8','ignore').encode("utf-8")
	# Get all unicode characters
	print(range(sys.maxunicode))
	all_chars = (chr(i) for i in range(sys.maxunicode))
	print(all_chars)
	# Get all non printable characters
	control_chars = ''.join(c for c in all_chars if category(c) == 'Cc')
	# Create regex of above characters
	p1 = re.compile('[%s]' % re.escape(control_chars))
	# Substitute these characters by empty string in the original string.
	processed_text = p1.sub(r'', text)
	return processed_text

def join_ellipsis(text):
	p1 = re.compile(r'^(#+.*\.\.\.) *\n+#+ *([a-zA-Z])', re.MULTILINE | re.UNICODE)
	p2 = re.compile(r'(\.\.\.) *\n+ *([a-z])', re.UNICODE)
	processed_text = p1.sub(r'\1 \2', text)
	processed_text = p2.sub(r'\1 \2', processed_text)
	return processed_text
	
def join_subtraction(text):
	p1 = re.compile(r'(\d) *\n+ *(- *\d)', re.UNICODE)
	processed_text = p1.sub(r'\1 \2', text)
	return processed_text

def fix_marks(text):
	p1 = re.compile(r'(\w|\)) *(\.|,|:|;)', re.UNICODE)
	processed_text = p1.sub(r'\1\2', text)
	return processed_text

def remove_false_titles(text):
	p1 = re.compile(r'^#+ *([^\-\w¿\?\n]*)$', re.MULTILINE | re.UNICODE)
	processed_text = p1.sub(r'\1', text)
	return processed_text

def join_by_colon(text):
	p1 = re.compile(r'(:) *\n+ *([a-z])', re.MULTILINE | re.UNICODE)
	#p1 = re.compile(r'(:) *\n+ *(\w)', re.MULTILINE | re.UNICODE)

	processed_text = p1.sub(r'\1 \2', text)
	return processed_text

def join_title_questions(text):
	line_regex = re.compile(r'^.*$', re.MULTILINE | re.UNICODE)
	line_list = re.findall(line_regex, text)
	title_regex = re.compile(r'^(#+)(.*)$', re.MULTILINE | re.UNICODE)
	question_beggining_regex = re.compile(r'^#+.*¿[^\n\?]*$', re.MULTILINE | re.UNICODE)
	question_ending_regex = re.compile(r'^#+[^\n¿]*\?.*$', re.MULTILINE | re.UNICODE)
	processed_text = ""
	question_text = ""
	highest_level = 0
	for line in line_list:
		title_regex_match = title_regex.search(line)
		if(title_regex_match):
			# Title line
			question_regex_match = question_beggining_regex.search(line)
			if(question_regex_match and question_text == ""):
				highest_level = max(highest_level, len(title_regex_match.group(1)))
				question_text += title_regex_match.group(2)
			elif(not question_regex_match and question_ending_regex.search(line) and question_text != ""):
				highest_level = max(highest_level, len(title_regex_match.group(1)))
				question_text += title_regex_match.group(2)
				# Append text
				processed_text += '#' * highest_level + question_text + '\n'
				question_text = ""
				highest_level = 0
			elif(question_text != ""):
				question_text += title_regex_match.group(2)
			elif(not question_regex_match and question_text == ""):
				processed_text += line + '\n'


		else:
			# Standard line
			if(question_text != ""):
				# Append text
				processed_text += '#' * highest_level + question_text + '\n'
				question_text = ""
				highest_level = 0
			processed_text += line + '\n'

	return processed_text

def remove_duplicated_dashes(text):
	p1 = re.compile(r'^ *(- +)+', re.MULTILINE | re.UNICODE)
	#p1 = re.compile(r'(:) *\n+ *(\w)', re.MULTILINE | re.UNICODE)

	processed_text = p1.sub(r'- ', text)
	return processed_text

def remove_useless_lines(text):
	# Useless lines
	p1 = re.compile(r'^[^\w\n]*$', re.MULTILINE | re.UNICODE)
	processed_text = p1.sub(r'', text)   
	return processed_text

def remove_repeated_strings(text):
	# Repeated strings
	p1 = re.compile(r'([^#IVX0\n]{1,4}?)(\1){3,}', re.UNICODE)
	processed_text = p1.sub(r'\1', text)
	return processed_text


def convert_md_to_json(text, name):
	p1 = re.compile(r'^.+$', re.MULTILINE | re.UNICODE)
	p2 = re.compile(r'^(#+) *(.*)$', re.MULTILINE | re.UNICODE)
	p3 = re.compile(r'\\ *#', re.MULTILINE | re.UNICODE)
	match_list = re.findall(p1, text)
	doc = {
		"document": name,
		"level" : 0
	}
	content_list = [[doc]]

	level = 0
	prev_level = level
	
	for match in match_list:
		heading_match = p2.search(match)
		if(heading_match == None):
			# Standard text
			level = 7
			match = p3.sub(r'#', match)
			x = {
				"text": match,
				"level" : level
			}
			
		else:
			# Title text
			level = len(heading_match.group(1))
			match = p3.sub(r'#', match)
			x = {
				"text" : heading_match.group(2),
				"level" : level
			}

		if(level > prev_level):
			content_list.append([x]) # New sublist
		elif(level < prev_level):
			while(content_list[-2][-1]["level"] >= level):
				content_list[-2][-1]["content"] = content_list[-1]
				del content_list[-1]
			content_list[-1].append(x)
		else:
			content_list[-1].append(x)

		prev_level = level

	while(content_list[-1][-1]["level"] > 0):
		content_list[-2][-1]["content"] = content_list[-1]
		del content_list[-1]        
	
	return json.dumps(doc, ensure_ascii=False).encode('utf8')
