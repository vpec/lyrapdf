import json
import yaml
import re
import pdfppl.dialogflow_adapter as df


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
    title_regex = re.compile(r'^Preguntas para responder$', re.MULTILINE | re.UNICODE)
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

def create_intent_yaml(document, training_phrases):
    intent_dict = {
        "type" : "intent",
        "name" : document,
        "utterances" : training_phrases
    }
    with open('intent_dict.yml', 'w') as outfile:
        yaml.dump(intent_dict, outfile, default_flow_style=False)
    

def feed_chatbot(json_bytes, project_id = "PROJECT_ID"):
    doc_json = json.loads(json_bytes)
    message_texts = ["Te recomiendo este documento " + doc_json["document"]]
    text_list = text_under_title(doc_json, "Preguntas a responder")
    if(text_list != None and text_list != []):
        df.create_intent(project_id, doc_json["document"], text_list, message_texts)

    # Create intent YAML
    create_intent_yaml(doc_json["document"], text_list)

