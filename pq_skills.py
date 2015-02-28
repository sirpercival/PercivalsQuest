"""
Skills module for Percival's Quest RPG
containing a bunch of skill declarations
and the library for calling them by name.
"""
#
#  pq_skills.py
#  part of Percival's Quest RPG

from pq_utilities import atk_roll, send_to_console
import random

pq_reverse_stats = {0:"Attack", 1:"Defense", 2:"Reflexes",
    3:"Fortitude", 4:"Mind", 5:"Skill"}

#ACTIVE SKILLS:

def pq_smite(user, target):
    """Perform a Smite -- a single attack with a buff of 1dSkill"""
    temp_atk = user.combat['atk']
    temp_atk[1] += random.randint(1, user.stats[5])
    hit = atk_roll(temp_atk, target.combat['dfn'], \
        user.temp['stats'].get("Attack", 0), \
        target.temp['stats'].get("Defense", 0))
    return (hit > 0, hit)

def pq_cure(user, target):
    """Perform a Cure (healing 1dSkill + level), 
    followed by a normal attack."""
    cure = random.randint(1, user.stats[5] + \
        user.temp['stats'].get("Skill", 0)) + user.level[1]
    user.cure(cure)
    hit = atk_roll(user.combat['atk'], target.combat['dfn'], \
        user.temp['stats'].get("Attack", 0), \
        target.temp['stats'].get("Defense", 0))
    targstring = "You are " if hasattr(user,"player") else "The monster is " 
    send_to_console(targstring+"cured for "+str(cure)+" hp! An attack follows.")
    return (hit > 0, hit)

def pq_trip(user, target):
    """Perform a Trip -- a single attack for half damage + 
    debuff Attack 1dSkill"""
    hit = atk_roll(user.combat['atk'], target.combat['atk'], \
        user.temp['stats'].get("Attack", 0), \
        target.temp['stats'].get("Attack", 0))
    if hit > 0:
        hit = max([hit/2, 1])
        targstring = "The monster is " if hasattr(user, "gear") \
            else "You are "
        send_to_console(targstring + "tripped!")
        target.temp['condition']["tripped"] = 2
        debuff = max([0, random.choice([random.randint(0, user.stats[5]) \
            for i in range(0, 6)]) + user.temp['stats'].get("Skill", 0)])
        target.temp_bonus(["Attack"], debuff, 4)
    return (hit > 0, hit)

def pq_missile(user, target):
    """Perform a Missile -- a single attack, Skill vs Reflexes"""
    num_missile = user.level[1]/3 + 1
    targstring = "You send " if hasattr(user, "gear") \
        else "The monster sends "
    send_to_console(targstring + str(num_missile) +" missiles!")
    hit = 0
    for i in range(num_missile):
        hit += max([0, atk_roll([0, user.stats[5]], [0, target.stats[2]], \
            user.temp['stats'].get("Skill", 0), \
            target.temp['stats'].get("Reflex", 0))])
    return (hit > 0, hit)

def pq_doublestrike(user, target):
    """Perform a Doublestrike -- two attacks at -2"""
    hit1 = max([0, atk_roll(user.combat['atk'], target.combat['dfn'], \
        user.temp['stats'].get("Attack", 0)-2, \
        target.temp['stats'].get("Defense", 0))])
    hit2 = max([0, atk_roll(user.combat['atk'], target.combat['dfn'], \
        user.temp['stats'].get("Attack", 0)-2, \
        target.temp['stats'].get("Defense", 0))])
    hit = hit1 + hit2
    return (hit > 0, hit)

def pq_backstab(user, target):
    """Perform a Backstab -- a single attack which does x2 damage
    if you succeed at Skill vs Fortitude"""
    check = atk_roll([0, user.stats[5]], [0, target.stats[3]], \
        user.temp['stats'].get("Skill", 0), \
        target.temp['stats'].get("Fortitude", 0))
    hit = atk_roll(user.combat['atk'], target.combat['dfn'], \
        user.temp['stats'].get("Attack", 0), \
        target.temp['stats'].get("Defense", 0))
    if hit > 0 and check > 0:
        return (hit > 0, hit * 2)
    return (hit > 0, hit)

