"""
This is the big one -- handles the actual RPG instance and management. 
The Town and Dungeon processing is in the main module, though.
"""
#
#  pq_rpg.py
#  part of Percival's Quest RPG

import random, textwrap
from pq_characters import PQ_Character
from pq_enemies import PQ_Quest
from pq_combat import PQ_Combat
from pq_puzzle import PQ_Puzzle
from pq_equipment import pq_treasuregen, pq_item_worth, pq_gear, pq_magic
from pq_utilities import choose_from_list, color, get_user_input, \
    collapse_stringlist, save, send_to_console
from pq_namegen import sandgen, godgen

def display_itemlist(itemlist, sell = False):
    """Format a list of items for display in the shop."""
    unique_items = collapse_stringlist(itemlist, sortit = True, \
        addcounts = False)
    items_with_counts = collapse_stringlist(itemlist, sortit = True, \
        addcounts = True)
    items = []
    for j, i in enumerate(unique_items):
        price = pq_item_worth(i)
        if sell:
            price = max([price / 2, 1])
        if i.lower() in [x.lower() for x in pq_magic['ring'].keys()]:
            items.append(str(j + 1) + ". Ring of " + items_with_counts[j] + \
                " (" + str(price) + ")")
        else:
            items.append(str(j + 1) + ". " + items_with_counts[j] + \
                " (" + str(price) + ")")
    return items

