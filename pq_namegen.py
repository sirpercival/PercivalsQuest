#
#  pq_namegen.py
#  part of Percival's Quest RPG


"""
pq_namegen.py - A bunch of random name and flavor generators for Percival's Quest.

I don't claim to have created ANY of these, though for most of them I translated them to python.
(I guess I can take credit for the God generator, though that really belongs to Lovecraft et al...)
I found these scattered across the far corners of the internet and appropriated them for my RPG. 
Sadly, in most cases I don't remember where I found them, so I can't give credit.
HOWEVER, the monster description generator was kindly provided by the bodacious Swordgleam over at ChaoticShiny.com
(which website has the most awesome set of generators ever).
"""

import random
import json

#generate a sandwich!
def sandgen(n=1):
    """Generates a random sandwich"""
    such = random.choice([random.sample((' a beautiful',' a delicious',' an elegant',' a fantastic',
       ' a mesmerizing',' an enchanting',' an amazing',' a fabulous',' a deadly',
       ' an adventurous',' an ambitious',' a brave',' a creative',' a discreet',
       ' an exuberant',' a faithful',' a friendly',' a gentle',' a damn good',
       ' an imaginative',' an intellectual',' a loving',' a loyal',' a modest',
       ' a neat',' an optimistic',' a jovial',' a kick-ass',' a healthy',' a passionate',
       ' a pioneering',' a plucky',' a philosophical',' a quirky',' a reliable',
       ' a sincere',' a thoughtful',' a terrific',' an understated',' a vivacious',
       ' a wonderful',' a xenophilic',' a youthful',' a zany'),n) for i in range(6)])
    topping = random.choice([random.sample(('avocado','lettuce','tomato','mozzarella cheese','bacon',
       'spam','peanut butter','bratwurst','cruelty-free PETA-approved fake guinea-pig',
       'digital','cucumber','tofu','-if slightly burnt-','recursive','banana','ice-cream',
       'ham&jam','tuna','double cheese','olive','..erm.. just','self-made','generic','sand',
       'witch','two-hander'),n) for i in range(6)])
    sandwich = [such[i]+' '+topping[i] for i in range(n)]
    if n == 1:
        return sandwich[0]
    return sandwich


#A simple name generator using scrabble distribution

consonants = [('b',  2),('c',  2),('ch', 1),('d',  4),('f',  2),('g',  3),
    ('h',  2),('j',  1),('k',  1),('l',  4),('m',  2),('n',  6),('p',  2),
    ('q',  1),('qu', 1),('r',  6),('s',  4),('t',  6),('v',  2),('w',  2),
    ('x',  1),('z',  1),]
vowels = [('a', 9),('e', 12),('i', 9),('o', 8),('u', 4),('y', 2)]

def selection(table):
    if type(table[-1]) is not type(0):
        s = 0
        for i in range(len(table)):
            s += table[i][1]
        table.append(s)
    else:
        s = table[-1]
    # now the selection
    n = random.randrange(s) + 1
    for i in range(len(table)-1):
        n -= table[i][1]
        if n <= 0:
            return table[i][0]
    # should not happen
    return ''

def simple_namegen(minsyl = 1, maxsyl = 3, n = 1):
    """Name generator using scrabble letter distribution"""
    names = [] 
    for j in range(0,n):
        numsyl = random.randint(minsyl, maxsyl)
        word = []
        for i in range(numsyl):
            flag = 0
            if random.randrange(100) < 60:
                word.append(selection(consonants))
                flag = 1
            word.append(selection(vowels))
            if not flag or random.randrange(100) < 40:
                word.append(selection(consonants))
        names.append("".join(word))
    if n == 1:
        return names[0]
    return names
    
###A name generator which grabs from dicelog.com

def web_namegen(minsyl = 1, maxsyl = 3, n = 1):
    """Grab a randgen name from dicelog.com"""
    import xmlrpclib
    proxy = xmlrpclib.ServerProxy("http://dicelog.com/yaf/rpc")
    return proxy.names(minsyl,maxsyl,n)
    
###A syllable agglutinator namegen for dragons

dragonname = (('Vi','Ig','R','Ci','Ni','Ba','Be','Bi','Bre','Bry','Ca','Ce','Che','Ci','Co','Col',
    'Cu','Da','De','Do','Du','Em','Fe','Fi','Ga','Gi','He','He','Ho','In','Ir','Ith','Je','Ji',
    'Ka','Ke','Ki','Ko','Ky','Le','Li','Lo','Lu','Ly','Ma','Me','Mo','Mi','Mne','My','Na','Ne',
    'No','Pa','Pe','Po','Que','Qui','Quo','Ra','Re','Rho','Ri','Ro','Ru','Ry','Sa','Se','Sha',
    'She','Sho','Shu','Si','So','Ste','Su','Sy','Tae','Ta','Te','Ti','To','Tu','Ty','Va','Ve',
    'Vo','Ze','Zi','Ju','Hi','Fu','Bri','Oh','Gre','Gra','Av','Rha','Um','Hu','Nv','Ap','As','At',
    'Fa','Fra','Cor','Cul','Dal','Dar','Mer','Mar'),
    ('ar','al','am','ath','an','ad','bi','el','en','lu','ta','thy','th','ir','il',
    'ith','in','re','ri','ro','ra','rth','rro','gh','ga','li','lth','lla','la','si',
    'sa','lo','vo','na','nth','ni','nnu','no','nno','ne','yo','yd','oth','dre','do',
    'de','da','du','mma','mro','mi','sso','ssi','zz','ze','vu','nni','ja','us','zo',
    'lle'))
    
