#In need of remodeling
#Created April 28, 2014 at 22:28

import settings

if not settings.ios:
	import pygame #load all of pygame
	from pygame.locals import *
else: import scene

import font, tileset, data, music

#dialog definitions
dialogs = {
	"standard": {
		"file":"dialogboxes/dialog.png",
		"choice_file":"dialogboxes/dialog_choice_tiles.png",
		"text_rect":pygame.Rect(11,8,settings.screen_x,settings.screen_y/4),
		"font":"fonts/dialog_font.xml"
	},
	"sign": {
		"file":"dialogboxes/signdialog.png",
		"choice_file":"dialogboxes/dialog_choice_tiles.png",
		"text_rect":pygame.Rect(11,8,settings.screen_x,settings.screen_y/4),
		"font":"fonts/dialog_font.xml"
	},
	"notify": {
		"file":"dialogboxes/selfdialog.png",
		"choice_file":"dialogboxes/self_dialog_choice_tiles.png",
		"text_rect":pygame.Rect(8,8,settings.screen_x,settings.screen_y/4),
		"font":"fonts/selfdialog_font.xml"
	},
	"battle": {
		"file":"dialogboxes/battledialog.png",
		"choice_file":"dialogboxes/self_dialog_choice_tiles.png",
		"text_rect":pygame.Rect(8,8,settings.screen_x,settings.screen_y/4),
		"font":"fonts/selfdialog_font.xml"
	}
}

