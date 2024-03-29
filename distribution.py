#! /usr/bin/env python3

"""
Generate Graphs Directly in the (ASCII- or Unicode-based) Terminal

If you find yourself typing:
  [long | list | of | commands | sort | uniq -c | sort -rn]

Replace:
  [| sort | uniq -c | sort -rn]

With:
  [| distribution]

Then bask in the glory of your new-found data visualization. There are other
use cases as well.
"""

import math
import os
import re
import shutil
import sys
import time
from pathlib import Path


class Histogram:
    """
    Takes the tokenDict built in the InputReader class and goes through it,
    printing a histogram for each of the highest height entries
    """

    def __init__(self):
        pass

    def histogram_bar(self, s, histWidth, maxVal, barVal):
        # given a value and max, return string for histogram bar of the proper
        # number of characters, including unicode partial-width characters
        returnBar = ""

        # first case is partial-width chars
        if s.charWidth < 1:
            zeroChar = s.graphChars[-1]
        elif len(s.histogramChar) > 1 and not s.unicodeMode:
            zeroChar = s.histogramChar[0]
            oneChar = s.histogramChar[1]
        else:
            zeroChar = s.histogramChar
            oneChar = s.histogramChar

        # write out the full-width integer portion of the histogram
        if s.logarithmic:
            maxLog = math.log(maxVal)
            barLog = math.log(barVal) if barVal > 0 else 0
            intWidth = int(barLog / maxLog * histWidth)
            remainderWidth = (barLog / maxLog * histWidth) - intWidth
        else:
            intWidth = int(barVal * 1.0 / maxVal * histWidth)
            remainderWidth = (barVal * 1.0 / maxVal * histWidth) - intWidth

        # write the zeroeth character intWidth times...
        returnBar += zeroChar * intWidth

        # we always have at least one remaining char for histogram - if
        # we have full-width chars, then just print it, otherwise do a
        # calculation of how much remainder we need to print
        #
        # FIXME: The remainder partial char printed does not take into
        # account logarithmic scale (can humans notice?).
        if s.charWidth == 1:
            returnBar += oneChar
        elif s.charWidth < 1:
            # this is high-resolution, so figure out what remainder we
            # have to represent
            if remainderWidth > s.charWidth:
                whichChar = int(remainderWidth / s.charWidth)
                returnBar += s.graphChars[whichChar]

        return returnBar

    def write_hist(self, s, tokenDict):
        maxTokenLen = 0
        outputDict = {}

        numItems = 0
        maxVal = 0
        s.totalValues = int(s.totalValues)

        # given a dict, create a comparison tuple that sorts first by the value of a key,
        # then by the key itself in case of a tie. this allows us to create deterministic sorts
        # when we have multiple entries in our histogram with the same frequency.
        def value_key_compare(dict):
            return lambda key: (dict.get(key), key)

        for k in sorted(tokenDict, key=value_key_compare(tokenDict), reverse=True):
            # can't remember what feature "if k:" adds - i think there's an
            # off-by-one death the script sometimes suffers without it.
            if k:
                outputDict[k] = tokenDict[k]
                if len(str(k)) > maxTokenLen:
                    maxTokenLen = len(str(k))
                if outputDict[k] > maxVal:
                    maxVal = outputDict[k]
                numItems += 1
                if numItems >= s.height:
                    break

        s.endTime = int(time.time() * 1000)
        totalMillis = s.endTime - s.startTime
        if s.verbose:
            sys.stderr.write(f"tokens/lines examined: {s.totalObjects:,d}\n")
            sys.stderr.write(f" tokens/lines matched: {s.totalValues:,d}\n")
            sys.stderr.write(f"       histogram keys: {len(tokenDict):,d}\n")
            sys.stderr.write(f"              runtime: {totalMillis:,.2f}ms\n")

        # the first entry will determine these values
        maxValueWidth = 0
        maxPctWidth = 0
        sortedOutput = sorted(
            outputDict, key=value_key_compare(outputDict), reverse=True
        )
        for i in range(0, len(sortedOutput)):
            k = sortedOutput[i]
            # can't remember what feature "if k:" adds - i think there's an
            # off-by-one death the script sometimes suffers without it.
            if k:
                if maxValueWidth == 0:
                    testString = f"{outputDict[k]}"
                    maxValueWidth = len(testString)
                    testString = f"({outputDict[k] * 1.0 / s.totalValues * 100:2.2f}%)"
                    maxPctWidth = len(testString)

                    # we always output a single histogram char at the end, so
                    # we output one less than actual number here
                    histWidth = (
                        s.width
                        - (maxTokenLen + 1)
                        - (maxValueWidth + 1)
                        - (maxPctWidth + 1)
                        - 1
                    )

                    # output a header
                    sys.stderr.write("Key".rjust(maxTokenLen) + "|")
                    sys.stderr.write("Ct".ljust(maxValueWidth) + " ")
                    sys.stderr.write("(Pct)".ljust(maxPctWidth) + " ")
                    sys.stderr.write("Histogram")

                    # get ready for the output, but sorting gets hosed if we print the
                    # colour code before the key, so put it on the line before
                    sys.stderr.write(s.keyColour)
                    sys.stderr.write("\n")

                sys.stdout.write(str(k).rjust(maxTokenLen))
                sys.stdout.write(s.regularColour)
                sys.stdout.write("|")
                sys.stdout.write(s.ctColour)

                outVal = f"{outputDict[k]}"
                sys.stdout.write(outVal.rjust(maxValueWidth) + " ")

                pct = f"({outputDict[k] * 1.0 / s.totalValues * 100:2.2f}%)"
                sys.stdout.write(s.pctColour)
                sys.stdout.write(pct.rjust(maxPctWidth) + " ")

                sys.stdout.write(s.graphColour)
                sys.stdout.write(
                    self.histogram_bar(s, histWidth, maxVal, outputDict[k])
                )

                if i == len(sortedOutput) - 1:
                    # put the terminal back into a normal-colour mode on last entry
                    sys.stdout.write(s.regularColour)
                else:
                    # we do these antics of printing $keyColour on the line before
                    # the key so that piping output to sort will work
                    sys.stdout.write(s.keyColour)
                sys.stdout.write("\n")


