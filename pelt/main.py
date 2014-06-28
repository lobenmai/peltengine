#In need of MAJOR remodeling
#Created April 28, 2014 at 22:28

import settings, game, savegame, titlescreen, error, data, music

if not settings.ios:
	import pygame
	from pygame.locals import *
	music.init()
else: import scene

#import parts of game that need loading
import poke_types, pokemon, map

class Container: pass #blank class to store global variables

class Game(object):
	def __init__(self):
		#Mouse Button Numbers
		#1: Left Mouse
		#2: Middle Mouse
		#3: Right Mouse
		#4: Scroll Up
		#5: Scroll Down

		self.mouse = [False]*settings.MOUSE_BUTTON_COUNT
		self.mouse_pos = (0, 0)
		self.curr_mouse = list(self.mouse)

		#self.keys = [False]*len(settings.keys) #variable to hold states of keys
		self.keys = {}
		self.curr_keys = dict(self.keys)

		screen = pygame.display.set_mode((settings.screen_x*settings.screen_scale, settings.screen_y*settings.screen_scale)) #create a window to draw on
		self.screen = screen #store it in the globals
		self.set_caption("PELT Engine") #set screen title

		#self.next_frame = 0 #tick number of the next frame
		#self.fps = 0 #current FPS
		#self.next_fps = 0 #next FPS
		#self.prev_secs = 0 #previous number of seconds

		self.next_frame = pygame.time.get_ticks()

		self.sounds = {
			'shift': music.Sound(data.get_resource("sounds/shift.ogg")),
			'select': music.Sound(data.get_resource("sounds/select.ogg")),
			'reject': music.Sound(data.get_resource("sounds/reject.ogg")),
			'openMenu': music.Sound(data.get_resource("sounds/openMenu.ogg")),
			'load': music.Sound(data.get_resource("sounds/load.ogg")),
			'save': music.Sound(data.get_resource("sounds/save.ogg"))
		}

	def set_caption(self, caption): pygame.display.set_caption(caption)

	def wait_frame(self):
		self.last_frame = self.next_frame
		self.next_frame = self.last_frame + settings.framerate
		now = pygame.time.get_ticks()
		if self.next_frame > now:
			pygame.time.wait(int(self.next_frame-now))

	#def wait_frames(self): #wait for the next frame
	#	self.next_frame += 1000.0/settings.framerate #calculate time of next frame
	#	now = pygame.time.get_ticks() #get current number of ticks
	#	self.next_fps += 1 #increment one frame
	#	if self.next_frame < now: #if we've already passed the next frame
	#		self.next_frame = now #try to go as fast as possible
	#	else: #if we haven't
	#		pygame.time.wait(int(self.next_frame)-now) #wait for next frame
	#	if now / 1000 != self.prev_secs: #if one frame has passed
	#		self.fps = self.next_fps #set framerate
	#		self.next_fps = 0 #clear next framerate
	#		self.prev_secs = now/1000 #store the second this number was calculated

	def reset(self): #reset the game
		self.game = None #destroy current game
		self.save.new() #create a new save file
		self.title_screen = titlescreen.TitleScreen(self) #initialize title screen
		self.update_func = self.title_screen.update #set update function

	def mainloop(self): #main loop of the game
		running = True
		while running: #loop while we are still running
			self.curr_keys = {}
			self.curr_mouse = [False]*settings.MOUSE_BUTTON_COUNT

			for event in pygame.event.get(): #process events
				if event.type == QUIT: #if we're being told to quit
					running = False #stop running
					break #and stop processing events
				elif event.type == KEYDOWN:
					self.keys[event.key] = True
					self.curr_keys[event.key] = True
				elif event.type == KEYUP:
					self.keys[event.key] = False

				elif event.type == pygame.MOUSEBUTTONDOWN:
					self.mouse[event.button] = True
					self.curr_mouse[event.button] = True
				elif event.type == pygame.MOUSEBUTTONUP:
					self.mouse[event.button] = False
				elif event.type == pygame.MOUSEMOTION:
					self.mouse_pos = tuple([x / settings.screen_scale
						for x in pygame.mouse.get_pos()])

			if self.keys.get(pygame.K_ESCAPE) or not running: break

			surface = self.update_func() #tell current object to update for one frame
			if 'debug' in settings.args:
				if self.mouse[1]: color = (0, 255, 0)
				elif self.mouse[3]: color = (0, 0, 255)
				else: color = (255, 0, 0)
				pygame.draw.circle(surface, color, self.mouse_pos, 5)
			pygame.transform.scale(surface, (settings.screen_x*settings.screen_scale, settings.screen_y*settings.screen_scale), self.screen) #draw the screen scaled properly
			pygame.display.flip() #flip double buffers
			self.wait_frame()

g = Game()

def main():
	#start the game running
	try:
		poke_types.load_data() #load pokemon type data
		pokemon.load_data()
		map.load_data()
		settings.load(g)
		g.save = savegame.SaveGame(g) #initialize a new savegame manager
		g.reset() #reset the game
		g.mainloop() #start the main loop
	except error.QuitException: #if it was just a forced quit
		pass #don't do anything
	except Exception as e: #if it's any other exception
		error.exception_handler(g, e) #pass it to exception handler
	g.keeprunning = False

if __name__ in '__main__':
	main()
