from snips_nlu import SnipsNLUEngine


def question_and_answer(engine_dir):
    # Load general engine from the engines' folder
	general_engine = SnipsNLUEngine.from_path(engine_dir + "/general")
    # Initialize context engine as None
	context_engine = None
    # Folder where data (intents and respondes) is stored
	data_dir = "chatbot/"
    # Initialize context data subfolder as empty string
	context_data_dir = ""
	while(True):
        # Get query from standard input
		query = input("Enter query:\n")
        # If context isn't set up
		if(context_engine == None):
			# General engine
			print("GENERAL ENGINE")
            # Parse query using the general engine
			parsing = general_engine.parse(query)
            # Show parsing result
			print("Document:", parsing["intent"]["intentName"])
			print("Confidence:", parsing["intent"]["probability"])
            # Check if parsing results isn't None intent
			if(parsing["intent"]["intentName"]):
				# Set up context engine
				context_engine = SnipsNLUEngine.from_path(engine_dir + "/" + parsing["intent"]["intentName"])
                # Set up context data directory
				context_data_dir = data_dir + parsing["intent"]["intentName"] + "/"
        # If context is set up
		if(context_engine):
			# Context engine
			print("CONTEXT ENGINE")
            # Parse query using the context engine
			parsing = context_engine.parse(query)
            # Show parsing result
			print("Intent:", parsing["intent"]["intentName"])
			print("Confidence:", parsing["intent"]["probability"])
            # Check if parsing results isn't None intent
			if(parsing["intent"]["intentName"]):
                # Retrieve response
				response = open(context_data_dir + parsing["intent"]["intentName"] + "_intent.txt", 'r').read()
                # Show response
				print("Confidence:", parsing["intent"]["probability"])
				print("RESPONSE:\n", response)
				print()
		