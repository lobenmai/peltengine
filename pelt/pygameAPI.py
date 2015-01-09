import pygame

class Color(object):
	def __init__(self, *args, **kwargs):
		pygame.Color(*args, **kwargs)

class display(object): pass
for m in ['flip', 'get_surface', 'get_caption', 'set_mode']:
	setattr(display, m, staticmethod(getattr(pygame.display, m))) 
class Broker(object):
	original_class = None
	methods = []

	def __init__(self, *args, **kwargs):
		self.obj = self.original_class(*args, **kwargs)
		for m in self.methods:
			setattr(self, m, lambda *args, **kwargs: getattr(self.obj, m)(*args, **kwargs))

class Surface(Broker):
	original_class = pygame.Surface
	methods = ["blit", "convert", "convert_alpha", "copy", "fill", "get_height", "get_rect", "get_width", "scroll", "set_alpha", "set_clip", "set_colorkey"]
