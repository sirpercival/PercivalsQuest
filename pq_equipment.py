#
#  pq_equipment.py
#  Part of Percival's Quest RPG

import random

pq_magic = {
    'ring':{'Protection':'Evade', 'Fury':'Smite', 'Subtlety':'Backstab',
        'Regeneration':'Cure', 'Glibness':'Charm', 'Webs':'Entangle', 
        'Force':'Missile','Speed':'Doublestrike', 'Berserking':'Rage', 
        'Venom':'Poison', 'Avoidance':'Flee','Intimidation':'Fear', 
        'Basilisk':'Petrify', 'Influence':'Dominate'},
    'armor':{'Caster':{'Masterwork':1,'Spidersilk':2,'Enchanted':3},
        'Cloth':{'Masterwork':1,'Thistledown':2,'Twilight':3},
        'Leather':{'Masterwork':1,'Leafweave':2,'Dragonhide':3},
        'Mail':{'Masterwork':1,'Mithril':2,'Adamantine':3}},
    'rarmor':{'Caster':{1:'Masterwork',2:'Spidersilk',3:'Enchanted'},
        'Cloth':{1:'Masterwork',2:'Thistledown',3:'Twilight'},
        'Leather':{1:'Masterwork',2:'Leafweave',3:'Dragonhide'},
        'Mail':{1:'Masterwork',2:'Mithril',3:'Adamantine'}},
    'weapon':{'Swords':{'Masterwork':1,'Keen':2,'Vorpal':3},
        'Axes':{'Masterwork':1,'Wounding':2,'Vicious':3},
        'Polearms':{'Masterwork':1,'Lunging':2,'Valorous':3},
        'Clubs':{'Masterwork':1,'Impactful':2,'Dolorous':3},
        'Whips':{'Masterwork':1,'Animated':2,'Dancing':3}},
    'rweapon':{'Swords':{1:'Masterwork',2:'Keen',3:'Vorpal'},
        'Axes':{1:'Masterwork',2:'Wounding',3:'Vicious'},
        'Polearms':{1:'Masterwork',2:'Lunging',3:'Valorous'},
        'Clubs':{1:'Masterwork',2:'Impactful',3:'Dolorous'},
        'Whips':{1:'Masterwork',2:'Animated',3:'Dancing'}}}
        
pq_gear = {
    'armor':{'Caster':{'Sack':0,'Robes':1,'Vestment':2,'Bolero':3,'Habit':4,'Djellaba':5},
        'Cloth':{'Shirt':0,'Jerkin':1,'Vest':2,'Padded':3,'Gi':4,'Mantle':5},
        'Leather':{'Loincloth':0,'Hide':1,'Studded':2,'Brigandine':3,'Lamellar':4,'Banded':5},
        'Mail':{'Barrel':0,'Splintmail':1,'Chainmail':2,'Scalemail':3,'Breastplate':4,'Platemail':5}},
    'rarmor':{'Caster':{0:'Sack',1:'Robes',2:'Vestment',3:'Bolero',4:'Habit',5:'Djellaba'},
        'Cloth':{0:'Shirt',1:'Jerkin',2:'Vest',3:'Padded',4:'Gi',5:'Mantle'},
        'Leather':{0:'Loincloth',1:'Hide',2:'Studded',3:'Brigandine',4:'Lamellar',5:'Banded'},
        'Mail':{0:'Barrel',1:'Splintmail',2:'Chainmail',3:'Scalemail',4:'Breastplate',5:'Platemail'}},
    'weapon':{'Swords':{'Dagger':0,'Machete':1, 'Rapier':2, 'Longsword':3,'Falchion':4,'Claymore':5},
        'Axes':{'Cleaver':0,'Hatchet':1,'Battleaxe':2,'Waraxe':3,'Lochaber':4,'Greataxe':5},
        'Polearms':{'Broom':0,'Quarterstaff':1,'Spear':2,'Pike':3,'Glaive':4,'Halberd':5},
        'Clubs':{'Sap':0,'Club':1,'Truncheon':2,'Warhammer':3,'Greatclub':4,'Maul':5},
        'Whips':{'Rope':0,'Whip':1,'Chain':2,'Flail':3,'Kusarigama':4,'Dragonfist':5}},
    'rweapon':{'Swords':{0:'Dagger',1:'Machete',2:'Rapier',3:'Longsword',4:'Falchion',5:'Claymore'},
        'Clubs':{0:'Sap',1:'Club',2:'Truncheon',3:'Warhammer',4:'Greatclub',5:'Maul'},
        'Axes':{0:'Cleaver',1:'Hatchet',2:'Battleaxe',3:'Waraxe',4:'Lochaber',5:'Greataxe'},
        'Polearms':{0:'Broom',1:'Quarterstaff',2:'Spear',3:'Pike',4:'Glaive',5:'Halberd'},
        'Whips':{0:'Rope',1:'Whip',2:'Chain',3:'Flail',4:'Kusarigama',5:'Dragonfist'}}}