def pq_rage(user, target):
    """Perform a Rage -- a single attack with +Skill buff, 
    and -2 Defense self-debuff for 2 rounds"""
    hit = atk_roll(user.combat['atk'], target.combat['dfn'], \
        user.temp['stats'].get("Attack", 0) + user.stats[5], \
        target.temp['stats'].get("Defense", 0))
    user.temp_bonus(["Defense"], -2, 4)
    return (hit > 0, hit)

def pq_poison(user, target):
    """Perform a Poison -- automatic damage = Skill if target is 
    at less than max hp"""
    hit = user.stats[5] if target.hitpoints[0] < target.hitpoints[1] else 0
    return (hit > 0, hit)

def pq_petrify(user, target):
    """Perform a Petrify vs Fortitude."""
    hit1 = atk_roll([0, user.stats[5]], [0, target.stats[3]], \
        user.temp['stats'].get("Skill", 0), \
        target.temp['stats'].get("Fortitude", 0))
    hit2 = atk_roll([0, user.stats[5]], [0, target.stats[3]], \
        user.temp['stats'].get("Skill", 0), \
        target.temp['stats'].get("Fortitude", 0))
    hit3 = atk_roll([0, user.stats[5]], [0, target.stats[3]], \
        user.temp['stats'].get("Skill", 0), \
        target.temp['stats'].get("Fortitude", 0))
    hit = hit1 > 0 and hit2 > 0 and hit3 > 0
    damage = user.hitpoints[0] if hit else 0
    return (hit, damage)
    
def pq_charm(user, target):
    """Perform a Charm vs Mind."""
    hit1 = atk_roll([0, user.stats[5]], [0, target.stats[4]], \
        user.temp['stats'].get("Skill", 0), \
        target.temp['stats'].get("Mind", 0))
    hit2 = atk_roll([0, user.stats[5]], [0, target.stats[4]], \
        user.temp['stats'].get("Skill", 0), \
        target.temp['stats'].get("Mind", 0))
    if hit1 > 0 and hit2 > 0:
        targstring = "The monster is " if hasattr(user, "gear") \
            else "You are "
        send_to_console(targstring + "charmed!")
        target.temp['condition']["charmed"] = 4
        return (True, 0)
    return (False, 0)

def pq_entangle(user, target):
    """Perform an Entangle (Skill vs Reflexes) to debuff."""
    hit = atk_roll([0, user.stats[5]], [0, target.stats[2]], \
        user.temp['stats'].get("Skill", 0), \
        target.temp['stats'].get("Reflex", 0))
    if hit > 0:
        targstring = "The monster is " if hasattr(user, "gear") \
            else "You are "
        send_to_console(targstring + "entangled!")
        target.temp['condition']["entangled"] = 4
        target.temp_bonus(["Attack", "Defense"], -hit, 4)
        return (True, 0)
    return (False, 0)

def pq_fear(user, target):
    """Perform a Fear (Skill vs Mind) to debuff."""
    hit = atk_roll([0, user.stats[5]], [0, target.stats[4]], \
        user.temp['stats'].get("Skill", 0), \
        target.temp['stats'].get("Mind", 0))
    if hit > 0:
        hit = max([1, hit/2])
        targstring = "The monster is " if hasattr(user, "gear") \
            else "You are "
        send_to_console(targstring + "frightened!")
        target.temp_bonus(["Attack"," Defense"], -hit, 4)
        return (True, 0)
    return (False, 0)
    
