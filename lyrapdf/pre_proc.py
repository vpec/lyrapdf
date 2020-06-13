import re
import json
import matplotlib.pylab as plt
from lyrapdf.ckmeans import ckmeans

#################################################################
#
#					CREATE FILES
#
#################################################################

def create_binary_file(path, text):
	"""Creates a binary file given a path and text in bytes format.

	Args:
		path (string): path where file is going to be stored.
		text (bytes): text to be stored in file.
	"""
	file = open(path,'wb+')
	file.write(text)
	file.close()



def create_text_file(path, text):
	"""Creates a text file given a path and text in string format.

	Args:
		path (string): path where file is going to be stored.
		text (string): text to be stored in file.
	"""
	file = open(path,'w+')
	file.write(text)
	file.close()



#################################################################
#
#					HTML PROCESSING
#
#################################################################

def split_spans(text):
	"""Processes html text splitting spans by a newline character.

	Args:
		text (string): html text that is going to be processed.

	Returns:
		string: text once it's processed.
	"""
	p1 = re.compile(r'(>)(<span)', re.MULTILINE | re.UNICODE)
	processed_text = p1.sub(r'\1\n\2',text)
	return processed_text

	
def delete_dup_greater_than(text):
	"""Processes html text deleting duplicated '>' generated after
		previous processing steps.

	Args:
		text (string): html text that is going to be processed.

	Returns:
		string: text once it's processed.
	"""
	p1 = re.compile(r'(<br>)(>)(</)', re.UNICODE)
	processed_text = p1.sub(r'\1\3',text)
	return processed_text

def delete_non_textual_elements(text):
	"""Processes html text deleting miscellaneous elements, keeping
		only text div containers.

	Args:
		text (string): html text that is going to be processed.

	Returns:
		string: text once it's processed.
	"""
	text_div_regex = re.compile(r'(<div style=)(.*?)(\n<span style=\"font-family)((.|\n)*?)(</span></div>)', re.MULTILINE | re.UNICODE)
	match_list = re.findall(text_div_regex, text)
	processed_text = ""
	for match in match_list:
		#print(match)
		processed_text += ''.join(match) + '\n'
	processed_text2 = delete_dup_greater_than(processed_text)
	return processed_text2

def get_page_bounds(text):
	"""Obtains bounds (in pixels) for each page in the document.
		The top of the page is considered lower bound and the bottom
		upper bound. The value is minimum at the beginning of the
		document and maximum at its end.

	Args:
		text (string): html text that is going to be processed.

	Returns:
		[(int, int)]: list of tuples containing lower bound and
			upper bound for each page.
	"""
	positions_regex = re.compile(r'<span style=\"position:absolute; border:.*?top:(.*?)px.*?height:(.*?)px.*?></span>\n<div style=\"position:absolute;.*?Page.*?</a></div>', re.UNICODE)
	# Find all matchings
	match_list = re.findall(positions_regex, text)
	# Bound coefficients
	kl = 0.05 # k lower
	ku = 0.08 # k upper
	bounds_list = []
	# Iterate through match list
	for match in match_list:
		# Get top parameter
		top = int(match[0])
		# Get height parameter
		height = int(match[1])
		# Calculate lower bound
		lower_bound = top + kl * height
		# Calculate upper bound
		upper_bound = (top + height) - ku * height
		# Append bounds to list
		bounds_list.append((lower_bound, upper_bound))
	return bounds_list

