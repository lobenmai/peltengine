import re

s = file('dialog_font.xml').readlines()
r = re.compile("\s<letter name=\"([^\"]+)\" coord=\"([0-9]+),([0-9]+)\" size=\"([0-9]+)\" />")


for l in s:
	m = r.search(l)
	if not m: print l
	else: print '	<letter name="%s" coord="%d,%d" size="%d" />' %(
		m.groups()[0],
		int(m.groups()[1])*2,
		int(m.groups()[2])*2,
		int(m.groups()[3])*2)

