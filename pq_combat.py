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
            self.enemy = PQ_Enemy()
            self.enemy.gen(lvl)
        else:
            self.enemy = enemy
        self.turn = -1
        self.char = char
        char_init = 1 + char.initiative if char.stats[2] < 2 else random.choice([random.randint(1,
            char.stats[2])+char.initiative for j in range(0,6)])
        enemy_init = 1 if self.enemy.stats[2] < 2 else random.choice([random.randint(1,
            self.enemy.stats[2]) for j in range(0,6)])
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
        if target == self.char:
            print "Ouch! You're bleeding, maybe a lot. You take "+str(dmg)+" damage, and have "+ \
                str(target.currenthp)+" hit points remaining."
        else:
            print "A hit! A very palpable hit! You deal "+str(dmg)+" damage."
        if target.currenthp <= 0:
            self.death(target)
            return True
        return False
    
    def death(self, target):
        """Handle if somebody dies"""
        if target == self.char:
            print 'Sorry, '+self.char.player+', you have died. You can load from ' \
                'your last save, quit, or make a new character.'
            self.temp = {}
            self.tempturns = {}
            self.char.dead = True
            self.done = True
            return
        if target == self.enemy:
            print 'You have defeated the '+self.enemy.name+'!'
            self.win_combat()
            return
        
    def attack_enemy(self, user, target):
        """Just a simple attack, Attack vs Defense. Basic, lovely."""
        if "charmed" in user.conditions:
            targstring = "You are " if user == self.char else "The monster is "
            print targstring+"charmed, and cannot attack!"
            self.advance_turn()
            return
        hit = atk_roll(user.atk, target.dfn, user.temp.get("Attack",0), target.temp.get("Defense",0))
        if hit > 0:
            if not self.be_hit(target, hit):
                self.advance_turn()
        else:
            print "The attack is unsuccessful."
            self.advance_turn()
            
    def use_skill(self, skill, user, target):
        """Parse the different skill options."""
        if skill not in user.skill:
            print "You don't have that skill..."
            return
        if user.currentsp == 0:
            print "Not enough skill points remaining to use that skill..."
            return
        if "charmed" in user.conditions:
            targstring = "You are " if user == self.char else "The monster is "
            print targstring+"charmed, and cannot use skills!"
            self.advance_turn()
            return
        user.currentsp -= 1
        
        #first check for flee or evade
        if skill == 'Flee': #escape from combat
            targstring = "You are " if hasattr(user,"player") else "The monster is "
            print targstring+"running away!"
            self.runaway(user, 1.)
            self.done = True
            return
        if skill == 'Evade': #buff self Defense
            targstring = "You feel " if hasattr(user,"player") else "The monster feels "
            print targstring+"more evasive!"
            user.temp_bonus(["Defense"],user.stats[5],4)
            self.advance_turn()
            return
        
        done = False
        
        #then check for SoD
        if skill == 'Petrify':
            hit = pq_petrify(user, target)
            if hit: 
                targstring = "The monster is " if hasattr(user,"player") else "You are "
                print targstring+"petrified!"
                self.death(target)
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
        elif skill == 'Dominate': #Skill vs Mind to make creature attack itself
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
            
        if hit and damage > 0:
            if self.be_hit(target, damage):
               return 
        elif not hit:
            targstring = "you." if hasattr(target,"player") else "the enemy."
            print "The "+skill+" failed to affect "+targstring
        self.advance_turn()

    def win_combat(self):
        """Handle scenarious where (by some miniscule chance) the player wins the combat."""
        self.char.defeat_enemy(self.enemy.level, self.enemy.treasure)
        exp = self.enemy.level
        print 'You receive '+str(exp)+' experience.'
        treasure = self.enemy.treasure
        msg = "In the monster's pockets, you find: "
        loot = []
        for i in treasure.keys():
            if treasure[i]:
                if i == 'gp':
                    loot.append(str(treasure[i])+" gp")
                elif i == 'ring':
                    loot.append("a Ring of "+treasure[i])
                elif i == 'quest':
                    loot.append(treasure[i])
                    self.char.queststatus = "complete"
                else:
                    loot.append("a "+treasure[i])
        if not loot:
            loot = "Nothing!"
        else:
            loot = ', '.join(loot) + '.'
        print msg + loot
        if self.char.exp >= self.char.level * 10:
            self.char.levelup()
        self.done = True
        
    def runaway(self, who, chance = 0.5):
        if "entangled" in who.conditions:
            targstring = "You are " if user == self.char else "The monster is "
            print targstring+"entangled, and cannot flee!"
            self.advance_turn()
            return
        if "tripped" in who.conditions:
            targstring = "You are " if user == self.char else "The monster is "
            print targstring+"tripped, and cannot flee!"
            self.advance_turn()
            return
        if random.random() < chance:
            if who == self.char:
                print "You successfully exercise your valor, vis a vis discretion."
            else:
                print "Your enemy turns tail and books it back into the dungeon."
            return True
        else:
            if who == self.char:
                print "You try to run, but the enemy boxes you in."
            else:
                print "You prevent your enemy from skedaddling."
            return False
    
    def pc_turn(self):
        """The player takes his/her turn. Joy."""
        if self.char.currentsp > 0:
            msg = "Attack, "+", ".join(self.char.skill)+", Flee, or Equip?"
            available = self.char.skill+["Attack","Flee","Equip"]
        else:
            msg = "You are out of skill points! Attack, Flee, or Equip?"
            available = ["Attack","Flee","Equip"]
        print msg
        action = choose_from_list("Action> ", available, rand=False,
            character=self.char,allowed=['sheet','help'])
        if action == "Attack":
            self.attack_enemy(self.char,self.enemy)
        elif action in self.char.skill:
            self.use_skill(action,self.char,self.enemy)
        elif action == "Flee":
            if not self.runaway(self.char):
                self.advance_turn()
        elif action == "Equip":
            self.char.equip()
            self.advance_turn()
            
    def monster_turn(self):
        """YAY THE ENEMY GOES... this handles the VERY SIMPLISTIC monster AI."""
        self.enemy.skillcounter -= 1
        if self.enemy.currentsp <= 0 or float(self.enemy.currenthp)/float(self.enemy.hp) < 0.1:
            if not self.runaway(self.enemy): #try to escape if it gets too hairy
                self.advance_turn()
            return
        skillcheck1 = self.enemy.currentsp > 0
        skills_ok = []
        skills_ok.append(self.enemy.skill == 'Petrify' and self.enemy.skillcounter < -3)
        skills_ok.append(self.enemy.skill == 'Flee' and self.turn >= 2)
        skills_ok.append(self.enemy.skill == 'Poison' and self.turn >= 2 and \
            self.char.currenthp < self.char.hp)
        if self.enemy.skillcounter < 0:
            avail_skills = pq_dragonskill.values()
            avail_skills.remove('Petrify')
            avail_skills.remove('Flee')
            avail_skills.remove('Poison')
            skills_ok.append(self.enemy.skill in avail_skills)
        if sum(skills_ok) and skillcheck1:
            print "The enemy uses "+self.enemy.skill+"!"
            self.enemy.reset_skillcounter()
            self.use_skill(self.enemy.skill,self.enemy,self.char)
        else:
            print "It tries to cause you bodily harm!"
            self.attack_enemy(self.enemy,self.char)
        
    def advance_turn(self):
        """Advance the turn, decrementing counters on temporary effects and adjudicating turn order."""
        self.turn += 1
        whos = self.turnorder[self.turn % 2]
        for i in self.char.temp.keys():
            self.char.tempturns[i] -= 1
            if self.char.tempturns[i] <= 0:
                del self.char.tempturns[i], self.char.temp[i]
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
            self.monster_turn()
        else:
            self.pc_turn()
