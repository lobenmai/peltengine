#PELT Credits Animation
#Created 5/21/14 at 22:26

# -*- coding: utf-8 -*-

import pygame
from sys import exit

pygame.font.init()

def credit(text, font, color):
	try: text = text.decode('utf-8')
	except: pass

	try: color = pygame.Color(color)
	except: color = Color(*color)

	clock = pygame.time.Clock()

	screen = pygame.display.get_surface()
	screenrect = screen.get_rect()
	bg = screen.copy()

	w, h = font.size(' ')
	Rright = screenrect.centerx + w*3
	Rleft = screenrect.centerx - w*3

	foo = []
	for i, l in enumerate(text.splitlines()):
		a, b, c = l.partition('\\')
		u = False

		if a:
			if a.startswith('_') and a.endswith('_'):
				u = True
				a = a.strip('_')

			rect = pygame.Rect((0, 0), font.size(a))
			if b: rect.topright = Rleft, screenrect.bottom + h * i
			else: rect.midtop = screenrect.centerx, screenrect.bottom + h * i

			foo.append([a, rect, u])

		u = False

		if c:
			if c.startswith('_') and c.endswith('_'):
				u = True
				c = c.strip('_')

			rect = Rect((0, 0), font.size(c))
			rect.topleft = Rright, screenrect.bottom + h * i
			foo.append([c, rect, u])

	y = 0
	while foo and not pygame.event.peek(pygame.QUIT):
		for e in pygame.event.get():
			if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
				pygame.quit()
				exit()

		pygame.event.clear()

		y -= 1
		for p in foo[:]:
			r = p[1].move(0, y)
			if r.bottom < 0:
				foo.pop(0)
				continue
			if not isinstance(p[0], pygame.Surface):
				if p[2]: font.set_underline(1)
				p[0] = font.render(p[0], 1, color)
				font.set_underline(0)

			screen.blit(p[0], r)
			if r.top >= screenrect.bottom: break

		clock.tick(40)
		pygame.display.flip()
		screen.blit(bg, (0, 0))
	
	pygame.display.flip()