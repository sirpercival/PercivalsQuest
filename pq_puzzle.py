#
#  pq_puzzle.py
#  part of Percival's Quest RPG

from pq_namegen import riddlegen, numgen
from pq_utilities import *
from pq_equipment import *
import random

pq_stats = {'Attack':0,'Defense':1,'Reflexes':2,'Fortitude':3,'Mind':4,'Skill':5}

class PQ_Puzzle(object):
	def __init__(self,lvl,character):
        """Initialize puzzle encounter based on dungeon level."""
		riddle = riddlegen()
        self.char = character
		self.answer = riddle[0]
		self.riddle = riddle[1]
		self.riddleguess = 3
		riches = []
		while not riches:
			tr = pq_treasuregen(lvl+2)
			for t in tr.keys():
				if t == 'gp':
					continue
				if tr[t]:
					riches.append(tr[t])
		self.riches = random.choice(riches)
		self.numcode = numgen()
		self.numguess = 10
		self.gold = sum([random.randint(1,100) for i in range(lvl)])
		self.damage = 0
		self.trial_num = lvl
		self.knowledge = lvl/2
		self.thing = random.choice(['mysterious dark spirit','regal sphinx','magic mirror','blind oracle'])
		self.choice = ""
        self.finished = False
		
	def puzzleinit(self):
        """Begin a puzzle encounter."""
		msg1 = "Exploring the depths of the Dungeon, you encounter a "+self.thing+" in a lonely room."
		if self.thing == 'magic mirror':
			msg1 += " A sinister face materializes in its murky surface, looking directly at you."
		else:
			msg1 += " The "+self.thing+" addresses you."
		msg2 = "'Welcome to the Dungeon, adventurer. Portents have foreshadowed your coming. I am here to aid you on your journey, should you prove worthy."
		msg2 += " I offer you choices three: you may play a game, for Gold; solve a riddle, for Riches; or undergo a Trial of Being, for Knowledge. Choose your prize, and choose well.'"
		msg3 = "(Your choices are Gold, Riches, Knowledge, or Skip.)"
		print msg1, '\n', msg2, '\n', msg3, '\n'
        choice = choose_from_list("Choice> ",["gold","riches","knowledge","skip"],character=self.char,allowed=['sheet','help','equip'])
		self.choice = choice
		if self.choice == "gold":
			msg = "The "+self.thing+" nods approvingly. 'You have chosen the game; here are the rules. I have selected a set of four digits, in some order. "
			msg += "You have 10 chances to guess the digits, in the correct order. If you are polite, I may be persuaded to give you a hint... Now, begin; you have 10 chances remaining.'"
			msg2 = "(Guess should be ####)"
			print msg, '\n', msg2, '\n'
            self.check_numguess()
			return
		elif self.choice == "riches":
			msg = "The "+self.thing+" nods slowly. 'You have chosen the riddle; here are the rules. I will tell you the riddle, which has an answer one word long. "
			msg += "You have three chances to guess the answer. If it goes poorly, I may decide to give you a hint. Here is the riddle: "
			msg2 = "Now, begin your guess. You have three chances remaining.'"
			print, msg, '\n', self.riddle, '\n', msg2, '\n'
            self.check_riddleguess()
			return
		elif self.choice == "knowledge":
			msg = "The "+self.thing+"'s face spreads in a predatory smile. 'As you wish. The Trial consists of three tests; if you succeed at all three, you will be rewarded."
			msg += " The first will begin as soon as you are ready.'"
			msg2 = "(Tell the "+self.thing+" that you're ready with .rpgpuzzle)"
			print msg, '\n', msg2, '\n'
            self.trialofbeing()
			return
		elif self.choice == "skip":
			self.failure()
	
	def failure(self):
        """Handler for failure to complete puzzle."""
		print "The "+self.thing+" stares at you impassively. 'You have been found wanting. How disappointing.' Then it vanishes, leaving no trace that this room of the dungeon was ever occupied.", '\n'
		if self.choice == "knowledge" and self.damage > 0:
			self.char.ouch(self.damage)
			msg = "The Trial was extremely taxing; you take "+str(self.damage)+" damage"
			if self.char.currenthp <= 0:
				msg += "..."
                self.char.dead = True
                print 'Sorry, '+self.character.player+', you have died. You can load from ' \
                'your last save, quit, or make a new character.', '\n'
			else:
				msg += ", and have "+str(char.currenthp)+" hit points remaining."
			print msg, '\n'
        self.finished = True
		return
	
	def success(self):
        """Handler for successful puzzle completion."""
		print "The "+self.thing+" seems pleased. 'You have proven worthy, and now may receive your reward.' Then it vanishes, leaving no trace that this room of the dungeon was ever occupied.", '\n'
		msg = "You gain "
		if self.choice == "gold":
			msg += str(self.gold)+" gp!"
			print msg, '\n'
			self.char.defeat_enemy(0,{'gp':self.gold})
		if self.choice == "riches":
			typ = item_type(self.riches)
			msg += "a "
			if typ[0] == "ring":
				msg += "Ring of "
			msg += self.riches+"!"
			print msg, '\n'
			self.char.defeat_enemy(0,{typ[0]:self.riches})
		if self.choice == "knowledge":
			msg = str(self.knowledge)+" experience!"
            print msg, '\n'
			self.char.defeat_enemy(self.knowledge,{})
            if self.char.exp >= 10*self.char.level:
				self.char.levelup()
        self.finished = True
		return
	
	def trialofbeing(self):
        """Run character through the Trial of Being."""
		sta = random.sample(['Attack','Defense','Reflexes','Fortitude','Mind','Skill'],3)
		tests = {'Attack':"All of a sudden, you find yourself inside a wooden box, 10 feet on a side. The walls begin to close in! You try to hack your way out...",
			'Defense':"Stalactites and stalagmites of various sizes start to elongate, sprouting from the floor, walls, and ceiling! You attempt to avoid being impaled...",
			'Reflexes':"The ground rumbles, twisting and gyrating in an earthquake! You try to keep your balance as chasms in the floor gape open...",
			'Fortitude':"An enormous python slithers out of thin air, coiling around you in an instant! You attempt to remain conscious as it constricts you...",
			'Mind':"You reel from a sudden psychic onslaught! You fight to keep your senses...",
			'Skill':"You are faced with a challenge that is both deadly and idiosyncratic! You try to defeat it using your ingenuity and cunning..."}
		win = {'Attack':"You break through the box before being crushed!",'Defense':"You protect yourself from evisceprogressn!",'Reflexes':"You remain on your feet!",
			'Fortitude':"You fight off the impending blackness!",'Mind':"You shake off the mental assault!",'Skill':"You are up to the task!"}
		lose = {'Attack':"The contracting walls squeeze you to unconsciousness...",'Defense':"The stone spikes break through your defenses...",
			'Reflexes':"You fall into a chasm...",'Fortitude':"You are forced to oblivion...",'Mind':"Your mental defenses are overcome...",'Skill':"You come up short..."}
		for i,s in enumerate(sta):
			print "The "+("first","second","third")[i]+" challenge begins. "+tests[s], '\n'
            result = atk_roll([0,self.char.stats[pq_stats[s]]],[0,self.trial_num],0,0)
			if result < 0:
				print lose[s], '\n'
				self.damage = result
				self.failure()
				return
			else:
				print win[s], '\n'
				self.knowledge += self.trial_num
		self.success()
		
	def check_riddleguess(self):
        """Handle guesses of the riddle answer."""
        while self.riddleguess > 0:
            guess = get_user_input("Guess> ", character=self.char, allow_sheet=True, allow_equip=True, allow_help=True)
            self.riddleguess -= 1
            #check for a valid guess
            badguess = 0
            import string
            if len(guess.split()) > 1:
                badguess = 1
            for i in guess:
                if i not in string.letters:
                    badguess = 2
                    break
            if badguess:
                badguess_message = ["your guess should be one word only.","what you said isn't even a word."][badguess-1]
                print "The "+self.thing+" frowns. 'I do not know why you would waste a guess on that... "+badguess_message+"'", '\n'
                continue
            #are they right?
            if guess.upper() == self.answer:
                self.success()
                return
            #are they done?
            if self.riddleguess <= 0:
                break
            answer_length = len(self.answer)
            pl = "s" if self.riddleguess != 1 else ""
            msg = "You have guessed incorrectly, leaving you with "+str(self.riddleguess)+" chance"+pl+" remaining. "
            msg += "Here is a hint to help you: the answer to the riddle is a single word with "+str(answer_length)+" letters."
            print msg, '\n'
        self.failure()
		return
		
	def check_numguess(self, guess):
        """A numeric Mastermind game! Give feedback on the guesses."""
        while self.numguess > 0:
            guess = get_user_input("Guess> ", character=self.char, allow_sheet=True, allow_equip=True, allow_help=True)
            self.numguess -= 1
            #check for a valid guess
            badguess = False
            if len(guess) != 4:
                badguess = True
            for i in guess:
                try:
                    j = int(i)
                except:
                    badguess = True
            if badguess:
                print "The "+self.thing+" frowns. 'I do not know why you would waste a guess on that.'", '\n'
                continue
            copy_answer = [i for i in self.numcode]
            copy_guess = [i for i in guess]
            correct = []
            #first pass: check for correct positions
            progress = 0
            for i in range(4):
                if copy_guess[i] == copy_ans[i]:
                    correct.append('rectus')
                    copy_answer[i] = '*'
                    copy_guess[i] = '*'
                    progress += 2
            #did they get it right?
            if ''.join(copy_answer) == '****' or progress == 8:
                self.success()
                return
            #if not, are they done?
            if self.numguess <= 0:
                break
            #if not, let's check for correct digits, incorrect positions
            for i in range(4):
                if copy_guess[i] != '*' and copy_guess[i] in copy_answer:
                    correct.append('proxime')
                    progress += 1
            #fill out the rest with evil BWHAHA
            ncorrect = len(correct)
            for i in range(4 - ncorrect):
                correct.append('malum')
            #concatenate results
            hint = []
            nums = ['','singuli','bini','terni','quaterni']
            for i in ['rectus','proxime','malum']:
                num = correct.count(i)
                if num > 0:
                    print num
                    hint.append(nums[num]+' '+i)
            hint = ', '.join(hint)+'.'
            progress = (progress+1)/2
            progmsg = ("The "+self.thing+" sighs. 'You are nearly as far from correct as it is possible to be. Perhaps this hint will help:",
                "The "+self.thing+" nods slowly. 'You have some small skill at this sort of thing, it would seem. A hint to aid your progress:",
                "The "+self.thing+" quirks an eyebrow. 'Perhaps you do not even need this hint, but I will provide it anyway:",
                "The "+self.thing+" smiles, showing a little too many teeth. 'I am impressed -- you are nearly there. Another hint:")
            if self.numguess > 1:
                nummsg = "You have "+str(self.numguess)+" guesses remaining. Use them wisely."
            else:
                nummsg = "You have one guess remaining. Use it wisely."
            print " ".join([progmsg[progress],hint,nummsg]), '\n'
        self.failure()
		return
        
