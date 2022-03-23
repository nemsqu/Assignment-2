#########################################################################################################
# Nelli Kemi
# 23.3.2022
#########################################################################################################

from datetime import datetime
import xmlrpc.client

def login():
    print("Welcome to the Notebook application. Would you like to log in or sign up?")
    logged_in = False
    username = ""
    while logged_in == False:
        print("L = Login")
        print("S = Sign up")
        choice = input("Your choice: ")
        if choice.lower() == 'l':
            username = input("Username: ")
            try:
                logged_in = s.authenticate_user(username)
            except Exception as e:
                print(e)
                return ""
            if logged_in == True:
                break
            else:
                print("No user found with the username.\n")
        elif choice.lower() == 's':
            username = input("Username: ")
            try:
                logged_in = s.create_user(username)
            except Exception as e:
                print(e)
                return ""
            if logged_in == True:
                print("User succesfully added.\n")
                break
            else:
                print("Username already in use.\n")
        else:
            print("Invalid input. Please try again.") 
            print("Write 'L' to log in or 'S' to sign up.\n")
    return username

def menu():
    print("\nWhat would you like to do?")
    print("1) Add a new note")
    print("2) Browse through your notebook")
    print("3) Add a Wikipedia reference to an existing topic")
    print("4) Quit")

def add_note(username):
    topic = input("\nTopic of your new note: ")
    name = input("\nName of your new note: ")
    print("\nWrite your note below. Write 'q' on a new line to finish.")
    addition = ""
    text = ""
    while(addition != 'q'):
        addition = input()
        if addition == 'q':
            break
        text = text + addition + "\n"
    date = datetime.now().strftime('%d-%m-%Y %H:%M')
    if len(text) == 0:
        print("Nothing to add to notebook.") 
    else:
        print("Adding note to notebook...")
        try:
            success = s.add_note(username, topic, name, text, date)
        except Exception as e:
            print(e)
            success = False
        if success:
            print("Note succesfully added.")
        else:
            print("Please try again later.") 

def open_topic(topic, username):
    print(f"Opening {topic}....\n")
    notes = []
    try:
        notes = s.get_notes(topic, username)
    except Exception as e:
        print(e)

    # Topics should not be created nor exist without notes
    if len(notes) == 0:
        print("Please try again later.") 
    else:
        for note in notes:
            print(f"{note['date']} : {note['name']}")
            print(note['content'])


def browse_notebook(username):
    options = []
    try:
        options = s.get_topics(username)
    except Exception as e:
        print(e)
        print("Please try again later.") 
        return

    if len(options) == 0:
        print("\nNo topics available. Please add a note first.") 
        return

    print("\nTopics available:")
    for i in range(1, len(options) +1):
        print(f"{i}) {options[i-1]}")
    
    choice = -1
    while choice != 'q':
        choice = input("\nNumber of topic to open ('q' to exit): ")

        if choice == 'q':
            break
        else:
            try:
                choice = int(choice)
            except ValueError:
                print("Invalid choice, please try again.")
                continue        
        if choice in range(1,len(options) +1):
            open_topic(options[choice-1], username)
            break
        else:
            print("Invalid choice, please try again.")

def add_wikipedia_note(username):
    topic = input("Name of topic to add note to: ")
    search_term = input("Search terms for looking up data on Wikipedia: ")
    try:
        error = s.search_wikipedia(search_term, topic, username)
    except Exception as e:
        print(e)
        print("Please try again later.")
        return

    if error != "":
        print(error)
    else:
        print(f"Note referencing Wikipedia added to topic {topic}")

s = xmlrpc.client.ServerProxy('http://localhost:8000')
username = login()
if len(username) == 0:
    print("\nLogin failed. Please try restarting the application.")
    exit(0)

print(f"Welcome to your notebook {username}.")
choice = "-1"
while (choice != "0"):
    menu()
    choice = input("Your choice: ")
    if choice == "1":
        add_note(username)
    elif choice == "2":
        browse_notebook(username)
    elif choice == "3":
        add_wikipedia_note(username)
    elif choice == "4":
        break
    else:
        print("Invalid choice. Please try again.")

print("Thank you for using the notebook.")
exit(0)