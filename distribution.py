#!/usr/bin/env python

# vim: set noexpandtab:
# --
# A recent battle with vim and a Go program finally settled this for me.
# Tabs for indent, spaces for formatting. If you change your shiftwidth and
# tabstop to different values and your code looks ugly, say aloud: tabs
# for indent, spaces for formatting.

"""
To generate graphs directly in the (ASCII-based) terminal. If you type:
  [long | list | of | commands | sort | uniq -c | sort -rn]
in the terminal, then you could replace the end bit of the command:
  [| sort | uniq -c | sort -rn]
with
  [| distribution]
and very likely be happier with what you see.
"""

import math,os,re,sys,time

class Histogram(object):
	"""
	Takes the tokenDict built in the InputReader class and goes
	through it, printing a histogram for each of the highest height
	entries
	"""
	def __init__(self):
		pass

	def write_hist(self, s, tokenDict):
		maxTokenLen = 0
		outputDict = {}

		numItems = 0
		maxVal = 0
		for k in sorted(tokenDict, key=tokenDict.get, reverse=True):
			if k:
				outputDict[k] = tokenDict[k]
				if len(k) > maxTokenLen: maxTokenLen = len(k)
				if outputDict[k] > maxVal: maxVal = outputDict[k]
				numItems += 1
				if numItems >= s.height:
					break

		# grab log of maxVal in case logarithmic graphs
		if s.logarithmic: maxLog = math.log(maxVal)

		# we always output a single histogram char at the end, so
		# we output one less than actual number here
		histWidth = s.width - maxTokenLen - 2 - 6 - 9

		s.endTime = int(time.time() * 1000)
		totalMillis = s.endTime - s.startTime
		if s.verbose == True:
			sys.stderr.write("tokens/lines examined: %d" % (s.totalObjects) + "\n")
			sys.stderr.write(" tokens/lines matched: %d" % (s.totalValues) + "\n")
			sys.stderr.write("       histogram keys: %d" % (len(tokenDict)) + "\n")
			sys.stderr.write("              runtime: %dms" % (totalMillis) + "\n")

		for k in sorted(outputDict, key=outputDict.get, reverse=True):
			if k:
				sys.stdout.write(s.keyColour)
				sys.stdout.write(k.rjust(maxTokenLen) + " ")
				sys.stdout.write(s.ctColour)
				sys.stdout.write("%5s " % outputDict[k])
				pct = "(%2.2f%%)" % (outputDict[k] * 1.0 / s.totalObjects * 100)
				sys.stdout.write(s.pctColour)
				sys.stdout.write("%8s " % pct)
				sys.stdout.write(s.graphColour)

				if s.logarithmic:
					sys.stdout.write(s.histogramChar[0] * (int(math.log(outputDict[k]) / maxLog * histWidth) - 1))
				else:
					sys.stdout.write(s.histogramChar[0] * (int(outputDict[k] * 1.0 / maxVal * histWidth) - 1))

				if len(s.histogramChar) > 1:
					sys.stdout.write(s.histogramChar[1])
				else:
					sys.stdout.write(s.histogramChar[0])
				sys.stdout.write(s.regularColour)
				sys.stdout.write("\n")

class InputReader(object):
	"""
	Reads stdin, parses it into a dictionary of key and value is number
	of appearances of that key in the input - this will also prune the
	token frequency dict on after a certain number of insertions to
	prevent OOME on large datasets
	"""
	def __init__(self):
		self.tokenDict = {}

	def prune_keys(self, s):
		newDict = {}
		numKeysTransferred = 0
		for k in sorted(self.tokenDict, key=self.tokenDict.get, reverse=True):
			if k:
				newDict[k] = self.tokenDict[k]
				numKeysTransferred += 1
				if numKeysTransferred > s.maxKeys:
					break
		self.tokenDict = newDict

	def tokenize_input(self, s):
		pruneObjects = 0

		# how to split the input...
		reSplitExp = r'\s+'
		if s.tokenize == 'white':
			reSplitExp = r'\s+'
		elif s.tokenize == 'word':
			reSplitExp = r'\W'
		elif s.tokenize != '':
			reSplitExp = s.tokenize

		# how to match (filter) the input...
		if   s.matchRegexp == 'word': s.matchRegexp = r'^[A-Z,a-z]+$'
		elif s.matchRegexp == 'num':  s.matchRegexp = r'^\d+$'

		# docs say these are cached, but i got about 2x speed boost
		# from doing the compile
		pt = re.compile(reSplitExp)
		pm = re.compile(s.matchRegexp)

		for line in sys.stdin:
			for token in pt.split(line):
				if pm.match(token):
					s.totalValues += 1
					pruneObjects += 1
					# prune the hash if it gets too large
					if pruneObjects > s.keyPruneInterval:
						self.prune_keys(s)
						pruneObjects = 0
					if token in self.tokenDict:
						self.tokenDict[token] += 1
					else:
						self.tokenDict[token] = 1

				# this is a count of total tokens considered
				s.totalObjects += 1


