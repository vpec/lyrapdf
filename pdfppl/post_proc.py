

def text_under_title(json, title):
    for node in json.values():
        print(node)
    return []

def feed_chatbot(json):
    text_under_title(json, "Preguntas a responder")