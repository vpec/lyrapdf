import sys
from os.path import abspath
from docbot.train import init_engine
from docbot.parse import question_and_answer

def run():
	if(len(sys.argv) == 3):
		if(sys.argv[1] == "-t"):
			# -t argument: Train
			dataset_file = abspath(sys.argv[2]) # dataset directory
			init_engine(dataset_file)
		elif(sys.argv[1] == "-p"):
			# -p argument: Parse
			engine_dir = abspath(sys.argv[2]) # engine directory
			question_and_answer(engine_dir)
		else:
			print("Invalid argument", sys.argv[1])
	else:
		print("Invalid number of arguments")