#dialog we can use to ask a choice
class ChoiceDialog:
	def __init__(self, g, type, selectsound=True, dlog=None):
		self.g = g #store parameters
		if dlog is not None: #if a dialog has been provided
			#copy its parameters
			self.type = dlog.type
			self.choice_tiles = dlog.choice_tiles
			self.dlog_font = dlog.dlog_font
			self.dlog = dialogs[self.type]
		else: #otherwise, if none was given
			dlog = dialogs[type] #get type
			self.choice_tiles = tileset.Tileset(dlog["choice_file"], 16, 16) #load choice tileset
			self.dlog_font = font.Font(dlog["font"]) #load font
			self.dlog = dlog
			self.type = type
		self.choices = [] #list of choices
		self.drawing = False #whether we're currently showing choices
		self.curr_choice = None #index of the currently selected choice
		self.cursor_tile = pygame.Surface((16, 16), SRCALPHA) #surface to hold cursor tile
		self.selectsound = selectsound #Do we want to play the selection sound?
	def show_choices(self, choices, opensound=True): #draw a list of choices
		prlx = settings.get_prlx(5, 1)
		if opensound: self.g.sounds['openMenu'].play()
		dlog_width = -1 #maximum choice width
		#calculate width of dialog box
		for choice in choices: #loop through choices provided:
			width = self.dlog_font.get_width(choice)+20 #get its width
			if width > dlog_width: #if it's greater than the current maximum
				dlog_width = width #update maximum
		dlog_height = 24 + (self.dlog_font.height*len(choices)) #calculate height of dialog
		dlog_width += 24 #add border size to width
		#turn height and width into multiples of eight
		if dlog_height % 16 > 0: dlog_height += (16-(dlog_height%16))
		if dlog_width % 16 > 0: dlog_width += (16-(dlog_width%16))
		self.dlog_height = dlog_height #store dimensions
		self.dlog_width = dlog_width
		self.dlog_surf = pygame.Surface((dlog_width, dlog_height), SRCALPHA) #create surface for the textbox
		#now draw dialog background
		#draw four corners
		self.choice_tiles.blit_tile(self.dlog_surf, (0, 0), 0, 0) #top left
		self.choice_tiles.blit_tile(self.dlog_surf, (dlog_width-16, 0), 2, 0) #top right
		self.choice_tiles.blit_tile(self.dlog_surf, (0, dlog_height-16), 0, 2) #bottom left
		self.choice_tiles.blit_tile(self.dlog_surf, (dlog_width-16, dlog_height-16), 2, 2) #bottom right
		#now, draw top and bottom edges
		for x in xrange(16, dlog_width-16, 16): #loop through tile positions
			self.choice_tiles.blit_tile(self.dlog_surf, (x, 0), 1, 0) #top edge
			self.choice_tiles.blit_tile(self.dlog_surf, (x, dlog_height-16), 1, 2) #bottom edge
		#draw left and right edges
		for y in xrange(16, dlog_height-16, 16): #loop through tile positions
			self.choice_tiles.blit_tile(self.dlog_surf, (0, y), 0, 1) #left edge
			self.choice_tiles.blit_tile(self.dlog_surf, (dlog_width-16, y), 2, 1) #right edge
		#now, fill in dialog middle
		for y in xrange(16, dlog_height-16, 16): #loop through rows
			for x in xrange(16, dlog_width-16, 16): #and tiles
				self.choice_tiles.blit_tile(self.dlog_surf, (x, y), 1, 1) #draw one tile
		#load cursor tile
		self.cursor_tile.fill((0, 0, 0, 0)) #clear tile buffer
		self.choice_tiles.get_tile(0, 3, self.cursor_tile) #load it
		#now, draw options
		y = 16 #current y position of drawing
		for choice in choices: #loop through choices
			self.dlog_font.render(choice, self.dlog_surf, (36, y)) #render one
			y += self.dlog_font.height #go to next line
		self.choices = choices #store choices
		self.drawing = True #we're currently showing something
		self.curr_choice = 0 #zero current choice
	def update(self, dest, where): #update ourselves
		prlx = settings.get_prlx(5, 0.5)
		if not self.drawing: return #return if we're not drawing
		if self.g.curr_keys.get(settings.key_up) or self.g.curr_mouse[4]: #if up has been pressed
			if self.curr_choice > 0: #if we're not already at the topmost choice
				self.curr_choice -= 1 #go up one choice
			else: self.curr_choice = len(self.choices)-1 #else loop around
			self.g.sounds['shift'].play()
		elif self.g.curr_keys.get(settings.key_down) or self.g.curr_mouse[5]: #if down has been pressed
			if self.curr_choice < len(self.choices)-1: #if we're not already at the bottom choice
				self.curr_choice += 1 #go down one choice
			else: self.curr_choice = 0 #else loop around
			self.g.sounds['shift'].play()
		if self.g.curr_keys.get(settings.key_accept):# or self.g.mouse[1]: #if the accept key has been pressed
			self.drawing = False #we're not drawing
			if self.selectsound: self.g.sounds['select'].play()
			return self.curr_choice #return current choice
		elif self.g.curr_keys.get(settings.key_cancel) or self.g.curr_mouse[3]: #if cancel key has been pressed
			self.drawing = False #we're not drawing
			self.g.sounds['reject'].play()
			return len(self.choices)-1 #return last choice
		if where[0] < 0: where = (settings.screen_x-self.dlog_width+where[0], where[1])
		if where[1] < 0: where = (where[0], settings.screen_y-self.dlog_height+where[1])
		dest.blit(self.dlog_surf, (where[0]+prlx[0], where[1]+prlx[1])) #draw the dialog
		#draw cursor
		dest.blit(self.cursor_tile, (where[0]+16+prlx[0], where[1]+20+(self.curr_choice*self.dlog_font.height)+prlx[1]))

