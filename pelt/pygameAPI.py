import pygame

class Color(object):
	def __init__(self, *args, **kwargs):
		pygame.Color(*args, **kwargs)

class display(object): pass
for m in ['flip', 'get_surface', 'get_caption', 'set_mode']:
	setattr(display, m, staticmethod(getattr(pygame.display, m))) 

class Surface(object):
	def __init__(self, *args, **kwargs):
		surf = pygame.Surface(*args, **kwargs)
for m in ["blit", "convert", "convert_alpha", "copy", "fill", "get_height", "get_rect", "get_width", "scroll", "set_alpha", "set_clip", "set_colorkey"]:
	setattr(Surface, m, getattr(Surface.surf, m))