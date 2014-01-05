#
#  pq_combat.py
#  part of Percival's Quest RPG

from pq_enemies import *
from pq_utilities import *
from pq_skills import *
from pq_equipment import *
import random

class PQ_Combat(object):
	def __init__(self, lvl, char, enemy):
        """Initialize a combat encounter instance, using either a supplied enemy or generating a new one."""
		if not enemy:
			self.enemy = PQ_Enemy(lvl)
			self.enemy.gen(lvl)
		else:
			self.enemy = enemy
		self.turn = -1
		self.char = char
		char_init = 1 + char.init if char.stats[2] < 2 else random.choice([random.randint(1,char.stats[2])+char.init for j in range(0,6)])
		enemy_init = 1 if self.enemy.stats[2] < 2 else random.choice([random.randint(1,self.enemy.stats[2]) for j in range(0,6)])
		self.turnorder = ['monster','player']
		if char_init > enemy_init:
			self.turnorder = ['player','monster']
		elif char_init == enemy_init:
			if char.stats[2] > self.enemy.stats[2]:
				self.turnorder = ['player','monster']
			elif char.stats[2] == self.enemy.stats[2]:
				if 'ImprovedInititiative' in char.feats:
					self.turnorder = ['player','monster']
				elif random.randint(0,1):
					self.turnorder = ['player','monster']
        self.done = False
        
    def be_hit(self, target, dmg):
        """Handle if somebody takes damage."""
		target.ouch(dmg)
		if target == self.character:
			print "Ouch! You're bleeding, maybe a lot. You take "+str(dmg)+" damage, and have "+str(target.currenthp)+" hit points remaining.", '\n'
		else:
			print "A hit! A very palpable hit! You deal "+str(dmg)+" damage.", '\n'
		if target.currenthp <= 0:
			self.death(target)
			return True
        return False
    
    def death(self, target):
        """Handle if somebody dies"""
		if target == self.character:
			print 'Sorry, '+self.character.player+', you have died. You can load from your last save, quit, or make a new character.', '\n'
			self.temp = {}
			self.tempturns = {}
			self.char.dead = True
			self.done = True
			return
		if target == self.combat.enemy:
			print 'You have defeated the '+self.enemy.name+'!', '\n'
			self.win_combat()
			return
        
    def attack_enemy(self, user, target):
        """Just a simple attack, Attack vs Defense. Basic, lovely."""
        if "charmed" in user.conditions:
            targstring = "You are " if user == self.char else "The monster is "
            print targstring+"charmed, and cannot attack!", '\n'
            self.advance_turn()
            return
		hit = atk_roll(user.atk, target.dfn, user.temp.get("Attack",0), target.temp.get("Defense",0))
		if hit > 0:
			if not self.be_hit(target, hit):
				self.advance_turn()
		else:
			print "The attack is unsuccessful.", '\n'
			self.advance_turn()
            
    def use_skill(self, skill, user, target):
        """Parse the different skill options."""
		if skill not in user.skill:
			print "You don't have that skill...", '\n'
            return
		if user.currentsp == 0:
			print "Not enough skill points remaining to use that skill...", '\n'
            return
        if "charmed" in user.conditions:
            targstring = "You are " if user == self.char else "The monster is "
            print targstring+"charmed, and cannot use skills!", '\n'
            self.advance_turn()
            return
		user.currentsp -= 1
        
        #first check for flee or evade
        if skill == 'Flee': #escape from combat
			targstring = "You are " if user.hasattr("player") else "The monster is "
			print targstring+"running away!", '\n'
			self.runaway(user, 1.)
			self.whereareyou = "dungeon"
			self.done = True
			return
        if skill == 'Evade': #buff self Defense
            targstring = "You feel " if user.hasattr("player") else "The monster feels "
			print targstring+"more evasive!", '\n'
            user.temp_bonus(["Defense"],user.skill[5],4)
            self.advance_turn()
            return
        
        done = False
        
        #then check for SoD
        elif skill == 'Petrify':
            hit = pq_petrify(user, target)
            if hit: self.death(target)
            return
		
        #then everything else:
        damage = 0
        
        if skill == 'Entangle': #debuff targets atk, def for 2 rounds, vs Ref, prevents flee
            hit = pq_entangle(user, target)
        elif skill == 'Fear': #debuff targets atk, def, skill for 2 rounds, vs Ref
            hit = pq_fear(user, target)
        elif skill == 'Charm': #disables attack, skill use for 2 rounds
            hit = pq_charm(user, target)
		elif skill == 'Smite': #attack with Atk+Skill
			damage = pq_smite(user, target)
            hit = damage > 0
		elif skill == 'Cure': #regain hp
			damage = pq_cure(user, target)
            hit = damage > 0
        elif skill = 'Dominate': #Skill vs Mind to make creature attack itself
            damage = pq_dominate(user, target)
            hit = damage > 0
        elif skill == 'Trip': #attack for half damage, debuff Attack by 1dSkill, prevents flee
            damage = pq_trip(user, target)
            hit = damage > 0
        elif skill == 'Missile': #attack Skill vs Ref
            damage = pq_missile(user, target)
            hit = damage > 0
        elif skill == 'Doublestrike': #attack twice at -2
            damage = pq_doublestrike(user, target)
            hit = damage > 0
        elif skill == 'Backstab': #Skill vs Fort for double dmg on attack
            damage = pq_backstab(user, target)
            hit = damage > 0
        elif skill == 'Rage': #attack with +atk, -def
            damage = pq_rage(user, target)
            hit = damage > 0
        elif skill == 'Poison': #Auto-dmg if not at max hp
            damage = pq_poison(user, target)
            hit = damage > 0
            
        if hit:
            if self.be_hit(target, damage):
               return 
        else:
            targstring = "you." if target.hasattr("player") else "the enemy."
            print "The "+skill+" failed to affect "+targstring,'\n'
        self.advance_turn()

    def win_combat(self):
        """Handle scenarious where (by some miniscule chance) the player wins the combat."""
		self.char.defeat_enemy(self.enemy.level, self.enemy.treasure)
		exp = self.enemy.level
		msg = 'You receive '+str(exp)+' experience.'
		if self.char.exp >= self.char.level * 10:
			self.char.levelup()
		treasure = self.enemy.treasure
		msg = "In the monster's pockets, you find: "
		loot = []
		for i in treasure.keys():
			if treasure[i]:
				if i == 'gp':
					loot.append(str(tr[i])+" gp")
				elif i == 'ring':
					loot.append("a Ring of "+tr[i])
				elif i == 'quest':
					loot.append(tr[i])
					self.char.queststatus = "complete"
				else:
					loot.append("a "+tr[i])
		if not loot:
			loot = "Nothing!"
		else:
			loot = ', '.join(loot) + '.'
		print msg + loot, '\n'
		self.done = True
        
    def runaway(self, who, chance = 0.5):
        if "entangled" in who.conditions:
            targstring = "You are " if user == self.char else "The monster is "
            print targstring+"entangled, and cannot flee!", '\n'
            self.advance_turn()
            return
        if "tripped" in who.conditions:
            targstring = "You are " if user == self.char else "The monster is "
            print targstring+"tripped, and cannot flee!", '\n'
            self.advance_turn()
            return
		if random.random() < chance:
			if who == self.char:
				print "You successfully exercise your valor, vis a vis discretion.", '\n'
			else:
				print "Your enemy turns tail and books it back into the dungeon.", '\n'
			return True
		else:
			if who == self.char:
				print "You try to run, but the enemy boxes you in.", '\n'
			else:
				print "You prevent your enemy from skedaddling.", '\n'
			return False
    
    def pc_turn(self):
        """The player takes his/her turn. Joy."""
        print "Attack, "+", ".join(self.char.skills)+", Flee, or Equip", '\n'
        action = choose_from_list("Action> ",["Attack",self.char.skills,"Flee","Sheet","Equip"],False)
        while action == "Sheet":
            self.char.tellchar()
            action = choose_from_list("Action> ",["Attack",self.char.skills,"Flee","Sheet","Equip"],False)
        if action == "Attack":
            self.attack_enemy(self.char,self.enemy)
        elif action in self.char.skills:
            self.use_skill(action,self.char,self.enemy)
        elif action == "Flee":
            if not self.runaway(self.char):
                self.advance_turn()
        elif action == "Equip":
            self.char.equip()m
            self.advance_turn()
		
	def advance_turn(self):
        """Advance the turn, decrementing counters on temporary effects and handling the VERY SIMPLISTIC monster AI."""
		self.turn += 1
		whos = self.turnorder[self.turn % 2]
		self.enemy.skillcounter -= 1
		for i in self.char.temp.keys():
			self.char.tempturns[i] -= 1
			if self.char.tempturns[i] <= 0:
				del self.char.tempturns[i], char.temp[i]
        for i in self.char.conditions.keys():
            self.char.conditions[i] -= 1
            if self.char.conditions[i] <= 0:
                del self.char.conditions[i]
		for i in self.enemy.temp.keys():
			self.enemy.tempturns[i] -= 1
			if self.enemy.tempturns[i] <= 0:
				del self.enemy.tempturns[i], self.enemy.temp[i]
        for i in self.enemy.conditions.keys():
            self.enemy.conditions[i] -= 1
            if self.enemy.conditions[i] <= 0:
                del self.enemy.conditions[i]
		if whos == 'monster':
            if self.enemy.currentsp <= 0 or float(self.enemy.currenthp)/float(self.enemy.hp) < 0.1:
                self.runaway(user)
			if self.enemy.currentsp > 0 and ((self.enemy.skill == 'Petrify' and self.enemy.skillcounter < -2) or self.enemy.skillcounter < 0):
				print "The enemy uses "+self.enemy.skill+"!", '\n'
				self.use_skill(self.enemy.skill,self.enemy,rpg.character)
				self.enemy.skillcounter = 1 if self.enemy.skill != 'Flee' else -1
			else:
				print "It tries to cause you bodily harm!", '\n'
				self.attack_enemy(self.enemy,self.character)
        else:
            self.pc_turn()
