#
#  pq_characters.py
#  Part of Percival's Quest RPG

from pq_namegen import web_namegen
from pq_utilities import *
from pq_equipment import *
import random, textwrap

pq_classes = {
    'fighter': {'stat':(5,3,2,4,0,1), 'skill':'Trip'},
    'paladin': {'stat':(5,3,0,4,2,1), 'skill':'Smite'},
    'ranger': {'stat':(4,5,3,2,1,0), 'skill':'Doublestrike'},
    'cleric': {'stat':(2,5,0,1,3,4), 'skill':'Cure'},
    'rogue': {'stat':(3,2,5,0,1,4), 'skill':'Backstab'},
    'bard': {'stat':(1,2,5,0,4,3), 'skill':'Charm'},
    'barbarian': {'stat':(4,3,2,5,1,0), 'skill':'Rage'},
    'druid': {'stat':(1,2,0,5,3,4), 'skill':'Entangle'},
    'monk': {'stat':(3,4,2,0,5,1), 'skill':'Evade'},
    'wizard': {'stat':(0,2,3,1,4,5), 'skill':'Missile'},
    'psion': {'stat':(0,1,2,3,5,4), 'skill':'Dominate'},
    'samurai': {'stat':(4,3,0,2,1,5), 'skill':'Fear'}}
    
pq_races = {
    'human': {'stat':(0,0,0,0,0,0), 'ben':'Bonus feat'},
    'dwarf': {'stat':(0,0,0,1,1,0), 'ben':'+1 Fortitude, +1 Mind'},
    'elf': {'stat':(0,0,1,0,0,1), 'ben':'+1 Reflexes, +1 Skill'},
    'halfling': {'stat':(0,1,1,0,0,0), 'ben':'+1 Defense, +1 Reflexes'},
    'gnome': {'stat':(0,0,0,1,0,1), 'ben':'+1 Fortitude, +1 Skill'},
    'orc': {'stat':(1,1,0,0,0,0), 'ben':'+1 Attack, +1 Defense'},
    'drow': {'stat':(1,0,0,0,1,0), 'ben':'+1 Attack, +1 Mind'}}

pq_feats = {'PowerAttack':0,'StoutDefense':1,'LightningReflexes':2, 
    'Toughness':3,'IronWill':4,'Prodigy':5,'ImprovedInitiative':-1}
        
pq_stats_short = {0:'Atk',1:'Def',2:'Ref',3:'Frt',4:'Mnd',5:'Skl'}
        