def is_header(bounds_list, position, font_size, i):
	"""Determines whether a piece of text is considered header or not.

	Args:
		bounds_list ([(int, int)]): text position bounds for each page
			in the document.
		position (int): pixel position of a piece of text.
		font_size (int): font size of a piece of text.
		i (int): number of page to look at in bounds_list.

	Returns:
		(bool, int): a tuple containing a boolean that indicates if
			the piece of text is a header or not, and an integer
			that represents the document page where text is located.
	"""
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
	"""Removes pieces of text considered headers (text located at top or bottom
		of a page), such as page numbers or other text repeated in every page
		of the document.

	Args:
		text (string): html text that is going to be processed.
		bounds_list ([(int, int)]): text position bounds for each page
			in the document.

	Returns:
		string: text once it's processed.
	"""
	headers_regex = re.compile(r'(<div style=\"position:absolute; border:.*?top:(.*?)px.*?<span style=\"font-family:.*?font-size:(.*?)px.*?</div>)', re.UNICODE | re.DOTALL)
	# Store processed text
	processed_text = ""
	match_list = re.findall(headers_regex, text)
	i = 0 # variable for iterating bounds list
	for match in match_list:
		matched = match[0]
		position = int(match[1])
		font_size = int(match[2])
		# Check if piece of text is header
		it_is_header, i = is_header(bounds_list, position, font_size, i)
		if(not it_is_header):
			# If it isn't header
			processed_text += matched
	return processed_text


def delete_vertical_text(text):
	"""Removes from the html text that is considered vertical.
		This is text that hasn't had a correct extraction from
		the original document.

	Args:
		text (string): html text that is going to be processed.

	Returns:
		string: text once it's processed.
	"""
	vertical_text_regex = re.compile(r'((<div style=\"position:absolute; border:.*?)\n(<span style=\"font-family:.*?>.{1,5}</span>\n){5,}?(.|\n)*?</div>)', re.UNICODE)
	processed_text = vertical_text_regex.sub("", text)
	return processed_text


def kmeans(font_size_list):
	"""Generates intervals for unidimensional dataset (list of font
		sizes), selecting as number of intervals (clusters) the
		minimum between 6 and the number of elements provided.

	Args:
		font_size_list ([int]): list containing the data.

	Returns:
		{int: int}: dictionary containing font sizes in argument's
			list as keys, and title or heading level assigned as value.
	"""
	# Check if font_size_list isn't empty
	if(font_size_list == []):
		return {}
	# Define number of clusters (k)
	k = min(6, len(font_size_list))
	# Get intervals (execute ckmeans)
	intervals = list(reversed(ckmeans(font_size_list, k)))
	# Initialize headings_dict as empty dictionary
	headings_dict = {}
	i = 1
	# Fill headings dictionary
	for sublist in intervals:
		for font_size in sublist:
			headings_dict[font_size] = i
		i += 1
	return headings_dict


def analyze_font_size(text):
	"""Analyzes font sizes in the document, calculating a font
		size threshold for what it's supposed to be "standard"
		text, a dictionary for indentifying each size larger than
		that as title level, and what size is supposed to be the
		maximum for a number to be considered a quote reference.

	Args:
		text (string): html text that is going to be processed.

	Returns:
		int, {int: int}, float: a tuple containing the standard
			text size threshold, the dictionary for title levels,
			and the size threshold for quote reference numbers.
	"""
	span_regex = re.compile(r'<span style=\"font-family: (.*?); font-size:(.*?)px\">((?:.|\n)*?)</span>', re.UNICODE)
	# Find all matchings
	match_list = re.findall(span_regex, text)
	# Initialize font size dictionary
	font_size_dict = {}
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
		# For plotting purposes
		data += [font_size] * matched_text_len

	# Plot data
	#plt.hist(data)
	#plt.show()

	# Delete font size 0 if it exists in dictionary
	# Commonly it happens when all blank spaces in document
	# have been detect as 0 size, so it distorts analysis results
	if(0 in font_size_dict):
		print("delete element 0")
		del font_size_dict[0]
	# Accumulated percentage threshold for standard/title text
	percentage = 0.95
	# Accumulated percentage threshold for quote/standard text
	percentage_quote = 0.10
	# Sort keys in dictionary
	sorted_font_size_dict = sorted(font_size_dict)
	print(sorted_font_size_dict)
	print(max(font_size_dict, key=font_size_dict.get))
	# Total number of characters in document with size > 0
	total = sum(font_size_dict.values())
	percentage_sum = 0
	max_quote = 0
	i = 0 # Keep track of the index
	for key in sorted_font_size_dict:
		# Update accumulated percentage
		percentage_sum += (font_size_dict[key] / total)
		# Increase i
		i += 1
		# Check if quote/standard threshold hasn't been surpassed
		if(percentage_sum <= percentage_quote):
			i_quote = i
			max_quote = key
		# Check if standard/title threshold has been surpassed
		if(percentage_sum >= percentage):
			font_threshold = key
			break
	# Get intervals for title text font sizes
	headings_dict = kmeans(sorted_font_size_dict[i:])
	# Update max_quote if font_threshold by a factor is higher
	max_quote = max(max_quote, font_threshold * 0.8)
	return font_threshold, headings_dict, max_quote


