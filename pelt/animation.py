#PELT Animation
#Created May 19, 2014 at 16:24

import settings

if not settings.ios: import pygame
else: import scene
import math

import tileset
import data

import sys

class Animation():
	def __init__(self, anim_group, anim_dom):
		self.agroup = anim_group
		self.frames = []
		self.currframe = 0
		self.framesleft = 0 #Frames left of the current frame
		self.animdom = anim_dom
		
		if anim_dom.getAttribute('loop') == 'true': self.loop = True
		else: self.loop = False
		
		child = anim_dom.firstChild #Get first frame
		while child is not None:
			if child.localName == "frame":
				sheet = child.getAttribute('sheet')
				pos = child.getAttribute('pos').split(',')
				wait = int(child.getAttribute('wait'))
				
				pos_x = int(pos[0].strip())
				pos_y = int(pos[1].strip())
				
				#image = self.anim_group.sheets[sheet].get_tile(pos_x, pos_y)
				imagesheet = self.agroup.sheets[sheet]
				image = imagesheet.get_tile(pos_x, pos_y)
				
				self.frames.append([image, wait])
				
			child = child.nextSibling
	
	def start(self):
		self.currframe = 0
		self.agroup.sprite.image = self.frames[0][0]
		self.framesleft = self.frames[0][1]
	
	def update(self):
		"""Plays the next frame of the animation"""
		
		self.framesleft -= 1
		if self.framesleft: return
		
		self.currframe += 1
		if self.currframe == len(self.frames):
			if self.loop: self.currframe = 0
			else:
				self.agroup.curranim = self.agroup.oldanim
				self.agroup.curranim.start()
				return
			
		self.agroup.sprite.image = self.frames[self.currframe][0]
		self.framesleft = self.frames[self.currframe][1]

class AnimationGroup():
	def __init__(self, g, sprite, anim_file):
		self.g = g
		self.sprite = sprite
		self.afile = anim_file
		
		self.animations = {}
		self.sheets = {}
		self.curranim = None
		self.oldanim = None
		
		anim_dom = data.load_xml(anim_file).documentElement
		
		for sheet in anim_dom.getElementsByTagName('sheet'):
			width = int(sheet.getAttribute('tilewidth'))
			height = int(sheet.getAttribute('tileheight'))
			image = sheet.getAttribute('from')
			id = sheet.getAttribute('id')
			self.sheets[id] = tileset.Tileset(image, width, height)
			
		for anim in anim_dom.getElementsByTagName('animation'):
			id = anim.getAttribute('id')
			self.animations[id] = Animation(self, anim)
	
	def set_animation(self, anim_id):
		self.oldanim = self.curranim
		self.curranim = self.animations[anim_id]
		self.curranim.start()
	
	def update(self): self.curranim.update()

