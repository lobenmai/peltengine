#In need of remodeling
#Created April 28, 2014 at 22:28

import settings #load game settings

if not settings.ios:
	import pygame #import everything pygame-related
	from pygame.locals import *
else: import scene
import os.path as path
import os, sys

if settings.steamAPI:
	try: import PySteamAPI as steam
	except ImportError: settings.steamAPI = False

import game, dialog, font, error, data, music, menu

class TitleScreen: #class for the title screen
	def __init__(self, g, m=True):
		self.g = g #store globals
		self.game = g #store globals again .-.
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

		size = self.bg.get_size()
		scalefactor = max(settings.screen_x/size[0], settings.screen_y/size[1])
		self.scalefactor = scalefactor

		self.bg = pygame.transform.scale(self.bg, (settings.screen_x, settings.screen_y))
		self.logo = pygame.transform.scale(self.logo, tuple([x*scalefactor / 4 for x in self.logo.get_size()]))
		self.logomask = pygame.transform.scale(self.logomask, tuple([x*scalefactor / 4 for x in self.logomask.get_size()]))
		self.shine = pygame.transform.scale(self.shine, tuple([x*scalefactor for x in self.shine.get_size()]))

		self.surf.blit(self.bg, (0,0)) #draw background of titlescreen
		self.surf.blit(self.logo, (18, 12)) #and logo

		#create a surface to draw the shine on with the same dimensions as the logo
		self.shinesurf = pygame.Surface(self.logo.get_size(), SRCALPHA)
		#create a surface for the text
		self.textsurf = pygame.Surface(self.textbg.get_size(), SRCALPHA)
		#now, we need to draw Press X! on screen
		f = font.Font("fonts/selfdialog_font.xml") #load font to draw with
		f.render("Welcome, %s!" %settings.name, self.textbg, (15, 2))
		#calculate dimensions for everything
		self.shine_y = (self.logo.get_height()-self.shine.get_height())/2
		self.shine_x = -500 #current x position of shine
		#set up variables for fading text
		self.fadein = True
		self.textopacity = 10 #opacity goes backwards for faster drawing

		if m: self.music = music.load(data.get_resource("music/main.ogg"))

		self.check_environment() #make sure the environment is up to snuff
		if m: music.play(-1)
		
		self.titlemenu = menu.TitleMenu(self.g, self, self.surf)
		
		self.update_func = self.main_update
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
				self.dlog.draw_text("Error! Your pygame version isn't up to date{br}and the game won't be able to run.{wait}")
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
	def main_update(self, surf, choices=True): #update showing the picture
		prlx = settings.get_prlx(5, 1)

		width, height = self.shine.get_size()
		self.surf.blit(self.logo, (18+self.shine_x, 12), (0+self.shine_x, 0, width, height)) #and logo

		#move shine
		self.shine_x += 3 * self.scalefactor
		if self.shine_x > self.logo.get_width():
			self.shine_x = -500

		self.shinesurf.fill((0, 0, 0, 0)) #clear out temp shine
		self.shinesurf.blit(self.shine, (self.shine_x, self.shine_y)) #draw shine
		self.shinesurf.blit(self.logomask, (0, 0), special_flags=BLEND_RGBA_MULT) #mask it to fit logo
		# self.surf.blit(self.bg, (0,0)) #draw background of titlescreen
		# self.surf.blit(self.logo, (18+prlx[0], 12+prlx[1])) #and logo
		self.surf.blit(self.shinesurf, (18+prlx[0], 12+prlx[1])) #and shine
		
		#now, calculate for welcome text!
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

		if choices:
			self.active_menu.update()
			#self.surf.fill((255, 255, 255)) #show white background
			# choice = self.dlog.update(self.surf, (1, -60)) #draw choice dialog
# 			if choice is not None: #if the user chose something
# 				self.handle_c(choice) #handle the choice

	# 	if self.g.curr_keys.get(settings.key_accept) or self.g.curr_mouse[1]: #if accept key was pressed
	# 		self.update_func = self.choice_update #switch update functions
	# 		self.start_choices() #and start showing choices

	def update(self): #update ourselves
		self.update_func(self.surf) #call specified update function
		return self.surf #return our surface
