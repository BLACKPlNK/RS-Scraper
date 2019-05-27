import pickle
import re 

# Manually defer to the user to specify the correct item based on the string (will have to be done somewhat often, 
# there are many cases that must be user reviewed because the wiki can't just list the items in order)
# Return "none" if item name is specified as "BAD"
def manualDefer(string): 
    print("Manually deferring...") 
    print("Given string: " + string) 
    item_name = raw_input("Enter the correct item name: ")
    if item_name.upper() == "BAD":
        print("Invalid item recognized! Returning None.")
        return None
    print("Thank you!") 
    item_num = raw_input("Enter the correct item amount: ") 

    # Assume no hacky input for now. TODO: Make it still capture and save the additional comments automatically
    return (item_name, int(item_num))

# Process a string and return a tuple consisting of the item name, and the quantity
# of the item as specified by the string. In cases where the regex is unfamiliar, 
# defer to a manual entry of the item into the list.
def processString(string):

    # Split the regex strings into groups based on intended functionality 

    #multi_item_check = r"(\*(\d|,)+) \[\[((\w+ *)+)\]\][^\(]*(\((.*)\))*"
    item_catch_str = r"\[\[((\w+[ ,-,']*)+)\]\]"
    note_catch_str = r"[^\(]*(\((.*)\))*"
    single_item_str = r"(\* *A(n)*){1} "
    multi_item_str = r"(\* *(\d|,)+) "
    multi_range_str = r"(\* *(\d|,)+)-(\*(\d|,)+) "
    or_search = "or \[\["

    # If it is X or Y, there are too many variables about which is the correct item, so defer to manual review
    # or else it will likely be saved as an incorrect item 
    or_match = re.search(or_search, string) 
    if or_match: 
        return manualDefer(string)

    generic_multi_check = r"\*" + item_catch_str + r"s( )*" + note_catch_str
    generic_multi_match = re.match(generic_multi_check,string)
    # To do: Return unspecified quantity
    if generic_multi_match:
        return ((generic_multi_match.groups()[0]).split("|")[0], 999)


    generic_check = r"\*" + item_catch_str + note_catch_str
    generic_match = re.match(generic_check,string)
    if generic_match:
        return ((generic_match.groups()[0]).split("|")[0], 1)

    single_item_check = single_item_str + item_catch_str + note_catch_str
    single_item_match = re.match(single_item_check, string)

    if single_item_match: 
        return ((single_item_match.groups()[2]).split("|")[0], 1)
    
    multi_item_check = multi_item_str + item_catch_str + note_catch_str

    multi_item_match = re.match(multi_item_check, string) 
   
    # TO DO: Change return type to return an object containing: item name, item quantity, 
    # array of additional notes, nature of item quantity (distinguish exact amount vs
    # an optional range of amounts) ** Probably make item name and quantity an array too for OR
    # comparisons, so when it is time to display items, it is easy to display X OR Y 
    # Additional category: unspecified number (common general case) 

    if multi_item_match:
        num_amount = int(multi_item_match.groups()[0].translate(None, ''.join([',','*'])))
        item_name = multi_item_match.groups()[2]
        # The split is done so (Monkey corpse|corpse) just becomes monkey corpse for example (it is unclear
        # if the thing after the | is ever useful
        return (item_name.split("|")[0],num_amount)
   

    multi_range_check = multi_range_str + item_catch_str + note_catch_str

    multi_range_match = re.match(multi_range_check, string) 
    
    if multi_range_match:
        num_amount = int(multi_item_match.groups()[1].translate(None, ''.join([',','*'])))
        item_name = multi_item_match.groups()[3]
        return (item_name.split("|")[1],num_amount)

    # when in doubt, defer manually
    return manualDefer(string) 

# Get the scraped raw list back, and take the steps to separate it
with open('item_list.pickle', 'rb') as data: 
    item_list = pickle.load(data)


test_list = item_list["One Small Favour"]

test_split = test_list.split(r"\\n")
test_split[0] = test_split[0].strip('items":"')

print(test_split) 

complete_item_list = [] 

for string in test_split:
    rec_limiter = re.search("Recommended:", string, re.IGNORECASE) 
    # This should've been filtered out, but for now, break whenever reached recommended items
    # (Currently only focused on needed items)
    if rec_limiter: 
        print("Recommended portion reached! String: " + string) 
        break
    result = processString(string)
    if result:
        complete_item_list.append(("Item name: " + result[0] + " ||| Num amount: " + str(result[1])))

for item in complete_item_list:
    print(item) 
