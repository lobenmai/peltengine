#In need of MAJOR remodeling
#Created April 28, 2014 at 22:28

import settings, game, savegame, titlescreen, error, data, music, dialog, map

import logging
from time import sleep

if not settings.ios:
	import pygame
	from pygame.locals import *
	pygame.init()
	music.init()
else: import scene

if settings.steamAPI: import PySteamAPI as steam

# import parts of game that need loading
# import poke_types, pokemon

class StatusMessage(object):
	def __init__(self, g, screen):
		self.surf = pygame.Surface((256, 44)) #resize the surface to the image
		self.screen = screen
		self.g = g
		self.dlog = dialog.Dialog(self.g, "standard")
		self.frames_left = 0

	def show_msg(self, msg):
		self.clear()

		self.dlog.draw_text(str(msg)+"{wait}")
		logging.debug("Status Message set to %s.", msg)

		self.frames_left = (len(msg) * 3) + 30
		logging.debug("The status message will show for %d frames.", self.frames_left)

	def clear(self):
		self.frames_left = 0
		self.surf.set_alpha(255)

		self.dlog.drawing = False
		self.dlog.waiting = False
		self.dlog.fill_allowed = False
		
	def update(self):
		if not self.frames_left: return
		self.surf.fill((255, 255, 255))
		self.dlog.update(self.surf, (0, 0), prlx_enable=False, ignore_keys=True)
		self.screen.blit(self.surf, ((settings.screen_x*2)-256, (settings.screen_y*2)-44))

		self.frames_left -= 1

		if self.frames_left <= 0:
			self.clear()

		elif self.frames_left == 30:
			logging.debug("Status message is now fading out.")

		elif self.frames_left < 30:
			alpha = ((255/30)*self.frames_left)
			self.surf.set_alpha(alpha)

class Container: pass #blank class to store global variables