class InputReader:
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
        s.numPrunes += 1

    def tokenize_input(self, s):
        # how to split the input... typically we split on whitespace or
        # word boundaries, but the user can specify any regexp
        if s.tokenize == "white":
            s.tokenize = r"\s+"
        elif s.tokenize == "word":
            s.tokenize = r"\W"

        # how to match (filter) the input... typically we want either
        # all-alpha or all-numeric, but again, user can specify
        if s.matchRegexp == "word":
            s.matchRegexp = r"^[A-Z,a-z]+$"
        elif s.matchRegexp in ["num", "number"]:
            s.matchRegexp = r"^\d+$"

        # docs say these are cached, but i got about 2x speed boost
        # from doing the compile
        pt = re.compile(s.tokenize)
        pm = re.compile(s.matchRegexp)

        nextStat = time.time() + s.statInterval

        pruneObjects = 0
        for line in sys.stdin:
            line = line.rstrip("\n")
            if s.tokenize:
                for token in pt.split(line):
                    # user desires to break line into tokens...
                    s.totalObjects += 1
                    if pm.match(token):
                        s.totalValues += 1
                        pruneObjects += 1
                        if token in self.tokenDict:
                            self.tokenDict[token] += 1
                        else:
                            self.tokenDict[token] = 1
            else:
                # user just wants every line to be a token
                s.totalObjects += 1
                if pm.match(line):
                    s.totalValues += 1
                    pruneObjects += 1
                    if line in self.tokenDict:
                        self.tokenDict[line] += 1
                    else:
                        self.tokenDict[line] = 1

            # prune the hash if it gets too large
            if pruneObjects >= s.keyPruneInterval:
                self.prune_keys(s)
                pruneObjects = 0

            if s.verbose and time.time() > nextStat:
                sys.stderr.write(
                    f"tokens/lines examined: {s.totalObjects:,d} ; hash prunes: {s.numPrunes:,d}..."
                    + chr(13)
                )
                nextStat = time.time() + s.statInterval

    def read_pretallied_tokens(self, s):
        # the input is already just a series of keys with the frequency of the
        # keys precomputed, as in "du -sb" - vk means the number is first, key
        # second. kv means key first, number second
        vk = re.compile(r"^\s*(\d+)\s+(.+)$")
        kv = re.compile(r"^(.+?)\s+(\d+)$")
        if s.graphValues == "vk":
            for line in sys.stdin:
                m = vk.match(line)
                try:
                    if m.group(2) in self.tokenDict:
                        self.tokenDict[m.group(2)] += int(m.group(1))
                    else:
                        self.tokenDict[m.group(2)] = int(m.group(1))
                    s.totalValues += int(m.group(1))
                    s.totalObjects += 1
                except Exception:
                    sys.stderr.write(
                        f" E Input malformed+discarded (perhaps pass -g=kv?): {line}\n"
                    )
        elif s.graphValues == "kv":
            for line in sys.stdin:
                m = kv.match(line)
                try:
                    if m.group(1) in self.tokenDict:
                        self.tokenDict[m.group(1)] += int(m.group(2))
                    else:
                        self.tokenDict[m.group(1)] = int(m.group(2))
                    s.totalValues += int(m.group(2))
                    s.totalObjects += 1
                except Exception:
                    sys.stderr.write(
                        f" E Input malformed+discarded (perhaps pass -g=vk?): {line}\n"
                    )

    def read_numerics(self, s, h):
        # in this special mode, we print out the histogram here instead
        # of later - because it's a far simpler histogram without all the
        # totals, percentages, etc of the real histogram. we're just
        # showing a graph of a series of numbers
        lastVal = 0
        maxVal = 0
        maxWidth = 0
        sumVal = 0
        outList = []
        for line in sys.stdin:
            try:
                line = float(line.rstrip())
            except Exception:
                line = lastVal

            graphVal = 0
            if s.numOnly == "mon":
                if s.totalObjects > 0:
                    graphVal = line - lastVal
                lastVal = line
            else:
                graphVal = line

            if graphVal > maxVal:
                maxVal = graphVal
                maxWidth = len(str(graphVal))

            sumVal += int(graphVal)

            if s.totalObjects > 0:
                outList.append(graphVal)
            s.totalObjects += 1

        # simple graphical output
        for k in outList:
            sys.stdout.write(s.keyColour)
            sys.stdout.write(str(int(k)).rjust(maxWidth))
            pct = f"({float(k) / float(sumVal) * 100:2.2f}%)"
            sys.stdout.write(s.pctColour)
            sys.stdout.write(pct.rjust(9) + " ")
            sys.stdout.write(s.graphColour)
            sys.stdout.write(
                h.histogram_bar(s, s.width - 11 - maxWidth, maxVal, k) + "\n"
            )
            sys.stdout.write(s.regularColour)