def dragon_namegen(minsyl = 2, maxsyl = 4, n = 1):
    """Agglutinate syllables into a draconic name."""
    names = []
    for i in range(0,n):
        word = [random.choice([random.choice(dragonname[0]) for k in range(0,6)])]
        numsyl = random.randint(minsyl,maxsyl)
        for j in range(0,numsyl):
            word.append(random.choice([random.choice(dragname[1]) for k in range(0,6)]))
        names.append("".join(word))
    if n == 1:
        return names[0]
    return names
    
###Artifact generator!
    
def artygen(n = 1):
    """Generate a powerful artifact."""
    with open('pq_artifact_dict.json') as f:
        arty = json.load(f)
    artifact = []
    for k in range(0,n):
        artifact_pieces = []
        for i in arty:
            artifact_pieces.append(random.choice([random.choice(i) for j in range(0,6)]))
        artifact.append(' '.join(rr))
    if n == 1:
        return artifact[0]
    return artifact


###MONSTER DESCRIPTION GENERATOR, courtesy of the awesome Swordgleam from ChaoticShiny.com!

def monster_gen(n = 1):
    """Generate a monster description"""
    with open('pq_monster_description_dict.json') as f:
        monster_description = json.load(f)
    monster = []
    for kk in range(0,n):
        sz = random.choice(monster_description['size'])
        ty0 = random.randint(0,len(monster_description['type']))
        typ = monster_description['type'][ty0]
        if random.randint(0,1): 
            ', '.join([typ,random.choice([x for x in monster_description['type'] if x != typ])])
        th = random.choice(monster_description['thing'])
        lv = random.choice(monster_description['lives'])
        pl = random.choice(monster_description['place'])
        desc1 = 'This '+' '.join([sz,typ,th,lv,'in',pl+'.'])
        if random.randint(0,1):
            hw = random.choice(monster_description['how'])
            pt = 'its prey, which includes'
            z = random.randint(1,3)
            if z > 1:
                pr = ''
                for i in range(0,z):
                    pr += random.choice([x for x in monster_description['prey'] if x not in pr])+', '
            else: pr = random.choice(monster_description['prey'])
            pr += 'and '+random.choice([x for x in monster_description['prey'] if x not in pr])
            desc2 = ' '.join(['It',hw,pt,pr+'.'])
            desc = ' '.join([desc1,desc2])
        else: desc = desc1
        pt = 'It attacks with'
        matk = random.choice(monster_description['mattack'])
        z=0
        if random.randint(0,2) != 1: z += 1
        if random.randint(0,5) == 1: z += 1
        atk = ''
        for i in range(0,z):
            atk += random.choice([x for x in monster_description['attack'] if x not in atk])+', '
        atk += 'and '+random.choice([x for x in monster_description['attack'] if x not in atk])
        if not atk.startswith('and'):
            matk += ','
        desc = ' '.join([desc,pt,matk,atk+'.'])
        if random.randint(0,2) == 1: 
            desc = ' '.join([desc,'It',random.choice(monster_description['dis']),
                random.choice(monster_description['weak'])+'.'])
        if random.randint(0,9) > 5:
            hl = random.choice(monster_description['hl'])
            if random.randint(0,5) == 1: 
                grp = 'alone'
            else:
                r1 = random.randint(1,5)
                r2 = random.randint(1,20)+r1
                grp = ' '.join(['in',random.choice(monster_description['group']),'of',
                    '-'.join([str(r1),str(r2)])])
            desc = ' '.join([desc,'They',hl,grp+'.'])
        if random.randint(0,9) > 5:
            desc = ' '.join([desc,random.choice(monster_description['rumor']),random.choice(monster_description['rumor2'])+'.'])
        monster.append(desc)
    if n == 1:
        return monster[0]
    return monster
    
    
#Tavern name generator!

def taverngen(n = 1, long = False):
    """Generate a random tavern"""
    with open('pq_taverns_tuple.json') as f:
        taverns = json.load(f)
    tavern = []
    for kk in range(0,n):
        pick = random.choice([random.choice(taverns[0]) for i in range(0,6)])
        pick += random.choice([random.choice(taverns[1]) for i in range(0,6)]) 
        if long:
            pick += random.choice([random.choice(taverns[2]) for i in range(0,6)])
        taven.append(pick)
    if n == 1:
        return tavern[0]
    return tavern
    
#riddle generator, using wordlock chest riddles from betrayal at krondor
    
def riddlegen(n = 1):
    with open('pq_riddle_dict.json') as f:
        riddles = json.load(f)
    riddle = []
    for i in range(n):
        answer = random.choice([random.choice(riddles.keys()) for j in range(6)])
        text = riddles[ans]
        riddle.append((answer,text))
    if n == 1:
        riddle = riddle[0]
    return riddle
    
#generate a random set of numbers, as a string

def numgen(l = 4, n = 1):
    number = []
    for i in range(n):
        answer = ''
        for j in range(l):
            answer += str(random.randint(0,9))
        number.append(answer)
    if n == 1:
        number = number[0]
    return number
    
#produce a random deity from the Lovecraft mythos
    
def godgen(n = 1):
    with open('pq_gods_tuple.json') as f:
        gods = json.load(f)
    god = random.choice([random.sample(gods,n) for j in range(6)])
    if type(god) is list and len(god) == 1:
        return god[0]
    return god