class PQ_Character(object):
    def __init__(self):
        """Initialize Character instance"""
        self.name = ""
        self.level = 1
        self.hp = 1
        self.currenthp = 1
        self.sp = 1
        self.currentsp = 1
        self.race = ""
        self.clas = ""
        self.skill = []
        self.stats = [0,0,0,0,0,0]
        self.feats = [""]
        self.player = ""
        self.initiative = 0
        self.atk = [0,0]
        self.dfn = 0
        self.gear = {"armor":{'name':'','rating':0},"weapon":{'name':'','rating':0}, "ring":""}
        self.loot = {"quest":'', "gp":0, "items":[]}
        self.exp = 0
        self.temp = {}
        self.tempturns = {}
        self.dead = False
        self.queststatus = "inactive"
        self.conditions = {}
    
    def chargen(self,player):
        """Generate a new character using (possibly random) race, class, and feat choices."""
        print "It's time to generate a character! At any of the prompts below, enter 'random' (no quotes) to use a random choice."
        self.player = player
        self.name = color.GREEN+web_namegen(5,12,2).replace('\n',' ')+color.END
        self.level = 1
        print "Available races: "+", ".join(sorted(pq_races.keys()))
        race = choose_from_list("Race> ",pq_races.keys(),rand=True,character=self,allowed=['sheet','help'])
        print "Available classes: "+", ".join(sorted(pq_classes.keys()))
        clas = choose_from_list("Class> ",pq_classes.keys(),rand=True,character=self,allowed=['sheet','help'])
        nfeat = 2 if race.lower() == "human" else 1
        print "Available feats: "+", ".join(sorted(pq_feats.keys()))
        feats = []
        for i in range(nfeat):
            feat = choose_from_list("Feat> ",pq_feats.keys(),rand=True,character=self,allowed=['sheet','help'])
            feats.append(feat)
        self.race = race
        self.clas = clas
        self.exp = 0
        self.loot["gp"] = 0
        for i in range(0,6):
            statroll = random.choice([random.randint(1,4) for j in range(0,6)])
            self.stats[i] = statroll + pq_classes[self.clas]['stat'][i] + pq_races[self.race]['stat'][i]
        self.feats = feats
        for i in feats:
            for j in pq_feats.keys():
                if i.lower() == 'improvedinitiative': 
                    self.initiative += 2
                elif i.lower() == j.lower():
                    self.stats[pq_feats[j]] += 2
                    break
        self.hp = self.stats[3]
        self.sp = self.stats[5]
        self.currenthp = self.hp
        self.currentsp = self.sp
        self.gear['armor']['name'] = pq_gear['rarmor'][random.choice(pq_gear['rarmor'].keys())][0]
        self.gear['armor']['rating'] = 0
        self.gear['weapon']['name'] = pq_gear['rweapon'][random.choice(pq_gear['rweapon'].keys())][0]
        self.gear['weapon']['rating'] = 0
        self.gear['ring'] = ''
        self.atk = [self.gear['weapon']['rating'],self.stats[0]]
        self.dfn = [self.gear['armor']['rating'],self.stats[1]]
        self.skill = []
        self.skill.append(pq_classes[self.clas]['skill'])
        self.tellchar()
        
    def tellchar(self):
        """Print out the character sheet"""
        print color.BOLD+self.name+color.END+' (Player: '+self.player+')'
        print color.BOLD+' '.join([self.race.capitalize(),self.clas.capitalize(),str(self.level)])+color.END
        statstring = sum([[color.BOLD+pq_stats_short[i]+color.END,str(self.stats[i])] for i in range(0,6)],[])
        feats = collapse_stringlist(self.feats,True,True)
        feats = ', '.join(sorted(feats))
        print '; '.join([' '.join(statstring),color.BOLD+'hp '+color.END+str(self.currenthp)+'/'+str(self.hp),
            color.BOLD+'sp '+color.END+str(self.currentsp)+'/'+str(self.sp),
            color.BOLD+'exp '+color.END+str(self.exp)+'/'+str(self.level*10)])
        print textwrap.fill(feats)
        if not self.gear['armor']['name']:
            armor = color.BOLD+'Armor:'+color.END+' None (0)'
        else:
            armor = color.BOLD+'Armor:'+color.END+' '+self.gear['armor']['name']+ \
                ' ('+str(self.gear['armor']['rating'])+')'
        if not self.gear['weapon']['name']:
            weapon = color.BOLD+'Weapon:'+color.END+' None (-1)'
        else:
            weapon = color.BOLD+'Weapon:'+color.END+' '+self.gear['weapon']['name']+ \
                ' ('+str(self.gear['weapon']['rating'])+')'
        if not self.gear['ring']:
            ring = color.BOLD+'Ring:'+color.END+' None'
        else:
            ring = color.BOLD+'Ring:'+color.END+' '+self.gear['ring']
        print '; '.join([color.BOLD+'Skills: '+color.END+', '.join(self.skill),armor,weapon,ring])
        lootbag = collapse_stringlist(self.loot['items'],True,True)
        for i,f in enumerate(lootbag):
            for l in f.split():
                if l.lower() in [x.lower() for x in pq_magic['ring'].keys()]:
                    lootbag[i] = "Ring of "+lootbag[i]
        if not lootbag:
            lootbag = 'None'
        else:
            lootbag = ', '.join(lootbag)
        print textwrap.fill(str(self.loot['gp'])+' gp; loot: '+lootbag), '\n'
        
    def levelup(self):
        """Increasing level, including the feat choice that you get every level."""
        self.exp -= self.level * 10
        self.level += 1
        print "You have leveled up! Please choose a feat; if you would like one randomly chosen for you, enter Random."
        print "Available feats: "+", ".join(pq_feats.keys())
        feat_choice = choose_from_list("Feat> ",pq_feats.keys(),rand=True,character=self,allowed=['sheet','help','equip'])
        if feat_choice.lower() in 'improvedinitiative':
            self.initiative += 2
            self.feats.append('ImprovedInitiative')
        else:
            for i in pq_feats.keys():
                if i.lower() == feat_choice.lower():
                    self.stats[pq_feats[i]] += 2
                    self.feats.append(i)
        self.hp += random.choice([random.randint(max([1,self.stats[3]/2]),1+self.stats[3]) for j in range(0,6)])
        self.sp += 2
        self.atk = [self.gear['weapon']['rating'],self.stats[0]]
        self.dfn = [self.gear['armor']['rating'],self.stats[1]]
        print "Level up complete!"
        self.tellchar()
    
    def sleep(self):
        """Regain all hp and sp due to snoozage."""
        self.temp = {}
        self.tempturns = {}
        self.conditions = {}
        self.currenthp = self.hp
        self.currentsp = self.sp
        
    def ouch(self,damage):
        """Deal damage to self. OW"""
        self.currenthp -= damage
        
    def cure(self,damage):
        """Heal self. YAY"""
        self.currenthp = self.hp if self.currenthp + damage > self.hp else self.currenthp + damage
        
    def sammich(self, level):
        """Eat a sandwich slowly in an empty room, regain some sp and hp."""
        self.temp = {}
        self.tempturns = {}
        self.conditions = {}
        self.cure(level)
        self.currentsp = self.sp if self.currentsp + level > self.sp else self.currentsp + level
        
    def temp_bonus(self, stat, bonus, turns):
        """Apply a temporary bonus or penalty to self."""
        for i in stat:
            if self.temp.get(i,False):
                sign = -1 if bonus < 0 else 1
                bonus = sign * max([abs(self.temp[i]),abs(bonus)]) #overwrite with whichever bonus is higher, and reset turns
            self.temp[i] = bonus
            self.tempturns[i] = turns
        
    def equip(self):
        """Equip an item, unequipping extant item if necessary."""
        if not self.loot['items']:
            print "You have nothing to equip!"
            return
        print "What would you like to equip?"
        lootbag = ['Ring of '+i if i in pq_magic['ring'].keys() else i for i in self.loot['items']]
        lootbag_basic = collapse_stringlist(lootbag,sortit=True,addcounts=False)
        print textwrap.fill("Lootbag: "+", ".join(collapse_stringlist(lootbag,sortit=True,addcounts=True)))
        equipment = choose_from_list("Equip> ",lootbag_basic,rand=False,character=self,allowed=['sheet','help'])
        equipment = equipment.replace('Ring of ','')
        type = pq_item_type(equipment)
        oldequip = ''
        if type[0] == "ring":
            if self.gear['ring']:
                self.skill.remove(pq_magic['ring'][self.gear['ring']])
                self.loot['items'].append(self.gear['ring'])
                oldequip = self.gear['ring']
            self.skill.append(pq_magic['ring'][equipment])
            self.gear['ring'] = equipment
            self.loot['items'].remove(equipment)
        else:
            new_rating = pq_item_rating(type,equipment)
            if self.gear[type[0]]['name']:
                self.loot['items'].append(self.gear[type[0]]['name'])
                oldequip = self.gear[type[0]]['name']
            self.gear[type[0]]['name'] = equipment
            self.gear[type[0]]['rating'] = new_rating
            self.loot['items'].remove(equipment)
        self.atk = [self.gear['weapon']['rating'],self.stats[0]]
        self.dfn = [self.gear['armor']['rating'],self.stats[1]]
        print equipment+" equipped!"
        if oldequip:
            print oldequip+" unequipped!"
        return
            
    def complete_quest(self, exp, gp):
        """Get xp and gold for completing a quest; also, reset quest item slot"""
        self.loot['quest'] = ''
        self.exp += exp
        self.loot['gp'] += gp
        self.queststatus = "active"
    
    def sell_loot(self, sell, count = 1):
        """Character-side loot sale (removing item from lootbag, adding gp)"""
        if type(sell) is list:
            sell = sell[0]
        lowitems = [x.lower() for x in self.loot['items']]
        if sell.lower() not in lowitems: return False
        value = max([pq_item_worth(sell)/2,1])
        loot = []
        for j in sorted(self.loot['items']):
            if sell.lower() == j.lower() and count > 0:
                self.loot['gp'] += value
                count -= 1
            else:
                loot.append(j)
        self.loot['items'] = loot
        return True
        
    def buy_loot(self, buy, gp):
        """Character-side loot purchase (adding item to lootbag, subtracting gp)"""
        if type(buy) is list:
            buy = buy[0]
        buy = ' '.join([i.lower().capitalize() for i in buy.split()])
        self.loot['items'].append(buy)
        self.loot['gp'] -= gp
    
    def defeat_enemy(self, exp, loot):
        """Get loot and exp for defeating an enemy, or some other reason."""
        self.temp = {}
        self.tempturns = {}
        self.conditions = {}
        self.exp += exp
        for i in loot.keys():
            if i == 'gp':
                self.loot['gp'] += loot[i]
            elif i == 'quest' and not self.loot['quest']:
                self.loot['quest'] = loot['quest'] 
            elif loot[i]:
                self.loot['items'].append(loot[i])