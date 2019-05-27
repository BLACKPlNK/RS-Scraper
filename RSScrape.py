import pickle
import re
import os
import ast
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup

def valid_response(resp): 

    # True if HTML response received, False otherwise
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200 
            and content_type is not None
            and content_type.find('html') >= 0)

def error_log(e):

    # Yeah yeah print the errors
    print(e)


def get_url(url):
    
    # Make a get request. If HTML/XML, return text, otherwise None

    try:
        with closing(get(url, stream=True)) as resp:
            if valid_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        error_log('Error during requests to {0} : {1}'.format(url, str(e)))
        return None

raw_html = get_url('https://oldschool.runescape.wiki/w/Quests/List')
quest_list_html = BeautifulSoup(raw_html, 'html.parser')


# Get the text list of quests since its less messy than going href by href
text_list = quest_list_html.get_text()

# Remove the empty line space, as the method needed to determine if a line is actually a quest
# Requires comparing the line above and the line below

# Juggle the status of the previous lines because  
two_ago_int = False 
one_ago_int = False 
prev_line = "" 

# List of potential difficulties (Needed to ID a quest)
difficulty_list = ["Novice", "Intermediate", "Experienced", "Master", "Grandmaster", "Special"] 
quest_dict = {} 
# Go line by line, picking out all the quests based on the preceding and following line
text = os.linesep.join([s for s in text_list.splitlines() if s])
count = 0
for line in text.splitlines():
    # Match found if these conditions are met
    if (two_ago_int) and (line in difficulty_list): 
        count += 1
        quest_dict[prev_line] = "http://oldschool.runescape.wiki/w/" + prev_line.replace(" ", "_")
    two_ago_int = one_ago_int
    one_ago_int = line.isdigit()
    prev_line = line

# Now that the quest dict is complete, go through the lines 
# Test to see where the items are
is_good = "Good"
curr_itr = 0
for key in quest_dict:
    raw_html = get_url(quest_dict[key])
    quest_list_html = BeautifulSoup(raw_html, 'html.parser')

    # Build a list containing the required items for the quest 

    quest_info = quest_list_html.find_all("div", {"class": "hidden"})
    info_list = (re.search("items(.)*start", str(quest_info), re.DOTALL | re.I))
    if info_list is None: 
        print(key)
        is_good = "Bad"
    quest_dict[key] = info_list.group(0)
    curr_itr += 1
    if (curr_itr % 10 == 0): 
        print("Searches complete: " + str(curr_itr) + " searches.") 
print(is_good)

print(quest_dict)
item_list_file = open('item_list.pickle', 'wb')
pickle.dump(quest_dict, item_list_file)
item_list_file.close() 
