#In need of remodeling
#Created April 28, 2014 at 22:28

#miscellaneous helper functions
from xml.dom.minidom import parse
import os

import settings

if not settings.ios:
	import pygame #import everything pygame-related
	from pygame.locals import *
else: pass

def get_node_text(node, strip_newlines=True): #get all the text from a node
	texts = []
	for n in node.childNodes: #loop through children
		if n.nodeType == n.TEXT_NODE: #if it's text
			texts.append(n.data) #store its value
	texts = "".join(texts) #combine all the text together
	if strip_newlines: #if we're supposed to remove newlines
		return texts.replace("\r", "").replace("\n", "") #do so
	return texts #return combined text

def get_xml_prop(root, name, strip_newlines=True): #get the text from a "property" node with the given name
	try:
		return get_node_text(get_node(root, name), strip_newlines)
	except:
		return None

def get_node(root, name): #find a node with a given name
	return root.getElementsByTagName(name)[0]

def get_path(path, with_data=True): #convert a path to one appropriate for the host with the data directory
	path = path.replace("\\", "/") #convert backslashes to forward slashes
	if with_data: #if we're prepending the data directory
		ret = get_path(settings.data_path, False) #get it
	else: #if we aren't
		ret = "" #start with a blank string
	for part in path.split("/"): #loop through path components
		ret = os.path.join(ret, part) #join them together
	return ret #return finished product

def get_resource(path, with_data=True): #convert a path to one appropriate for the host with the data directory
	path = path.replace("\\", "/") #convert backslashes to forward slashes
	if with_data: #if we're prepending the data directory
		ret = get_resource(settings.resource_path, False) #get it
	else: #if we aren't
		ret = "" #start with a blank string
	for part in path.split("/"): #loop through path components
		ret = os.path.join(ret, part) #join them together
	return ret #return finished product

def load_image(path, peltdir=True): #load an image
	if peltdir: fullpath = get_resource(path)
	else: fullpath = get_path(path)
	try: return pygame.image.load(fullpath)
	except IOError: pygame.image.load(get_path(path))

def load_xml(path, peltdir=True): #load xml data
	if peltdir: fullpath = get_resource(path)
	else: fullpath = get_path(path)
	try: return parse(fullpath)
	except IOError: parse(get_path(path))
