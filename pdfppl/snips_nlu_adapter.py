import io
import yaml

def create_intent(intent_name, training_phrase, response):
    intent_dict = {
        "type" : "intent",
        "name" : intent_name,
        "utterances" : [training_phrase]
    }
    # Write intent
    with open( "chatbot/" + intent_name + '_intent.yml', 'w') as outfile:
        yaml.dump(intent_dict, outfile, default_flow_style=False, allow_unicode=True)
    # Write intent response
    with open( "chatbot/" + intent_name + '_intent.txt', 'w') as outfile:
        outfile.write(response)

def create_intent_from_list(document, training_phrases):
    intent_dict = {
        "type" : "intent",
        "name" : document,
        "utterances" : training_phrases
    }
    with open( "chatbot/" + document + '_intent.yml', 'w') as outfile:
        yaml.dump(intent_dict, outfile, default_flow_style=False, allow_unicode=True)