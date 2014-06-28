#PELT Item Classes
#Created on Febuary 16, 2014 at 19:53

import re

#define the attributes of an item
class Item(object):
	def __init__(self, name, description=None):
		self.name = name
		self.description = description
	
	def examine(self):
		if self.description: output(self.description, dict=False)
		else: output('itemnormal', addon=self.name)

class Chest(Item):
	placedRE = re.compile("placed (\d+) from ([a-zA-Z]+) (\d+) from ([a-zA-Z]+)")
	
	def __init__(self, contents=[], key=None):
		self.contents = contents
		self.copen = False
		if not key: self.locked = False
		else:
			self.locked = True
			self.key = key
		Item.__init__(self, "chest")
	
	def __str__(self):
		return 'chest'
	
	@classmethod
	def fromText(cls, text):
		
		placedMatch = cls.placedRE.search(text)
		if placedMatch:
			# assign to variables
			pass
		
		phrases = {
			'placed':  "placed (\d+) from ([a-zA-Z]+) (\d+) from ([a-zA-Z]+)",
			'facing': 'facing ([a-zA-Z]+)',
			'with': '\(([^\)]+)\)',
		}
		
		#for name, regex in phrases.items():
		#	if not match:
		#		pass#raise ParseError('Missing %s phrase in "%s"' %(name, text))
		
		"""Chest placed 1 from Left 1 from Top facing Bottom with (Rusty Key, $50)"""
		match = re.search('Chest placed (\d+) from ([a-zA-Z]+) (\d+) from ([a-zA-Z]+) facing ([a-zA-Z]+) with \(([^\)]+)\)', text)
		if match == None:
			noFacingMatch = re.search('Chest placed (\d+) from ([a-zA-Z]+) (\d+) from ([a-zA-Z]+) with \(([^\)]+)\)', text)
			if noFacingMatch == None:
				raise ParseError('Invalid syntax for "%s".  There is nothing else we know.' %text)
			else: raise NoFacingError('Tried to parse "%s", however I don\'t know which way that chest is facing.' %text)
		
		placed = match.group(1, 2, 3, 4, 5)
		itemsraw = match.group(6)
		
		itemsraw = itemsraw.split(', ')
		#for item in itemsraw: items.append(item)
		keymatch = re.search('locked with "([a-zA-Z]+)"', text)
		if keymatch != None: key = keymatch.group(1)
		else: key = None
		
		return cls(itemsraw, key)
	
	def examine(self):
		if self.open: output('chestdescopen', addon=', '.join(self.contents))
		else: output('chestdescclosed')
	
	def open(self, inventory):
		if self.locked:
			if self.key in inventory:
				self.locked = False
				output('chestunlocked', addon=self.key)
			else:
				output('chestlocked')
				return
		if self.copen: output('chestopenerror')
		else:
			self.copen = True
			output('chestopen', addon=', '.join(self.contents))
			for item in self.contents: inventory.append(item)

#define drink item
class Drink(Item):
	def __init__(self, name, description, poison):
		Item.__init__(self, name, description)
		self.poison = poison
	
	def drink(self):
		if self.poison:
			output('drinkpoisoned', addon=self.name)
			quit('drinkpoisonedmsg', addon=self.name)
		else: output('foodeaten', addon=self.name)

#define food item
class Food(Item):
	def __init__(self, name, description, poison):
		Item.__init__(self, name, description)
		self.poison = poison
	
	def eat(self):
		if self.poison:
			output('foodpoisoned', addon=self.name)
			quit('foodpoisonedmsg', addon=self.name)
		else: output('foodeaten', addon=self.name)

class BattleModifier(Item):
	def use(self, onPlayer):
		pass

class Potion(BattleModifier):
	def __init__(self, name, force, description):
		BattleModifier.__init__(self, name, description)
		self.force = force
	
	def use(self, onPlayer): onPlayer.life += self.force

class Tagger(BattleModifier):
	pass

class Thing(BattleModifier):
	def use(self, onPlayer): onPlayer.tags.append('blind')