class PartAnimationPart():
	def __init__(self, set_, g, dom):
		self.g = g
		self.set = set_
		
		self.id = dom.getAttribute('id')
		set_.parts[self.id] = self
		self.pos = [int(x.strip()) for x in dom.getAttribute('pos').split(',')]
		
		try: self.rot = float(dom.getAttribute('rotation'))
		except: self.rot = 0.0
		try: t = float(dom.getAttribute('scale'))
		except: t = 1.0
		self.xscale, self.yscale = t, t
		try:
			self.xscale = float(dom.getAttribute("xscale"))
			self.yscale = float(dom.getAttribute("yscale"))
		except: pass
		try: self.show = int(dom.getAttribute("show")) != 0
		except: self.show = True
		
		self.orig_pos = self.pos[:]
		self.orig_rot = self.rot
		self.orig_xscale = self.xscale
		self.orig_yscale = self.yscale
		
		self.orig_image = self.image = set_.part_images[dom.getAttribute('from')][0]
		self.orig_center = self.center = set_.part_images[dom.getAttribute("from")][1]
		self.offset = set_.part_images[dom.getAttribute("from")][2]
		self.orig_offset = self.offset[:]
		self.orig_show = self.show
	
	def render(self, surf, x, y, xs, ys, rot, center):
		if not self.show: return
		img = self.image
		
		pos = [(self.pos[0]-center[0]+self.center[0]), (self.pos[1]-center[1]+self.center[1])]
		
		npos = [0,0]
		npos[0] = ((math.cos(math.radians(-rot))*pos[0]) - (math.sin(math.radians(-rot))*pos[1]))
		npos[1] = ((math.sin(math.radians(-rot))*pos[0]) + (math.cos(math.radians(-rot))*pos[1]))
		npos[0] *= (1.0*xs*self.xscale)
		npos[1] *= (1.0*ys*self.yscale)
		npos[0] += center[0]-self.center[0]
		npos[1] += center[1]-self.center[1]
		
		pos = npos[:]
		
		if xs * self.xscale != 1.0 or ys * self.yscale != 1.0:
			old = (img.get_width(), image.get_height())
			size = (int(img.get_width() * xs * self.xscale), int(img.get_height() * ys * self.yscale))
			img = pygame.transform.scale(img, size)
			pos = (pos[0] - ((img.get_width() - old[0]) / 2), pos[1] - ((img.get_height() - old[1]) / 2))
		
		if rot + self.rot != 0:
			old = (img.get_width(), img.get_height())
			img = pygame.transform.rotate(img, rot + self.rot)
			pos = ( pos[0] - ((img.get_width() - old[0]) / 2), pos[1] - ((img.get_height() - old[1]) / 2) )
		
		surf.blit(img, (x + pos[0] - self.offset[0], y + pos[1] - self.offset[1]))
	
	def reset(self):
		self.pos = self.orig_pos[:]
		self.rot = self.orig_rot
		self.xscale = self.orig_xscale
		self.yscale = self.orig_yscale
		self.image = self.orig_image
		self.center = self.orig_center
		self.offset = self.orig_offset[:]
		self.show = self.orig_show

class PartAnimationGroup():
	def __init__(self, set_, g, dom):
		self.g = g
		self.set = set_
		
		self.id = dom.getAttribute('id')
		set_.parts[self.id] = self
		self.pos = [int(x.strip()) for x in dom.getAttribute('pos').split(',')]
		
		try: self.rot = float(dom.getAttribute('rotation'))
		except: self.rot = 0.0
		try: t = float(dom.getAttribute('scale'))
		except: t = 1.0
		self.xscale, self.yscale = t, t
		try:
			self.xscale = float(dom.getAttribute("xscale"))
			self.yscale = float(dom.getAttribute("yscale"))
		except: pass
		try: self.show = int(dom.getAttribute("show")) != 0
		except: self.show = True
		
		self.orig_pos = self.pos[:]
		self.orig_rot = self.rot
		self.orig_xscale = self.xscale
		self.orig_yscale = self.yscale
		self.orig_show = self.show
		
		node = dom.firstChild
		self.children = []
		while node is not None:
			if node.localName == 'group': self.children.append(PartAnimationGroup(set_, g, node))
			elif node.localName == 'part': self.children.append(PartAnimationPart(set_, g, node))
			node = node.nextSibling
		
		if dom.getAttribute('center') == "":
			center = [0, 0]
			numcenters = 0
			
			for child in self.children:
				center[0] += child.center[0] + child.pos[0]
				center[1] += child.center[1] + child.pos[1]
				numcenters += 1
			
			center[0] /= numcenters
			center[1] /= numcenters
			self.center = center
		else: self.center = [int(x.strip()) for x in dom.getAttribute('center').split(',')]
	
	def render(self, surf, x, y, xs, ys, rot, center):
		if not self.show: return
		
		pos = [(self.pos[0] - center[0] + self.center[0]), (self.pos[1] - center[1] + self.center[1])]
		
		npos = [0, 0]
		npos[0] = ((math.cos(math.radians(-rot)) * pos[0]) - (math.sin(math.radians(-rot)) * pos[1]))
		npos[1] = ((math.sin(math.radians(-rot)) * pos[0]) + (math.cos(math.radians(-rot)) * pos[1]))
		
		npos[0] += center[0] - self.center[0]
		npos[1] += center[1] - self.center[1]
		
		center = self.center[:]
		center[0] += (npos[0] - pos[0]) / 2.0
		center[1] += (npos[1] - pos[1]) / 2.0
		
		pos = npos[:]
		
		for child in self.children: child.render(surf, x + pos[0], y + pos[1], xs * self.xscale, ys * self.yscale, rot + self.rot, center)
	
	def reset(self):
		self.pos = self.orig_pos[:]
		self.rot = self.orig_rot
		self.xscale = self.orig_xscale
		self.yscale = self.orig_yscale
		self.show = self.orig_show
		for child in self.children: child.reset()

