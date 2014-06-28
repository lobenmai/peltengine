#PELT Entity Classes
#Created January 20, 2014 at 19:04

from i18n import m
from localio import output

class Entity(object):
	def __init__(self, name, level, life, attk=25, dfns=25, attacks=[], color='white'):
		self.name = name
		self.level = level
		self.life = life
		self.hp = life
		self.attk = attk
		self.dfns = dfns
		self.attacks = attacks
		self.color = color
	
	def __str__(self):
		return self.name

	def take_damage(self, dmg):
		self.hp -= dmg

	def add_attack(self, attack):
		if type(attack) == Attack: pass
		else: output('attackerror')

	def rem_attack(self): pass

	def speak(self, msg, dict=True, addon=None, s=0, newline=True):
		if dict: msg = m(msg, color=True)
		output(self.name+': '+'['+self.color+']'+msg, dict=False, addon=addon, newline=newline, s=s)

class Character(Entity):
	def __init__(self, name, level, life, attk=25, dfns=25, type='Normal', attacks=[], color='yellow'):
		self.type = type
		self.attacks = [Attack(m('attack1'), m('attack1desc'), 20, 0, m('type1'))]
		for attack in attacks: self.attacks.append(attack)
		Entity.__init__(self, name, level, life, attk, dfns, color=color)
	
	def take(self, item_name):
		item = self.location.getItem(item_name)
		self.inventory.append(item)

class Ally(Character):
	def __init__(self, location, name, last, species, gender, level, life=100, attk=25, dfns=25, color='green'):
		Character.__init__(self, name, level, life, attk, dfns, color=color)
		self.inventory = []
		self.location = location
		self.last = last
		self.species = species
		self.gender = gender
	
	def get_var(var):
		if var == 'all': return m('playerdesc') %(self.name, self.last, self.gender, self.species, self.inventory, self.location, self.level, self.attacks)
		else:
			try: return self.__getattribute__(var)
			except AttributeError: return None

class Enemy(Character):
	pass

class Attack(object):
	def __init__(self, name, desc, pwr, bonus, type):
		self.name = name
		self.desc = desc
		self.pwr = pwr
		self.bonus = bonus
		self.type = type
	
	def __repr__(self): return self.name
	
	def use(self, attacker, attacked):
		temp = 1.5 if self.type == attacked.type else 1
		dice = random.randint(0,10)
		if dice <= 1: crit = 0.5
		elif dice >= 10: crit = 1.5
		else: crit = 1
		damage = ((((((self.pwr + attacker.attk)*2)*temp)-(attacked.dfns/1.1))/3)*crit)+(random.randint(0,20)-10)
		damage = int(damage)
		attacked.take_damage(damage)
		output('entityhurt', addon=(str(attacked),str(damage)))
		crit += 5
		if crit == 0.5: output('ineffective')
		elif crit == 1.5: output('critical')

def action(msg, addon=None, s=0):
	output('[red]'+m(msg, color=True), dict=False, addon=None, s=s)
