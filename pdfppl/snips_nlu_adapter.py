import io
import yaml

def create_intent(document, training_phrases):
    intent_dict = {
        "type" : "intent",
        "name" : document,
        "utterances" : training_phrases
    }
    with open( "chatbot/" + document + '_intent.yml', 'w') as outfile:
        yaml.dump(intent_dict, outfile, default_flow_style=False, allow_unicode=True)