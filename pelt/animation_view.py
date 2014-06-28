#PELT Animation Viewer
#Created May 20, 2014 at 14:13

import pygame, sys, os
import animation, settings

def main(args):
	sys.path.append('..')

	screen = pygame.display.set_mode((settings.screen_x * settings.screen_scale, settings.screen_y * settings.screen_scale))

	anim_dest = pygame.Surface((settings.screen_x, settings.screen_y))

	anim = animation.PartAnimationSet(None, args[0], peltdir=False)
	anim.set_animation(args[1])

	posx, posy = int(args[2]), int(args[3])

	running = True
	clock = pygame.time.Clock()

	while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
				break
			
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE: running = False
				elif event.key == ord('r'):
					anim = animation.PartAnimationSet(None, sys.argv[1])
					anim.set_animation(sys.argv[2])
		
		if running == False: break
		
		anim_dest.fill((255, 255, 255))
		anim.update(anim_dest, posx, posy)
		
		pygame.transform.scale(anim_dest, (settings.screen_x * settings.screen_scale, settings.screen_y * settings.screen_scale), screen)
		
		pygame.display.flip()
		clock.tick(30)

if __name__ == "__main__": main(sys.argv[1:])
