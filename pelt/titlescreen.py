#In need of remodeling
#Created April 28, 2014 at 22:28

import settings #load game settings

if not settings.ios:
	import pygame #import everything pygame-related
	from pygame.locals import *
else: import scene
import os.path as path
import os, sys

import game, dialog, font, error, data, music

class TitleScreen: #class for the title screen
	def __init__(self, g):
		self.g = g #store globals
		self.dlog = dialog.ChoiceDialog(self.g, "standard", selectsound=False) #initialize new dialog for choices
		self.dlogtext = dialog.Dialog(self.g, "standard")
		#initialize new surface to draw stuff on
		self.surf = pygame.Surface((settings.screen_x, settings.screen_y))
		#load and create surfaces for all the title screen parts
		self.bg = data.load_image("titlescreen/background.png")	
		self.bg.convert()
		self.logo = data.load_image("titlescreen/logo.png")
		self.logo.convert_alpha()
		self.logomask = data.load_image("titlescreen/logomask.png")
		self.logomask.convert()
		self.shine = data.load_image("titlescreen/shine.png")
		self.shine.convert_alpha()
		self.textbg = data.load_image("titlescreen/fadetoblack.png")
		self.textbg.convert_alpha()

		self.scale()
		#create a surface to draw the shine on with the same dimensions as the logo
		self.shinesurf = pygame.Surface(self.logo.get_size(), SRCALPHA)
		#create a surface for the text
		self.textsurf = pygame.Surface(self.textbg.get_size(), SRCALPHA)
		#now, we need to draw Press X! on screen
		f = font.Font("fonts/selfdialog_font.xml") #load font to draw with
		f.render("Press X or Click!", self.textbg, (15, 2))
		#calculate dimensions for everything
		self.shine_y = (self.logo.get_height()-self.shine.get_height())/2
		self.shine_x = -75 #current x position of shine
		#set up variables for fading text
		self.fadein = True
		self.textopacity = 10 #opacity goes backwards for faster drawing

		self.music = music.load(data.get_resource("music/main.ogg"))

		self.check_environment() #make sure the environment is up to snuff
		self.start_main() #start main function
	def scale(self):
		size = self.bg.get_size()
		scalefactor = min(settings.screen_x/size[0], settings.screen_y/size[1])

		self.bg = pygame.transform.scale(self.bg, (settings.screen_x, settings.screen_y))
		self.logo = pygame.transform.scale(self.logo, tuple([x*scalefactor for x in self.logo.get_size()]))
		self.logomask = pygame.transform.scale(self.logomask, tuple([x*scalefactor for x in self.logomask.get_size()]))
		self.shine = pygame.transform.scale(self.shine, tuple([x*scalefactor for x in self.shine.get_size()]))
	def check_environment(self): #make sure environment is up to snuff
		expected = (1,9,1) #expected version to compare with
		real = pygame.version.vernum #given version
		incorrect = False
		for num in zip(real, expected): #check version tuples
			if num[0] > num[1]: #if real number is > expected, automatic win
				break
			elif num[0] < num[1]: #otherwise, if real is < expected, automatic fail
				incorrect = True
				break
		if incorrect: #if version number is incorrect
			try: #attempt to show pretty error
				self.dlog = dialog.Dialog(self.g, "standard") #load standard dialog
				#show error
				self.dlog.draw_text("Error! Your pygame version isn't up to snuff  and the game won't be able to run.{wait}")
				self.environ_error() #run function once to check for issues
				self.update_func = self.environ_error #set new update function
			except Exception as e: #if that couldn't be done
				print "-----ENVIRONMENT ERROR-----"
				print "Pygame is not up to date, game will not run!"
				print "-----ENVIRONMENT ERROR-----"
				raise error.QuitException()
	def environ_error(self): #show environment error
		self.surf.fill((0, 0, 0)) #clear out surface
		result = self.dlog.update(self.surf, (0, 1)) #show error dialog
		if result is True: #if dialog finished
			raise error.QuitException() #die
	def start_game(self): #start the game running
		self.g.title_screen = None #remove ourselves from the globals
		self.g.game = game.Game(self.g) #initialize a new game
		self.g.game.start() #tell it to start running
		self.g.update_func = self.g.game.update #store new update function
	def start_main(self): #start showing main title screen
		self.update_func = self.main_update #set our update function
		music.play(-1)
	def main_update(self): #update showing the picture
		prlx = settings.get_prlx(5, 1)
		self.shinesurf.fill((0, 0, 0, 0)) #clear out temp shine
		self.shinesurf.blit(self.shine, (self.shine_x, self.shine_y)) #draw shine
		self.shinesurf.blit(self.logomask, (0, 0), special_flags=BLEND_RGBA_MULT) #mask it to fit logo
		self.surf.blit(self.bg, (0,0)) #draw background of titlescreen
		self.surf.blit(self.logo, (18+prlx[0], 12+prlx[1])) #and logo
		self.surf.blit(self.shinesurf, (18+prlx[0], 12+prlx[1])) #and shine
		#move shine
		self.shine_x += 3
		if self.shine_x > 375:
			self.shine_x = -75
		#now, calculate for press x!
		self.textsurf.fill((0, 0, 0, 0))  #clear out text buffer
		self.textsurf.blit(self.textbg, (0, 0)) #draw text onto it
		#draw transparency
		self.textsurf.fill((255, 255, 255, self.textopacity), special_flags=BLEND_RGBA_MULT)
		self.surf.blit(self.textsurf, (prlx[0], settings.screen_y-47+prlx[1])) #draw faded surface onto screen
		if self.fadein: #change opacity
			self.textopacity += 12
			if self.textopacity > 255:
				self.textopacity = 255
				self.fadein = False
		else:
			self.textopacity -= 12
			if self.textopacity < 20:
				self.textopacity = 20
				self.fadein = True
		if self.g.curr_keys.get(settings.key_accept) or self.g.curr_mouse[1]: #if accept key was pressed
			self.update_func = self.choice_update #switch update functions
			self.start_choices() #and start showing choices
	def start_choices(self): #show load choice screen
		if path.exists(settings.save_name): #if save file exists
			self.save_exists = True #mark it
		else:
			self.save_exists = False
		choices = ["New Game", "Options", "Quit"]
		if self.save_exists: #if a save file exists
			choices.insert(0, "Load Game") #give option to load it
		self.dlog.show_choices(choices) #show choices
	def choice_update(self): #show load choices
		self.surf.fill((255, 255, 255)) #show white background
		choice = self.dlog.update(self.surf, (1, 1)) #draw choice dialog
		if choice is not None: #if the user chose something
			self.handle_choice(choice) #handle the choice
	def handle_choice(self, choice):
		if choice < 2:
			self.g.sounds['load'].play()
			music.fadeout(1000)
		if self.save_exists == False: #if no save exists
			choice += 1 #bump up choice number to account for missing option
		if choice == 0: #if load was pressed
			self.g.save.load(settings.save_name) #load savegame
		elif choice == 1: #if new was pressed
			self.g.save.new() #start a new savegame
		elif choice == 2: #if options was pressed
			self.update_func = self.options_update
			self.start_options()
		elif choice == 3:
			pygame.quit()
			raise error.UserQuit()
		if choice < 2: self.start_game() #start the game running if not options
	def start_options(self):
		if path.exists(settings.save_name): #if save file exists
			self.save_exists = True #mark it
		else:
			self.save_exists = False
		m = "On" if settings.option_music else "Off"
		s = "On" if settings.option_sound else "Off"
		p = "On" if settings.parallax else "Off"
		choices = ["Wipe Save (No Save!)", "Music (%s)" %m, "Sound (%s)" %s, "Mouse Parallax (%s)" %p, "Back"]
		if self.save_exists: choices[0] = "Wipe Save"
		self.dlog.show_choices(choices)
	def options_update(self):
		self.surf.fill((255, 255, 255))
		choice = self.dlog.update(self.surf, (1, 1))
		if choice is not None:
			self.handle_option(choice)
	def handle_option(self, choice):
		if choice == 0:
			if self.save_exists:
				self.dlogtext.draw_text("Are you sure you want to wipe your save file?{choices}Yes{endchoice}No{endchoice}{endchoices}")
				self.update_func = self.wipe_update
		if choice == 1:
			settings.option_music = not settings.option_music
			music.play(-1)
			if not settings.option_music: music.fadeout(500)
		if choice == 2: settings.option_sound = not settings.option_sound
		if choice == 3: settings.parallax = not settings.parallax
		if choice == 4:
			self.update_func = self.choice_update
			settings.save()
			self.start_choices()
		else: self.start_options()
	def wipe_update(self):
		choice = self.dlogtext.update(self.surf, (0, 1)) #draw dialog
		if choice == 0:
			self.dlogtext.draw_text("Wiping save...")
			os.remove(settings.save_name)
			self.g.sounds['save'].play()
			self.dlogtext.draw_text("Save successfully wiped!")
			self.save_exists = False
		elif choice == 1:
			self.update_func = self.options_update
			self.start_options
	def update(self): #update ourselves
		self.update_func() #call specified update function
		return self.surf #return our surface
