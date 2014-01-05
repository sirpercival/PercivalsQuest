#
#  percivalsquest.py
#  part of Percival's Quest RPG (duh)

logo = """
   ()    
   )(     
o======o           
   ||              
   ||    ___              _               _ _        ____                   _    
   ||   / _ \___ _ __ ___(_)_   ____ _| ( )__    /___ \_   _  ___  ___| |_ 
   ||  / /_)/ _ \ '__/ __| \ \ / / _` | |/ __|  //  / / | | |/ _ \/ __| __| 
   || / ___/  __/ | | (__| |\ V / (_| | |\__ \ / \_/ /| |_| |  __/\__ \ |_ 
   || \/    \___|_|  \___|_| \_/ \__,_|_||___/ \___,_\ \__,_|\___||___/\__| 
   ||                                                                     
   ||                            copyright 2013
   || 
   \/ 

"""

from pq_rpg import *
from pq_utilities import *

def town(rpg):
    """Maintain interactions with the town of North Granby."""
    print "Where would you like to go?",'\n', "Options: Home, Questhall, " \
        "Shop, Shrine, or Dungeon [Level#]"
    destinations = ["Dungeon", "Home", "Questhall", "Quest", "Shop", "Shrine"] + \
        ["Dungeon "+str(i) for i in range(1,rpg.maxdungeonlevel)]
    go = choose_from_list("Town> ",destinations,character=rpg.character,
        rand=False,allowed=["sheet","help","equip"])
    if go == "Home":
        print "You hit the sack. Once you've annoyed all the bedbugs with " \
            "your ineffectual fists, you lay down and sleep.", '\n'
        rpg.character.sleep()
        rpg.save()
        town(rpg)
        return
    elif go in ["Questhall", "Quest"]:
        print "You head to the Questhall.", '\n'
        rpg.questhall()
        town(rpg)
        return
    elif go == "Shop":
        print "You head into the shop.", '\n'
        rpg.visit_shop()
        town(rpg)
        return
    elif go == "Shrine":
        print "You head into the Shrine.", '\n'
        rpg.visit_shrine()
        town(rpg)
        return
    else:
        go = go.split()
        rpg.destination("start")
        if go[0] == "Dungeon" and len(go) == 1:
            rpg.dungeonlevel = 1
        else:
            rpg.dungeonlevel = int(go[1])
        print "You head into the Dungeon, level "+str(rpg.dungeonlevel)+".", '\n'
        dungeon(rpg)
        return

def dungeon(rpg):
    """Maintain interaction with the dungeon"""
    actions = ["Explore","Backtrack","Leave"]
    print "You're in the dank dark dungeon. What do you want to do?", \
        '\n', "Options: "+", ".join(actions)
    do = choose_from_list("Dungeon> ",actions,character=rpg.character,
        rand=False,allowed=["sheet","help","equip"])
    if go == "Leave":
        if rpg.whereareyou != "start":
            print "You can't leave from here; you have to backtrack to the start of the level.", '\n'
            dungeon(rpg)
            return
        else:
            rpg.destination("town")
            print "You head back to town.", '\n'
            town(rpg)
            return
    elif go == "Backtrack":
        if rpg.whereareyou == "start":
            print "You're already at the beginning of the level, Captain Redundant.", '\n'
            dungeon(rpg)
            return
        if rpg.check_bactrack():
            print "You successfully find your way back to the beginning of the level.", '\n'
            rpg.destination("start")
            dungeon(rpg)
            return
        else:
            print "On your way back, you get lost! You find yourself in another room of the dungeon..."
            rpg.destination("dungeon")
            rpg.explore()
            dungeon(rpg)
            return
    elif go == "Explore":
        rpg.destination("dungeon")
        rpg.explore()
        if rpg.character.dead:
            deadchar(rpg)
        else:
            dungeon(rpg)
        return
        
def deadchar(rpg):
    """Deal with character death"""
    print "What would you like to do? Options: Generate (a new character), Load, Quit", '\n'
    do = choose_from_list("Dead> ",["Generate","Load","Quit"],character=rpg.character,
        rand=False,allowed=["sheet","help"])
    if do == "Quit":
        confirm_quit()
        deadchar(rpg)
        return
    if do == "Load":
        d = shelve.open(os.path.expanduser('data/pq_saves.db'))
        rpg = d[player_name]
        d.close()
        print "Game successfully loaded!", '\n', "You begin in the town square.", '\n'
        town(rpg)
        return
    if do == "Generate":
        rpg = generate(rpg)
        print "You begin in the town square.", '\n'
        town(rpg)
        return
        
def generate(rpg):
    """Wrapper for making a new character"""
    print "Time to make a new character! It'll be saved under this player name. Here we go!", '\n'
    rpg.character.chargen(player_name)
    rpg.save()
    msg = "In the town of North Granby, the town militia has recently discovered that the plague of monsters "\
        "harrassing the townspeople originates from a nearby dungeon crammed with nasties. " \
        "As the resident adventurer, the Mayor of North Granby (a retired adventurer by the name of Sir Percival)" \
        " has recruited you to clear out the dungeon."
    print msg, '\n'
    return rpg

def main():
    """Initialize and start the game session"""
    print logo, '\n'
    print "Welcome to Percival's Quest! This is a solo (as of yet) random dungeoncrawl rpg written " \
        "in python by the ever-resourceful (and extremely humble) sirpercival." 
    player_name = raw_input("Please enter your player name> ")
    msg = "Welcome, "+player_name+"!"
    rpg_instance = PQ_RPG()
    d = shelve.open(os.path.expanduser('data/pq_saves.db'))
    if player_name in d:
        msg += " You currently have a game saved. Would you like to load it?"
        print msg, '\n'
        loadit = raw_input("Load (y/n)> ")
        if loadit.lower() in ["y","yes","load"]:
            rpg = d[player_name]
        else:
            newgame = True
    else:
        print msg + "You don't have a character saved...", '\n'
        newgame = True
    d.close()
    if newgame:
        rpg = generate(rpg)
    msg = "You begin in the town square. \n"
    msg += "(Please note that at almost any prompt, you can choose Sheet to look at your charsheet, " \
        "Equip to change your equipment, Help to enter the help library, or Quit to quit.)"
    print msg, '\n'
    rpg.telltown()
    town(rpg)
    
if __name__ == '__main__':
    main()