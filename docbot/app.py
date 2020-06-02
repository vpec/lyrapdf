import sys

from os.path import isfile, join, exists, abspath
from os import listdir, makedirs
from snips_nlu import SnipsNLUEngine
from snips_nlu.default_configs import CONFIG_ES
import json
import io

seed = 42

def init_engine_es(dataset_file):
	engine = SnipsNLUEngine(config=CONFIG_ES, random_state=seed)
	with io.open(dataset_file) as f:
		dataset = json.load(f)

	engine.fit(dataset)

	engine.persist("docbot/resources/engine")


def parse(engine_dir):
	engine = SnipsNLUEngine.from_path(engine_dir)
	while(True):
		query = input("Enter query:\n")
		parsing = engine.parse(query)
		print("Document:", parsing["intent"]["intentName"])
		print("Confidence:", parsing["intent"]["probability"])
		print()


def run():
	if(len(sys.argv) == 3):
		if(sys.argv[1] == "-t"):
			# Train
			dataset_file = abspath(sys.argv[2]) # dataset json file
			init_engine_es(dataset_file)
		elif(sys.argv[1] == "-p"):
			# Parse
			engine_dir = abspath(sys.argv[2]) # engine directory
			parse(engine_dir)

		else:
			print("Invalid argument", sys.argv[1])


	else:
		print("Invalid number of arguments")
