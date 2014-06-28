import pygame
import settings

def init(*args, **kwargs): pygame.mixer.init(*args, **kwargs)
def load(*args, **kwargs): return pygame.mixer.music.load(*args, **kwargs)
def play(*args, **kwargs):
	if settings.option_music: pygame.mixer.music.play(*args, **kwargs)
def fadeout(*args, **kwargs): pygame.mixer.music.fadeout(*args, **kwargs)

class Sound(pygame.mixer.Sound):
	def __init__(self, *args, **kwargs):
		self.sound = pygame.mixer.Sound(*args, **kwargs)

	def play(self, *args, **kwargs):
		if settings.option_sound: self.sound.play(*args, **kwargs)