class Settings:
    def __init__(self):
        self.totalMillis = 0
        self.startTime = int(time.time() * 1000)
        self.endTime = 0
        self.widthArg = 0
        self.heightArg = 0
        self.width = 80
        self.height = 15
        self.histogramChar = "-"
        self.colourisedOutput = False
        self.logarithmic = False
        self.numOnly = "XXX"
        self.verbose = False
        self.graphValues = ""
        self.size = ""
        self.tokenize = ""
        # by default, everything matches (nothing is stripped out)
        self.matchRegexp = "."
        # how often to give status if verbose
        self.statInterval = 1.0
        self.numPrunes = 0
        # for colourised output
        self.colourPalette = "0,0,32,35,34"
        self.regularColour = ""
        self.keyColour = ""
        self.ctColour = ""
        self.pctColour = ""
        self.graphColour = ""
        # for stats
        self.totalObjects = 0
        self.totalValues = 0
        # every keyPruneInterval keys, prune the hash to maxKeys top keys
        self.keyPruneInterval = 1500000
        self.maxKeys = 5000
        # for advanced graphing
        self.unicodeMode = False
        self.charWidth = 1
        self.graphChars = []
        self.partialBlocks = ["▏", "▎", "▍", "▌", "▋", "▊", "▉", "█"]  # char=pb
        self.partialLines = ["╸", "╾", "━"]  # char=hl

        # rcfile grabbing/parsing if specified
        if len(sys.argv) > 1 and "--rcfile" in sys.argv[1]:
            rcFile = sys.argv[1].split("=")[1]
            rcFile = os.path.expanduser(rcFile)
        else:
            rcFile = os.environ.get("HOME") + "/.distributionrc"

        # parse opts from the rcFile if it exists
        try:
            with open(rcFile) as f:
                rcfileOptList = f.readlines()
                for rcOpt in rcfileOptList:
                    rcOpt = rcOpt.rstrip().split("#")[0]
                    if rcOpt:
                        sys.argv.insert(0, rcOpt)
        except OSError:
            # don't die or in fact do anything if rcfile doesn't exist
            pass

        # manual argument parsing easier than getopts IMO
        for arg in sys.argv:
            if arg in ("-h", "--help"):
                doUsage(self)
                sys.exit(0)
            elif arg in ("-c", "--color", "--colour"):
                self.colourisedOutput = True
            elif arg in ("-g", "--graph"):
                # can pass --graph without option, will default to value/key ordering
                # since Unix prefers that for piping-to-sort reasons
                self.graphValues = "vk"
            elif arg in ("-l", "--logarithmic"):
                self.logarithmic = True
            elif arg in ("-n", "--numonly"):
                self.numOnly = "abs"
            elif arg in ("-v", "--verbose"):
                self.verbose = True
            else:
                argList = arg.split("=", 1)
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
            self.width, self.height = shutil.get_terminal_size()
            # convert to numerics from string
            self.width = int(self.width)
            self.height = int(self.height) - 3
            # need room for the verbosity output
            if self.verbose:
                self.height -= 4
            # in case tput went all bad, ensure some minimum size
            self.width = max(self.width, 40)
            self.height = max(self.height, 10)
        elif self.size in ("small", "sm", "s"):
            self.width = 60
            self.height = 10
        elif self.size in ("medium", "med", "m"):
            self.width = 100
            self.height = 20
        elif self.size in ("large", "lg", "l"):
            self.width = 140
            self.height = 35

        # synonyms "monotonically-increasing": derivative, difference, delta, increasing
        # so all "d" "i" and "m" words will be graphing those differences
        if self.numOnly[0] in ("d", "i", "m"):
            self.numOnly = "mon"
        # synonyms "actual values": absolute, actual, number, normal, noop,
        # so all "a" and "n" words will graph straight up numbers
        if self.numOnly[0] in ("a", "n"):
            self.numOnly = "abs"

        # override variables if they were explicitly given
        if self.widthArg != 0:
            self.width = self.widthArg
        if self.heightArg != 0:
            self.height = self.heightArg

        # maxKeys should be at least a few thousand greater than height to reduce odds
        # of throwing away high-count values that appear sparingly in the data
        if self.maxKeys < self.height + 3000:
            self.maxKeys = self.height + 3000
            if self.verbose:
                sys.stderr.write(f"Updated maxKeys to {self.maxKeys} (height + 3000)\n")

        # colour palette
        if self.colourisedOutput:
            cl = self.colourPalette.split(",")
            # ANSI color code is ESC+[+NN+m where ESC=chr(27), [ and m are
            # the literal characters, and NN is a two-digit number, typically
            # from 31 to 37 - why is this knowledge still useful in 2014?
            cl = [chr(27) + "[" + e + "m" for e in cl]
            (
                self.regularColour,
                self.keyColour,
                self.ctColour,
                self.pctColour,
                self.graphColour,
            ) = cl

        # some useful ASCII-->utf-8 substitutions
        if self.histogramChar == "ba":
            self.unicodeMode = True
            self.histogramChar = "▬"
        elif self.histogramChar == "bl":
            self.unicodeMode = True
            self.histogramChar = "Ξ"
        elif self.histogramChar == "em":
            self.unicodeMode = True
            self.histogramChar = "—"
        elif self.histogramChar == "me":
            self.unicodeMode = True
            self.histogramChar = "⋯"
        elif self.histogramChar == "di":
            self.unicodeMode = True
            self.histogramChar = "♦"
        elif self.histogramChar == "dt":
            self.unicodeMode = True
            self.histogramChar = "•"
        elif self.histogramChar == "sq":
            self.unicodeMode = True
            self.histogramChar = "□"

        # sub-full character width graphing systems
        if self.histogramChar == "pb":
            self.charWidth = 0.125
            self.graphChars = self.partialBlocks
        elif self.histogramChar == "pl":
            self.charWidth = 0.3334
            self.graphChars = self.partialLines

        # detect whether the user has passed a multibyte unicode character directly as the histogram char
        if ord(self.histogramChar[0]) >= 128:
            self.unicodeMode = True


