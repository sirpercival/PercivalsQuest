#
#  pq_utilities.py
#  part of Percival's Quest RPG

import json

def collapse_stringlist(thelist, sortit = False, addcounts = False):
    """Remove duplicate elements from a list, possibly sorting it in the process."""
    collapsed = []
    [collapsed.append(i) for i in thelist if not collapsed.count(i)]
    if sortit:
        collapsed = sorted(collapsed)
    if not addcounts:
        return collapsed
    for j,i in enumerate(collapsed):
        if type(i) is list:
            i = i[0]
        count = thelist.count(i)
        tag = ' x'+str(count) if count > 1 else ''
        collapsed[j] += tag
    return collapsed


def atk_roll(attack, defense, attack_adjust = 0, defense_adjust = 0):
    """Handle any opposed roll ('attack' roll)."""
    if attack[1] <= attack[0]:
        attack_res = attack[0] + attack_adjust
    else:
        attack_result = random.choice([random.randint(attack[0],attack[1]) for i in range(0,6)]) + attack_adjust    
    if defense[1] <= defense[0]:
        defense_result = defense[0] + defense_adjust 
    else:
        defense_res = random.choice([random.randint(defense[0],defense[1]) for i in range(0,6)]) + defense_adjust
    return attack_result - defense_result


def choose_from_list(prompt, options, rand = False, character = None, allowed = []):
    """Accept user input from a list of options."""
    allowed = [i.lower() for i in allowed]
    allow_sheet = "sheet" in allowed
    allow_help = "help" in allowed
    allow_equip = "equip" in allowed
    choice = get_user_input(prompt,character,allow_sheet,allow_help,allow_equip)
    while choice.lower() not in [i.lower() for i in options]:
        if rand and choice.lower() == "random":
            return random.choice(options)
        print "Sorry, I didn't understand your choice. Try again?"
        choice = get_user_input(prompt,character,allow_sheet,allow_help,allow_equip)
    for i in options:
        if i.lower() == choice.lower():
            return i

def confirm_quit():
    print "Remember that your last save was the last time you rested.", '\n'
    choice = raw_input("Are you sure you want to quit (y/n)? ")
    if choice.lower() in ["y","yes","quit"]:
        quit()

def get_user_input(prompt, character = None, allow_sheet = False, allow_help = False, allow_equip = False):
    user_input = raw_input(prompt)
    if allow_sheet and character and user_input.lower() == "sheet":
        character.tellchar()
        return get_user_input(prompt, character = character, allow_sheet = allow_sheet, allow_help = allow_help,
            allow_equip = allow_equip)
    if allow_help and user_input.lower() == "help":
        pq_help()
        return get_user_input(prompt, character = character, allow_sheet = allow_sheet, allow_help = allow_help,
            allow_equip = allow_equip)
    if allow_equip and character and user_input.lower() == "equip":
        character.equip()
        return get_user_input(prompt, character = character, allow_sheet = allow_sheet, allow_help = allow_help,
            allow_equip = allow_equip)
    if user_input.lower() == "quit":
        confirm_quit()
        return get_user_input(prompt, character = character, allow_sheet = allow_sheet, allow_help = allow_help,
            allow_equip = allow_equip)
    return user_input
            
def pq_help():
    with open('pq_help_strings.json') as f:
        help_topics = json.load(f)
    print "Help topics: "+", ".join(help_topics.keys())+"; Exit to return to game."
    topic = choose_from_list("Help> ",[help.topics.keys(),"Exit"])
    while topic != "Exit":
        print "TOPIC: "+topic.upper(), '\n'
        print help_topics[topic], '\n'