class PartAnimation():
	def __init__(self, set_, dom):
		self.set = set_

		self.frame_list = []
		self.wait = 0
		self.currframe = 0
		self.tweens = []

		self.loopreset = dom.getAttribute('loopreset') != ""

		currframe = dom.firstChild
		while currframe is not None:
			if currframe.localName == 'frame':
				delay = int(currframe.getAttribute('time'))
				cmds = []
				
				currcmd = currframe.firstChild
				while currcmd is not None:
					if currcmd.localName == 'rotate': cmds.append([1, currcmd.getAttribute('id'), int(currcmd.getAttribute('degrees'))])
					
					elif currcmd.localName == 'move':
						delta = [float(x.strip()) for x in currcmd.getAttribute('delta').split(',')]
						cmds.append([2, currcmd.getAttribute('id'), delta])
					
					elif currcmd.localName == 'set': cmds.append([3, currcmd.getAttribute('id'), currcmd.getAttribute('to')])
					
					elif currcmd.localName == 'scale':
						x, y = None, None
						
						try: x = float(currcmd.getAttribute('scale'))
						except: pass
						
						y = x
						try: x = float(currcmd.getAttribute('xscale'))
						except: pass
						
						try: y = float(currcmd.getAttribute('yscale'))
						except: pass
						
						if x != None: cmds.append([4, currcmd.getAttribute('id'), x])
						if y != None: cmds.append([5, currcmd.getAttribute('id'), x])
					
					elif currcmd.localName == 'show':
						try: show = int(currcmd.getAttribute('show')) != 0
						except: show = True
						cmds.append([6, currcmd.getAttribute('id'), show])
					currcmd = currcmd.nextSibling
				self.frame_list.append([delay, cmds])
			currframe = currframe.nextSibling
	
	def start(self):
		self.currframe = -1
		self.wait = 0
		self.tweens = []
		self.update()
	
	def _process_frame(self, frame):
		self.tweens = []
		self.wait = frame[0]
		
		for cmd in frame[1]:
			part_id = cmd[1]
			if cmd[0] == 1:
				step = (cmd[2] * 1.0) / self.wait
				self.tweens.append([cmd[0], cmd[1], step, cmd[2] + self.set.parts[part_id].rot])
			
			elif cmd[0] == 2:
				t = [float(x) for x in self.set.parts[part_id].pos]
				step = [cmd[2][0] / self.wait, cmd[2][1] / self.wait]
				final = [cmd[2][0] + int(t[0]), cmd[2][1] + int(t[1])]
				self.tweens.append([2, cmd[1], step, t, final])
			
			elif cmd[0] == 3:
				img = self.set.part_images[cmd[2]]
				self.set.parts[cmd[1]].image = img[0]
				self.set.parts[cmd[1]].center = img[1]
				self.set.parts[cmd[1]].offset = img[2]
			
			elif cmd[0] == 4:
				self = (cmd[2] - self.set.parts[cmd[1]].xscale) / self.wait
				self.tweens.append([4, cmd[1], step, cmd[2]])
			
			elif cmd[0] == 5:
				self = (cmd[2] - self.set.parts[cmd[1]].yscale) / self.wait
				self.tweens.append([5, cmd[1], step, cmd[2]])
			
			elif cmd[0] == 6: self.set.parts[cmd[1]].show = cmd[2]
	
	def _update_tween(self, tween):
		if tween[0] == 1: self.set.parts[tween[1]].rot += tween[2]
		elif tween[0] == 2:
			tween[3][0] += tween[2][0]
			tween[3][1] += tween[2][1]
			pos = [int(x) for x in tween[3]]
			self.set.parts[tween[1]].pos = pos
		elif tween[0] == 4: self.set.parts[tween[1]].xscale += tween[2]
		elif tween[0] == 5: self.set.parts[tween[1]].yscale += tween[2]
	
	def _finish_tween(self, tween):
		if tween[0] == 1: self.set.parts[tween[1]].rot = tween[3]
		elif tween[0] == 2: self.set.parts[tween[1]].pos = tween[4][:]
		elif tween[0] == 4: self.set.parts[tween[1]].xscale = tween[3]
		elif tween[0] == 5: self.set.parts[tween[1]].yscale = tween[3]
	
	def update(self):
		if self.wait == 0:
			for tween in self.tweens: self._finish_tween(tween)
			self.currframe += 1
			
			if self.currframe == len(self.frame_list):
				self.currframe = 0
				if self.loopreset: self.set.layout.reset()
			self._process_frame(self.frame_list[self.currframe])
		
		for tween in self.tweens: self._update_tween(tween)
		self.wait -= 1

