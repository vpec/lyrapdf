import sys
from pdfppl import extractionPyPDF2 as e1
from pdfppl import extractionTabula as e2
#from pdfppl import extraction_mupdf as e3
from os.path import isfile, join, exists, abspath
from os import listdir, makedirs
from pdfppl import txt_ext
from sspipe import p
from pdfppl import pre_proc
from pdfppl import outlines
from pdfppl import metadata
import ntpath
from pdfminer.pdfparser import PDFSyntaxError
from pdfminer.pdfdocument import PDFTextExtractionNotAllowed
from multiprocessing import Process, Lock, cpu_count
from multiprocessing import Pool
import time
from random import randint


def path_leaf(path):
	head, tail = ntpath.split(path)
	return tail or ntpath.basename(head)


def process(text, output_dir, file_name):
	'''
	processed_text = ( pre_proc.split_spans(text)           | p(pre_proc.delete_misc)
					)
	'''

	bounds_list = pre_proc.get_page_bounds(text)

	processed_text_html = ( pre_proc.split_spans(text) 		| p(pre_proc.delete_non_textual_elements)
														| p(pre_proc.delete_headers, bounds_list)
														| p(pre_proc.delete_vertical_text)
														| p(pre_proc.sort_html)
					)

	# Write processed HTML output 
	pre_proc.create_text_file(output_dir + "/html_" + file_name + "_post.html", processed_text_html)
	"""
	processed_text = ( pre_proc.replace_br(processed_text_html)
														| p(pre_proc.extract_text_md)
					)
	"""
	processed_text = ( pre_proc.extract_text_md(processed_text_html)
														| p(pre_proc.replace_br)
														| p(pre_proc.remove_false_titles)
														| p(pre_proc.remove_blank_lines)
														| p(pre_proc.replace_cid)
														| p(pre_proc.replace_with_dash)
														| p(pre_proc.join_by_hyphen)
														| p(pre_proc.join_lines)
														| p(pre_proc.join_lines)
														| p(pre_proc.join_et_al)
														| p(pre_proc.join_beta)
														| p(pre_proc.join_vs)
														| p(pre_proc.fix_enye)
														| p(pre_proc.join_ellipsis)
														| p(pre_proc.join_subtraction)
														| p(pre_proc.join_by_colon)
														| p(pre_proc.remove_duplicated_dashes)
														| p(pre_proc.fix_marks)
														| p(pre_proc.remove_useless_lines)
														| p(pre_proc.remove_duplicated_whitespaces)
														| p(pre_proc.remove_repeated_strings)
					)
	
	pre_proc.create_text_file(output_dir + "/" + file_name + "_post.md", processed_text)
	
	processed_json = pre_proc.convert_md_to_json(processed_text, file_name)		
	pre_proc.create_binary_file(output_dir + "/" + file_name + ".json", processed_json)


def extract_and_process(input_dir, pdf_path):
	print('Extracting text from: ', pdf_path)
	try:	
		texto_extraido = txt_ext.convert_pdf_to_txt(pdf_path, input_dir + "/output", path_leaf(pdf_path))
		
		print("Extraction finished: "+ pdf_path + ", starting processing")
		process(texto_extraido, input_dir + "/output", path_leaf(pdf_path))

	except PDFSyntaxError:
		print("PDFSyntaxError: Is this really a PDF? ", pdf_path)
	except PDFTextExtractionNotAllowed as e:
		print(e)


def get_listPDF(input_dir):
	'''
	:return: Returns list of file paths inside input_dir
	'''

	path_archivos = [input_dir +'/' + f for f in listdir(input_dir) if isfile(join(input_dir, f)) ]
	archivos = [f for f in listdir(input_dir) if isfile(join(input_dir, f)) ]

	return path_archivos,archivos

def f(x):
	time.sleep(randint(10,100)/100)
	
	print(x)

def run_test():
	input_dir = "/home/victor/pdfppl/pdfppl/resources/raw2"
	output_dir = "/home/victor/pdfppl/pdfppl/resources/raw2/output"
	raw_text_list, archivos = get_listPDF(input_dir)
	for pdf_path in raw_text_list:
			print('Processing raw text from: ', pdf_path)
			_file = open(pdf_path, 'r')
			text = _file.read()
			_file.close()
			process(text, output_dir, path_leaf(pdf_path))

def run():
	if(len(sys.argv) == 2):
		input_dir = abspath(sys.argv[1]) # Directory where are stored pdfs to be processed

		pdf_list, archivos = get_listPDF(input_dir)

		output_dir = input_dir + "/output"
		if not exists(output_dir):
			makedirs(output_dir)

		function_args = []
		for pdf in pdf_list:
			function_args.append((input_dir, pdf))

		#print(function_args)
		
		# Multithreading
		print("Number of CPU:", cpu_count())
		
		
		p = Pool(cpu_count())
		with p:
  			p.starmap(extract_and_process, function_args)
	
		"""
		for pdf_path in pdf_list:
			extract_and_process(input_dir, pdf_path)
		"""
	
		
	
			
	else:
		print("Invalid number of arguments")
