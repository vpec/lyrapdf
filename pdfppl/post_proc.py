import json
import yaml
import re
import pdfppl.dialogflow_adapter as df
import pdfppl.snips_nlu_adapter as snips


def get_standard_text(content_list):
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
    #title_regex = re.compile(r'^%s$' % title, re.MULTILINE | re.UNICODE)
    title_regex = re.compile(r'^' + f'{title}' + r'$', re.MULTILINE | re.UNICODE)
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
    root_content_list = doc_json["content"]
    return text_under_title_recursive(root_content_list, title)

def create_intent_snips(document, training_phrases):
    intent_dict = {
        "type" : "intent",
        "name" : document,
        "utterances" : training_phrases
    }
    with open( "chatbot/" + document + '_intent.yml', 'w') as outfile:
        yaml.dump(intent_dict, outfile, default_flow_style=False, allow_unicode=True)
    
def remove_numbers(text_list):
    numbers_regex = re.compile(r'\d+\.', re.UNICODE)
    letter_regex = re.compile(r'[a-zA-Z]', re.UNICODE)
    whitespace_regex = re.compile(r' +', re.UNICODE)
    inital_space_regex = re.compile(r'^ +', re.MULTILINE | re.UNICODE)
    final_space_regex = re.compile(r' +$', re.MULTILINE | re.UNICODE)
    left_square_brackets_regex = re.compile(r'\[', re.UNICODE)
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

def feed_chatbot(json_bytes, project_id = "PROJECT_ID"):
    doc_json = json.loads(json_bytes)
    message_texts = ["Te recomiendo este documento " + doc_json["document"]]
    text_list = text_under_title(doc_json, "Preguntas para responder")
    """
    if(text_list != None and text_list != []):
        df.create_intent(project_id, doc_json["document"], text_list, message_texts)
    """
    
    if(text_list != None):
        # Remove numbers from text list
        text_list = remove_numbers(text_list)
        if(text_list != []):
            # Create intent YAML
            create_intent_snips(doc_json["document"], text_list)

    #snips.init_engine_es()