class Settings(object):
	def __init__(self):
		self.totalMillis = 0
		self.startTime = int(time.time() * 1000)
		self.endTime = 0
		self.widthArg = 0
		self.heightArg = 0
		self.width = 80
		self.height = 15
		self.histogramChar = '|'
		self.colourisedOutput = False
		self.logarithmic = False
		self.numOnly = ''
		self.verbose = False
		self.graphValues = ''
		self.size = ''
		self.tokenize = ''
		self.matchRegexp = '.'
		# for colourised output
		self.colourPalette = '0,0,32,35,34'
		self.regularColour = ""
		self.keyColour = ""
		self.ctColour = ""
		self.pctColour = ""
		self.graphColour = ""
		# for stats
		self.totalObjects = 0
		self.totalValues = 0
		# every keyPruneInterval keys, prune the hash to maxKeys top keys
		self.keyPruneInterval = 120000
		self.maxKeys = 5000

		# manual argument parsing easier than getopts IMO
		for arg in sys.argv:
			if arg == '-h':
				doUsage(self)
				sys.exit(0)
			elif arg in ("-c", "--color", "--colour"):
				self.colourisedOutput = True
			elif arg in ("-g", "--graph"):
				# can pass --graph without option, will default to value/key ordering
				# since Unix prefers that for piping-to-sort reasons
				self.graphValues = 'vk'
			elif arg in ("-l", "--logarithmic"):
				self.logarithmic = True
			elif arg in ("-n", "--numonly"):
				self.numOnly = 'abs'
			elif arg in ("-v", "--verbose"):
				self.verbose = True
			else:
				argList = arg.split('=')
				if argList[0] in ("-w", "--width"):
					self.widthArg = int(argList[1])
				elif argList[0] in ("-h", "--height"):
					self.heightArg = int(argList[1])
				elif argList[0] in ("-k", "--keys"):
					self.maxKeys = int(argList[1])
				elif argList[0] in ("-c", "--char"):
					self.histogramChar = argList[1]
				elif argList[0] in ("-g", "--graph"):
					self.graphValues = argList[1]
				elif argList[0] in ("-n", "--numonly"):
					self.numOnly = argList[1]
				elif argList[0] in ("-p", "--palette"):
					self.colourPalette = argList[1]
					self.colourisedOutput = True
				elif argList[0] in ("-s", "--size"):
					self.size = argList[1]
				elif argList[0] in ("-t", "--tokenize"):
					self.tokenize = argList[1]
				elif argList[0] in ("-m", "--match"):
					self.matchRegexp = argList[1]

		# first, size, which might be further overridden by width/height later
		if self.size in ("full", "fl", "f"):
			# tput will tell us the term width/height even if input is stdin
			self.width, self.height = os.popen('echo "`tput cols` `tput lines`"', 'r').read().split()
			# convert to numerics from string
			self.width = int(self.width)
			self.height = int(self.height) - 3
			# need room for the verbosity output
			if self.verbose == True: self.height -= 5
			# in case tput went all bad, ensure some minimum size
			if self.width < 40: self.width = 40
			if self.height < 10: self.height = 10
		elif self.size in ("small", "sm", "s"):
			self.width  = 60
			self.height = 10
		elif self.size in ("medium", "med", "m"):
			self.width  = 100
			self.height = 20
		elif self.size in ("large", "lg", "l"):
			self.width  = 140
			self.height = 35

		# override variables if they were explicitly given
		if self.widthArg  != 0: self.width  = self.widthArg
		if self.heightArg != 0: self.height = self.heightArg

		# maxKeys should be at least a few thousand greater than height to reduce odds
		# of throwing away high-count values that appear sparingly in the data
		if self.maxKeys < self.height + 3000:
			self.maxKeys = self.height + 3000
			if self.verbose: sys.stderr.write("Updated maxKeys to %d (height + 3000)\n" % self.maxKeys)

		# colour palette
		if self.colourisedOutput == True:
			cl = self.colourPalette.split(',')
			cl = [chr(27) + '[' + e + 'm' for e in cl]
			(self.regularColour, self.keyColour, self.ctColour, self.pctColour, self.graphColour) = cl


