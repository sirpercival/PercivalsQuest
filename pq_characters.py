"""
Module for Percival's Quest

Declaration for Character object
"""


#
#  pq_characters.py
#  Part of Percival's Quest RPG

from pq_namegen import web_namegen
from pq_utilities import choose_from_list, collapse_stringlist, color
from pq_equipment import pq_gear, pq_magic, pq_item_type, \
    pq_item_rating, pq_item_worth
import random, textwrap

pq_feats = {'PowerAttack':0, 'StoutDefense':1, 'LightningReflexes':2, 
    'Toughness':3, 'IronWill':4, 'Prodigy':5, 'ImprovedInitiative':-1}
        
pq_stats_short = {0:'Atk', 1:'Def', 2:'Ref', 3:'Frt', 4:'Mnd', 5:'Skl'}

class PQ_Character(object):
    """Class for the Character object, aka the PC"""
    def __init__(self):
        """Initialize Character instance"""
        self.name = ["", ""] #character, player
        self.level = [1, 0] #exp, level
        self.hitpoints = [1, 1] #current, max
        self.skillpoints = [1, 1] #current, max
        self.raceclass = ["", ""] #race, class
        self.skill = []
        self.stats = [0, 0, 0, 0, 0, 0]
        self.feats = []
        self.combat = {'initiative':0, 'atk':[0, 0], 'dfn':[0, 0]}
        self.gear = {"armor":{'name':'', 'rating':0}, "weapon":{'name':'',
            'rating':0}, "ring":""}
        self.loot = {"quest":'', "gp":0, "items":[]}
        self.temp = {'stats':{}, 'statturns':{}, 'condition':{}}
        self.dead = False
        self.queststatus = "inactive"
    
    def chargen(self, player):
        """
        Generate a new character using (possibly random) race, class, 
        and feat choices.
        """
        import json
        print textwrap.fill("It's time to generate a character! At any " \
            "of the prompts below, enter 'random' (no quotes) to use " \
            "a random choice.")
        self.name = [color.GREEN + web_namegen(5, 12, 2).replace('\n', ' ') \
            + color.END, player]
        self.level = [0, 1]
        with open('data/pq_classes.json') as f:
            pq_classes = json.load(f)
        with open('data/pq_races.json') as f:
            pq_races = json.load(f)
        print "Available races: " + ", ".join(sorted(pq_races.keys()))
        race = choose_from_list("Race> ", pq_races.keys(), rand=True, \
            character=self, allowed=['sheet', 'help'])
        print "Available classes: " + ", ".join(sorted(pq_classes.keys()))
        clas = choose_from_list("Class> ", pq_classes.keys(), rand=True, \
            character=self, allowed=['sheet', 'help'])
        nfeat = 2 if race.lower() == "human" else 1
        print "Available feats: " + ", ".join(sorted(pq_feats.keys()))
        feats = []
        for i in range(nfeat):
            feat = choose_from_list("Feat> ", pq_feats.keys(), rand=True, \
                character=self, allowed=['sheet', 'help'])
            feats.append(feat)
        self.raceclass = [race, clas]
        self.loot["gp"] = 0
        for i in range(0, 6):
            statroll = random.choice([random.randint(1, 4) \
                for j in range(0, 6)])
            self.stats[i] = statroll + \
                pq_classes[self.raceclass[1]]['stat'][i] + \
                pq_races[self.raceclass[0]]['stat'][i]
        self.feats = feats
        for i in feats:
            for j in pq_feats.keys():
                if i.lower() == 'improvedinitiative': 
                    self.combat['initiative'] += 2
                elif i.lower() == j.lower():
                    self.stats[pq_feats[j]] += 2
                    break
        self.hitpoints = [self.stats[3], self.stats[3]]
        self.skillpoints = [self.stats[5], self.stats[5]]
        self.gear['armor']['name'] = pq_gear['rarmor'][random.choice \
            (pq_gear['rarmor'].keys())]['0']
        self.gear['armor']['rating'] = 0
        self.gear['weapon']['name'] = pq_gear['rweapon'][random.choice \
            (pq_gear['rweapon'].keys())]['0']
        self.gear['weapon']['rating'] = 0
        self.gear['ring'] = ''
        self.combat['atk'] = [self.gear['weapon']['rating'], self.stats[0]]
        self.combat['dfn'] = [self.gear['armor']['rating'], self.stats[1]]
        self.skill = []
        self.skill.append(pq_classes[self.raceclass[1]]['skill'])
        self.tellchar()
        
    def tellchar(self):
        """Print out the character sheet"""
        print color.BOLD + self.name[0] + color.END + ' (Player: ' + \
            self.name[1] + ')'
        print color.BOLD + ' '.join([self.raceclass[0].capitalize(), \
            self.raceclass[1].capitalize(), str(self.level[1])]) + color.END
        statstring = sum([[color.BOLD + pq_stats_short[i] + color.END, \
            str(self.stats[i])] for i in range(0,6)], [])
        feats = collapse_stringlist(self.feats, True, True)
        feats = ', '.join(sorted(feats))
        print '; '.join([' '.join(statstring), color.BOLD + 'hp ' + \
            color.END + str(self.hitpoints[0]) + '/' + \
            str(self.hitpoints[1]), color.BOLD + 'sp ' + color.END + \
            str(self.skillpoints[0]) + '/' + str(self.skillpoints[1]), \
            color.BOLD + 'exp ' + color.END + str(self.level[0]) + '/' + \
            str(self.level[1]*10)])
        print textwrap.fill(feats)
        if not self.gear['armor']['name']:
            armor = color.BOLD + 'Armor:' + color.END + ' None (0)'
        else:
            armor = color.BOLD + 'Armor:' + color.END + ' ' + \
                self.gear['armor']['name'] + ' (' + \
                str(self.gear['armor']['rating']) + ')'
        if not self.gear['weapon']['name']:
            weapon = color.BOLD + 'Weapon:' + color.END + ' None (-1)'
        else:
            weapon = color.BOLD + 'Weapon:' + color.END + ' '+  \
                self.gear['weapon']['name'] + ' (' + \
                str(self.gear['weapon']['rating']) + ')'
        if not self.gear['ring']:
            ring = color.BOLD + 'Ring:' + color.END + ' None'
        else:
            ring = color.BOLD + 'Ring:' + color.END + ' ' + self.gear['ring']
        print '; '.join([color.BOLD + 'Skills: ' + color.END + \
            ', '.join(self.skill), armor, weapon, ring])
        lootbag = collapse_stringlist(self.loot['items'], True, True)
        for i, f in enumerate(lootbag):
            for l in f.split():
                if l.lower() in [x.lower() for x in pq_magic['ring'].keys()]:
                    lootbag[i] = "Ring of " + lootbag[i]
        if not lootbag:
            lootbag = 'None'
        else:
            lootbag = ', '.join(lootbag)
        print textwrap.fill(str(self.loot['gp']) + \
            ' gp; loot: ' + lootbag), '\n'
        
    def levelup(self):
        """Increasing level, including the feat choice 
        that you get every level."""
        self.level[0] -= self.level[1] * 10
        self.level[1] += 1
        print "You have leveled up! Please choose a feat; if you would like " \
            "one randomly chosen for you, enter Random."
        print "Available feats: " + ", ".join(pq_feats.keys())
        feat_choice = choose_from_list("Feat> ", pq_feats.keys(), rand=True, \
            character=self, allowed=['sheet', 'help', 'equip'])
        if feat_choice.lower() in 'improvedinitiative':
            self.combat['initiative'] += 2
            self.feats.append('ImprovedInitiative')
        else:
            for i in pq_feats.keys():
                if i.lower() == feat_choice.lower():
                    self.stats[pq_feats[i]] += 2
                    self.feats.append(i)
        self.hitpoints[1] += random.choice([random.randint(max([1, \
            self.stats[3] / 2]), 1 + self.stats[3]) for j in range(0, 6)])
        self.skillpoints[1] += 2
        self.combat['atk'] = [self.gear['weapon']['rating'], self.stats[0]]
        self.combat['dfn'] = [self.gear['armor']['rating'], self.stats[1]]
        print "Level up complete!"
        self.tellchar()
    
    def sleep(self):
        """Regain all hp and sp due to snoozage."""
        for i in self.temp:
            self.temp[i] = {}
        self.hitpoints[0] = self.hitpoints[1]
        self.skillpoints[0] = self.skillpoints[1]
        
    def ouch(self, damage):
        """Deal damage to self. OW"""
        self.hitpoints[0] -= damage
        
    def huh(self, damage):
        """Deal damage to self's skill points. WHUT"""
        self.skillpoints[0] -= damage
        
    def cure(self, damage):
        """Heal self. YAY"""
        self.hitpoints[0] = self.hitpoints[1] if self.hitpoints[0] + damage > \
            self.hitpoints[1] else self.hitpoints[0] + damage
        
    def sammich(self, level):
        """Eat a sandwich slowly in an empty room, regain some sp and hp."""
        for i in self.temp:
            self.temp[i] = {}
        self.cure(level)
        self.skillpoints[0] = self.skillpoints[1] if self.skillpoints[0] + \
            level > self.skillpoints[1] else self.skillpoints[0] + level
        
    def temp_bonus(self, stat, bonus, turns):
        """Apply a temporary bonus or penalty to self."""
        for i in stat:
            if self.temp.get(i, False):
                sign = -1 if bonus < 0 else 1
                bonus = sign * max([abs(self.temp[i]), abs(bonus)])
            self.temp['stats'][i] = bonus
            self.temp['statturns'][i] = turns
        
    def equip(self):
        """Equip an item, unequipping extant item if necessary."""
        if not self.loot['items']:
            print "You have nothing to equip!"
            return
        print "What would you like to equip?"
        lootbag = ['Ring of ' + i if i in pq_magic['ring'].keys() \
            else i for i in self.loot['items']]
        lootbag_basic = collapse_stringlist(lootbag, sortit=True, \
            addcounts=False)
        print textwrap.fill("Lootbag: " + \
            ", ".join(collapse_stringlist(lootbag, sortit=True, \
            addcounts=True)))
        equipment = choose_from_list("Equip> ", lootbag_basic, rand=False, \
            character=self, allowed=['sheet', 'help'])
        equipment = equipment.replace('Ring of ', '')
        itemtype = pq_item_type(equipment)
        oldequip = ''
        if itemtype[0] == "ring":
            if self.gear['ring']:
                self.skill.remove(pq_magic['ring'][self.gear['ring']])
                self.loot['items'].append(self.gear['ring'])
                oldequip = self.gear['ring']
            self.skill.append(pq_magic['ring'][equipment])
            self.gear['ring'] = equipment
            self.loot['items'].remove(equipment)
        else:
            new_rating = pq_item_rating(itemtype, equipment)
            if self.gear[itemtype[0]]['name']:
                self.loot['items'].append(self.gear[itemtype[0]]['name'])
                oldequip = self.gear[itemtype[0]]['name']
            self.gear[itemtype[0]]['name'] = equipment
            self.gear[itemtype[0]]['rating'] = new_rating
            self.loot['items'].remove(equipment)
        self.combat['atk'] = [self.gear['weapon']['rating'], self.stats[0]]
        self.combat['dfn'] = [self.gear['armor']['rating'], self.stats[1]]
        print equipment + " equipped!"
        if oldequip:
            print oldequip + " unequipped!"
        return
            
    def complete_quest(self, experience, gold):
        """Get xp and gold for completing a quest; 
        also, reset quest item slot"""
        self.loot['quest'] = ''
        self.level[0] += experience
        self.loot['gp'] += gold
        self.queststatus = "active"
    
    def sell_loot(self, sell, count = 1):
        """Character-side loot sale (removing item 
        from lootbag, adding gp)"""
        if type(sell) is list:
            sell = sell[0]
        lowitems = [x.lower() for x in self.loot['items']]
        if sell.lower() not in lowitems: 
            return False
        value = max([pq_item_worth(sell)/2, 1])
        loot = []
        for j in sorted(self.loot['items']):
            if sell.lower() == j.lower() and count > 0:
                self.loot['gp'] += value
                count -= 1
            else:
                loot.append(j)
        self.loot['items'] = loot
        return True
        
    def buy_loot(self, buy, cost):
        """Character-side loot purchase (adding item 
        to lootbag, subtracting gp)"""
        if type(buy) is list:
            buy = buy[0]
        buy = ' '.join([i.lower().capitalize() for i in buy.split()])
        self.loot['items'].append(buy)
        self.loot['gp'] -= cost
    
    def defeat_enemy(self, exp, loot):
        """Get loot and exp for defeating an enemy, or some other reason."""
        for i in self.temp:
            self.temp[i] = {}
        self.level[0] += exp
        for i in loot.keys():
            if i == 'gp':
                self.loot['gp'] += loot[i]
            elif i == 'quest' and not self.loot['quest']:
                self.loot['quest'] = loot['quest'] 
            elif loot[i]:
                self.loot['items'].append(loot[i])