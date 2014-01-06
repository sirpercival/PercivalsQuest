#
#  pq_skills.py
#  part of Percival's Quest RPG

from pq_utilities import atk_roll
from pq_characters import pq_stats_short
import random

pq_reverse_stats = {0:"Attack", 1:"Defense", 2:"Reflexes",
    3:"Fortitude", 4:"Mind", 5:"Skill"}

def pq_smite(user, target):
    """Perform a Smite -- a single attack with a buff of 1dSkill"""
    temp_atk = user.atk
    temp_atk[1] += random.randint(1,user.stats[5])
    hit = atk_roll(temp_atk, target.dfn, user.temp.get("Attack",0), target.temp.get("Defense",0))
    return hit

def pq_cure(user, target):
    """Perform a Cure (healing 1dSkill + level), followed by a normal attack."""
    cure = random.randint(1,user.stats[5]+user.temp.get("Skill",0)) + user.level
    user.cure(cure)
    hit = atk_roll(user.atk, target.dfn, user.temp.get("Attack",0), target.temp.get("Defense",0))
    targstring = "You are " if hasattr(user,"player") else "The monster is " 
    print targstring+"cured for "+str(cure)+" hp! An attack follows."
    return hit

def pq_trip(user, target):
    """Perform a Trip -- a single attack for half damage + debuff Attack 1dSkill"""
    hit = atk_roll(user.atk,target.atk,user.temp.get("Attack",0),target.temp.get("Attack",0))
    if hit > 0:
        hit = max([hit/2,1])
        targstring = "The monster is " if hasattr(user,"player") else "You are "
        print targstring+"tripped!"
        if "tripped" not in target.conditions:
            target.conditions["tripped"] = 2
        debuff = max([0,random.choice([random.randint(0,user.stats[5]) for i in range(0,6)]) + user.temp.get("Skill",0)])
        target.temp_bonus(["Attack"], debuff,4)
    return hit

def pq_missile(user, target):
    """Perform a Missile -- a single attack, Skill vs Reflexes"""
    num_missile = user.level/3 + 1
    targstring = "You send " if hasattr(user,"player") else "The monster sends "
    print targstring + str(num_missile)+" missiles!"
    hit = 0
    for i in range(num_missile):
        hit += max([0,atk_roll([0,user.stats[5]],[0,target.stats[2]],user.temp.get("Skill",0),target.temp.get("Reflex",0))])
    return hit

def pq_doublestrike(user, target):
    """Perform a Doublestrike -- two attacks at -2"""
    hit1 = max([0,atk_roll(user.atk,target.dfn,user.temp.get("Attack",0)-2,target.temp.get("Defense",0))])
    hit2 = max([0,atk_roll(user.atk,target.dfn,user.temp.get("Attack",0)-2,target.temp.get("Defense",0))])
    return hit1 + hit2

def pq_backstab(user, target):
    """Perform a Backstab -- a single attack which does x2 damage if you succeed at Skill vs Fortitude"""
    check = atk_roll([0,user.stats[5]],[0,target.stats[3]],user.temp.get("Skill",0),target.temp.get("Fortitude",0))
    hit = atk_roll(user.atk,target.dfn,user.temp.get("Attack",0),target.temp.get("Defense",0))
    if hit > 0 and check > 0:
        return hit * 2
    return hit

def pq_rage(user, target):
    """Perform a Rage -- a single attack with +Skill buff, and -2 Defense self-debuff for 2 rounds"""
    hit = atk_roll(user.atk,target.dfn,user.temp.get("Attack",0)+user.stats[5],target.temp.get("Defense",0))
    user.temp_bonus(["Defense"],-2,4)
    return hit

def pq_poison(user, target):
    """Perform a Poison -- automatic damage = Skill if target is at less than max hp"""
    hit = user.stats[5] if target.currenthp < target.hp else 0
    return hit

def pq_petrify(user, target):
    """Perform a Petrify vs Fortitude."""
    hit1 = atk_roll([0,user.stats[5]],[0,target.stats[3]],user.temp.get("Skill",0),target.temp.get("Fortitude",0))
    hit2 = atk_roll([0,user.stats[5]],[0,target.stats[3]],user.temp.get("Skill",0),target.temp.get("Fortitude",0))
    hit3 = atk_roll([0,user.stats[5]],[0,target.stats[3]],user.temp.get("Skill",0),target.temp.get("Fortitude",0))
    return hit1 > 0 and hit2 > 0 and hit3 > 0
    
def pq_charm(user, target):
    """Perform a Charm vs Mind."""
    hit1 = atk_roll([0,user.stats[5]],[0,target.stats[4]],user.temp.get("Skill",0),target.temp.get("Mind",0))
    hit2 = atk_roll([0,user.stats[5]],[0,target.stats[4]],user.temp.get("Skill",0),target.temp.get("Mind",0))
    if hit1 > 0 and hit2 > 0:
        targstring = "The monster is " if hasattr(user,"player") else "You are "
        print targstring+"charmed!"
        if "charmed" not in target.conditions:
            target.conditions["charmed"] = 4
        return True
    return False

def pq_entangle(user, target):
    """Perform an Entangle (Skill vs Reflexes) to debuff."""
    hit = atk_roll([0,user.stats[5]],[0,target.stats[2]],user.temp.get("Skill",0),target.temp.get("Reflex",0))
    if hit > 0:
        targstring = "The monster is " if hasattr(user,"player") else "You are "
        print targstring+"entangled!"
        if "entangled" not in target.conditions:
            target.conditions["entangled"] = 4
        target.temp_bonus(["Attack","Defense"],-hit,4)
        return True
    return False

def pq_fear(user, target):
    """Perform a Fear (Skill vs Mind) to debuff."""
    hit = atk_roll([0,user.stats[5]],[0,target.stats[4]],user.temp.get("Skill",0),target.temp.get("Mind",0))
    if hit > 0:
        hit = max([1,hit/2])
        targstring = "The monster is " if hasattr(user,"player") else "You are "
        print targstring+"frightened!"
        target.temp_bonus(["Attack","Defense"],-hit,4)
        return True
    return False
    
def pq_dominate(user, target):
    """Perform a Dominate (Skill vs Mind); if successful, enemy attacks self"""
    affect = atk_roll([0,user.stats[5]],[0,target.stats[4]],user.temp.get("Skill",0),target.temp.get("Mind",0))
    if affect > 0:
        hit = atk_roll(target.atk,target.dfn,target.temp.get("Attack",0)+affect,target.temp.get("Defense",0))
        targstring = "The monster is " if hasattr(user,"player") else "You are "
        targstring2 = "s itself!" if hasattr(user,"player") else " yourself!"
        print targstring+"dominated, and attack"+targstring2
        return hit
    return affect