def sort_html(text):
	"""Sorts div containers in a given html document by its top
		defined position in pixels.

	Args:
		text (string): html text that is going to be processed.

	Returns:
		string: text once it is processed.
	"""
	div_container_regex = re.compile(r'(<div style=\"position:absolute; border:(?:.|\n)*?left:(.*?)px; top:(.*?)px(?:.|\n)*?height:(.*?)px(?:.|\n)*?<span style=\"font-family:(?:.|\n)*?font-size:(.*?)px(?:.|\n)*?</div>)', re.UNICODE)
	# Find all regex matchings
	match_list = re.findall(div_container_regex, text)
	n = len(match_list)
	i = 0
	top = 0
	prev_top = 0
	# Iterate through div container matchings
	while(i < n):
		top = int(match_list[i][2])
		# Check if top value is not decreasing
		if(top >= prev_top):
			prev_top = top
			i += 1
		else:
			# If top value decreases
			element = match_list[i]
			bad_i = i
			# Look backwards until correct position is found
			while(top < int(match_list[i-1][2]) and i > 0):
				i -= 1
			# Relocate the element
			del match_list[bad_i]
			match_list.insert(i, element)
			prev_top = top
	
	# Check if sorting went good
	top = 0
	prev_top = 0
	for match in match_list:
		top = int(match[2])
		if(top < prev_top):
			print("BAD SORTING")
		prev_top = top       

	# Compose new text string with sorted elements
	processed_text = ""
	for match in match_list:
		processed_text += match[0]

	return processed_text


def extract_text_md(text):
	"""Extracts text from a html document and convert it to
		MarkDown format, classifying standard and title text
		based on its font size.

	Args:
		text (string): html text that is going to be processed.

	Returns:
		string: text in MarkDown format.
	"""
	# Get font size analysis results
	font_threshold, headings_dict, max_quote = analyze_font_size(text)
	span_regex = re.compile(r'<span style=\"font-family: (.*?); font-size:(.*?)px\">((?:.|\n)*?)</span>', re.UNICODE)
	newline_regex = re.compile(r'\n+', re.UNICODE)
	quote_reference_number_regex = re.compile(r'^ *\d+(?: *(?:,|-) *\d+)* *(?:<br>)*$', re.MULTILINE | re.UNICODE)
	number_sign_regex = re.compile(r'(^|<br>)( *#)', re.MULTILINE | re.UNICODE)
	# Find all span regex matchings
	match_list = re.findall(span_regex, text)
	processed_text = ""
	prev_font_size = 0
	# Iterate through span's match list
	for match in match_list:
		font = match[0]
		font_size = int(match[1])
		matched_text = match[2]
		# Convert matched text \n to <br>
		matched_text = newline_regex.sub(r'<br>', matched_text)
		# Convert lines beginning with '#' to '\#',
		# so they aren't confused with MarkDown titles
		matched_text = number_sign_regex.sub(r'\1\\\2', matched_text)
		# Check if font size > 0 and text isn't considered a quote reference number
		if((quote_reference_number_regex.search(matched_text) == None or font_size > max_quote) and font_size > 0):
			if(prev_font_size <= font_threshold and font_size <= font_threshold):
				# Append text as standard text
				processed_text += '\n' + matched_text
			elif(font_size == prev_font_size):
				# Append text as title text continuation
				processed_text += ' ' + matched_text
			elif(font_size > font_threshold):
				# Append text as a starting title text
				processed_text += '\n' + '#' * headings_dict[font_size] + ' ' + matched_text
			elif(prev_font_size > font_threshold):
				# Append text as standard text
				processed_text += '\n' + matched_text
			else:
				# Uncovered case (never happends)
				print("uncovered case")
				print("font_size", font_size)
				print("prev_font_size", prev_font_size)
				print("most_common_size", font_threshold)
			# Update previous font size value
			prev_font_size = font_size

	return processed_text


