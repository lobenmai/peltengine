import sys, traceback, os

try: from pelt import error, settings
except ImportError: sys.exit("PELT engine was not found!")

try:
	import console
	console.clear()
except ImportError: pass

try:
	import pelt
	from pelt import main, animation_view

	settings.steamAPI = False #disable the Steam API for now

	#try: import PySteamAPI as steam
	#except ImportError: settings.steamAPI = False
	
	if settings.steamAPI:
		try:
			steam.init()
			settings.name = steam.getName()
		except steam.error as e:
			print e
			settings.steamAPI = False
	if "animview" in sys.argv[1:]: animation_view.main(sys.argv[2:])
	if "nosound" in sys.argv[1:]:
		settings.option_music = False
		settings.option_sound = False

	if "profile" in sys.argv[1:]:
		import cProfile
		cProfile.run('main.main()', 'peltProfile.out')
	else: main.main()
	if settings.steamAPI: steam.shutdown()

except error.UserQuit: pass
except: traceback.print_exc()