class Global(object):
	def __init__(self):
		#self.logger = logging.Logger("PELTlog")
		logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)
		#self.logger.setLevel(logging.DEBUG)

		#Mouse Button Numbers
		#1: Left Mouse
		#2: Middle Mouse
		#3: Right Mouse
		#4: Scroll Up
		#5: Scroll Down

		self.MOUSEBUTTONS = {
			1: "LMB",
			2: "MMB",
			3: "RMB",
			4: "Wheel Up",
			5: "Wheel Down"
		}

		self.mouse = [False]*settings.MOUSE_BUTTON_COUNT
		self.mouse_pos = (0, 0)
		self.curr_mouse = list(self.mouse)

		#self.keys = [False]*len(settings.keys) #variable to hold states of keys
		self.keys = {}
		self.curr_keys = dict(self.keys)

		self.joy = [False]*12
		self.joy_pos = (0, 0)
		self.curr_joy = list(self.joy)

		try: j = pygame.joystick.Joystick(0)
		except: pass

		self.playingGame = False
		self.set_screen()

		self.next_frame = 0 #tick number of the next frame
		self.fps = 0 #current FPS
		self.next_fps = 0 #next FPS
		self.prev_secs = 0 #previous number of seconds

		self.next_frame = pygame.time.get_ticks()

		self.sounds = {
			'shift': music.Sound(data.get_resource("sounds/shift.ogg")),
			'select': music.Sound(data.get_resource("sounds/select.ogg")),
			'reject': music.Sound(data.get_resource("sounds/reject.ogg")),
			'openMenu': music.Sound(data.get_resource("sounds/openMenu.ogg")),
			'load': music.Sound(data.get_resource("sounds/load.ogg")),
			'save': music.Sound(data.get_resource("sounds/save.ogg"))
		}

		self.quitting = False
		self.gframesleft = 0

		self.status_msg = StatusMessage(self, self.screen) #initialize StatusMessage() class

	def set_screen(self):
		fullscreen = pygame.FULLSCREEN if settings.fullscreen else 0 #if fullscreen is turned on in the settings, enable it

		# if self.playingGame: scale = 2
		# else: scale = 1
		scale = 1
		screen = pygame.display.set_mode((settings.screen_x*scale, settings.screen_y*scale), fullscreen) #create a window to draw on
		
		self.screen = screen #store it in the globals
		self.set_caption("PELT Engine - " + settings.name) #set screen titles

	def set_caption(self, caption):
		pygame.display.set_caption(caption)
		#self.status_msg.show_msg("Caption set to: %s" %caption)
		logging.warning("Caption changed!  It is now '%s'", caption)

	def wait_frame(self):
		self.next_fps += 1 #increment one frame
		self.last_frame = self.next_frame
		self.next_frame = self.last_frame + settings.framerate
		now = pygame.time.get_ticks()
		if self.next_frame > now: pygame.time.wait(int(self.next_frame-now))
		if now / 1000 != self.prev_secs: #if one frame has passed
			self.fps = self.next_fps #set framerate
			self.next_fps = 0 #clear next framerate
			self.prev_secs = now/1000 #store the second this number was calculated

	# def wait_frames(self): #wait for the next frame
	# 	self.next_frame += 1000.0/settings.framerate #calculate time of next frame
	# 	now = pygame.time.get_ticks() #get current number of ticks
	# 	self.next_fps += 1 #increment one frame
	# 	if self.next_frame < now: #if we've already passed the next frame
	# 		self.next_frame = now #try to go as fast as possible
	# 	else: #if we haven't
	# 		pygame.time.wait(int(self.next_frame)-now) #wait for next frame
	# 	if now / 1000 != self.prev_secs: #if one frame has passed
	# 		self.fps = self.next_fps #set framerate
	# 		self.next_fps = 0 #clear next framerate
	# 		self.prev_secs = now/1000 #store the second this number was calculated

	def reset(self): #reset the game
		self.game = None #destroy current game
		#self.save.new() #create a new save file
		self.playingGame = False
		self.set_screen()
		self.menu_showing = False
		
		self.title_screen = titlescreen.TitleScreen(self) #initialize title screen
		self.update_func = self.title_screen.update #set update function

	def mainloop(self): #main loop of the game
		running = True
		while running: #loop while we are still running
			try:
				self.curr_keys = {}
				self.curr_mouse = [False]*settings.MOUSE_BUTTON_COUNT

				for event in pygame.event.get(): #process events
					if event.type == QUIT: #if we're being told to quit
						logging.warning("Game has been quit!")
						running = False #stop running
						break #and stop processing events
					elif event.type == KEYDOWN:
						self.keys[event.key] = True
						self.curr_keys[event.key] = True
						logging.debug("Key %s pressed.", pygame.key.name(event.key))
					elif event.type == KEYUP:
						self.keys[event.key] = False
						logging.debug("Key %s released.", pygame.key.name(event.key))

					elif event.type == pygame.MOUSEBUTTONDOWN:
						self.mouse[event.button] = True
						self.curr_mouse[event.button] = True
						logging.debug("Mouse button %s pressed down at %s, %s", self.MOUSEBUTTONS.get(event.button, "Button %s" %event.button), self.mouse_pos[0], self.mouse_pos[1])
					elif event.type == pygame.MOUSEBUTTONUP:
						self.mouse[event.button] = False
						logging.debug("Mouse button %s released at %s, %s", self.MOUSEBUTTONS.get(event.button, "Button %s" %event.button), self.mouse_pos[0], self.mouse_pos[1])
					elif event.type == pygame.MOUSEMOTION:
						self.mouse_pos = tuple([x / settings.screen_scale
							for x in pygame.mouse.get_pos()])

				if not running: break
				#if self.keys.get(pygame.K_ESCAPE) or not running: break

				surface = self.update_func() #tell current object to update for one frame
				if 'debug' in settings.args:
					if self.mouse[1]: color = (0, 255, 0)
					elif self.mouse[3]: color = (0, 0, 255)
					else: color = (255, 0, 0)
					pygame.draw.circle(surface, color, self.mouse_pos, 5)

				if self.quitting:
					self.qframesleft -= 1
					if self.qframesleft == 0: raise error.QuitException

				# if self.playingGame: scale = 1
				# else: scale = 1
				
				pygame.transform.scale(surface, (settings.screen_x, settings.screen_y), self.screen) #draw the screen scaled properly
				if self.menu_showing == True: #if the menu is being shown
					self.menu.update() #update the menu
				try:
					if self.game.dialog_drawing == True:
						self.screen.blit(self.game.dlog_surf, (0, settings.screen_y-self.game.dlog_surf.get_height()/2))
				except AttributeError: pass

				self.status_msg.update()

				pygame.display.flip() #flip double buffers
				self.wait_frame()

			except error.UserQuit:
				logging.warning("Game is now quitting!")
				self.status_msg.show_msg("Game is now quitting!")
				self.quitting = True
				self.qframesleft = 30
				music.fadeout(1000*self.qframesleft/settings.framerate)

g = Global()

def main():
	#start the game running
	try:
		# poke_types.load_data() #load pokemon type data
		# pokemon.load_data()
		map.load_data()
		settings.load(g)
		g.save = savegame.SaveGame(g) #initialize a new savegame manager
		g.reset() #reset the game
		g.mainloop() #start the main loop
	except error.QuitException: #if it was just a forced quit
		pass
	except Exception as e: #if it's any other exception
		error.exception_handler(g, e) #pass it to exception handler
	g.keeprunning = False

if __name__ in '__main__':
	main()