#################################################################
#
#					MARKDOWN PROCESSING
#
#################################################################

def replace_br(text):
	"""Replaces <br> in text for a newline character if the line
		is standard, and replacing it for a blank space if the line
		is a title.

	Args:
		text (string): markdown text that is going to be processed.

	Returns:
		string: text once it is processed.
	"""
	line_regex = re.compile(r'^.*?$', re.UNICODE | re.MULTILINE)
	title_line_regex = re.compile(r'^#+.*?$', re.UNICODE | re.MULTILINE)
	br_regex = re.compile(r'(?:<br>)+', re.UNICODE | re.MULTILINE)
	# Initialize processed text string
	processed_text = ""
	# Find all line regex matchings
	match_list = re.findall(line_regex, text)
	# Iterate through all lines in text
	for match in match_list:
		if(title_line_regex.search(match) != None):
			# If it is a title, replace <br> with blank space
			processed_match = br_regex.sub(r' ', match)
		else:
			# If it is not a title, replace <br> with \n
			processed_match = br_regex.sub(r'\n', match)
		processed_text += processed_match + '\n'
	return processed_text

def remove_blank_lines(text):
	"""Removes blank lines from the document.

	Args:
		text (string): markdown text that is going to be processed.

	Returns:
		string: text once it is processed.
	"""
	blank_line_regex = re.compile(r'^\s+$', re.UNICODE | re.MULTILINE)
	processed_text = blank_line_regex.sub(r'', text)
	return processed_text

def replace_cid(text):
	"""Replaces cid elements (a format to encode some characters
		extracted by PDFMiner) for its unicode character equivalent
		(not 100% accurate, specially in extended ASCII characters).

	Args:
		text (string): markdown text that is going to be processed.

	Returns:
		string: text once it is processed.
	"""
	# Replace with dashes
	cid_regex_1 = re.compile(r'(\(cid:(114|131)\) *)') 
	text = cid_regex_1.sub(r'- ',text)
	# Replace with ó
	cid_regex_2 = re.compile(r'(\(cid:214\) *)') 
	text = cid_regex_2.sub(r'ó',text)
	# Replace with cid:1 (blank space)
	cid_regex_3 = re.compile(r'\(cid:[0-5]\) *', re.MULTILINE | re.DOTALL |re.UNICODE)
	text = cid_regex_3.sub(r'(cid:1)', text)
	# Replace with ASCII extended chars
	cid_regex_4 = re.compile(r'(\(cid:(19[0-9])\) *)', re.MULTILINE | re.DOTALL |re.UNICODE)
	text4 = cid_regex_4.sub(lambda m: chr(int(m.group(2))+27),text)
	cid_regex_5 = re.compile(r'(\(cid:((21[5-9]|22[0-9]))\) *)', re.MULTILINE | re.DOTALL |re.UNICODE)
	text = cid_regex_5.sub(lambda m: chr(int(m.group(2))+30),text)
	cid_regex_6 = re.compile(r'(\(cid:(2[0-9][0-9])\) *)', re.MULTILINE | re.DOTALL |re.UNICODE)
	text = cid_regex_6.sub(lambda m: chr(int(m.group(2))+28),text)
	# Generic replacing
	cid_regex_generic = re.compile(r'(\(cid:([0-9]+)\) *)', re.MULTILINE | re.DOTALL |re.UNICODE)
	text = cid_regex_generic.sub(lambda m: chr(int(m.group(2))+31),text)
	return text

def replace_with_dash(text):
	"""Replaces a set of symbols with '-' in provided text.

	Args:
		text (string): markdown text that is going to be processed.

	Returns:
		string: text once it is processed.
	"""
	dash_regex = re.compile(r'(•|–|·|—|−|―|▪)')
	text = dash_regex.sub(r'-',text)
	text = text.replace(chr(61623), "-")
	return text


