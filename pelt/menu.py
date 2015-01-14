#In need of remodeling
#Created April 28, 2014 at 22:28

import settings #load game settings

if not settings.ios:
	import pygame #import everything pygame-related
	from pygame.locals import *
else: import scene
import sys, os
from os import path

if settings.steamAPI:
	try: import PySteamAPI as steam
	except ImportError: settings.steamAPI = False

import dialog, font, game, music, error

class Menu: #class to manage the in-game menus
	def __init__(self, game, surf):
		self.game = game #store given parameters
		self.g = game.g

		self.surf = surf
		#initialize dialogs
		self.choice_dlog = dialog.ChoiceDialog(self.g, "standard")
		self.dlog = dialog.Dialog(self.g, "standard")
		self.start_main_update() #start displaying main selection
		self.show = self.start_main_update #set function to show ourselves
	def start_main_update(self): #start displaying main selection
		self.choices = ["Party", "Save", "Title Screen", "Cancel"] #store currently shown choices
		self.choice_dlog.show_choices(self.choices) #start choice dialog showing
		self.update_func = self.main_update #store our update function
	def main_update(self): #display main selection
		self.menu = None
		choice = self.choice_dlog.update(self.surf, (0, 0)) #draw selection
		if choice is None: #if a choice hasn't been picked yet
			return #don't do anything
		if self.choices[choice] == "Cancel": #if cancel was pressed
			self.g.menu_showing = False #menu isn't showing anymore
		elif self.choices[choice] == "Title Screen": #if title screen was pressed
			self.start_title_screen() #start showing info
		elif self.choices[choice] == "Save": #if save was pressed
			self.start_save()
		elif self.choices[choice] == "Party":
			self.menu = PartyMenu(self, self.surf) #create party menu
			self.update_func = self.menu.update #start its update function
	def start_title_screen(self): #start showing title screen questions
		#show question
		self.dlog.draw_text("Would you like to return to the title screen, {br}%s?{choices}Yes{endchoice}No{endchoice}{endchoices}" %settings.name)
		self.update_func = self.title_screen_update #store our update function
	def title_screen_update(self): #update for title screen
		choice = self.dlog.update(self.surf, (0, 1)) #draw dialog
		if choice == 0: #if yes has been pressed
			#self.start_save() #ask the user if they want to save before returning to title screen
			self.g.reset() #do a reset
		elif choice == 1: #if no was pressed
			self.g.menu_showing = False #menu shouldn't be showing any more
	def start_save(self):
		self.menu = SaveMenu(self, self.surf)
		self.update_func = self.menu.update
	def update(self): #update ourselves
		self.update_func() #call current update function

class TitleMenu:
	def __init__(self, g, titlescreen, surf):
		self.g = self.game = g
		self.surf = surf
		self.titlescreen = titlescreen
		
		self.dlog = dialog.ChoiceDialog(self.g, "standard", selectsound=False) #initialize new dialog for choices
		self.dlogtext = dialog.Dialog(self.g, "standard")
		
		self.show()
		
	def update(self):
		prlx = settings.get_prlx(5, 1)
		
		choice = self.dlog.update(self.surf, (1, -60)) #draw choice dialog
		if choice is not None: # and choice is not False: #if the user chose something
			self.handle_c(choice) #handle the choice

	def show(self):
		self.titlescreen.active_menu = self
		#self.titlescreen.update_func = self.titlescreen.main_update
		self.handle_c = self.handle_choice #handle the choice
		self.dlog.show_choices(["Start Game", "Options", "Quit (Or Press Z)"], opensound=False) #show choices
	
	def handle_choice(self, choice):
		if choice == 0: #if start game was pressed
			self.menu = self.titlescreen.menu = SaveMenu(self, self.surf, save=False)
			self.titlescreen.active_menu = self.menu
			#self.titlescreen.update_func = self.menu.update
		elif choice == 1: #if options was pressed
			self.handle_c = self.handle_option
			self.start_options()
		elif choice == 2:
			self.g.sounds['reject'].play()
			raise error.UserQuit()
		elif choice == 3:
			self.g.status_msg.show_msg("TESTING")
			self.show()

	def start_options(self):
		self.save_exists = False
		for x in range(settings.maxsaves):
			if path.exists(settings.save_name %x): #if save file exists
				self.save_exists = True #mark it
		
		m = "On" if settings.option_music else "Off"
		s = "On" if settings.option_sound else "Off"
		p = "On" if settings.parallax else "Off"
		f = "On" if settings.fullscreen else "Off"
		choices = ["Wipe All Saves (No Saves!)", "Music (%s)" %m, "Sound (%s)" %s, "Mouse Parallax (%s)" %p, "Fullscreen (%s)" %f, "Back (Or Press Z)"]
		if self.save_exists: choices[0] = "Wipe All Saves"
		self.dlog.show_choices(choices)
	
	def handle_option(self, choice):
		if choice == 0: # if we want to wipe our saves...
			self.dlog.show_choices(["Yes, wipe all of my saves.", "No, I want to keep my saves."])
			self.handle_c = self.handle_wipe
		elif choice == 5: # ...or return to the main menu, we should not use our start_options() function for our toggles.
			self.update_func = self.update
			settings.save()

			sub_bg_pos = (1, settings.screen_y-self.dlog.dlog_height-60)
			sub_bg =  self.titlescreen.bg.subsurface(pygame.Rect(
													sub_bg_pos, (self.dlog.dlog_width, self.dlog.dlog_height) ))

			# red_rect = pygame.Surface((self.dlog.dlog_width, self.dlog.dlog_height))
			# red_rect.fill((255, 0, 0))
			self.surf.blit(sub_bg, sub_bg_pos)

			self.g.sounds['openMenu'].play()
			self.show()
		else: # otherwise, we should activate our toggle switch and refresh the options menu
			if choice == 1:
				settings.option_music = not settings.option_music
				music.play(-1)
				if not settings.option_music: music.fadeout(500)
			elif choice == 2: settings.option_sound = not settings.option_sound
			elif choice == 3: settings.parallax = not settings.parallax
			elif choice == 4:
				fullscreen = pygame.FULLSCREEN if settings.fullscreen else 0 #if fullscreen is turned on in the settings, enable it
				self.g.screen = pygame.display.set_mode((settings.screen_x*settings.screen_scale, settings.screen_y*settings.screen_scale), fullscreen) #recreate the window to draw on
			self.start_options()

	def handle_wipe(self, choice):
		if choice == 0:
			self.dlogtext.draw_text("Wiping saves...")
			for x in range(settings.maxsaves):
				try: os.remove(settings.save_name %x)
				except OSError: pass
			self.g.sounds['save'].play()
			self.dlogtext.draw_text("Saves successfully wiped!{wait}")
			self.save_exists = False
		elif choice == 1 or choice is False:
			self.handle_c = self.handle_option
			self.start_options()