class PartAnimationSet():
	def __init__(self, g, anim_file, peltdir=True):
		self.g = g
		
		images = {}
		self.part_images = {}
		self.parts = {}
		self.layout = None
		
		anim_dom = data.load_xml(anim_file, peltdir).documentElement 
		
		for image in anim_dom.getElementsByTagName('image'):
			f = image.getAttribute('from')
			id = image.getAttribute('id')
			surf = data.load_image(f, peltdir)
			surf.convert_alpha()
			images[id] = surf
		
		for part_image in anim_dom.getElementsByTagName('part_image'):
			image = images[part_image.getAttribute('from')]
			coord = [int(x.strip()) for x in part_image.getAttribute('coord').split(',')]
			
			if part_image.getAttribute('center') == "":
				surf = pygame.Surface((coord[2], coord[3]), pygame.SRCALPHA)
				surf.blit(image, (0, 0), coord)
				pos = [0, 0]
			
			else:
				center = [int(x.strip()) for x in part_image.getAttribute('center').split(',')]
				center_diff = ((coord[2] / 2) - center[0], (coord[3] / 2) - center[1])
				size = (coord[2] + abs(center_diff[0]), coord[3] + abs(center_diff[1]))
				pos = [max(0, center_diff[0]), max(0, center_diff[1])]
				surf = pygame.Surface(size, SRCALPHA)
				surf.blit(image, pos, coord)
			
			if part_image.getAttribute('origin') != "":
				origin = [int(x.strip()) for x in part_image.getAttribute('origin').split(',')]
				pos[0] += origin[0]
				pos[1] += origin[1]
			
			center = (surf.get_width() / 2, surf.get_height() / 2)
			self.part_images[part_image.getAttribute('id')] = (surf, center, pos)
		
		self.layout = PartAnimationGroup(self, g, anim_dom.getElementsByTagName('layout')[0])
		self.curr_animation = None
		self.animations = {}
		for anim in anim_dom.getElementsByTagName('anim'): self.animations[anim.getAttribute('id')] = PartAnimation(self, anim)
		for anim in anim_dom.getElementsByTagName('anim'): self.animations[anim.getAttribute('id')] = PartAnimation(self, anim)
	
	def set_animation(self, anim):
		self.layout.reset()
		self.curr_animation = self.animations[anim]
		self.curr_animation.start()
	
	def update(self, surf, x, y):
		if self.curr_animation is not None: self.curr_animation.update()
		self.layout.render(surf, x, y, 1, 1, 0, self.layout.center)
