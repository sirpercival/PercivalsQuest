"""
Equipment-related functions
for Percival's Quest RPG.
"""

#
#  pq_equipment.py
#  Part of Percival's Quest RPG

import random, json

with open('data/pq_magic.json') as f:
    pq_magic = json.load(f)

with open('data/pq_gear.json') as f:
    pq_gear = json.load(f)

pq_value = (1, 10, 100, 500, 1000, 5000, 10000, 50000, 100000)

def pq_item_type(item):
    """Determine the item type (ring, armor, weapon, and subtypes therein)"""
    if item.lower() in [x.lower() for x in pq_magic['ring'].keys()]:
        return ['ring']
    itemsplit = item.split()
    gear_list = []
    for j in pq_gear['armor'].keys():
        for k in pq_gear['armor'][j].keys():
            gear_list.append((k, 'armor', j))
    for j in pq_gear['weapon'].keys():
        for k in pq_gear['weapon'][j].keys():
            gear_list.append((k, 'weapon', j))
    for i in itemsplit:
        for j in gear_list:
            if i.lower() == j[0].lower():
                return j[1:]
                    
def pq_item_rating(itemtype, item):
    """Determine the rating of the weapon or armor"""
    itemsplit = item.split()
    rating = 0
    for i in itemsplit:
        rating += pq_gear[itemtype[0]][itemtype[1]].get(i, 0) + \
            pq_magic[itemtype[0]][itemtype[1]].get(i, 0)
    return rating
    
def pq_item_worth(item):
    """Determine the value of the item at the General Store"""
    itemtype = pq_item_type(item)
    if not itemtype:
        return 0
    if itemtype[0] == 'ring':
        return 3000
    return pq_value[pq_item_rating(itemtype, item)]

def pq_treasuregen(level):
    """Generate random monster or chest treasure 
    based on the level of the dungeon it's found on."""
    treasure = {'armor':'', 'weapon':'', 'gp':0}
    treasure['gp'] = random.randint(0, 10*level) #roll for gp
    armor_chance = random.randint(1, 10) #roll for armor
    if armor_chance <= level:
        itemtype = random.choice(pq_gear['armor'].keys())
        max_rating = min([level / 2, 5])
        rating = 0 if max_rating < 1 else random.randint(0, max_rating)
        magic_chance = random.randint(1, 10) #roll for magic
        magic = ''
        if magic_chance <= level:
            max_magic = min([level / 3, 3])
            magic = pq_magic['rarmor'][itemtype].get(str(random.randint(0, \
                max_magic)), '')
            if magic: 
                magic += ' '
        treasure['armor'] = magic + pq_gear['rarmor'][itemtype][str(rating)]
    weapon_chance = random.randint(1, 10) #roll for weapon
    if weapon_chance <= level:
        itemtype = random.choice(pq_gear['weapon'].keys())
        max_rating = min([level / 2, 5])
        rating = 0 if max_rating < 1 else random.randint(0, max_rating)
        magic_chance = random.randint(1, 10) #roll for magic
        magic = ''
        if magic_chance <= level:
            max_magic = min([level / 3, 3])
            magic = pq_magic['rweapon'][itemtype].get(str(random.randint(0, \
                max_magic)), '')
            if magic: 
                magic += ' '
        treasure['weapon'] = magic + pq_gear['rweapon'][itemtype][str(rating)]
    ring_chance = random.randint(3, 15) #roll for ring
    if ring_chance <= level:
        treasure['ring'] = random.choice(pq_magic['ring'].keys())
    return treasure