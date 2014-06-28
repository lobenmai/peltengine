#PELT Configuration
#Created December 4, 2013 at 15:22

ios = False

try: import pygame
except ImportError: ios = True
import pickle, os, sys

args = sys.argv[1:]

r = os.path.dirname(__file__)

if hasattr(sys,"frozen") and sys.frozen in ("windows_exe", "console_exe"):
	r = os.path.dirname(os.path.abspath(sys.executable))

rootdir = os.path.dirname(r)

save_name = "save.peltsav"
data_path = "data"
resource_path = "resources"

resourcedir = os.path.join(rootdir, resource_path)
langdir = os.path.join(resourcedir, 'langs')
fontdir = os.path.join(resourcedir, 'fonts')
mapdir = os.path.join(resourcedir, 'levels')
optionspath = os.path.join(resourcedir, 'options.pyp')
musicdir = os.path.join(resourcedir, 'music')

devplayer = False
annoy = False
gui = True
color = True
instmsg = False

scrollspeed = 'Medium'
scroll = 0.03
lang = 'en'

if len(args) > 0:
	if "nostory" in args: loc = 'p1MainRoom'
	if "betatester" in args: devplayer = True
	if "annoy" in args: annoy = True
	if "nocolor" in args: color = False
	if "instmsg" in args: instmsg = True

final_screen_x = 1024
final_screen_y = 768
final_screen = (final_screen_x, final_screen_y)

screen_scale = 2 #scale factor of the screen before displaying
screen_x = final_screen_x / screen_scale
screen_y = final_screen_y / screen_scale
framerate = 30 #framerate to keep

if not ios:
	key_escape = pygame.K_ESCAPE
	key_up = pygame.K_UP
	key_down = pygame.K_DOWN
	key_left = pygame.K_LEFT
	key_right = pygame.K_RIGHT
	key_accept = pygame.K_x
	key_debug = pygame.K_p
	key_cancel = pygame.K_z
	key_dbg_save = pygame.K_j
	key_dbg_load = pygame.K_k
	key_menu = pygame.K_i

option_music = False
option_sound = True
parallax = True
parallax_scale = 30

MOUSE_BUTTON_COUNT = 5 + 1

TILE_NORMAL = 0
TILE_SOLID = 1
TILE_WATER = 2
TILE_WARP = 3
TILE_GRASS = 5
TILE_DOUBLEGRASS = 8

def save():
	settingsdict = {
		'lang': lang,
		'music': option_music,
		'sound': option_sound,
		'parallax': parallax,
		'prlx_scale': parallax_scale
	}
	pickle.dump(settingsdict, file(optionspath, 'wb'))

def load(gi):
	global settingsdict, lang, option_music, option_sound, parallax, parallax_scale, g
	try:
		s = pickle.load(file(optionspath, 'rb'))
		lang = s['lang']
		option_music = s['music']
		option_sound = s['sound']
		parallax = s['parallax']
		parallax_scale = s['prlx_scale']
	except IOError: pass
	g = gi

def get_prlx(offset, prlx_local_scale):
	if parallax: return ((offset - g.mouse_pos[0] / parallax_scale * prlx_local_scale) , (5 - g.mouse_pos[1] / parallax_scale * prlx_local_scale)) #  and 0 < g.mouse_pos[0] < final_screen_x / screen_scale and 0 < g.mouse_pos[1] < final_screen_y / screen_scale:
	else: return (0, 0)