def join_lines(text):
	"""Processes text so lines that are part of the same
		semantic paragraph are merged into a single line.

	Args:
		text (string): markdown text that is going to be processed.

	Returns:
		string: text once it is processed.
	"""
	processed_text = ""
	line_regex = re.compile(r'^.*$', re.MULTILINE | re.UNICODE)
	title_line_regex = re.compile(r'^ *#.*$', re.MULTILINE | re.UNICODE)
	lines_to_join_regex = re.compile(r'([^\.\n: \+\*\?¿√] *?)\n+( *?[^\-\n \+\*\?¿√])', re.MULTILINE | re.UNICODE)

	# Initialize processed_match variable. Only standard text lines have to be processed.
	processed_match = ""
	# Find all regex line matchings
	match_list = re.findall(line_regex, text)
	# Iterate through all line matchings
	for match in match_list:
		# Check if it is a title line
		if(title_line_regex.search(match) != None):
			# It is a title
			# Process previous standard text
			processed_match = lines_to_join_regex.sub(r'\1 \2',processed_match)
			# Append previous standard text once is processed
			processed_text += processed_match
			# Empty processed_match string
			processed_match = ""
			# Append title text (current match)
			processed_text += match + '\n'
		else:
			# It is not a title, append to processed_match string
			processed_match += match + '\n'
	# Process previous standard text, in case some hasn't been processed yet
	processed_match = lines_to_join_regex.sub(r'\1 \2',processed_match)
	processed_text += processed_match
	return processed_text
	

def join_by_hyphen(text):
	"""Joins lines that are separated by hyphen, so the word
		in between in reconstructed.

	Args:
		text (string): markdown text that is going to be processed.

	Returns:
		string: text once it is processed.
	"""
	hyphen_regex = re.compile(r'(\w) *(?:-|\u00AD) *\n+ *(\w)', re.MULTILINE | re.UNICODE)
	# Execute first hyphen union processing
	processed_text = hyphen_regex.sub(r'\1\2', text)

	line_regex = re.compile(r'^.*$', re.MULTILINE | re.UNICODE)
	title_regex = re.compile(r'^#', re.MULTILINE | re.UNICODE)
	hyphen_in_title_regex = re.compile(r'^(#+[^\-\u00AD\n]*[a-zA-Z])(?:\-|\u00AD) +([a-zA-Z])', re.MULTILINE | re.UNICODE)
	# Find all line regex matchings (in previously processed text)
	match_list = re.findall(line_regex, processed_text)
	# Initialize second processing string
	processed_text2 = ""
	# Iterate through line regex matchings
	for match in match_list:
		if(title_regex.search(match) == None):
			# Standard text
			processed_text2 += match + '\n'
		else:
			# Title text
			while(hyphen_in_title_regex.search(match) != None):
				# Contains a hyphen
				match = hyphen_in_title_regex.sub(r'\1\2', match)
			processed_text2 += match + '\n'
	
	return processed_text2

def remove_duplicated_whitespaces(text):
	"""Removes duplicated whitespaces in the text, and also
		remove whitespace at the beginning and end of lines.

	Args:
		text (string): markdown text that is going to be processed.

	Returns:
		string: text once it is processed.
	"""
	tab_regex = re.compile(r'\t+', re.MULTILINE | re.UNICODE)
	blank_space_regex = re.compile(r' +', re.MULTILINE | re.UNICODE)
	beginning_blank_space = re.compile(r'^ +', re.MULTILINE | re.UNICODE)
	ending_blank_space = re.compile(r' +$', re.MULTILINE | re.UNICODE)
	processed_text = tab_regex.sub(r' ', text)
	processed_text = blank_space_regex.sub(r' ', processed_text)
	processed_text = beginning_blank_space.sub(r'', processed_text)
	processed_text = ending_blank_space.sub(r'', processed_text)
	return processed_text
	
def join_et_al(text):
	"""Joins lines in text separated because of the dot in 'et al.'
		when it's located at the end of a line.

	Args:
		text (string): markdown text that is going to be processed.

	Returns:
		string: text once it is processed.
	"""
	et_al_regex = re.compile(r'(et +al *\.) *\n+ *(.)', re.UNICODE)
	processed_text = et_al_regex.sub(r'\1 \2', text)
	return processed_text

