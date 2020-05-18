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


def path_leaf(path):
	head, tail = ntpath.split(path)
	return tail or ntpath.basename(head)

def segundo_procesado(text):
	'''
		Se encarga de la gestionar los parrafos, extraerlos y añadirles una cabecera y una cola
		para identificarlos teniendo la siguiente estructura:
		..  note::
			Ejemplo de output del segundo procesado:

			<idParrafo><NombreDocumento>
			TEXTOTEXTOTEXTO
			<idParrafo><NombreDocumento\>
		:return:    Un string con todos los párrafos etiquetados y además saca la salida al fichero
					"salida_segundo_procesado" en la carpeta "ficheros_salida"

	'''

	texto_procesado = (p2ttk.par_proc.extraccion_parrafos(text,etiquetado) | p(p2ttk.par_proc.detectar_headers))
	p2ttk.pre_proc.fichero_text('ficheros_salida/salida_segundo_procesado.txt',texto_procesado)  
	return texto_procesado

def primer_procesado(text, output_dir, file_name):
	'''
		- Elimina dashes(guiones de texto) y caracteres raros en el texto
		- Espacios en blanco dobles
		- Saltos de linea en palabras inacabadas y lineas del mismo parrafo
		  elimina carácteres no identificados 


		:param text:    String a realizar el procesado
		:return:        String con el tratamiento del texto y saca un fichero "salida_primer_procesado" en
						"ficheros_entrada"
	'''
	
	texto_procesado = ( pre_proc.delete_0C(text)            | p(pre_proc.delete_false_headers)
																| p(pre_proc.label_lists)
																| p(pre_proc.delete_dash)
																| p(pre_proc.delete_tabs)
																| p(pre_proc.delete_whitespaces)
																| p(pre_proc.delete_jumps)
																| p(pre_proc.label_ordered_lists)
																| p(pre_proc.process_lists)
																| p(pre_proc.label_headers)
																| p(pre_proc.relabel_ol)
																| p(pre_proc.fit_titles)
					   )
	
												
	pre_proc.create_text_file(output_dir + "/" + file_name + ".txt", texto_procesado)
	return texto_procesado+'\n'


def process(text, output_dir, file_name):
	'''
	processed_text = ( pre_proc.split_spans(text)           | p(pre_proc.delete_misc)
					)
	'''

	bounds_list = pre_proc.get_page_bounds(text)

	processed_text_html = ( pre_proc.split_spans(text) 		| p(pre_proc.delete_non_textual_elements)
														| p(pre_proc.delete_headers, bounds_list)
														| p(pre_proc.delete_vertical_text)
					)

	# Write processed HTML output 
	pre_proc.create_text_file(output_dir + "/html_" + file_name + ".html", processed_text_html)
	"""
	processed_text = ( pre_proc.replace_br(processed_text_html)
														| p(pre_proc.extract_text_md)
					)
	"""
	processed_text = ( pre_proc.extract_text_md(processed_text_html)
														| p(pre_proc.replace_br)
														#| p(pre_proc.remove_non_printable)
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
														| p(pre_proc.remove_duplicated_whitespaces)
					)
	
	pre_proc.create_text_file(output_dir + "/" + file_name + "_post.md", processed_text)			
	#pre_proc.create_json_file(output_dir + "/" + file_name + ".json", processed_text)
	#pre_proc.create_text_file(output_dir + "/html2_" + file_name + ".html", processed_text)
	# Removed headers' text (for debugging)
	#pre_proc.create_text_file(output_dir + "/removed_" + file_name + ".html", processed_text_tuple[1])

def get_listPDF(input_dir):
	'''
	:return: Returns list of file paths inside input_dir
	'''

	path_archivos = [input_dir +'/' + f for f in listdir(input_dir) if isfile(join(input_dir, f)) ]
	archivos = [f for f in listdir(input_dir) if isfile(join(input_dir, f)) ]

	return path_archivos,archivos

def run_test():
	input_dir = "/home/victor/pdfppl/pdfppl/resources/raw"
	output_dir = "/home/victor/pdfppl/pdfppl/resources/output"
	raw_text_list, archivos = get_listPDF(input_dir)
	for pdf_path in raw_text_list:
			print('Processing raw text from: ', pdf_path)
			_file = open(pdf_path, 'r')
			text = _file.read()
			_file.close()
			process(text, output_dir, path_leaf(pdf_path))

def run():
	if(len(sys.argv) == 2):
		# e1.extract(sys.argv[1])
		# e2.extract(sys.argv[1])
		input_dir = abspath(sys.argv[1]) # Directory where are stored pdfs to be processed
		# etiquetado = ParLabel(dir_entrada, "GPC_465_Insomnio_Lain_Entr_compl.pdf")


		
		### DEBUG
		"""
		f = open("/home/victor/pdfppl/pdfppl/resources/test/output/raw_pr_1_IACS_Protocolo_Migranya_Profesionales.pdf.html", "r")
		texto_extraido = f.read()
		process(texto_extraido, "/home/victor/pdfppl/pdfppl/resources/test/output", "pr_1_IACS_Protocolo_Migranya_Profesionales.pdf")

		return 0
		"""
		


		pdf_list, archivos = get_listPDF(input_dir)
		#p2ttk.pre_proc.fichero_text('ficheros_salida/salida_primer_procesado.txt','')
		texto_extraido = ''
		texto_total = ''
		i = 0
		output_dir = input_dir + "/output"
		if not exists(output_dir):
			makedirs(output_dir)

		for pdf_path in pdf_list:
			print('Extracting text from: ', pdf_path)

			#e2.extract(pdf_path, input_dir + "/output", path_leaf(pdf_path))
			
			
			#  etiquetado.set_path(archivos[i])
			#  etiquetado.set_document(archivos[i].split(".")[0])
			
			# metadata.get_metadata_pypdf2(pdf_path)
			#txt_ext.convert_pdf_to_txt_pypdf2(pdf_path, input_dir + "/output", path_leaf(pdf_path))
			
			
			#outlines.get_outlines_pdfminer(pdf_path)
			

			#e3.extract(pdf_path)
			try:
			
				#print(input_dir + "/output")
				texto_extraido = txt_ext.convert_pdf_to_txt(pdf_path, input_dir + "/output", path_leaf(pdf_path))
				# nombre_archivo = archivos[i]
				
				print("Extraction finished: "+ pdf_path + ", starting processing")
				process(texto_extraido, input_dir + "/output", path_leaf(pdf_path))
				#texto_procesado = primer_procesado(texto_extraido, input_dir + "/output", path_leaf(pdf_path))
				
				#texto_procesado = (      primer_procesado(texto_extraido) | p(segundo_procesado) 
				#                    )
				
				#texto_total = texto_total + texto_procesado + '\n\n'
			except PDFSyntaxError:
				print("PDFSyntaxError: Is this really a PDF? ", pdf_path)
			except PDFTextExtractionNotAllowed as e:
				print(e)
			
			i+=1
			
			
			
			
			
			
		# mostrar_estadisticas()
		# return texto_total




	else:
		print("Invalid number of arguments")