def pq_dominate(user, target):
    """Perform a Dominate (Skill vs Mind); if successful, enemy attacks self"""
    affect = atk_roll([0, user.stats[5]], [0, target.stats[4]], \
        user.temp['stats'].get("Skill", 0), \
        target.temp['stats'].get("Mind", 0))
    if affect > 0:
        hit = atk_roll(target.combat['atk'], target.combat['dfn'], \
            target.temp['stats'].get("Attack", 0) + affect, \
            target.temp['stats'].get("Defense", 0))
        targstring = "The monster is " if hasattr(user, "gear") \
            else "You are "
        targstring2 = "s itself!" if hasattr(user, "gear") else " yourself!"
        send_to_console(targstring + "dominated, and attack" + targstring2)
        return (hit > 0, hit)
    return (affect > 0, 0)
    
def pq_confusion(user, target):
    """Perform a Confuse (Mind vs Mind); if successful, 
    deal 1dSkill skill points damage"""
    affect = atk_roll([0, user.stats[4]], [0, target.stats[4]], \
        user.temp['stats'].get("Mind", 0), \
        target.temp['stats'].get("Mind", 0))
    if affect > 0:
        damage = max([0, random.choice([random.randint(1, user.stats[5]) \
            for i in range(0, 6)]) + user.temp['stats'].get("Skill", 0)])
        targstring = "The monster is " if hasattr(user, "gear") \
            else "You are "
        pl= "s" if hasattr(user, "gear") else ""
        send_to_console(targstring + "confused, and lose" + pl + " " + str(damage) \
            + " skill points!")
        target.huh(damage)
    return (affect > 0, 0)
    
def pq_evade(user, target):
    """Buff self with an Evade (+Skill to Defense)"""
    targstring = "You feel " if hasattr(user, "gear") \
        else "The monster feels "
    send_to_console(targstring + "more evasive!")
    user.temp_bonus(["Defense"], user.stats[5], 4)
    return (True, 0)
    
def pq_acidspray(user, target):
    """Perform an Acidspray -- Fort vs Def, full damage
    + 1/2 damage as Def debuff for 2 rounds"""
    hit = atk_roll([0, user.stats[3]], target.combat['dfn'], \
        user.temp['stats'].get("Fortitude", 0), \
        target.temp['stats'].get("Defense", 0))
    if hit > 0:
        debuff = max([hit/2, 1])
        targstring = "The monster is " if hasattr(user, "gear") \
            else "You are "
        send_to_console(targstring + "sprayed with acid!")
        target.temp_bonus(["Defense"], debuff, 4)
    return (hit > 0, hit)
    
def pq_telekinesis(user, target):
    """Perform a TK (Skill vs Ref); if successful, enemy attacks self"""
    affect = atk_roll([0, user.stats[5]], [0, target.stats[3]], \
        user.temp['stats'].get("Skill", 0), \
        target.temp['stats'].get("Reflexes", 0))
    if affect > 0:
        hit = atk_roll(target.combat['atk'], target.combat['dfn'], \
            target.temp['stats'].get("Attack", 0) + affect, \
            target.temp['stats'].get("Defense", 0))
        targstring = "The monster is " if hasattr(user, "gear") \
            else "You are "
        targstring2 = "s itself!" if hasattr(user, "gear") else " yourself!"
        send_to_console(targstring + "manipulated, and attack" + targstring2)
        return (hit > 0, hit)
    return (affect > 0, 0)
    
def pq_prismspray(user, target):
    """Perform a Prismatic Spray (Skill vs random stat
    to debuff that stat"""
    effectstring = ('blunted', 'diminished', 'made sluggish', \
        'weakened', 'befuddled', 'disconcerted')
    statpick = random.choice([random.randint(0, 5) for i in range(6)])
    affect = atk_roll([0, user.stats[5]], [0, target.stats[statpick]], \
        user.temp['stats'].get("Skill", 0), \
        target.temp['stats'].get(pq_reverse_stats[statpick], 0))
    if affect > 0:
        targstring = "The monster is " if hasattr(user, "gear") \
            else "You are "
        send_to_console(targstring + effectstring[statpick] + "!")
        target.temp_bonus([pq_reverse_stats[statpick]], -affect, 4)
    return (affect > 0, 0)
    
