import io
import yaml

def create_intent(dataset_dir, document, intent_name, training_phrase, response):
    """Creates an intent using intent_name argument as intent name and
        training_phrase as utterance (only one). The result is a yaml
        file stored in the given path and another file (txt) storing
        the response that has to be provided by the chatbot when intent
        triggers.

    Args:
        dataset_dir (string): path where intent is going to be stored.
        document (string): name of the document (added to path).
        intent_name (string): name of the intent.
        training_phrase (string): training phrase (utterance).
        response (string): text that may be answered by the chatbot.
    """
    intent_dict = {
        "type" : "intent",
        "name" : intent_name,
        "utterances" : [training_phrase]
    }
    # Write intent
    with open(dataset_dir + "/" + document + "/" + intent_name + '_intent.yml', 'w') as outfile:
        yaml.dump(intent_dict, outfile, default_flow_style=False, allow_unicode=True)
    # Write intent response
    with open(dataset_dir + "/" + document + "/" + intent_name + '_intent.txt', 'w') as outfile:
        outfile.write(response)

def create_intent_from_list(dataset_dir, document, training_phrases):
    """Creates an intent using document argument as intent name and
        training_phrases as utterances. The result is a yaml file
        stored in the given path.

    Args:
        dataset_dir (string): path where intent is going to be stored.
        document (string): name of the document.
        training_phrases ([string]): list containing training phrases.
    """
    intent_dict = {
        "type" : "intent",
        "name" : document,
        "utterances" : training_phrases
    }
    with open(dataset_dir + "/general/" + document + '.yml', 'w') as outfile:
        yaml.dump(intent_dict, outfile, default_flow_style=False, allow_unicode=True)