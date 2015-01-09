import pstats
p = pstats.Stats('peltProfile.out')
p.strip_dirs().sort_stats('cumulative').print_stats()