class PQ_RPG(object):
    """RPG instance declaration"""
    def __init__(self, player):
        """Initialize the game session."""
        self.character = PQ_Character(self)
        self.player_name = player
        self.questlevel = 0
        self.dungeonlevel = 1
        self.maxdungeonlevel = 1
        self.quest = {}
        self.store = [
            pq_gear['rarmor'][random.choice(pq_gear['rarmor'].keys())]['0'],
            pq_gear['rweapon'][random.choice(pq_gear['rweapon'].keys())]['0']
            ]
        self.whereareyou = "Town"
        self.shrinexp = 0
        self.shrinegp = 0
        self.combat = None
        self.puzzle = None
        self.gods = ["",""]
                
    def new_char(self):
        """Re-initialize for a new character"""
        self.character.dead = 0
        self.questlevel = 0
        self.dungeonlevel = 1
        self.maxdungeonlevel = 1
        self.quest = {}
        self.character.queststatus = "inactive"
        self.store = [
            pq_gear['rarmor'][random.choice(pq_gear['rarmor'].keys())]['0'],
            pq_gear['rweapon'][random.choice(pq_gear['rweapon'].keys())]['0']
            ]
        
    def destination(self, goto):
        """Set the destination of the character."""
        self.whereareyou = goto

    def check_backtrack(self):
        """Determine if the character successfully backtracks
        to the start of the level.
        Backtrack chance is 50% for Mind = dungeon level,
        asymptotic to 1/6 for Mind < dungeon level,
        asymptotic to 5/6 for Mind > dungeon level
        """
        differential = self.character.stats[4] - self.dungeonlevel
        if differential < 0:
            cutoff = float(3 - differential) / float(6 - 6 * differential)
        else:
            cutoff = float(3 + 5 * differential) / float(6 + 6 * differential)
        return random.random() < cutoff

    def init_quest(self, level):
        """Initialize a Quest! With a Capital Q!"""
        self.quest = PQ_Quest()
        self.quest.gen(level)

    def addshopitem(self):
        """Add an item to the shop."""
        shop_items = pq_treasuregen(self.character.level[1])
        for i in shop_items.keys():
            if shop_items[i] and i != 'gp' and shop_items[i] not in self.store:
                self.store.append(shop_items[i])
    
    def questhall(self):
        """The character enters the Questhall! It's super effective!"""
        if self.character.queststatus == "active":
            msg = "As you enter the Questhall, Mayor Percival looks at you " \
                "expectantly. " + color.BOLD + "'Did you collect the item " \
                "and defeat the monster? No? Well, then, get back out there!" \
                " I suggest you try Dungeon level " + str(self.questlevel) + \
                ".'" + color.END
            send_to_console(textwrap.fill(msg))
            return
        self.questlevel += 1
        self.init_quest(self.questlevel)
        if self.character.queststatus == "inactive":
            msg1 = "In the Questhall, Mayor Percival frets behind his desk. " \
                + color.BOLD + "'" + self.character.name[0] + "! Just the " \
                "person I was looking for. There's... something I need you " \
                "to do. See, there are rumors of a horrible creature, " \
                "called " + self.quest.name + ", roaming the dungeon. " + \
                self.quest.description + "This monstrosity " \
                "draws its power from " + self.quest.artifact[0] + ", " + \
                self.quest.artifact[1].lower() + " I need you to go into " \
                "the dungeon, kill that beast, and bring back the artifact " \
                "so my advisors can destroy it. The townspeople will be " \
                "very grateful, and you'll receive a substantial reward! " \
                "Now, get out of here and let me finish my paperwork.'" \
                + color.END
            send_to_console(textwrap.fill(msg1))
        elif self.character.queststatus == "complete":
            send_to_console("Mayor Percival looks up excitedly. " + color.BOLD + \
                "'You have it! Well, thank my lucky stars. " \
                "You're a True Hero, " + self.character.name[0] + "!'" + \
                color.END)
            exp = 5 * (self.questlevel - 1)
            gold = int(random.random() * 2 + 1) * exp
            send_to_console("You gain " + str(exp) + " experience and " + str(gold) \
                + " gp!")
            self.character.complete_quest(exp, gold)
            if self.character.level[0] >= self.character.level[1] * 10:
                self.character.levelup()
            self.addshopitem()
            msg1 = "Percival clears his throat hesitantly. " + color.BOLD + \
                "'Since I have you here, there... have been rumors of " \
                "another problem in the dungeon. "
            msg2 = self.quest.name + " is its name. " + self.quest.description
            msg3 = " The source of its power is " + self.quest.artifact[0] + \
                ", " + self.quest.artifact[1] + " Will you take this quest, " \
                "same terms as last time (adjusting for inflation)? Yes? " \
                "Wonderful! Now get out.'" + color.END
            send_to_console(textwrap.fill(msg1 + msg2 + msg3))
        self.character.queststatus = "active"
        
    def godownstairs(self):
        """Head to the next lower dungeon level."""
        self.whereareyou = "start"
        self.dungeonlevel += 1
        if self.dungeonlevel > self.maxdungeonlevel:
            self.maxdungeonlevel = self.dungeonlevel
            self.addshopitem()
        send_to_console("You head down the stairs to level " + str(self.dungeonlevel))
        return

    def explore(self):
        """Explore the dungeon!"""
        room = random.choice([random.randint(1, 20) for i in range(6)])
        self.whereareyou = "dungeon"
        if room <= 2:
            send_to_console("You find a flight of stairs, leading down! " \
                "Go down, or Stay?")
            choice = choose_from_list("Stairs> ", \
                ["down", "go down", "stay"], rand=False, \
                character=self.character, allowed=['sheet', 'help', 'equip'])
            if choice != "stay":
                self.godownstairs()
            else:
                send_to_console("You decide to stick around on level " + \
                    str(self.dungeonlevel) + " a little while longer.")
            return
        elif room > 2 and room <= 5:
            msg = "You found a chest! "
            chest = pq_treasuregen(self.dungeonlevel)
            self.character.defeat_enemy(0, chest)
            loot = []
            for i in chest.keys():
                if chest[i]:
                    if i == 'gp':
                        loot.append(str(chest[i]) + " gp")
                    elif i == 'ring':
                        loot.append("a Ring of " + chest[i])
                    else:
                        loot.append("a " + chest[i])
            if not loot:
                msg += "Sadly, it was empty."
            else:
                msg += "Inside, you find " + ", ".join(loot) + "."
            send_to_console(msg)
            return
        elif room > 5 and room <= 8:
            msg = "The room echoes with a hollow emptiness, and you " \
                "reflect on the vagaries of living life alone... Then " \
                "you eat" + sandgen() + ", and get ready to kill more things."
            send_to_console(textwrap.fill(msg), "\nYou regain " + \
                str(self.dungeonlevel) + " hp and sp!")
            self.character.sammich(self.dungeonlevel)
            return
        elif room > 8 and room <= 10:
            self.whereareyou = "puzzle"
            self.puzzle = PQ_Puzzle(self.dungeonlevel, self.character)
            self.puzzle.puzzleinit()
        #elif room > 10 and room <= 12:
        #    self.whereareyou = "trap"
        #
        #elif room > 12:
        elif room > 10:
            msg = "You've stumbled on an enemy! It seems to be... "
            questcheck = self.maxdungeonlevel - self.questlevel
            cutoff = float(1 + questcheck) / float(10 + 2 * questcheck)
            if self.dungeonlevel == self.questlevel and self.quest and \
                self.character.queststatus == "active" and random.random() \
                < cutoff:
                self.combat = PQ_Combat(self.dungeonlevel, self.character, \
                    self.quest)
                msg += self.quest.name+'!'
            else: 
                self.combat = PQ_Combat(self.dungeonlevel, \
                    self.character, None)
                if self.dungeonlevel >= 10:
                    msg += self.combat.enemy.name + '!'
                else:
                    msg += 'a ' + self.combat.enemy.name + '!'
            if self.combat.turnorder[0] == 'player':
                msg += ' You get the jump on it.'
            else:
                msg += ' It gets the jump on you.'
            send_to_console(msg)
            self.whereareyou = "combat"
            self.combat.advance_turn()
            self.combat = None

    def visit_shop(self):
        """Wrapper for shopping"""
        send_to_console("The shopkeep greets you cheerfully. 'Welcome, hero! " \
            "What can I do for you?'")
        self.transactions()
    
    def transactions(self):
        """Handle transactions with the shop."""
        msg1 = "His current inventory is: "
        inventory = display_itemlist(self.store)
        inventory_basic = collapse_stringlist(self.store, sortit = True, \
            addcounts = False)
        if not inventory:
            msg1 += "Nothing!"
        else:
            msg1 += " ".join(inventory) + "."
        send_to_console(textwrap.fill(msg1))
        msg2 = "Your current loot bag contains " + \
            str(self.character.loot['gp']) + " gp, and: "
        lootbag = display_itemlist(self.character.loot['items'], True)
        lootbag_basic = collapse_stringlist(self.character.loot['items'], \
            sortit = True, addcounts = False)
        if not lootbag:
            msg2 += "Nothing!"
        else:
            msg2 += " ".join(lootbag) + "."
        send_to_console(textwrap.fill(msg2))
        send_to_console("Buy Item# [Amount], Sell Item# [Amount], or Leave.")
        buylist = [" ".join(["buy", str(i), str(j)]) for i in range(1, \
            len(inventory) + 1) for j in range(1, self.store.count( \
            inventory_basic[i - 1]) + 1)] + ["buy " + str(i) for i \
            in range(1, len(inventory) + 1)]
        sellist = [" ".join(["sell", str(i), str(j)]) for i in \
            range(1, len(lootbag) + 1) for j in range(1, self.character.loot[\
            'items'].count(lootbag_basic[i - 1]) + 1)] + \
            ["sell " + str(i) for i in range(1, len(lootbag) + 1)]
        choice = choose_from_list("Shop> ", buylist + sellist + ["leave"], \
            rand=False, character=self.character, allowed=['sheet', 'help'])
        if choice == "leave":
            send_to_console("You leave the shop and head back into the town square.\n")
            return
        else:
            choice = choice.split()
            try:
                item = int(choice[1])
                item = inventory_basic[item - 1] if choice[0] == "buy" \
                    else lootbag_basic[item - 1]
                worth = pq_item_worth(item)
            except ValueError:
                worth = 0
            count = 1 if len(choice) < 3 else choice[2]
            try:
                count = int(count)
            except ValueError:
                count = 1
            if not worth:
                send_to_console("I'm sorry, I don't know what that item is. " \
                    "Can you try again?")
            elif choice[0] == "buy":
                if worth > self.character.loot['gp']:
                    send_to_console("You don't have enough gold to buy that, cheapskate!")
                else:
                    pl = "" if count == 1 else "s"
                    send_to_console("You buy " + str(count) + " " + item + pl + "!")
                    for i in range(count):
                        self.character.buy_loot(item, worth)
                        self.store.remove(item)
            elif choice[0] == "sell":
                pl = "" if count == 1 else "s"
                send_to_console("You sell " + str(count) + " " + item + pl + "!")
                self.character.sell_loot(item, count)
            self.transactions()
        
    def visit_shrine(self):
        """Head to the Shrine of the Unknowable Gods to make offerings."""
        self.gods = godgen(2)
        msg = "The Shrine is mostly deserted at this time of day. " \
            "Two of the altars catch your eye: one (choice 1) to " \
            + self.gods[0] + ", which offers Enlightenment on a sliding " \
            "tithe scale; and one (choice 2) to " + self.gods[1] + ", " \
            "which promises Materialism for a single lump sum of 30,000gp."
        send_to_console(textwrap.fill(msg)+"\nOptions: Choice# Offering, or Leave")
        choice = get_user_input("Shrine> ", character = self.character, \
            options = ["leave", "sheet", "equip", "help"]).lower()
        while choice != "leave":
            choice = choice.split()
            if len(choice) < 2 or (choice[0] != "1" and choice[0] != "2"):
                send_to_console("You need to pick both an altar number (1 or 2) " \
                    "and an offering amount.")
                choice = get_user_input("Shrine> ", \
                    character = self.character, \
                    options = ["leave", "sheet", "equip", "help"]).lower()
                continue
            try:
                offering = int(choice[1])
            except ValueError:
                send_to_console("You need to pick both an altar number (1 or 2) and " \
                    "an offering amount.")
                choice = get_user_input("Shrine> ", \
                    character = self.character, \
                    options = ["leave", "sheet", "equip", "help"]).lower()
                continue
            self.offering(choice[0], offering)
            save(self)
            choice = get_user_input("Shrine> ", \
                    character = self.character, \
                    options = ["leave", "sheet", "equip", "help"]).lower()
        send_to_console("You leave the shrine and head back into the town square.\n")
        
    def offering(self, choice, amount):
        """Give money to tha GODZ"""
        if amount < 0:
            send_to_console(textwrap.fill("You can't take money out of the offering " \
                "bowl, not without offending " + self.gods[int(choice) - 1] + \
                ", which you do NOT want to do."))
            return
        elif amount == 0:
            send_to_console("Nothing ventured, nothing gained.")
            return
        elif amount > self.character.loot['gp']:
            send_to_console(textwrap.fill("You don't have enough gold for that, man. " \
                "Go back to the dungeon and make some scratch! " \
                "(Or at least, put less in the offering bowl.)"))
            return
        if choice == '1':
            try:
                self.shrinegp += amount
            except AttributeError:
                self.shrinegp = amount
            from math import sqrt
            newexp = int((1. + sqrt(1. + 8. * float(self.shrinegp))) / 4.)
            try:
                netexp = newexp - self.shrinexp
            except AttributeError:
                netexp = newexp
            self.shrinexp = newexp
            msg = "The bounds of your mind are expanded by a moment of " \
                "attention from " + self.gods[0] + "; this may not actually " \
                "be a good thing, but at least you gain " + str(netexp) + \
                " experience."
            send_to_console(textwrap.fill(msg))
            self.character.defeat_enemy(netexp, {'gp':-amount})
            if self.character.level[0] >= self.character.level[1] * 10:
                self.character.levelup()
            return
        elif str(choice) == '2':
            if amount < 30000:
                msg = "Nothing happens except for a feeling of insufficient " \
                    "funds... you scoop the gold back out of the offering " \
                    "bowl before anyone sees you, cheapskate."
                send_to_console(textwrap.fill(msg))
                return
            typechoice = random.choice([random.randint(0, 2) \
                for i in range(6)])
            type1 = ["ring", "rarmor", "rweapon"][typechoice]
            type1a = ["ring", "armor", "weapon"][typechoice]
            if type1 == "ring":
                riches = random.choice([random.choice(pq_magic[\
                'ring'].keys()) for i in range(6)])
            else:
                type2 = random.choice([random.choice(pq_gear[\
                    type1].keys()) for i in range(6)])
                rating = random.choice([random.randint(0, 8) \
                    for i in range(6)])
                if rating == 0:
                    riches = pq_gear[type1][type2]['0']
                else:
                    magic = random.choice([random.randint(max([rating - 5, \
                        0]), min([3, rating])) for i in range(6)]) \
                        if rating < 8 else 3
                    nonmagic = str(rating - magic)
                    riches = '' if magic == 0 else pq_magic[type1]\
                        [type2][str(magic)] + ' '
                    riches += pq_gear[type1][type2][nonmagic]
            self.character.defeat_enemy(0, {'gp':-amount, type1a:riches})
            msg = "The gold disappears from the offering bowl"
            if amount > 30000:
                msg += " (with a thank you very much for the extra donation)"
            msg += ", and you discover a "
            if type1a == "ring":
                msg += "Ring of "
            msg += riches + " in your lootbag!"
            send_to_console(textwrap.fill(msg))
            return