def doUsage(s):
	print ""
	print "usage: <commandWithOutput> | %s" % (scriptName)
	print "         [--rcfile=<rcFile>]"
	print "         [--size={sm|med|lg|full} | --width=<width> --height=<height>]"
	print "         [--color] [--palette=r,k,c,p,g]"
	print "         [--tokenize=<tokenChar>]"
	print "         [--graph[=[kv|vk]] [--numonly[=mon|abs]]"
	print "         [--char=<barChars>|<substitutionString>]"
	print "         [--help] [--verbose]"
	print "  --keys=K       every %d values added, prune hash to K keys (default 5000)\n" % (s.keyPruneInterval)
	print "  --char=C       character(s) to use for histogram character, some substitutions follow:"
	print "        hl       Use 1/3-width unicode partial lines to simulate 3x actual terminal width"
	print "        pb       Use 1/8-width unicode partial blocks to simulate 8x actual terminal width"
	print "  --color        colourise the output"
	print "  --graph[=G]    input is already key/value pairs. vk is default:"
	print "        kv       input is ordered key then value"
	print "        vk       input is ordered value then key"
	print "  --height=N     height of histogram, headers non-inclusive, overrides --size"
	print "  --help         get help"
	print "  --logarithmic  logarithmic graph"
	print "  --match=RE     only match lines (or tokens) that match this regexp, some substitutions follow:"
	print "        word     ^[A-Z,a-z]+\$ - tokens/lines must be entirely alphabetic"
	print "        num      ^\\d+\$        - tokens/lines must be entirely numeric"
	print "  --numonly[=N]  input is numerics, simply graph values without labels"
	print "        abs      input is absolute values (default)"
	print "        mon      input monotonically-increasing, graph differences (of 2nd and later values)"
	print "  --palette=P    comma-separated list of ANSI colour values for portions of the output"
	print "                 in this order: regular, key, count, percent, graph. implies --color."
	print "  --rcfile=F     use this rcfile instead of \$HOME/.distributionrc - must be first argument!"
	print "  --size=S       size of histogram, can abbreviate to single character, overridden by --width/--height"
	print "        small    40x10"
	print "        medium   80x20"
	print "        large    120x30"
	print "        full     terminal width x terminal height (approximately)"
	print "  --tokenize=RE  split input on regexp RE and make histogram of all resulting tokens"
	print "        word     [^\\w] - split on non-word characters like colons, brackets, commas, etc"
	print "        white    \\s    - split on whitespace"
	print "  --width=N      width of the histogram report, N characters, overrides --size"
	print "  --verbose      be verbose"
	print ""
	print "You can use single-characters options, like so: -h=25 -w=20 -v. You must still include the ="
	print ""
	print "Samples:"
	print "  du -sb /etc/* | %s --palette=0,37,34,33,32 --graph" % (scriptName)
	print "  du -sk /etc/* | awk '{print \$2\" \"\$1}' | %s --graph=kv" % (scriptName)
	print "  zcat /var/log/syslog*gz | %s --char=o --tokenize=white" % (scriptName)
	print "  zcat /var/log/syslog*gz | awk '{print \$5}'  | %s --t=word --m-word --h=15 --c=/" % (scriptName)
	print "  zcat /var/log/syslog*gz | cut -c 1-9        | %s --width=60 --height=10 --char=em" % (scriptName)
	print "  find /etc -type f       | cut -c 6-         | %s --tokenize=/ --w=90 --h=35 --c=dt" % (scriptName)
	print "  cat /usr/share/dict/words | awk '{print length(\$1)}' | %s --c=* --w=50 --h=10 | sort -n" % (scriptName)
	print ""

# simple argument parsing and call top-level routines
def main(argv):
	s = Settings()
	i = InputReader()
	i.tokenize_input(s)
	h = Histogram()
	h.write_hist(s, i.tokenDict)

scriptName = sys.argv[0]
if __name__ == "__main__":
	main(sys.argv[1:])