def join_beta(text):
	"""Joins lines in text separated by character beta when it's
		located at the end of a line.

	Args:
		text (string): markdown text that is going to be processed.

	Returns:
		string: text once it is processed.
	"""
	beta_regex = re.compile(r'(β) *\n+ *(-)', re.UNICODE)
	processed_text = beta_regex.sub(r'\1\2', text)
	return processed_text

def join_vs(text):
	"""Joins lines in text separated because of the dot in 'vs.'
		when it's located at the end of a line.

	Args:
		text (string): markdown text that is going to be processed.

	Returns:
		string: text once it is processed.
	"""
	vs_regex = re.compile(r'(vs) *\. *\n+ *(.)', re.UNICODE)
	processed_text = vs_regex.sub(r'\1. \2', text)
	return processed_text

def fix_enye(text):
	"""Reconstructs 'ñ' character if it's broken.

	Args:
		text (string): markdown text that is going to be processed.

	Returns:
		string: text once it is processed.
	"""
	enye_regex = re.compile(r'˜ *n', re.UNICODE)
	processed_text = enye_regex.sub(r'ñ', text)
	return processed_text

def join_ellipsis(text):
	"""Merges lines that are separated by ellipsis located at the
		end of a line, when its continuation is supposed to be part
		of the same paragraph.

	Args:
		text (string): markdown text that is going to be processed.

	Returns:
		string: text once it is processed.
	"""
	title_ellipsis_regex = re.compile(r'^(#+.*\.\.\.) *\n+#+ *([a-zA-Z])', re.MULTILINE | re.UNICODE)
	ellipsis_regex = re.compile(r'(\.\.\.) *\n+ *([a-z])', re.UNICODE)
	processed_text = title_ellipsis_regex.sub(r'\1 \2', text)
	processed_text = ellipsis_regex.sub(r'\1 \2', processed_text)
	return processed_text
	
def join_subtraction(text):
	"""Merges lines that are separated because of a line starting with
		dash, when it's actually a subtraction.

	Args:
		text (string): markdown text that is going to be processed.

	Returns:
		string: text once it is processed.
	"""
	subtraction_regex = re.compile(r'(\d) *\n+ *(- *\d)', re.UNICODE)
	processed_text = subtraction_regex.sub(r'\1 \2', text)
	return processed_text

def fix_marks(text):
	"""Removes incorrect whitespaces between some words and
		punctuation marks.

	Args:
		text (string): markdown text that is going to be processed.

	Returns:
		string: text once it is processed.
	"""
	marks_regex = re.compile(r'(\w|\)) *(\.|,|:|;)', re.UNICODE)
	processed_text = marks_regex.sub(r'\1\2', text)
	return processed_text

def remove_false_titles(text):
	"""Removes title lines that don't contain any word.

	Args:
		text (string): markdown text that is going to be processed.

	Returns:
		string: text once it is processed.
	"""
	false_title_regex = re.compile(r'^#+ *([^\-\w¿\?\n]*)$', re.MULTILINE | re.UNICODE)
	processed_text = false_title_regex.sub(r'\1', text)
	return processed_text

def join_by_colon(text):
	"""Merges lines separated by a colon at the end of a line when
		the next one starts with lower case.

	Args:
		text (string): markdown text that is going to be processed.

	Returns:
		string: text once it is processed.
	"""
	colon_separated_regex = re.compile(r'(:) *\n+ *([a-z])', re.MULTILINE | re.UNICODE)
	processed_text = colon_separated_regex.sub(r'\1 \2', text)
	return processed_text

def join_title_questions(text):
	"""In some documents, a single title can be composed by words with
		different font sizes, so it can be separated in multiple lines with
		distinct title level. This function merges that lines into a single
		line when the title is a question, because it can easily be detected
		(at least in spanish) due to '¿' and '?' symbols. The resulting
		title level is the highest (less significant) of the levels that were
		composing the question.

	Args:
		text (string): markdown text that is going to be processed.

	Returns:
		string: text once it is processed.
	"""
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
	"""Removes duplicated consecutive dashes from text.

	Args:
		text (string): markdown text that is going to be processed.

	Returns:
		string: text once it is processed.
	"""
	dup_dashes_regex = re.compile(r'^ *(- +)+', re.MULTILINE | re.UNICODE)
	processed_text = dup_dashes_regex.sub(r'- ', text)
	return processed_text

