import sys, traceback

try: from pelt import error, settings
except ImportError: sys.exit("PELT engine was not found!")

try:
	import console
	console.clear()
except ImportError: pass

try:
	import pelt
	from pelt import main, animation_view
	#import PySteamAPI as steam
	
	steamAPI = True
	
	#try: steam.init()
	#except Steam.InitError as e:
	#	print e
	#	steamAPI = False
	if "animview" in sys.argv[1:]: animation_view.main(sys.argv[2:])
	if "nosound" in sys.argv[1:]:
		settings.option_music = False
		settings.option_sound = False
	else: main.main()
	#if steamAPI: steam.shutdown()

except error.UserQuit: pass
except: traceback.print_exc()