def doUsage(s):
    print(
        f"""
usage: <commandWithOutput> | {scriptName}
         [--rcfile=<rcFile>]
         [--size={{sm|med|lg|full}} | --width=<width> --height=<height>]
         [--color] [--palette=r,k,c,p,g]
         [--tokenize=<tokenChar>]
         [--graph[=[kv|vk]] [--numonly[=derivative,diff|abs,absolute,actual]]
         [--char=<barChars>|<substitutionString>]
         [--help] [--verbose]
  --keys=K       every {s.keyPruneInterval} values added, prune hash to K keys (default 5000)
  --char=C       character(s) to use for histogram character, some substitutions follow:
        pl       Use 1/3-width unicode partial lines to simulate 3x actual terminal width
        pb       Use 1/8-width unicode partial blocks to simulate 8x actual terminal width
        ba       (▬) Bar
        bl       (Ξ) Building
        em       (—) Emdash
        me       (⋯) Mid-Elipses
        di       (♦) Diamond
        dt       (•) Dot
        sq       (□) Square
  --color        colourise the output
  --graph[=G]    input is already key/value pairs. vk is default:
        kv       input is ordered key then value
        vk       input is ordered value then key
  --height=N     height of histogram, headers non-inclusive, overrides --size
  --help         get help
  --logarithmic  logarithmic graph
  --match=RE     only match lines (or tokens) that match this regexp, some substitutions follow:
        word     ^[A-Z,a-z]+\\$ - tokens/lines must be entirely alphabetic
        num      ^\\d+\\$        - tokens/lines must be entirely numeric
  --numonly[=N]  input is numerics, simply graph values without labels
        actual   input is just values (default - abs, absolute are synonymous to actual)
        diff     input monotonically-increasing, graph differences (of 2nd and later values)
  --palette=P    comma-separated list of ANSI colour values for portions of the output
                 in this order: regular, key, count, percent, graph. implies --color.
  --rcfile=F     use this rcfile instead of ~/.distributionrc - must be first argument!
  --size=S       size of histogram, can abbreviate to single character, overridden by --width/--height
        small    40x10
        medium   80x20
        large    120x30
        full     terminal width x terminal height (approximately)
  --tokenize=RE  split input on regexp RE and make histogram of all resulting tokens
        word     [^\\w] - split on non-word characters like colons, brackets, commas, etc
        white    \\s    - split on whitespace
  --width=N      width of the histogram report, N characters, overrides --size
  --verbose      be verbose

You can use single-characters options, like so: -h=25 -w=20 -v. You must still include the =

Samples:
  du -sb /etc/* | {scriptName} --palette=0,37,34,33,32 --graph
  du -sk /etc/* | awk '{{print $2\" \"$1}}' | {scriptName} --graph=kv
  zcat /var/log/syslog*gz | {scriptName} --char=o --tokenize=white
  zcat /var/log/syslog*gz | awk '{{print $5}}'  | {scriptName} -t=word -m-word -h=15 -c=/
  zcat /var/log/syslog*gz | cut -c 1-9        | {scriptName} -width=60 -height=10 -char=em
  find /etc -type f       | cut -c 6-         | {scriptName} -tokenize=/ -w=90 -h=35 -c=dt
  cat /usr/share/dict/words | awk '{{print length($1)}}' | {scriptName} -c=* -w=50 -h=10 | sort -n
"""
    )


# simple argument parsing and call top-level routines
def main():
    # instantiate our classes
    s = Settings()
    i = InputReader()
    h = Histogram()

    if s.graphValues:
        # user passed g=vk or g=kv
        i.read_pretallied_tokens(s)
    elif s.numOnly != "XXX":
        # s.numOnly was specified by the user
        i.read_numerics(s, h)
        # read_numerics will have output a graph already, so exit
        sys.exit(0)
    else:
        # this is the original behaviour of distribution
        i.tokenize_input(s)

    h.write_hist(s, i.tokenDict)


# what is this magic?
scriptName = str(Path(sys.argv[0]).name)
if __name__ == "__main__":
    main()