#dialog we can use to draw text
class Dialog:
	def __init__(self, g, type):
		global dialogs
		self.type = type #store parameters
		self.g = g
		dlog = dialogs[type] #get attributes of dialog
		self.dlog = dlog #store it
		self.image = data.load_image(dlog["file"]) #load image file
		self.image.convert() #convert it so it will draw faster
		self.choice_tiles = tileset.Tileset(dlog["choice_file"], 16, 16) #load choice tileset
		self.dlog_rect = dlog["text_rect"] #get text rect
		self.dlog_font = font.Font(dlog["font"]) #load font we're going to use for drawing
		self.waiting = False #whether we're waiting for the player to press action
		self.text = [] #list of characters to draw
		self.text_surf = pygame.Surface(self.dlog_rect.size) #create a surface to draw text on
		self.text_surf.set_colorkey((127, 182, 203)) #set a colorkey for it
		self.text_surf.fill((127, 182, 203)) #fill it with the colorkey value
		self.text_surf.convert() #convert it to blit faster
		self.drawing = False #whether we're currently drawing the dialog box
		self.choice_dialog = None #store current choice dialog, if any
		self.fill_allowed = False #whether the user can draw the whole dialog at once
	def draw_text(self, str): #draw a string
		if str == "": #if it's an empty string
			self.drawing = False #stop drawing
			return #don't render it
		command = None #temporary text command
		self.text = [] #clear list of characters to draw
		self.next_pos = [0, 0] #position for next letter to be drawn
		for char in str: #loop through characters in given string
			if char == "{" and command is None: #if we've encountered a command start
				command = "{" #start command
			elif char == "}" and command is not None: #if we've encountered a command end
				command += "}" #end command
				self.text.insert(0, command) #add it to the list of letters
				command = None #clear command
			else:
				if command is not None: #if we're in a command
					command += char #add the current character to it
				else: #otherwise
					self.text.insert(0, char) #add the current character to the list of characters
		self.text_surf.fill((127, 182, 203)) #clear the text surface
		self.fill_allowed = False #dialog can't be filled yet
		self.drawing = True #and we're currently drawing!
	def _next_line(self): #go to the next line
		self.next_pos[1] += self.dlog_font.height #increment height
		if self.next_pos[1] >= (self.dlog_rect.height-self.dlog_font.height): #if we're past the drawing edge
			self.next_pos[1] -= self.dlog_font.height #subtract height
			self.text_surf.scroll(0, -self.dlog_font.height) #scroll the text surface
			#clear out new line
			self.text_surf.fill((127, 182, 203), ((0, self.next_pos[1]), self.dlog_rect.size))
		self.next_pos[0] = 0 #clear x coord
	def _parse_choices(self): #parse a choice command
		choices = [] #list of choices found
		curr_choice = "" #text of the current choice
		while True: #parse the choices
			letter = self.text.pop() #get a letter
			if letter == "{endchoice}": #if we've hit the end of a choice
				choices.append(curr_choice) #add it to the choice list
				curr_choice = "" #clear current choice
			elif letter == "{endchoices}": #If we've hit the end of all choices
				break #stop parsing choices
			else: #otherwise
				curr_choice += letter #add the letter to the current choice text
		self.choice_dialog = ChoiceDialog(self.g, 0, dlog=self) #create a new choice dialog
		self.choice_dialog.show_choices(choices) #show found choices
	def _next_char(self, ignore_keys=False): #draw the next character
		if ignore_keys: curr_keys = {}
		else: curr_keys = self.g.curr_keys

		if not self.drawing: #if we're not drawing anything
			return True #say so
		#test various wait conditions
		if self.waiting == 1: #if we're waiting for a keypress
			if curr_keys.get(settings.key_accept): #if it has been pressed
				self.waiting = False #we're not waiting any more
				self.fill_allowed = False #we're not allowed to fill
		elif self.waiting == 2: #if we're waiting fopr a transition
			if self.g.game.curr_transition is None: #if none are happening
				self.waiting = False #stop waiting
		if self.waiting != False: return True #if we're still waiting, return
		if len(self.text) == 0: #if we don't have any more characters to draw
			self.drawing = False #we're not drawing any more
			return True #we've finished drawing
		letter = self.text.pop() #get a letter
		#test for special commands
		if letter == "{br}": #if we've hit a line break command
			self._next_line() #go to next line
		elif letter == "{wait}": #if we've hit a wait command
			self.waiting = 1 #mark that we're waiting for a keypress
			self.fill_allowed = False #we aren't allowed to fill the dialog
			return True #we're waiting
		elif letter == "{tr_wait}": #if we've hit a transition wait command
			self.waiting = 2 #mark it
			return True #we're waiting
		elif letter == "{clear}": #if we've hit a clear screen command
			self.next_pos = [0, 0] #reset next position
			self.text_surf.fill((127, 182, 203)) #clear text
			self.fill_allowed = False #we can't fill the dialog
		elif letter == "{choices}": #if we've hit a choice command
			self._parse_choices() #handle it
		else: #if we've hit anything else
			width = self.dlog_font.get_width(letter) #get the letter's width
			if self.next_pos[0]+width >= self.dlog_rect.width: #if we've exceeded width
				self._next_line() #go to next line
			self.dlog_font.render(letter, self.text_surf, self.next_pos) #render letter
			self.next_pos[0] += width #add width to current position
	def update(self, surf, surf_pos, force=False, prlx_enable=True, ignore_keys=False, choice_above=True): #update the dialog box, returns true when done
		if prlx_enable: prlx = settings.get_prlx(5, 0.5)
		else: prlx = (0, 0)

		if ignore_keys: curr_keys = {}
		else: curr_keys = self.g.curr_keys

		if not self.drawing: #if we're not drawing anything
			if not force: return True #return saying we're done if we're not supposed to draw anyway
			try: #attempt to draw the dialog box
				surf.blit(self.image, (surf_pos[0]+prlx[0], surf_pos+prlx[1])) #draw dialog box image
				surf.blit(self.text_surf, (surf_pos[0]+self.dlog_rect.left+prlx[0], surf_pos[1]+self.dlog_rect.top+prlx[1])) #and text surface
			except: #if it couldn't be done for some reason
				pass #don't worry about it
			return True #say we're done
		choice_ret = None #store the result of a choice update
		if self.choice_dialog is None: #if we're not currently drawing a choice dialog
			if curr_keys.get(settings.key_accept) and self.fill_allowed and self.waiting == False: #if the accept key has been pressed and we're allowed to fill
				r = False
				while r != True: #loop until we're told to stop
					r = self._next_char(ignore_keys) #render another character
			else:
				self.fill_allowed = True #we can fill the dialog now
				r = False
				for x in xrange(2):
					if self._next_char(ignore_keys) == True:
						r = True
						break
			if r == True: #if we've finished drawing
				if self.choice_dialog is not None or self.drawing is True: #if we drew a choice dialog
					self.drawing = True #we're still drawing
				else: #otherwise
					if force: #If we're forcing the dialog box to be drawn
						surf.blit(self.image, (surf_pos[0]+prlx[0], surf_pos[1]+prlx[1])) #draw dialog box image
						surf.blit(self.text_surf, (surf_pos[0]+self.dlog_rect.left+prlx[0], surf_pos[1]+self.dlog_rect.top+prlx[1]))
					return True #say so
		else: #if we are drawing a choice dialog
			if choice_above: h = self.image.get_height()+50
			else: h = surf.get_height() - self.dlog_rect.get_height() * 2
			choice_ret = self.choice_dialog.update(surf, (4, h)) #draw it
		#draw the current dialog box
		surf.blit(self.image, (surf_pos[0]+prlx[0], surf_pos[1]+prlx[1])) #draw dialog box image
		surf.blit(self.text_surf, (surf_pos[0]+self.dlog_rect.left+prlx[0], surf_pos[1]+self.dlog_rect.top+prlx[1])) #and text surface
		if choice_ret is not None: #if the choice dialog has returned something
			self.drawing = False #we're not drawing
			self.choice_dialog = None #destroy choice dialog
			return choice_ret #and return result
