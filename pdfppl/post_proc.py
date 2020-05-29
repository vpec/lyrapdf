import json
import re


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
    text_list = text_under_title_recursive(root_content_list, title)
    return text_list

def feed_chatbot(json_bytes):
    doc_json = json.loads(json_bytes)
    print(text_under_title(doc_json, "Preguntas a responder"))