def remove_useless_lines(text):
	"""Removes lines that don't contain a word nor a number.

	Args:
		text (string): markdown text that is going to be processed.

	Returns:
		string: text once it is processed.
	"""
	# Useless lines
	useless_line_regex = re.compile(r'^[^\w\n]*$', re.MULTILINE | re.UNICODE)
	processed_text = useless_line_regex.sub(r'', text)   
	return processed_text

def remove_repeated_strings(text):
	"""Removes strings that are identical and consecutive (repeated
		more than 3 times).

	Args:
		text (string): markdown text that is going to be processed.

	Returns:
		string: text once it is processed.
	"""
	# Repeated strings
	repeated_strings_regex = re.compile(r'([^#IVX0\n]{1,4}?)(\1){3,}', re.UNICODE)
	processed_text = repeated_strings_regex.sub(r'\1', text)
	return processed_text


def convert_md_to_json(text, name):
	"""Converts markdown text to JSON, creating a dictionary where its
		root is:
		
		{
			"document" : document_name
			"level": 0
			"content" : []
		}

		content contains a list where each node has a lower level than
		any of its children. A node might not have any children. If it
		has, they are contained in a list in "content". A node is composed
		like this:

		{
			"text": text_of_the_node
			"level": X
			"content": [] # Optional
		}

		Levels go from 0 to 7, where 0 is document root node, 7 is
		standard text, and 1 to 6 are title levels, being 1 the most significant
		and 6 the least.


	Args:
		text (string): markdown text that is going to be processed.
		name (string): name of the document.

	Returns:
		bytes: document JSON binary.
	"""
	line_regex = re.compile(r'^.+$', re.MULTILINE | re.UNICODE)
	title_regex = re.compile(r'^(#+) *(.*)$', re.MULTILINE | re.UNICODE)
	number_sign_regex = re.compile(r'\\ *#', re.MULTILINE | re.UNICODE)
	# Find all non blank line matchings
	match_list = re.findall(line_regex, text)
	# Document dictionary
	doc = {
		"document": name,
		"level" : 0
	}
	# Initialize list of sublists
	content_list = [[doc]]

	level = 0
	prev_level = level
	# Iterate through lines in text
	for match in match_list:
		heading_match = title_regex.search(match)
		# Check if line is a title
		if(heading_match == None):
			# Standard text
			level = 7
			# Restore number signs to normal
			match = number_sign_regex.sub(r'#', match)
			# Matched text dictionary
			x = {
				"text": match,
				"level" : level
			}
		else:
			# Title text
			# Obtain title level: number of '#'
			level = len(heading_match.group(1))
			# Restore number signs to normal
			match = number_sign_regex.sub(r'#', match)
			# Matched text dictionary
			x = {
				"text" : heading_match.group(2),
				"level" : level
			}
		if(level > prev_level):
			# If current level is higher
			# Create new sublist and append
			content_list.append([x])
		elif(level < prev_level):
			# If current level is lower
			# Insert higher level elements as "content" of the
			# latest same or lower level element
			while(content_list[-2][-1]["level"] >= level):
				content_list[-2][-1]["content"] = content_list[-1]
				del content_list[-1]
			# Append to current sublist
			content_list[-1].append(x)
		else:
			# If current level is the same as the previous one
			# Append to current sublist
			content_list[-1].append(x)
		# Update previous level value before new iteration
		prev_level = level
	# Insert higher level elements as "content" of the
	# latest same or lower level element, until the "document"
	# level is reached (level 0).
	while(content_list[-1][-1]["level"] > 0):
		content_list[-2][-1]["content"] = content_list[-1]
		del content_list[-1]        
	# Return document dictionary as JSON
	return json.dumps(doc, ensure_ascii=False).encode('utf8')