pq_value = (1,10,100,500,1000,5000,10000,50000,100000)

def pq_item_type(item):
    """Determine the item type (ring, armor, weapon, and subtypes therein)"""
    if item in pq_magic['ring'].keys():
        return ['ring']
    itemsplit = item.split()
    gear_list = [(k,'armor',j) for j in pq_gear['armor'].keys() for k in pq_gear['armor'][j].keys(),
        (k,'weapon',j) for j in pq_gear['weapon'].keys() for k in pq_gear['weapon'][j].keys()]
    for i in itemsplit:
        for j in gear_list:
            if i.lower() == j[0].lower():
                return j[1:]
                    
def pq_item_rating(type, item):
    """Determine the rating of the weapon or armor"""
    itemsplit = item.split()
    rating = 0
    for i in itemsplit:
        rating += pq_gear[type[0]][type[1]].get(i,0) + pq_magic[type[0]][type[1]].get(i,0)
    return rating
    
def pq_item_worth(item):
    """Determine the value of the item at the General Store"""
    type = pq_item_type(item)
    if type[0] == 'ring':
        return 3000
    elif type:
        return pq_value[pq_item_rating(type,item)]
    else:
        return 0

def pq_treasuregen(level):
    """Generate random monster or chest treasure based on the level of the dungeon it's found on."""
    treasure = {'armor':'', 'weapon':'', 'gp':0}
    treasure['gp'] = random.randint(0,10*level) #roll for gp
    armor_chance = random.randint(1,10) #roll for armor
    if armor_chance <= level:
        type = random.choice(pq_gear['armor'].keys())
        max_rating = min([level/2,5])
        rating = random.randint(1,max_rating)
        magic_chance = random.randint(1,10) #roll for magic
        magic = ''
        if magic_chance <= level:
            max_magic = min([level/3,3])
            magic = pq_magic['rarmor'][type].get(random.randint(0,max_magic),'')
            if magic: magic += ' '
        treasure['armor'] = magic + pq_gear['rarmor'][type][rating]
    weapon_chance = random.randint(1,10) #roll for weapon
    if weapon_chance <= level:
        type = random.choice(pq_gear['weapon'].keys())
        max_rating = min([level/2,5])
        rating = random.randint(0,max_rating)
        magic_chance = random.randint(1,10) #roll for magic
        magic = ''
        if magic_chance <= level:
            max_magic = min([level/3,3])
            magic = pq_magic['rweapon'][type].get(random.randint(0,max_magic),'')
            if magic: magic += ' '
        treasure['weapon'] = magic + pq_gear['rweapon'][type][rating]
    ring_chance = random.randint(3,15) #roll for ring
    if ring_chance <= level:
        treasure['ring'] = random.choice(pq_magic['ring'].keys())
    return treasure