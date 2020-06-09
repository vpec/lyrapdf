from snips_nlu import SnipsNLUEngine
from snips_nlu.default_configs import CONFIG_ES
from os.path import isdir, join, exists
from os import makedirs, listdir
from shutil import rmtree
import json
import io
from ntpath import split, basename

seed = 42

def path_leaf(path):
	head, tail = split(path)
	return tail or basename(head)

def get_dir_list(input_dir):
	'''
	:return: Returns list of file paths inside input_dir
	'''
	path_dirs = [input_dir +'/' + f for f in listdir(input_dir) if isdir(join(input_dir, f)) ]
	return path_dirs

def init_engine(dataset_dir, _config = CONFIG_ES):
	print(dataset_dir)
    # First, check if output engine folder already exists
	if exists("docbot/resources/engine/"):
        # Delete existing folder
		rmtree("docbot/resources/engine/")
    # Create engine output folder
	makedirs("docbot/resources/engine/")
    # Iterate through subfolders in dataset_dir to get dataset files
	for subfolder in get_dir_list(dataset_dir):
        # Initialize engine for this dataset
		engine = SnipsNLUEngine(config = _config, random_state = seed)
        # Open dataset.json file and load it into "dataset"
		with io.open(subfolder + "/dataset.json") as f:
			dataset = json.load(f)
        # Use the dataset to train the engine
		engine.fit(dataset)
        # Make engine persistant (stored in a folder)
		engine.persist("docbot/resources/engine/" + path_leaf(subfolder))