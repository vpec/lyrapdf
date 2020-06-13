import json
import re
import lyrapdf.snips_nlu_adapter as snips
from os.path import exists
from os import makedirs


def get_standard_text(content_list):
	"""Retrieves all standard text contained in the list of
		nodes provided and their children.

	Args:
		content_list ([{node}]): list of dictionary nodes

	Returns:
		[string]: list of text lines retrieved
	"""
	text_list = []
	for node in content_list:
		if(node["level"] == 7):
			text_list.append(node["text"])
		else:
			# Recursive call
			if("content" in node.keys()):
				text_list += get_standard_text(node["content"])                    
	return text_list


def text_under_title_recursive(content_list, title):
	"""Retrieves standard text contained in the child nodes
		of the first node in list of nodes and their children
		which text is exactly the one stored in title variable
		and it's also a title node. In-depth search is used.

	Args:
		content_list ([{node}]): list of dictionary nodes
		title ([type]): text to be matched

	Returns:
		[string]: list of text lines retrieved
	"""
	title_regex = re.compile(r'^' + f'{re.escape(title)}' + r'$', re.MULTILINE | re.UNICODE)
	for node in content_list:
		if(node["level"] != 7 and title_regex.search(node["text"])):
			print("Found in level", node["level"])
			if("content" in node.keys()):
				return get_standard_text(node["content"])
		else:
			# Recursive call
			if("content" in node.keys()):
				result = text_under_title_recursive(node["content"], title)
				if(result != None):
					return result               
	return None


def text_under_title(doc_json, title):
	"""Retrieves standard text contained in the child nodes
		of the first node in document dictionary which text is
		exactly the one stored in title variable and it's also a
		title node. In-depth search is used.

	Args:
		doc_json (dictionary): json document as a Python dictionary
		title (string): text to be matched

	Returns:
		[string]: list of text lines retrieved
	"""
	root_content_list = doc_json["content"]
	return text_under_title_recursive(root_content_list, title)

	
def remove_numbers(text_list):
	numbers_regex = re.compile(r'\d+\.', re.UNICODE)
	letter_regex = re.compile(r'[a-zA-Z]', re.UNICODE)
	whitespace_regex = re.compile(r' +', re.UNICODE)
	inital_space_regex = re.compile(r'^ +', re.MULTILINE | re.UNICODE)
	final_space_regex = re.compile(r' +$', re.MULTILINE | re.UNICODE)
	left_square_brackets_regex = re.compile(r'\[', re.UNICODE)
	right_square_brackets_regex = re.compile(r'\]', re.UNICODE)
	right_square_brackets_regex = re.compile(r'\]', re.UNICODE)
	processed_text_list = []
	for text in text_list:
		# Remove numbers
		text = numbers_regex.sub(r'', text)
		if(letter_regex.search(text) != None):
			# If text contains any letter, process and append
			text = whitespace_regex.sub(r' ', text)
			text = inital_space_regex.sub(r'', text)
			text = final_space_regex.sub(r'', text)
			text = left_square_brackets_regex.sub(r'(', text)
			text = right_square_brackets_regex.sub(r')', text)
			processed_text_list.append(text)
	return processed_text_list


def get_next_paragraph_recursive(content_list, text, next_paragraph_text = "", found = False, ocurrences = 0):
	text_regex = re.compile(f'{re.escape(text)}', re.UNICODE)
	for node in content_list:
		if(found and node["level"] == 7):
			ocurrences += 1
			if(len(next_paragraph_text) < len(node["text"])):
				next_paragraph_text = node["text"]
			found = False
		if(node["level"] == 7 and text_regex.search(node["text"])):
			found = True
		# Recursive call
		if("content" in node.keys()):
			next_paragraph_text, found, ocurrences = get_next_paragraph_recursive(node["content"], text, next_paragraph_text, found, ocurrences)
	return next_paragraph_text, found, ocurrences



def get_next_paragraph(doc_json, text):
	root_content_list = doc_json["content"]
	next_paragraph_text, found, ocurrences = get_next_paragraph_recursive(root_content_list, text)
	if(next_paragraph_text != "" and ocurrences > 1):
		return next_paragraph_text
	else:
		return None

def get_questions_recursive(content_list):
	"""Retrieves question titles in a list of nodes and their children.
		Questions must be in spanish format (¿blah blah blah?).

	Args:
		content_list ([{node}]): list of dictionary nodes

	Returns:
		[string]: list of questions retrieved
	"""
	questions_list = []
	question_regex = re.compile(r'^.*?¿.*?\?.*$', re.MULTILINE | re.UNICODE)
	for node in content_list:
		if(node["level"] != 7 and question_regex.search(node["text"])):
			questions_list.append(node["text"])
		# Recursive call
		if("content" in node.keys()):
			questions_list += get_questions_recursive(node["content"])
	return questions_list

def get_questions(doc_json):
	"""Retrieves titles in document that contain a question in
		spanish format (¿blah blah blah?)

	Args:
		doc_json (dictionary): json document as a Python dictionary

	Returns:
		[string]: list of questions retrieved
	"""
	root_content_list = doc_json["content"]
	questions_list = get_questions_recursive(root_content_list)
	return questions_list


def feed_chatbot(json_bytes, dataset_dir):
	"""Finds document titles that are questions in spanish
		format (¿blah blah blah?) and creates a intent representing
		the document, where the training phrases are the questions
		themselves. It also creates an intent for each question
		(unique utterance), storing in a txt file the text content
		below the title	as a response for the question.

	Args:
		json_bytes (bytes): json document binary
		dataset_dir (string): path where intents are going
			to be stored
	"""
	doc_json = json.loads(json_bytes)
	#message_texts = ["Te recomiendo este documento " + doc_json["document"]]
	#text_list = text_under_title(doc_json, "Preguntas para responder")
	questions_list = get_questions(doc_json)
	print(questions_list)
	if(questions_list != []):
		# Create intent folder
		if not exists(dataset_dir + "/" + doc_json["document"]):
			makedirs(dataset_dir + "/" + doc_json["document"])
		i = 1
		for question in questions_list:
			#print(question)
			text_list = text_under_title(doc_json, question)
			if(text_list != None):
				if(text_list != []):
					# Remove numbers from question
					[question] = remove_numbers([question])
					response_text = ""
					for element in text_list:
						response_text += element + '\n'
					# Create phrase intent
					snips.create_intent(dataset_dir, doc_json["document"], doc_json["document"] + "_" + str(i), question, response_text)
					i += 1
		# Create document intent YAML
		questions_list = remove_numbers(questions_list)
		snips.create_intent_from_list(dataset_dir, doc_json["document"], questions_list)

