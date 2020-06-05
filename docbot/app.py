import sys

from os.path import isdir, join, exists, abspath
from os import listdir, makedirs
from snips_nlu import SnipsNLUEngine
from snips_nlu.default_configs import CONFIG_ES
import json
import io
import ntpath

seed = 42

def path_leaf(path):
	head, tail = ntpath.split(path)
	return tail or ntpath.basename(head)

def get_dir_list(input_dir):
	'''
	:return: Returns list of file paths inside input_dir
	'''

	path_dirs = [input_dir +'/' + f for f in listdir(input_dir) if isdir(join(input_dir, f)) ]

	return path_dirs

def init_engine_es(dataset_dir):
	print(dataset_dir)
	# Create general intent folder
	if not exists("docbot/resources/engine/"):
		makedirs("docbot/resources/engine/")
	for subfolder in get_dir_list(dataset_dir):
		print(subfolder)

		engine = SnipsNLUEngine(config=CONFIG_ES, random_state=seed)

		with io.open(subfolder + "/dataset.json") as f:
			dataset = json.load(f)

		engine.fit(dataset)

		engine.persist("docbot/resources/engine/" + path_leaf(subfolder))


def parse(engine_dir):
	general_engine = SnipsNLUEngine.from_path(engine_dir + "/general")
	context_engine = None

	data_dir = "chatbot/"
	context_data_dir = ""
	while(True):
		query = input("Enter query:\n")
		if(context_engine == None):
			# General engine
			print("GENERAL ENGINE")
			parsing = general_engine.parse(query)
			print("Document:", parsing["intent"]["intentName"])
			print("Confidence:", parsing["intent"]["probability"])
			if(parsing["intent"]["intentName"]):
				# Load context engine
				context_engine = SnipsNLUEngine.from_path(engine_dir + "/" + parsing["intent"]["intentName"])
				context_data_dir = data_dir + parsing["intent"]["intentName"] + "/"
		if(context_engine):
			# Context engine
			print("CONTEXT ENGINE")
			parsing = context_engine.parse(query)
			print("Intent:", parsing["intent"]["intentName"])
			print("Confidence:", parsing["intent"]["probability"])
			if(parsing["intent"]["intentName"]):
				response = open(context_data_dir + parsing["intent"]["intentName"] + "_intent.txt", 'r').read()
				print("Confidence:", parsing["intent"]["probability"])
				print("RESPONSE:\n", response)
				print()
		


def run():
	if(len(sys.argv) == 3):
		if(sys.argv[1] == "-t"):
			# Train
			dataset_file = abspath(sys.argv[2]) # dataset directory
			init_engine_es(dataset_file)
		elif(sys.argv[1] == "-p"):
			# Parse
			engine_dir = abspath(sys.argv[2]) # engine directory
			parse(engine_dir)

		else:
			print("Invalid argument", sys.argv[1])


	else:
		print("Invalid number of arguments")