class SaveMenu():
	def __init__(self, menu, surf, save=True):
		self.game = menu.game #store parameters
		self.g = menu.g
		self.save = save
		self.menu = menu
		self.surf = surf
		#initialize stuff
		self.choice_dlog = dialog.ChoiceDialog(self.g, "sign")
		self.dlog = dialog.Dialog(self.g, "sign")
		self.font = font.Font("fonts/dialog_font.xml") #create font for drawing

		if save:
			self.text = "Would you like to save"
			self.update_handle = self.save_update
		else:
			self.text = "Which slot would you like to load"
			self.update_handle = self.load_update

		self.text += ", {br}%s?{choices}" %settings.name

		for idx in range(settings.maxsaves):
			if path.exists(settings.save_name %idx): desc = "In Use"
			else: desc = "Open" 
			self.text += "Save %d - %s{endchoice}" %(idx, desc)

		self.text += "Cancel{endchoice}{endchoices}"

		self.slot = 0
		self.finished = False
		#show question
		self.dlog.draw_text(self.text)

	def menu_return(self):
		self.menu.show() #re-show the menu
		return

	def update(self):
		choice = self.dlog.update(self.surf, (0, 1)) #draw dialog

		if choice == None: pass
		elif choice == settings.maxsaves or self.finished: self.menu_return() #cancel/return
		elif choice is True:
			self.finished = True
			if self.save: self.save_update(self.surf, self.slot)
			else: self.load_update(self.surf, self.slot)
		elif choice >= 0 and choice < settings.maxsaves:
			self.slot = choice
			if self.save: self.dlog.draw_text("Saving...") #show saving message if choice is within save count range

	def save_update(self, surf, choice): #update ourselves
		self.game.save(choice) #cue to start saving
		self.dlog.draw_text("Game has been saved!{wait}") #show game saved message

	def load_update(self, surf, choice):
		save_file = settings.save_name %choice
		if path.exists(save_file): self.g.save.load(save_file)
		else: self.g.save.new()

		self.g.sounds['load'].play()
		music.fadeout(1000)

		self.g.title_screen = None #remove ourselves from the globals
		self.g.game = game.Game(self.g) #initialize a new game
		self.g.game.start(not path.exists(save_file)) #tell it to start running
		self.g.update_func = self.g.game.update #store new update function

class PartyMenu: #menu for displaying the party members
	def __init__(self, menu, surf):
		self.game = menu.game #store parameters
		self.g = menu.g
		self.menu = menu
		self.surf = surf
		#initialize stuff
		self.font = font.Font("fonts/dialog_font.xml") #create font for drawing
	def finish(self):
		self.menu.show() #re-show the menu
	def update(self): #update ourselves
		self.surf.fill((255, 255, 255)) #clear surface
		ypos = 10
		for member in self.game.player.party: #loop through player's party
			self.font.render(member.show_name, self.surf, (10, ypos)) #show the character's name
			ypos += self.font.height
			self.font.render("HP: "+str(member.hp)+"/"+str(member.stats[0])+" Lv: "+str(member.level), self.surf, (10, ypos))
			ypos += self.font.height+4
		if self.g.curr_keys.get(settings.key_accept): #if accept has been pressed
			self.finish() #we're done
