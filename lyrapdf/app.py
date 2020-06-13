import sys
from lyrapdf import post_proc
from os.path import isfile, join, exists, abspath
from os import listdir, makedirs
from lyrapdf import txt_ext
from sspipe import p
from lyrapdf import pre_proc
from lyrapdf import outlines
import ntpath
from pdfminer.pdfparser import PDFSyntaxError
from pdfminer.pdfdocument import PDFTextExtractionNotAllowed
from multiprocessing import Process, Lock, cpu_count
from multiprocessing import Pool
import time
import argparse


def path_leaf(path):
	"""Returns the leaf of a given path.

	Args:
		path (string): path that is going to be processed.

	Returns:
		string: path leaf.
	"""
	head, tail = ntpath.split(path)
	return tail or ntpath.basename(head)


def process_html(raw_html_text):
	"""Processes hmtl raw text (originally a pdf) and gets rid of
		unnecessary elements, keeping the text content in it.

	Args:
		raw_html_text (string): html text to be processed.

	Returns:
		string: html text once is processed.
	"""
	bounds_list = pre_proc.get_page_bounds(raw_html_text)

	processed_text_html = ( pre_proc.split_spans(raw_html_text) 	| p(pre_proc.delete_non_textual_elements)
																	| p(pre_proc.delete_headers, bounds_list)
																	| p(pre_proc.delete_vertical_text)
																	| p(pre_proc.sort_html)
		)
	return processed_text_html

def process_md(processed_text_html):
	"""Processes html text and converts it to markdown, representing
		as titles text originally large, so it reconstructs the 
		title-content structure of the document.

	Args:
		processed_text_html (string): html text to be processed.

	Returns:
		string: markdown text once is processed.
	"""
	processed_text_md = ( pre_proc.extract_text_md(processed_text_html)
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
														| p(pre_proc.join_title_questions)
														| p(pre_proc.remove_useless_lines)
														| p(pre_proc.remove_duplicated_whitespaces)
														| p(pre_proc.remove_repeated_strings)
														
		)
	return processed_text_md

def process(text, output_dir, file_name):
	"""Processes a document in html format (originally a pdf) so
		at the end it is converted to JSON, reconstructing the
		semantic structure of the titles and its contents. This 
		JSON document is stored in output_dir.

	Args:
		text (string): html that is going to be processed.
		output_dir (string): path where the output files are
			going to be stored.
		file_name (string): name of the document.
	"""
	# Process HTML
	processed_text_html = process_html(text)
	# Write processed HTML output 
	pre_proc.create_text_file(output_dir + "/html_" + file_name + "_pre.html", processed_text_html)

	# Process MD
	processed_text_md = process_md(processed_text_html)
	# Write processed MD output 
	pre_proc.create_text_file(output_dir + "/" + file_name + "_post.md", processed_text_md)
	
	# Process JSON
	processed_json = pre_proc.convert_md_to_json(processed_text_md, file_name)
	# Write processed JSON output 
	pre_proc.create_binary_file(output_dir + "/" + file_name + "_pre.json", processed_json)

	# Feed chatbot
	dataset_dir  = "chatbot"
	# Create general intent folder
	if not exists(dataset_dir + "/general"):
		makedirs(dataset_dir + "/general")
	post_proc.feed_chatbot(processed_json, dataset_dir)

	

def extract_and_process(input_dir, pdf_path):
	"""Extracts a PDF document to HTML format, processing it so
		at the end it is converted to JSON, reconstructing the
		semantic structure of the titles and its contents. This 
		JSON document is stored in output_dir.

	Args:
		input_dir (string): path of the directory where the
			document is stored.
		pdf_path (string): path where pdf document is stored.
	"""
	print('Extracting text from: ', pdf_path)
	output_dir = input_dir + "/output"
	try:
		# Extract PDF to HTML format
		extracted_text = txt_ext.extract_pdf_to_html(pdf_path)
		# Write raw HTML
		pre_proc.create_text_file(output_dir + "/raw_" + path_leaf(pdf_path) + "_post.html", extracted_text)
		
		print("Extraction finished: "+ pdf_path + ", starting processing")
		process(extracted_text, output_dir, path_leaf(pdf_path))

	except PDFSyntaxError:
		print("PDFSyntaxError: Is this really a PDF? ", pdf_path)
	except PDFTextExtractionNotAllowed as e:
		print(e)


def get_listPDF(input_dir):
	"""Returns a list of paths. Each one is a file stored in
		input_dir directory.

	Args:
		input_dir (string): path of the directory.

	Returns:
		[string]: list of paths.
	"""
	file_paths = [input_dir +'/' + f for f in listdir(input_dir) if isfile(join(input_dir, f)) ]
	return file_paths


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

def run_chatbot():
	if(len(sys.argv) == 2):
		input_dir = abspath(sys.argv[1]) # Directory where are stored JSON to be processed
		dataset_dir  = "chatbot"
		json_list = get_listPDF(input_dir)
		# Create general intent folder
		if not exists(dataset_dir + "/general"):
			makedirs(dataset_dir + "/general")
		for json_doc_path in json_list:
			json_doc = open(json_doc_path, 'rb').read()
			# Feed chatbot
			post_proc.feed_chatbot(json_doc, dataset_dir)

def run():
	parser = argparse.ArgumentParser(description='Extract text from a PDF and convert to JSON, preserving its structure.')
	parser.add_argument('path', metavar='path', type=str,
                    help='the path to PDF file or directory')
	parser.add_argument('--threads', metavar='threads', type=int, default=1,
                    help='number of threads used for processing')
	args = parser.parse_args()

	# Get directory where are stored pdfs to be processed
	input_dir = abspath(args.path)
	# Get list of pdf from input directory
	pdf_list = get_listPDF(input_dir)
	# Define ouptut directory
	output_dir = input_dir + "/output"
	# Create output directory if it doesn't exist
	if not exists(output_dir):
		makedirs(output_dir)
	# Define chatbot directory
	chatbot_dir = "chatbot"
	# Create chatbot directory if it doesn't exist
	if not exists(chatbot_dir):
		makedirs(chatbot_dir)
	# Create function arguments for multithreading
	function_args = []
	for pdf in pdf_list:
		function_args.append((input_dir, pdf))
	# Multithreading
	cpu_threads = min(cpu_count(), args.threads)
	print("Number of CPU threads:", cpu_threads)
	# Initialize multithreading pool
	p = Pool(cpu_count())
	with p:
		# Execute function in multiprocess mode
		p.starmap(extract_and_process, function_args)

	"""
	for pdf_path in pdf_list:
		extract_and_process(input_dir, pdf_path)
	"""

