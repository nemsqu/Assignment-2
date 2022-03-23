#########################################################################################################
# Nelli Kemi
# 23.3.2022
#########################################################################################################

from datetime import datetime
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import xml.etree.ElementTree as ET
# import requests <-- doesn't work in VS code for some reason https://stackoverflow.com/questions/48775755/importing-requests-into-python-using-visual-studio-code
from pip._vendor import requests

# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

# Create data structure for storing notes
tree = ET.fromstring("<data></data>")

def check_match(username):
    match = False
    for user in tree.findall('user'):
        if user.find('username').text == username:
            match = True
    return match

def add_user(username):
    user = ET.SubElement(tree, 'user')
    name = ET.SubElement(user, 'username')
    name.text = username

def search_wikipedia(search):
    URL = "https://en.wikipedia.org/w/api.php"
    PARAMS = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": search
    }

    result = requests.get(url=URL, params=PARAMS)
    return result.json()


with SimpleXMLRPCServer(('localhost', 8000), requestHandler=RequestHandler) as server:
    server.register_introspection_functions()

    def authenticate_user(username):
        print(f"Authenticating {username}")
        return check_match(username)
    server.register_function(authenticate_user, 'authenticate_user')

    def create_user(username):
        print(f"Creating {username}")
        match = check_match(username)
        if match == False:
            add_user(username)
        return not match # Match means failure so return !match
    server.register_function(create_user, 'create_user')

    def add_note(username, topic, name, text, date):
        users = tree.findall('user')
        user = ""
        success = False

        # First find user from tree
        for u in users:
            if u.find('username').text == username:
                user = u
                break

        if user != "":
            existing_topic = ""

            # Check if topic exists already
            for t in user.findall('topic'):
                if t.text == topic:
                    existing_topic = t
                    break

            if existing_topic != "":
                addition = False

                # Check if note with same name exists, update existing not if yes, create new note if no
                for n in existing_topic.findall('name'):
                    if n.text == name:
                        addition = True
                        print("Adding contents to note " + name)
                        n.find('content').text = n.find('content').text + text
                        n.find('date').text = date
                        break
                if not addition:
                    print("Creating note " + name)
                    note_name = ET.SubElement(existing_topic, 'name')
                    note_name.text = name
                    note_content = ET.SubElement(note_name, 'content')
                    note_content.text = text
                    date_time = ET.SubElement(note_name, 'date')
                    date_time.text = date
                success = True
            else:
                print(f"Creating new topic {topic} and new note {name}")
                note_topic = ET.SubElement(user, 'topic')
                note_topic.text = topic
                note_name = ET.SubElement(note_topic, 'name')
                note_name.text = name
                note_content = ET.SubElement(note_name, 'content')
                note_content.text = text
                date_time = ET.SubElement(note_name, 'date')
                date_time.text = date
                success = True
        return success
    server.register_function(add_note, 'add_note')

    def get_topics(username):
        users = tree.findall('user')
        topics = []
        for user in users:
            if user.find('username').text == username:
                for topic in user.findall('topic'):
                    topics.append(topic.text)
                break
        return topics 
    server.register_function(get_topics, "get_topics")

    def get_notes(topic, username):
        users = tree.findall('user')
        notes = [] 
        for user in users:
            if user.find('username').text == username:
                for t in user.findall('topic'):
                    if t.text == topic:
                        for note in t.findall('name'):
                            notes.append({'name': note.text, 'content': note.find('content').text, 'date': note.find('date').text})
        return notes
    server.register_function(get_notes, "get_notes")

    def add_wikipedia_notes(search_term, topic, username):
        data = search_wikipedia(search_term)
        error = ""
        if data['query']['searchinfo']['totalhits'] == 0:
            error = "Found nothing matching your search terms."
            return error
        match = False

        # Find user and topic to add note to
        for user in tree.findall('user'):
            if user.find('username').text == username:
                for t in user.findall('topic'):
                    if t.text == topic:
                        match = True
                        new_note = ET.SubElement(t, 'name')
                        new_note.text = "Wikipedia notes"
                        contents = ET.SubElement(new_note, 'content')
                        title = data['query']['search'][0]['title'].replace(' ', "_")
                        snippet = data['query']['search'][0]['snippet'].replace('<span class=\"searchmatch\">', "").replace("</span>", "")
                        contents.text = data['query']['search'][0]['title'] + " available at " + "https://en.wikipedia.org/wiki/" + title + "\nSnippet: " + snippet + "...\n"
                        date = ET.SubElement(new_note, 'date')
                        date.text = datetime.now().strftime('%d-%m-%Y %H:%M')
                        break
                break
        if not match:
            error = "Topic was not found. Please verify the topic exists before adding Wikipedia notes."
        return error
    server.register_function(add_wikipedia_notes, "search_wikipedia")  

    # Run server's main loop
    server.serve_forever()