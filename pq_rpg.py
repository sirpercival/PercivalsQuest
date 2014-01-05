#
#  pq_rpg.py
#  part of Percival's Quest RPG

"""
This is the big one -- handles the actual RPG instance and management. 
Player input handling, however, will be in a different file.
"""

import random
from pq_characters import *
from pq_enemies import *
from pq_combat import *
from pq_puzzle import *
from pq_equipment import *
from pq_utilities import *
from pq_namegen import sandgen, godgen

class PQ_RPG(object):
	def __init__(self,player):
        """Initialize the game session."""
		self.character = PQ_Character()
		self.player_name = player
		self.questlevel = 0
		self.dungeonlevel = 1
		self.maxdungeonlevel = 1
		self.quest = {}
		self.store = [pq_gear['rarmor'][random.choice(pq_gear['rarmor'].keys())][0],
            pq_gear['rweapon'][random.choice(pq_gear['rweapon'].keys())][0]]
		self.whereareyou = "Town"
		self.shrinexp = 0
		self.shrinegp = 0
				
	def new_char(self):
        """Re-initialize for a new character"""
		self.character.death = 0
		self.questlevel = 0
		self.dungeonlevel = 1
		self.maxdungeonlevel = 1
		self.quest = {}
		self.character.queststatus = "inactive"
		self.store = ['Dagger']
        
    def destination(self,go):
        """Set the destination of the character."""
        self.whereareyou = go

	def check_backtrack(self):
        """Determine if the character successfully backtracks to the start of the level."""
		differential = self.character.stats[4] - self.dungeonlevel
		if differential < 0: #Backtrack chance is 50% for Mind = dungeon level
			cutoff = float(3 - chk)/float(6 - 6 * chk) #asymptotic to 1/6 for Mind < dungeon level
		else:
			cutoff = float(3 + 5 * chk)/float(6 + 6 * chk) #asymptotic to 5/6 for Mind > dungeon level
		return random.random() < cutoff

	def init_quest(self, level):
        """Initialize a Quest! With a Capital Q!"""
		self.quest = PQ_Quest()
		self.quest.gen(level)

	def addshopitem(self):
        """Add an item to the shop. Currently, this algorithm makes the shop suck."""
		shop_items = pq_treasuregen(self.questlevel)
		for i in shop_items.keys():
			if shop_items[i] and i != 'gp' and shop_items[i] not in self.store:
                self.store.append(shop_items[i])
		
	def telltown(self,start = False):
        """Describe the town square."""
		msg = "You begin in the town square. " if start else ""
		msg += "To the East is your humble abode and warm bed; to the North, the General Store where various and sundry goods may be purchased; "
		msg += "to the West, the Questhall where the mayor makes his office; "
		msg += "to the Northwest, the local Shrine to the Unknowable Gods; and to the South lie the gates of the city, leading out to the Dungeon."
		print msg, '\n'
	
	def questhall(self):
        """The character enters the Questhall! It's super effective!"""
		if self.character.queststatus == "active":
            msg = "As you enter the Questhall, Mayor Percival looks at you expectantly. 'Did you collect the item and defeat the monster? "
			msg += "No? Well, then, get back out there! I suggest you try Dungeon level "+str(self.questlevel)+"."
            print msg, '\n'
			return
		self.questlevel += 1
		self.init_quest(self.questlevel)
		if self.character.queststatus == "inactive":
			msg1 = "In the Questhall, Mayor Percival frets behind his desk. '"+self.character.name+"! Just the person I was looking for. "
            msg1 += "There's... something I need you to do. See, there are rumors of a horrible creature, called "+self.quest.name+", roaming the dungeon."
			msg2 = "This monstrosity draws its power from "+self.quest.arty[0]+","+self.quest.arty[1].lower()+" I need you to go into the dungeon, "
            msg2 += "kill that beast, and bring back the artifact so my advisors can destroy it. The townspeople will be very grateful, "
            msg2 += "and you'll receive a substantial reward! Now, get out of here and let me finish my paperwork.'"
			print msg1, '\n', self.quest.description, '\n', msg2, '\n'
		elif self.character.queststatus == "complete":
			print "Mayor Percival looks up excitedly. 'You have it! Well, thank my lucky stars. You're a True Hero, "+self.character.name+"!'", '\n'
			exp = 5 * (self.questlevel-1)
			gp = int(random.random()*2+1) * exp
			print "You gain "+str(exp)+" experience and "+str(gp)+" gp!", '\n'
			self.character.complete_quest(exp,gp)
			limit = self.character.level*10
			if self.character.exp + exp >= limit:
                self.character.levelup()
			self.addshopitem()
			msg1 = "Percival clears his throat hesitantly. 'Since I have you here, there... have been rumors of another problem in the dungeon. "
			msg2 = self.quest.name+" is its name. "+self.quest.desc
			msg3 = "The source of its power is "+self.quest.arty[0]+", "+self.quest.arty[1]+" Will you take this quest, same terms as last time "
            msg3 += "(adjusting for inflation)? Yes? Wonderful! Now get out.'"
            print msg1, '\n', msg2, '\n', msg3, '\n'
        self.character.queststatus = "active"
		
	def godownstairs(self):
        """Head to the next lower dungeon level."""
		self.whereareyou = "start"
		self.dungeonlevel += 1
		if self.dungeonlevel > self.maxdungeonlevel:
			self.maxdungeonlevel = self.dungeonlevel
		print "You head down the stairs to level "+str(self.dungeonlevel), '\n'
		return

	def explore(self):
        """Explore the dungeon!"""
		room = random.choice([random.randint(1,20) for i in range(0,6)])
        self.whereareyou = "dungeon"
		if room <= 2:
			print "You find a flight of stairs, leading down! Go down, or Stay?", '\n'
            choice = choose_from_list("Stairs> ",["down","go down","stay"],rand=False,
                character=self.character,allowed=['sheet','help','equip'])
            if choice != "stay":
                self.godownstairs()
            else:
                print "You decide to stick around on level "+str(self.dungeonlevel)+" a little while longer.", '\n'
			return
		elif room > 2 and room <= 5:
			msg = "You found a chest! "
			chest = pq_treasuregen(self.dungeonlevel)
			self.character.defeat_enemy(0,chest)
			loot = []
			for i in chest.keys():
				if chest[i]:
					if i == 'gp':
						loot.append(str(chest[i])+" gp")
					elif i == 'ring':
						loot.append("a Ring of "+chest[i])
					else:
						loot.append("a "+chest[i])
			if not loot:
				msg += "Sadly, it was empty."
			else:
				msg += "Inside, you find "+", ".join(loot) + "."
			print msg, '\n'
			return
		elif room > 5 and room <= 8:
			msg = "The room echoes with a hollow emptiness, and you reflect on the vagaries of living life alone... "
            msg += "Then you eat"+sandgen()+", and get ready to kill more things."
			print msg, '\n', "You regain "+str(self.dungeonlevel)+" hp and sp!", '\n'
			self.character.sammich(self.dungeonlevel)
            return
		elif room > 8 and room <= 10:
			self.whereareyou = "puzzle"
			self.puzzle = PQ_Puzzle(self.dungeonlevel,self.character)
			self.puzzle.puzzleinit()
		elif room > 10:
			msg = "You've stumbled on an enemy! It seems to be... "
			questcheck = self.maxdgnlevel - self.questlevel #goes from .1 to .5 asymptotically as you adventure farther
			cutoff = float(1 + questcheck)/float(10 + 2*questcheck)
			if self.dungeonlevel == self.questlevel and self.quest and self.character.queststatus == "active" and random.random() < cutoff:
				self.combat = PQ_Combat(self.dungeonlevel, self.character, self.quest)
				msg += self.quest.name+'!'
			else: 
				self.combat = PQ_Combat(self.dungeonlevel, self.character, None)
				if self.dungeonlevel >= 10:
					msg += self.combat.enemy.name+'!'
				else:
					msg += 'a '+self.combat.enemy.name+'!'
			if self.combat.turnorder[0] == 'player':
				msg += ' You get the jump on it.'
			else:
				msg += ' It gets the jump on you.'
			print msg, '\n'
			self.whereareyou = "combat"
			self.combat.advance_turn()
            self.combat = None

	def display_itemlist(self,itemlist,sell = False):
        """Format a list of items for display in the shop."""
		items = collapse_stringlist(itemlist, sortit=True, addcounts=True)
		for j,i in enumerate(items):
			price = pq_item_worth(i)
			if sell:
				price = max([price/2,1])
			if i.lower() in [x.lower() for x in pq_magic['ring'].keys()]:
				items[j] = (str(j+1)+". Ring of "+i+" ("+str(price)+")"
			else:
				items[j] = (str(j+1)+". "+i+" ("+str(price)+")"
		return items

	def visit_shop(self):
		print "The shopkeep greets you cheerfully. 'Welcome, hero! What can I do for you?'", '\n'
        msg1 = "His current inventory is: "
		inventory = self.display_itemlist(self.store)
        inventory_basic = collapse_stringlist(self.store,sortit=True,addcounts=False)
		if not inventory:
			msg1 += "Nothing!"
		else:
			msg1 += " ".join(inventory) + "."
		print msg1, '\n'
        self.transactions()
    
    def transactions(self)
		msg2 = "Your current loot bag contains "+str(self.character.loot['gp'])+" gp, and: "
		lootbag = self.display_itemlist(self.character.loot['items'],True)
        lootbag_basic = collapse_stringlist(self.character.loot['items'],sortit=True,addcounts=False)
		if not lootbag:
			msg2 += "Nothing!"
		else:
			msg2 += " ".join(lootbag) + "."
		print msg2, '\n' "Buy Item# [Amount], Sell Item# [Amount], or Leave."
        buylist = [" ".join("buy",str(i),str(j)) for i in range(1,len(inventory)+1) 
            for j in range(1,self.store.count(inventory_basic[i-1]))] + 
            ["buy "+str(i) for i in range(1,len(inventory)+1)]
        sellist = [" ".join("sell",str(i),str(j)) for i in range(1,len(lootbag)+1) 
            for j in range(1,self.character.loot['items'].count(lootbag_basic[i-1]))] + 
            ["sell "+str(i) for i in range(1,len(lootbag)+1)]
        choice = choose_from_list("Shop> ",[buylist,sellist,"leave"],rand=False,
            character=self.character,allowed=['sheet','equip','help'])
		if choice != "leave":
            choice = choice.split()
            item = choice[1]
            count = 1 if len(choice) > 2 else choice[2]
            if choice[0] == "buy":
                for i in range(count):
                    self.character.buy_loot(item,pq_item_worth(item))
                    self.store.remove(item)
            elif choice[0] == "sell":
                self.character.sell_loot(item,count)
            self.transactions()
        print "You leave the shop and head back into the town square.",'\n'
		
	def visit_shrine(self):
        """Head to the Shrine of the Unknowable Gods to make offerings."""
		self.gods = godgen(2)
		msg = "The Shrine is mostly deserted at this time of day. Two of the altars catch your eye: one (choice 1) to "+self.gods[0]+", which offers Enlightenment on a sliding tithe scale; "
		msg += "and one (choice 2) to "+self.gods[1]+", which promises Materialism for a single lump sum of 30,000gp."
        print msg, '\n', "Choice# Offering, or Leave"
		choice = get_user_input("Shrine> ",character=self.character,allow_sheet=True,allow_equip=True,allow_help=True).lower()
        while choice != "leave":
            choice = choice.split()
            if len(choice) < 2 or (choice[0] != "1" and choice[0] != "2"):
                print "You need to pick both an altar number (1 or 2) and an offering amount."
                choice = raw_input("Shrine> ").lower()
                continue
            try:
                offering = int(choice[1])
            except:
                print "You need to pick both an altar number (1 or 2) and an offering amount."
                choice = raw_input("Shrine> ").lower()
                continue
            self.offering(choice[0],offering)
            choice = get_user_input("Shrine> ",character=self.character,allow_sheet=True,allow_equip=True,allow_help=True).lower()
        print "You leave the shrine and head back into the town square.",'\n'
		
	def offering(self,choice,amount):
		if amount < 0:
			print "You can't take money out of the offering bowl, not without offending "+self.gods[int(choice)-1]+", which you do NOT want to do.", '\n'
			return
		elif amount == 0:
			print "Nothing ventured, nothing gained.", '\n'
			return
		elif amount > self.character.loot['gp']:
			print "You don't have enough gold for that, man. Go back to the dungeon and make some scratch! (Or at least, put less in the offering bowl.)", '\n'
			return
		if choice == '1':
			try:
				self.shrinegp += amount
			except AttributeError:
				self.shrinegp = amount
			from math import sqrt
			newexp = int((1. + sqrt(1. + 8. * float(self.shrinegp)))/4.)
			try:
				netexp = newexp - self.shrinexp
			except AttributeError:
				netexp = newexp
			self.shrinexp = newexp
			msg = "The bounds of your mind are expanded by a moment of attention from "+self.gods[0]
            msg += "; this may not actually be a good thing, but at least you gain "+str(netexp)+" experience."
            print msg, '\n'
			self.character.defeat_enemy(netexp,{'gp':-amount})
			if self.character.exp >= self.character.level * 10:
				self.character.levelup()
			return
		elif str(choice) == '2':
			if amount < 30000:
				msg = "Nothing happens except for a feeling of insufficient funds... "
                msg += "you scoop the gold back out of the offering bowl before anyone sees you, cheapskate."
                print msg, '\n'
				return
			typechoice = random.choice([random.randint(0,2) for i in range(6)])
			type1 = ["ring","rarmor","rweapon"][t]
			type1a = ["ring","armor","weapon"][t]
			if type1 == "ring":
				riches = random.choice([random.choice(pq_magic['ring'].keys()) for i in range(6)])
			else:
				type2 = random.choice([random.choice(pq_gear[type1].keys()) for i in range(6)])
				rating = random.choice([random.randint(0,8) for i in range(6)])
				if rating == 0:
					riches = pq_gear[type1][type2][0]
				else:
					magic = random.choice([random.randint(max([rating-5,0]),min([3,rating])) for i in range(6)]) if rating < 8 else 3
					nonmagic = rating - magic
					riches = '' if magic == 0 else pq_magic[type1][type2][magic]+' '
					riches += pq_gear[type1][type2][nonmagic]
			self.character.defeat_enemy(0,{'gp':-amount,type1a:riches})
			msg = "The gold disappears from the offering bowl"
			if amount > 30000:
				msg += " (with a thank you very much for the extra donation)"
			msg += ", and you discover a "
			if type1a == "ring":
				msg += "Ring of "
			msg += riches+" in your lootbag!"
			print msg, '\n'
			return

	def save(self):
		d = shelve.open(os.path.expanduser('data/pq_saves.db'))
		d[self.player] = self
		d.close()