"""
Combat object module for Percival's Quest RPG
for managing... y'know... combat.
"""
#
#  pq_combat.py
#  part of Percival's Quest RPG

from pq_enemies import PQ_Enemy, pq_dragonskill
from pq_utilities import choose_from_list, atk_roll
from pq_skills import pq_skill_library as pqsl
#from pq_equipment import *
import random, textwrap

class PQ_Combat(object):
    """The Combat Object(TM)(notreallyTM)"""
    def __init__(self, lvl, char, enemy):
        """Initialize a combat encounter instance, using either \
        a supplied enemy or generating a new one."""
        if not enemy:
            self.enemy = PQ_Enemy()
            self.enemy.gen(lvl)
        else:
            self.enemy = enemy
        self.turn = -1
        self.char = char
        initiative_differential = atk_roll([0, self.char.stats[2]], \
            [0, self.enemy.stats[2]], self.char.combat['initiative'], 0)
        self.turnorder = ['monster', 'player']
        if initiative_differential > 0:
            self.turnorder = ['player', 'monster']
        elif initiative_differential == 0:
            if char.stats[2] > self.enemy.stats[2]:
                self.turnorder = ['player', 'monster']
            elif char.stats[2] == self.enemy.stats[2]:
                if 'ImprovedInititiative' in char.feats:
                    self.turnorder = ['player', 'monster']
                elif random.randint(0, 1):
                    self.turnorder = ['player', 'monster']
        self.done = False
        
    def be_hit(self, target, dmg):
        """Handle if somebody takes damage."""
        target.ouch(dmg)
        if target == self.char:
            print "Ouch! You're bleeding, maybe a lot. You take " + str(dmg) \
                + " damage, and have "+ str(target.hitpoints[0]) + \
                " hit points remaining."
        else:
            print "A hit! A very palpable hit! You deal " + str(dmg) + \
                " damage."
        if target.hitpoints[0] <= 0:
            self.death(target)
            return True
        return False
    
    def death(self, target):
        """Handle if somebody dies"""
        if target == self.char:
            print 'Sorry, '+self.char.player+', you have died. You can load ' \
                'from your last save, quit, or make a new character.'
            for i in self.char.temp:
                self.char.temp[i] = {}
            self.char.dead = True
            self.done = True
            return
        if target == self.enemy:
            print 'You have defeated the ' + self.enemy.name + '!'
            self.win_combat()
            return
        
    def attack_enemy(self, user, target):
        """Just a simple attack, Attack vs Defense. Basic, lovely."""
        if "charmed" in user.temp['condition']:
            targstring = "You are " if user == self.char else "The monster is "
            print targstring + "charmed, and cannot attack!"
            self.advance_turn()
            return
        hit = atk_roll(user.combat['atk'], target.combat['dfn'], \
            user.temp['stats'].get("Attack", 0), \
            target.temp['stats'].get("Defense", 0))
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
        if user.skillpoints[0] == 0:
            print "Not enough skill points remaining to use that skill..."
            return
        if "charmed" in user.temp['condition']:
            targstring = "You are " if user == self.char else "The monster is "
            print targstring + "charmed, and cannot use skills!"
            self.advance_turn()
            return
        user.skillpoints[0] -= 1
        
        #first check for flee
        if skill == 'Flee': #escape from combat
            targstring = "You are " if hasattr(user, "gear") \
                else "The monster is "
            print targstring+"running away!"
            self.runaway(user, 1.)
            self.done = True
            return
        #then everything else, using the skill library
        hit = pqsl[skill](user, target)
        if hit[0] and hit[1] > 0:
            if self.be_hit(target, hit[1]):
                return 
        elif not hit[0]:
            targstring = "you." if hasattr(target, "player") else "the enemy."
            print "The " + skill + " failed to affect " + targstring
        self.advance_turn()

    def win_combat(self):
        """Handle scenarious where (by some miniscule chance)
        the player wins the combat."""
        self.char.defeat_enemy(self.enemy.level[1], self.enemy.treasure)
        exp = self.enemy.level[1]
        print 'You receive ' + str(exp) + ' experience.'
        treasure = self.enemy.treasure
        msg = "In the monster's pockets, you find: "
        loot = []
        for i in treasure.keys():
            if treasure[i]:
                if i == 'gp':
                    loot.append(str(treasure[i]) + " gp")
                elif i == 'ring':
                    loot.append("a Ring of " + treasure[i])
                elif i == 'quest':
                    loot.append(treasure[i])
                    self.char.queststatus = "complete"
                else:
                    loot.append("a " + treasure[i])
        if not loot:
            loot = "Nothing!"
        else:
            loot = ', '.join(loot) + '.'
        print msg + loot
        if self.char.level[0] >= self.char.level[1] * 10:
            self.char.levelup()
        self.done = True
        
    def runaway(self, who, chance = 0.5):
        """Check Flee chance"""
        condition = ''
        if "entangled" in who.temp['condition']:
            condition = "entangled"
        if "tripped" in who.temp['condition']:
            condition = "tripped"
        if condition:
            targstring = "You are " if who == self.char else "The monster is "
            print targstring + condition + ", and cannot flee!"
            self.advance_turn()
            return
        if random.random() < chance:
            if who == self.char:
                print "You successfully exercise your valor, " \
                    "vis a vis discretion."
            else:
                print "Your enemy turns tail and books it back " \
                    "into the dungeon."
            return True
        else:
            if who == self.char:
                print "You try to run, but the enemy boxes you in."
            else:
                print "You prevent your enemy from skedaddling."
            return False
    
    def pc_turn(self):
        """The player takes his/her turn. Joy."""
        if self.char.skillpoints[0] > 0:
            msg = "Attack, " + ", ".join(self.char.skill) + \
                ", Run Away, or Equip?"
            available = self.char.skill + ["Attack", "Run Away", "Equip"]
        else:
            msg = "You are out of skill points! Attack, Run Away, or Equip?"
            available = ["Attack", "Run Away", "Equip"]
        print textwrap.fill(msg)
        action = choose_from_list("Action> ", available, rand=False,
            character=self.char, allowed=['sheet', 'help'])
        if action == "Attack":
            self.attack_enemy(self.char, self.enemy)
        elif action in self.char.skill:
            self.use_skill(action, self.char, self.enemy)
        elif action == "Run Away":
            if not self.runaway(self.char):
                self.advance_turn()
        elif action == "Equip":
            self.char.equip()
            self.advance_turn()
            
    def monster_turn(self):
        """YAY THE ENEMY GOES... this handles 
        the VERY SIMPLISTIC monster AI."""
        self.enemy.skillcounter -= 1
        hitpointratio = float(self.enemy.hitpoints[0]) / \
            float(self.enemy.hitpoints[1])
        if self.enemy.skillpoints[0] <= 0 or hitpointratio < 0.1:
            if not self.runaway(self.enemy):
                self.advance_turn()
            return
        skillcheck1 = self.enemy.skillpoints[0] > 0
        skills_ok = []
        skills_ok.append(self.enemy.skill == 'Petrify' and \
            self.enemy.skillcounter < -3)
        skills_ok.append(self.enemy.skill == 'Flee' and self.turn >= 2)
        skills_ok.append(self.enemy.skill == 'Poison' and self.turn >= 2 and \
            self.char.hitpoints[0] < self.char.hitpoints[1])
        if self.enemy.skillcounter < 0:
            avail_skills = pq_dragonskill.values()
            avail_skills.remove('Petrify')
            avail_skills.remove('Flee')
            avail_skills.remove('Poison')
            skills_ok.append(self.enemy.skill in avail_skills)
        if sum(skills_ok) and skillcheck1:
            print "The enemy uses "+self.enemy.skill+"!"
            self.enemy.reset_skillcounter()
            self.use_skill(self.enemy.skill, self.enemy, self.char)
        else:
            print "It tries to cause you bodily harm!"
            self.attack_enemy(self.enemy, self.char)
        
    def advance_turn(self):
        """Advance the turn, decrementing counters on 
        temporary effects and adjudicating turn order."""
        self.turn += 1
        whos = self.turnorder[self.turn % 2]
        expired = []
        for i in self.char.temp['stats']:
            self.char.temp['statturns'][i] -= 1
            if self.char.temp['statturns'][i] <= 0:
                expired.append(i)
        for i in expired:
            del self.char.temp['stats'][i], \
                self.char.temp['statturns'][i]
        expired = []
        for i in self.char.temp['condition']:
            self.char.temp['condition'][i] -= 1
            if self.char.temp['condition'][i] <= 0:
                expired.append(i)
        for i in expired:
            del self.char.temp['condition'][i]
        expired = []
        for i in self.enemy.temp['stats']:
            self.enemy.temp['statturns'][i] -= 1
            if self.enemy.temp['statturns'][i] <= 0:
                expired.append(i)
        for i in expired:
            del self.enemy.temp['statturns'][i], \
                self.enemy.temp['stats'][i]
        expired = []
        for i in self.enemy.temp['condition']:
            self.enemy.temp['condition'][i] -= 1
            if self.enemy.temp['condition'][i] <= 0:
                expired.append(i)
        for i in expired:
            del self.enemy.temp['condition'][i]
        if whos == 'monster':
            self.monster_turn()
        else:
            self.pc_turn()