def pq_burn(user, target):
    """Perform a Burn (Atk vs Ref, applies Burning condition which
    re-calls the skill each turn for 1dSkill turns."""
    hit = atk_roll(user.combat['atk'], [0, target.stats[3]], \
        user.temp['stats'].get("Attack", 0), \
        target.temp['stats'].get("Reflexes", 0))
    if hit > 0 and "burning" not in target.temp['condition']:
        
        targstring = "The monster is " if hasattr(user, "gear") \
            else "You are "
        send_to_console(targstring + "burning!")
        target.temp['condition']["burning"] = 4
    return (hit > 0, hit)
    
def pq_leech(user, target):
    """Perform a Leech -- a single attack which 
    cures for half the damage it deals, up to Skill"""
    hit = atk_roll(user.combat['atk'], [0, target.stats[3]], \
        user.temp['stats'].get("Attack", 0), \
        target.temp['stats'].get("Fortitude", 0))
    if hit > 0:
        cure = max([hit/2, 1])
        targstring = "You drain " if hasattr(user, "gear") \
            else "The monster drains "
        send_to_console(targstring + str(cure) + " hit points!")
        user.cure(cure)
    return (hit > 0, hit)
    
#TIME FOR THE PASSIVE SKILLS!

def pq_bardicknowledge(user, target):
    """Passive skill: Learn information about the target"""
    trigger_chance = user.level[1] * 0.02
    if random.random() < trigger_chance:
        statstring = sum([[pq_stats_short[i], str(target.stats[i])] \
            for i in range(6)], [])
        send_to_console("You recall learning about this kind of creature!")
        send_to_console("Enemy stats: " + " ".join(statstring))
    return

def pq_turning(user, target):
    """Passive skill: chance to apply Turned condition, 
    which prevents attack"""
    trigger_chance = float(1 + 3 * user.level[1]) / \
        float(50 + 4 * user.level[1])
    if random.random() < trigger_chance:
        target.temp['condition']["turned"] = 2
        targstring = "Enemy is " if hasattr(user, "gear") else "You are "
        send_to_console(targstring + "turned!")
    return

def pq_regeneration(user, target):
    """Passive skill: regain lvl hp each round."""
    regen = max([user.level[1]/2, 1])
    user.cure(regen)
    targstring = "You regenerate " if hasattr(user, "gear") else \
        "Enemy regenerates "
    send_to_console(targstring + str(regen) + " hitpoints!")
    return
    
def pq_shapechange(user, target):
    """Passive skill: chance to gain 1-round buff every round."""
    stats = ["Attack", "Defense", "Reflexes", "Fortitude"]
    trigger_chance = user.level[1] * 0.02
    if random.random() < trigger_chance:
        targstring = "You change shape!" if hasattr(user, "gear") else \
            "The enemy changes shape!"
        send_to_console(targstring)
        buff = random.randint(1, user.level[1]) if user.level[1] > 1 else 1
        user.temp_bonus(stats, buff, 2)
    return
        
def pq_bushido(user, target):
    """Passive skill: chance to remove a random condition."""
    trigger_chance = user.level[1] * 0.02
    if random.random() < trigger_chance and user.temp['condition']:
        condition_remove = random.choice(user.temp['condition'].keys())
        targstring = "You shrug" if hasattr(user, "gear") else \
            "The enemy throws"
        send_to_console(targstring + " off the " + condition_remove + "condition!")
        del user.temp['condition'][condition_remove]
    return

def pq_grace(user, target):
    """Passive skill: chance to gain +1dLevel to Ref, Fort, 
    Mind as a 2-round buff."""
    stats = ["Reflexes", "Fortitude", "Mind"]
    trigger_chance = user.level[1] * 0.02
    if random.random() < trigger_chance:
        targstring = "You glow" if hasattr(user, "gear") else \
            "The enemy glows"
        send_to_console(targstring + " with divine impetus!")
        buff = random.randint(1, user.level[1]) if user.level[1] > 1 else 1
        user.temp_bonus(stats, buff, 4)
    return

