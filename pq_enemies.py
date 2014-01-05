#
#  pq_enemies.py
#  part of Percival's Quest RPG

import random
from pq_equipment import pq_treasuregen
from pq_namegen import dragon_namegen, simple_namegen, monster_gen, artygen

pq_monsters = { #more will be added at some point...
	1: {'goblin':{'stat':(0,0,0,0,0,0), 'skill':'Flee'},
		'troglodyte':{'stat':(1,0,1,1,0,0), 'skill':'Poison'},
		'skeleton':{'stat':(1,1,0,0,1,0), 'skill':'Fear'}},
	2: {'bugbear':{'stat':(2,1,0,1,0,0), 'skill':'Rage'},
		'imp':{'stat':(0,0,2,0,1,1), 'skill':'Charm'},
		'worg':{'stat':(1,1,1,1,0,0), 'skill':'Trip'}},
	3: {'cockatrice':{'stat':(1,2,0,1,1,0), 'skill':'Petrify'},
		'ogre':{'stat':(3,1,0,1,0,0), 'skill':'Smite'},
		'wight':{'stat':(1,1,1,0,1,2), 'skill':'Fear'}},
	4: {'ettin':{'stat':(3,1,0,2,0,0), 'skill':'Doublestrike'},
		'manticore':{'stat':(2,2,0,1,0,1), 'skill':'Missile'},
		'wyvern':{'stat':(1,1,2,1,0,1), 'skill':'Poison'}},
	5: {'succubus':{'stat':(1,1,2,1,0,1,2), 'skill':'Charm'},
		'gorgon':{'stat':(2,2,0,2,0,2), 'skill':'Petrify'},
		'ogre mage':{'stat':(3,0,0,1,1,3), 'skill':'Missile'}},
	6: {'frost giant':{'stat':(4,2,0,2,2,0), 'skill':'Smite'},
		'rakshasa':{'stat':(2,2,1,1,1,3), 'skill':'Entangle'},
		'hydra':{'stat':(5,2,0,3,0,0), 'skill':'Doublestrike'}},
	7: {'kraken':{'stat':(5,3,0,4,0,0), 'skill':'Trip'},
		'stone golem':{'stat':(3,4,0,3,2,0), 'skill':'Evade'},
		'purple worm':{'stat':(5,2,0,3,0,2), 'skill':'Poison'}},
	8: {'astral deva':{'stat':(4,2,1,2,2,3), 'skill':'Fear'},
		'storm giant':{'stat':(5,2,1,2,2,3), 'skill':'Smite'},
		'nightshade':{'stat':(3,4,1,3,0,3), 'skill':'Backstab'}},
	9: {'marilith':{'stat':(4,3,2,3,2,2), 'skill':'Doublestrike'},
		'pit fiend':{'stat':(5,3,1,3,3,2), 'skill':'Poison'},
		'tarrasque spawn':{'stat':(6,5,0,5,0,0), 'skill':'Smite'}}}
        
pq_dragonskill = {'Bronze':'Evade','Gold':'Smite','Blue':'Backstab',
    'Silver':'Cure','Brass':'Charm','Green':'Entangle','Red':'Rage',
	'Force':'Missile','Mercury':'Doublestrike','Crystal':'Dominate',
    'Black':'Poison','White':'Flee','Bone':'Fear','Stone':'Petrify'}

