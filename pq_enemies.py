"""
Enemy and Quest(enemy) class declarations
for Percival's Quest RPG
"""
#
#  pq_enemies.py
#  part of Percival's Quest RPG

import random, json
from pq_equipment import pq_treasuregen
from pq_namegen import dragon_namegen, simple_namegen, monster_gen, artygen
        
pq_dragonskill = {'Bronze':'Evade', 'Gold':'Smite', 'Blue':'Backstab',
    'Silver':'Cure', 'Brass':'Charm', 'Green':'Entangle', 'Red':'Rage',
    'Force':'Missile', 'Mercury':'Doublestrike', 'Crystal':'Dominate',
    'Black':'Poison', 'White':'Flee', 'Bone':'Fear', 'Stone':'Petrify'}

class PQ_Enemy(object):
    """Enemy class declaration"""
    def __init__(self):
        """Initialize the random monster."""
        self.name = ''
        self.level = [0, 0]
        self.hitpoints = [0, 0]
        self.skillpoints = [0, 0]
        self.stats = [0, 0, 0, 0, 0, 0]
        self.treasure = {'weapon':'', 'armor':'', 'ring':'', 'gp':0}
        self.skill = ''
        self.temp = {'stats':{}, 'statturns':{}, 'condition':{}}
        self.combat = {'atk':[0, self.stats[0]], 'dfn':[0, self.stats[1]]}
        self.skillcounter = 1
        self.flee = True
        
    def gen(self, lvl):
        """Generate the monster based on dungeon level."""
        if lvl >= 10: #if we're at level 10, face Dragons!
            self.dragongen(lvl)
        else:
            with open('data/pq_bestiary.json') as f:
                pq_monsters = json.load(f)
            self.level = [lvl, lvl]
            self.name = random.choice(pq_monsters[str(lvl)].keys())
            this_monster = pq_monsters[str(lvl)][self.name]
            for i in range(0, 6):
                stat_roll = random.choice([random.randint(1, 6) \
                    for j in range(0, 6)])
                self.stats[i] = stat_roll + this_monster['stat'][i]
            self.skill = this_monster['skill']
            for i in range(0, lvl):
                hpi = random.choice([random.randint(max([1, \
                    self.stats[3] / 2]), self.stats[3]) for j in range(0, 6)])
                self.hitpoints = [x + hpi for x in self.hitpoints]
            spi = random.choice([random.randint(1, self.stats[5]) \
                for j in range(0, 6)]) + 2 * (lvl - 1)
            self.skillpoints = [spi, spi]
            self.treasure = pq_treasuregen(lvl)
            self.combat['atk'] = [0, self.stats[0]]
            self.combat['dfn'] = [0, self.stats[1]]
            self.flee = this_monster.get("flee",True)
    
    def dragongen(self, lvl):
        """Generate a random dragon based on dungeon level, for level 10+ """
        self.level = [lvl, lvl]
        color = random.choice([random.choice(pq_dragonskill.keys()) \
            for i in range(0, 6)])
        self.name = dragon_namegen(2, 6) + ' the ' + color + ' Dragon'
        for i in range(0, 6):
            statroll = random.choice([random.randint(1, 6) \
                for j in range(0, 6)])
            self.stats[i] = statroll + lvl - 5
        self.skill = pq_dragonskill[color]
        for i in range(0, lvl):
            hpi = random.choice([random.randint(max([1, self.stats[3] / 2]), \
                self.stats[3]) for j in range(0, 6)])
            self.hitpoints = [x + hpi for x in self.hitpoints]
        spi = random.choice([random.randint(1, self.stats[5]) \
            for j in range(0, 6)]) + 2 * (lvl - 1)
        self.skillpoints = [spi, spi]
        self.treasure = pq_treasuregen(lvl)
        self.combat['atk'] = [lvl / 3, self.stats[0]]
        self.combat['dfn'] = [lvl / 3, self.stats[1]]
        self.flee = False
        
    def ouch(self, damage):
        """Deal damage to self. WHY WOULD YOU DO THIS IT'S INHUMANE"""
        self.hitpoints[0] -= damage
        
    def huh(self, damage):
        """Deal damage to self's skill points. WHUT"""
        self.skillpoints[0] -= damage
    
    def reset_skillcounter(self):
        """Reset the counter... for the skills..."""
        self.skillcounter = 1
    
    def cure(self, damage):
        """Cure damage to self. Much nicer."""
        self.hitpoints[0] = self.hitpoints[1] if self.hitpoints[0] + damage \
            > self.hitpoints[1] else self.hitpoints[0] + damage

    def temp_bonus(self, stat, bonus, turns):
        """Apply a temporary bonus or penalty to self."""
        for i in stat:
            if self.temp['stats'].get(i, False):
                sign = -1 if bonus < 0 else 1
                bonus = sign * max([abs(self.temp['stats'][i]), abs(bonus)])
            self.temp['stats'][i] = bonus
            self.temp['statturns'][i] = turns
        
class PQ_Quest(PQ_Enemy):
    """Quest Monster version of the enemy class declaration."""
    def __init__(self):
        """Initialize Quest monster and item."""
        PQ_Enemy.__init__(self)
        self.description = ''
        self.artifact = []
    
    def gen(self, lvl):
        """Generate a Quest monster and Macguffin I mean artifact."""
        self.level = [lvl, lvl]
        self.name = simple_namegen(2, 5).capitalize()
        self.description = monster_gen()
        for i in range(0, 6): 
            statroll = random.choice([random.randint(1, 6) \
                for j in range(0, 6)])
            self.stats[i] = statroll + lvl
        artifact = artygen().split(':')
        self.treasure['quest'] = artifact[0].strip()
        self.artifact = [a.strip() for a in artifact]
        self.skill = 'Cure'
        for i in range(0, lvl):
            hpi = random.choice([random.randint(max([1, self.stats[3] / 2]), \
                self.stats[3]) for j in range(0, 6)])
            self.hitpoints = [x + hpi for x in self.hitpoints]
        spi = random.choice([random.randint(1, self.stats[5]) \
            for j in range(0, 6)]) + 2 * (lvl - 1)
        self.skillpoints = [spi, spi]
        self.combat['atk'] = [lvl / 2, self.stats[0]]
        self.combat['dfn'] = [lvl / 2, self.stats[1]]
        self.flee = False