def pq_spellcraft(user, target):
    pass #not implemented yet!
    return
    
def pq_resilience(user, target):
    """Passive skill: chance to regain a skill and/or point"""
    trigger_chance = float(1 + 5 * user.level[1]) / \
        float(50 + 6 * user.level[1])
    hp_trig = random.random() < trigger_chance and user.hitpoints[0] \
        < user.hitpoints[1]
    sp_trig = random.random() < trigger_chance and user.skillpoints[0] \
        < user.skillpoints[1]
    targstring = ("You are ", "") if hasattr(user, "gear") \
        else ("The enemy is ", "s")
    effectstring = ""
    if hp_trig:
        effectstring += "1 hit point"
        user.cure(1)
    if sp_trig:
        if hp_trig:
            effectstring += " and "
        effectstring += "1 skill point"
        user.huh(-1)
    send_to_console(targstring[0] + "feeling very resilient, and recover" + \
        targstring[1] + " " + effectstring + "!")
    return
    
def pq_stealth(user, target):
    pass #not implemented yet! i'm not sure what to do with this.

def pq_precog(user, target):
    """Passive skill: Mind vs Mind for 1-round buff to attack and defense"""
    buff = atk_roll([0, user.stats[4]], [0, target.stats[4]], \
        user.temp['stats'].get("Mind", 0), \
        target.temp['stats'].get("Mind", 0))
    if buff > 0:
        targstring = "You predict the enemy's actions!" if \
            hasattr(user, "gear") else "The enemy predicts your actions!"
        user.temp_bonus(["Attack", "Defense"], buff, 2)
        send_to_console(targstring)
    return
    
def pq_track(user, target):
    """Passive skill: stops opponent from fleeing for rest of combat"""
    trigger_chance = 0.02 * user.level[1]
    if random.random() < trigger_chance and not \
        target.temp['condition'].get("tracked",None):
        target.temp['condition']["tracked"] = 999
        targstring = "You have tracked the enemy!" if \
            hasattr(user, "gear") else "The enemy has tracked you!"
        send_to_console(targstring)
    return
    
def pq_unarmed(user, target):
    """Passive skill: chance to gain +1dSkill as a buff to Attack"""
    trigger_chance = 0.02 * user.level[1]
    if random.random() < trigger_chance:
        buff = random.randint(1, user.stats[5]) if user.stats[5] > 1 else 1
        user.temp_bonus(["Attack"], buff, 4)

pq_skill_library = {
    "Acidspray": pq_acidspray,
    "Backstab": pq_backstab,
    "Burn": pq_burn,
    "Charm": pq_charm,
    "Confusion": pq_confusion,
    "Cure": pq_cure,
    "Darkness": pq_fear,
    "Dominate": pq_dominate,
    "Doublestrike": pq_doublestrike,
    "Entangle": pq_entangle,
    "Evade": pq_evade,
    "Fear": pq_fear,
    "Flameblast": pq_burn,
    "Leech": pq_leech,
    "Missile": pq_missile,
    "Petrify": pq_petrify,
    "Poison": pq_poison,
    "Prismatic Spray": pq_prismspray,
    "Rage": pq_rage,
    "Smite": pq_smite,
    "Telekinesis": pq_telekinesis,
    "Trip": pq_trip
    }
    
pq_passive_skills = {
    "Bardic Knowledge": pq_bardicknowledge,
    "Bushido": pq_bushido,
    "Grace": pq_grace,
    "Precognition": pq_precog,
    "Regeneration": pq_regeneration,
    "Resilience": pq_resilience,
    "Shapechange": pq_shapechange,
    "Spellcraft": pq_spellcraft,
    "Stealth": pq_stealth,
    "Track": pq_track,
    "Turning": pq_turning,
    "Unarmed Strike": pq_unarmed
    }