class PQ_Enemy(object):
	def __init__(self):
        """Initialize the random monster."""
		self.name = ''
		self.level = 0
		self.hp = 0
		self.currenthp = 0
		self.sp = 0
		self.currentsp = 0
		self.stats = [0,0,0,0,0,0]
		self.treasure = {'weapon':'', 'armor':'', 'ring':'', 'gp':0}
		self.skill = ''
		self.temp = {}
		self.tempturns = {}
		self.atk = [0,self.stats[0]]
		self.dfn = [0,self.stats[1]]
		self.skillcounter = 1
        self.conditions = {}
		
	def gen(self, lvl):
        """Generate the monster based on dungeon level."""
		if lvl >= 10: #if we're at level 10, face Dragons!
			self.dragongen(lvl)
		else:
			self.level = lvl
			self.name = random.choice(pq_monsters[lvl].keys())
			for i in range(0,6):
				stat_roll = random.choice([random.randint(1,6) for j in range(0,6)])
				self.stats[i] = stat_roll + pq_monsters[lvl][self.name]['stat'][i]
			self.skill = pq_monsters[lvl][self.name]['skill']
			for i in range(0,lvl):
				self.hp += random.choice([random.randint(max([1,self.stats[3]/2]),self.stats[3]) for j in range(0,6)])
			self.currenthp = self.hp
			self.sp = random.choice([random.randint(1,self.stats[5]) for j in range(0,6)])+2*(lvl-1)
			self.currentsp = self.sp
			self.treasure = pq_treasuregen(lvl)
			self.atk = [0,self.stats[0]]
			self.dfn = [0,self.stats[1]]
	
	def dragongen(self, lvl):
        """Generate a random dragon based on dungeon level, for level 10+ """
		self.level = lvl
		color = random.choice([random.choice(pq_dragonskill.keys()) for i in range(0,6)])
		self.name = dragon_namegen(2,6)[0] + ' the '+color+' Dragon'
		for i in range(0,6):
			statroll = random.choice([random.randint(1,6) for j in range(0,6)])
			self.stats[i] = statroll + lvl - 5
		self.skill = pq_dragonskill[color]
		for i in range(0,lvl):
			self.hp += random.choice([random.randint(max([1,self.stats[3]/2]),self.stats[3]) for j in range(0,6)])
		self.currenthp = self.hp
		self.sp = random.choice([random.randint(1,self.stats[5]) for j in range(0,6)])+2*(lvl-1)
		self.currentsp = self.sp
		self.treasure = pq_treasuregen(lvl)
		self.atk = [lvl/3,self.stats[0]]
		self.dfn = [lvl/3,self.stats[1]]
        
    def ouch(self, damage):
        """Deal damage to self. WHY WOULD YOU DO THIS IT'S INHUMANE"""
        self.currenthp -= damage
    
    def cure(self, damage):
        """Cure damage to self. Much nicer."""
        self.currenthp = self.hp if self.currenthp + lvl > self.hp else self.currenthp + lvl

    def temp_bonus(self, stat, bonus, turns):
        """Apply a temporary bonus or penalty to self."""
		for i in stat:
			if self.temp.get(i,False):
				sign = -1 if bonus < 0 else 1
				bonus = sign * max([abs(self.temp[i]),abs(bonus)]) #overwrite with whichever bonus is higher, and reset turns
			self.temp[i] = bon
			self.tempturns[i] = turns
		
class PQ_Quest(PQ_Enemy):
	def __init__(self):
        """Initialize Quest monster and item."""
		PQ_Enemy.__init__(self)
		self.description = ''
	
	def gen(self, lvl):
        """Generate a Quest monster and Macguffin I mean artifact."""
		self.level = lvl
		self.name = simple_namegen(2,5)[0].capitalize()
		self.description = monster_gen()[0]
		for i in range(0,6): 
			statroll = random.choice([random.randint(1,6) for j in range(0,6)])
			self.stats[i] = statroll + lvl
		artifact = namegen.artygen()[0].split(':')
		self.treasure['quest'] = artifact[0].strip()
		self.artifact = [a.strip() for a in artifact]
		self.skill = 'Cure'
		for i in range(0,lvl):
			self.currenthp += random.choice([random.randint(max([1,self.stats[3]/2]),self.stats[3]) for j in range(0,6)])
		self.currentsp = random.choice([random.randint(1,self.stats[5]) for j in range(0,6)]) + 2*(lvl-1)
		self.hp = self.currenthp
		self.sp = self.currentsp
		self.atk = [lvl/2,self.stats[0]]
		self.dfn = [lvl/2,self.stats[1]]
