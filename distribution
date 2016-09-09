#!/usr/bin/env perl

# vim: set noexpandtab sw=4 ts=4:
# --
# A recent battle with vim and a Go program finally settled this for me.
# Tabs for indent, spaces for formatting. If you change your shiftwidth and
# tabstop to different values and your code looks ugly, say aloud: tabs
# for indent, spaces for formatting.

# distribution - creates histograms based on input
#
# Version 1.0
#
# Written by Tim Ellis of Fifth Sigma, Inc.
# Copyright (c) 2012-2014 by Tim Ellis
# Released under the terms of GNU GPLv2:
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, visit http://www.gnu.org/licenses/gpl-2.0.html in your
# web browser.
#
# If you're still living in the 1800's, you can instead write to:
#
# Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301, USA.

use warnings;
use strict;

# Time::HiRes will be used if found, to provide more precise timings
# with --verbose.
BEGIN {
    eval { require Time::HiRes; Time::HiRes->import('time'); 1; };
}

# for determining how long this program ran
my $startTime = time() * 1000;

# defaults - overridden first by distributionrc then by commandline options
my $size = '';
my $width = 80;
my $height = 15;
my $widthArg = 0;
my $heightArg = 0;
my $logarithmic = 0;
# every keyPruneInterval keys, prune the hash to maxKeys top keys
my $keyPruneInterval = 1500000;
my $maxKeys = 5000;
my $numOnly = '';
my $histogramChar = "-";
my $unicode = 0;
my $tokenize = 0;
# by default, everything matches (nothing is stripped out)
my $matchRegexp = ".";
# status and summary statistics
my $verbose = 0;
# how often to give status if verbose
my $statInterval = 1.0;
my $numPrunes = 0;
# whether or not to parse input into bins (if data is pre-summarised and we're
# just presenting results)
my $graphValues = "";

# variables to support colourised output
my $colourisedOutput = 0;
my $colourPalette = '0,0,32,35,34';
my $regularColour = "";
my $keyColour = "";
my $ctColour = "";
my $pctColour = "";
my $graphColour = "";

# we'll re-use inLine at various times for reading files
my $inLine;

# if they want an rcfile, must be first arg
my $rcFile = $ENV{"HOME"} . "/.distributionrc";
if (@ARGV && $ARGV[0] =~ /^-+r(cfile)*=(.+)$/) { $rcFile = $2; }

# read in rcfile if it exists - it'll just be args
if (open (IFILE, "< $rcFile")) {
	while ($inLine = <IFILE>) {
		chomp ($inLine);
		# must put args from rcfile at start so options passed on the
		# commandline will override them
		unshift (@ARGV, $inLine);
	}
}

# process input arguments -- any arguments that aren't known switches are stuck
# onto @extraArgs - note that you can have one or two dashes before the option,
# and only need the first character. also options that take values and switches
# can be overloaded, so -c=o -c means use the o character and colourise the
# output. this can be confusing.
my @extraArgs;
foreach my $arg (@ARGV) {
	if ($arg =~ /^-+h(elp)*$/)               { doArgs(); exit 0; }
	elsif ($arg =~ /^-+w(idth)*=(.+)$/)      { $widthArg = $2; }
	elsif ($arg =~ /^-+h(eight)*=(.+)$/)     { $heightArg = $2; }
	elsif ($arg =~ /^-+k(eys)*=(.+)$/)       { $maxKeys = $2; }
	# --char takes option...
	elsif ($arg =~ /^-+c(har)*=(.+)$/)       { $histogramChar = $2; }
	# ...--color doesn't.
	elsif ($arg =~ /^-+c(olor)*$/)           { $colourisedOutput = 1; }
	# can pass --graph without option, will default to value/key ordering
	# since Unix prefers that for piping-to-sort reasons
	elsif ($arg =~ /^-+g(raph)*=(.+)$/)      { $graphValues = $2; }
	elsif ($arg =~ /^-+g(raph)*$/)           { $graphValues = 'vk'; }
	elsif ($arg =~ /^-+l(ogarithmic)*$/)     { $logarithmic = 2; }
	# can pass --numonly without option
	elsif ($arg =~ /^-+n(umonly)$/)          { $numOnly = 'abs'; }
	elsif ($arg =~ /^-+n(umonly)*=(.+)$/)    { $numOnly = $2; }
	# palette is a comma-separated list of ANSI colour values
	elsif ($arg =~ /^-+p(alette)*=(.+)$/)    { $colourPalette = $2; $colourisedOutput = 1; }
	# size has somewhat complex override semantics including some
	# non-obvious ones like if passing --numonly for example
	elsif ($arg =~ /^-+s(ize)*=(.+)$/)       { $size = $2; }
	# tokenize the input based on Perl regexp
	elsif ($arg =~ /^-+t(okenize)*=(.+)$/)   { $tokenize = $2; }
	# match tokens based on Perl regexp
	elsif ($arg =~ /^-+m(atch)*=(.+)$/)      { $matchRegexp = $2; }
	elsif ($arg =~ /^-+v(erbose)*$/)         { $verbose = 1; }
	else { push (@extraArgs, $arg); }
}

# variables to support colourised output
if ($colourisedOutput) {
	# input should be comma-separated list of numerals
	my @cp = split (',', $colourPalette);
	# add ANSI colour commands around the values - final looks like ^[[32m
	for (my $i=0; $i < scalar @cp; $i++) {
		$cp[$i] = chr(27) . '[' . $cp[$i] . 'm';
	}
	($regularColour, $keyColour, $ctColour, $pctColour, $graphColour) = @cp;
}

# for advanced graphing
my $verticalBlocks =   ["▁", "▂", "▃", "▄", "▅", "▆", "▇", "█"]; # for future?
my $partialBlocks =    ["▏", "▎", "▍", "▌", "▋", "▊", "▉", "█"]; # char=pb
my $partialCircles =   ["◖", "●"]; # char=pc
my $partialLines =     ["╸", "╾", "━"]; # char=pl

# some useful substitutions for prettiness
if ($histogramChar eq "ba") { $unicode = 1; $histogramChar = "▬"; }
elsif ($histogramChar eq "bl") { $unicode = 1; $histogramChar = "Ξ"; }
elsif ($histogramChar eq "em") { $unicode = 1; $histogramChar = "—"; }
elsif ($histogramChar eq "me") { $unicode = 1; $histogramChar = "⋯"; }
elsif ($histogramChar eq "di") { $unicode = 1; $histogramChar = "♦"; }
elsif ($histogramChar eq "dt") { $unicode = 1; $histogramChar = "•"; }
elsif ($histogramChar eq "sq") { $unicode = 1; $histogramChar = "□"; }

# high-bit set means we're not in ASCIIland anymore
if (ord (substr ($histogramChar, 0, 1)) >= 128) { $unicode = 1; }

# sub-full character width graphing systems
my $charWidth = 1;
my $graphChars = undef;
if ($histogramChar eq "pb") {
	$charWidth = 0.125;
	$graphChars = $partialBlocks;
} elsif ($histogramChar eq "pl") {
	$charWidth = 0.3334;
	$graphChars = $partialLines;
}

# some useful regexp replacements
if ($matchRegexp eq 'word') { $matchRegexp = '^[A-Z,a-z]+$'; }
elsif ($matchRegexp eq 'num')  { $matchRegexp = '^\d+$'; }
if ($tokenize eq 'word')    { $tokenize = '[^\w]'; }
elsif ($tokenize eq 'white')   { $tokenize = '\s'; }

# set the heigh/width of the histogram based on size input,
# this is the lowest level of height/width priority
if ($size =~ /^f/) {
	$width = int (`tput cols` * 0.99);
	if ($width < 80) { $width = 80; }
	$height = int (`tput lines` - 3);
	if ($verbose) { $height -= 4; }
	if ($height < 20) { $height = 20; }
} elsif ($size =~ /^s/) {
	$width = 60;
	$height = 10;
} elsif ($size =~ /^m/) {
	$width = 100;
	$height = 20;
} elsif ($size =~ /^l/) {
	$width = 140;
	$height = 35;
}

# if they passed in --width or --height, they probably meant it moreso than
# defaults or the --size parameter - so code this last
if ($widthArg) { $width = $widthArg; }
if ($heightArg) { $height = $heightArg; }

# maxKeys should be at least a few thousand greater than height to reduce odds
# of throwing away high-count values that appear sparingly in the data
if ($maxKeys < $height + 3000) {
	$maxKeys = $height + 3000;
	print STDERR "Updated maxKeys to $maxKeys (height + 3000)\n";
}

my $nextStat = time() + $statInterval;
my $valuesDict;
my $totalValues = 0;
my $totalObjects = 0;
my $graphVal = 0;
my $maxVal = 0;

# build the dict/map/hash of input values in one of the three modes of operation
if ($numOnly) {
	readNumerics();
} elsif ($graphValues) {
	readPretalliedTokens();
} else {
	readLinesBuildHash();
}

# see if there was input
checkValuesObjects();

my $totalKeys;
my @sortedKeys;

# if we're just graphing a bunch of numbers, no need to sort
# the values dict/map/hash
if ($numOnly) {
	# here we sort on KEYS not VALUES like other cases
	@sortedKeys = sortKeysByKey();

	# we graph everything we're given - throw away nothing! this overrides
        # --height or --size options! it is the highest priority height directive
	$height = $totalObjects;
} else {
	# build the sorted dict/map/hash
	@sortedKeys = sortKeysByValueFrequency();
	$maxVal = $valuesDict->{$sortedKeys[0]};
}

# if there aren't height # of distinct values, choose the number
# of values so the loop later on doesn't have to check for special
# cases
$totalKeys = scalar @sortedKeys;
if ($totalKeys < $height) { $height = $totalKeys; }

# for logarithmic graphs
my $maxLog = 0;
if ($logarithmic) {
	$maxLog = log($maxVal);
}

my $i;
my $j;
my $keyText;
my $ctText;
my $pctText;
my $preBarLen;
my $barWidth;
my $maxPreBarLen = 0;
my $maxKeyLen = 0;

# here is the complex part - read it carefully
for ($i = 0; $i < $height; $i++) {
	# print the i'th most-common key
	$keyText->[$i] = $sortedKeys[$i];

	# how many times this key occurred in the input
	my $count = $valuesDict->{$sortedKeys[$i]};

	# determine the bar width based on key occurence
	if ($logarithmic) {
		if ($count > 0) {
			$barWidth->[$i] = log($count) / $maxLog;
		} else {
			$barWidth->[$i] = 0;
		}
	} else {
		$barWidth->[$i] = $count / $maxVal;
	}

	# determine the percent of key frequency
	my $percentile = $count / $totalValues * 100;

	# graph axis labels, really
	$ctText->[$i] = sprintf ("%d", $count);
	$pctText->[$i] = sprintf ("(%3.02f%%)", $percentile);
	$preBarLen = length ($ctText->[$i]) + length ($pctText->[$i]);

	# determine the longest key name and longest count/percent text for
	# aligning the output
	if ($preBarLen > $maxPreBarLen) { $maxPreBarLen = $preBarLen; }
	if (length ($sortedKeys[$i]) > $maxKeyLen) { $maxKeyLen = length ($sortedKeys[$i]); }
}

my $endTime = time() * 1000;
my $totalMillis = sprintf ("%.2f", ($endTime - $startTime));

# TODO: Collect stats on histogram keys, like how many times maxKeys was
# reached and pruned, and present them here. For now that seems complicated
# for the end-user, so I'll wait until there's a feature request
if ($verbose) {
	print STDERR "tokens/lines examined: " . addCommas($totalObjects) . "    \n";
	print STDERR " tokens/lines matched: " . addCommas($totalValues) . "\n";
	print STDERR "       histogram keys: " . addCommas($totalKeys) . "\n";
	print STDERR "              runtime: " . addCommas($totalMillis) . "ms\n";
}

# almost done now!
outputGraph();

exit 0;

# --------------------------------------------------------------------------- #
#                                 subroutines
# --------------------------------------------------------------------------- #

# get the keys ordered - we'll only print the most common keys
sub sortKeysByValueFrequency {
	# sort first by the value of a key, then by the key itself in case of a tie.
	# this allows us to create deterministic sorts when we have multiple entries
	# in our histogram with the same frequency. particularly important given that
	# perl intentionally randomizes the order of dictionary keys, so not even a
	# stable sort would save us.
	my @sortedKeys = reverse sort { int($valuesDict->{$a}) <=> int($valuesDict->{$b}) || $a cmp $b } keys %{$valuesDict};
	return @sortedKeys;
}

# keep only the most maxKeys keys
sub pruneKeys {
	my $newDict;
	my $numKeysTransferred = 0;
	foreach my $key (&sortKeysByValueFrequency) {
		$newDict->{$key} = $valuesDict->{$key};
		$numKeysTransferred++;
		last if ($numKeysTransferred > $maxKeys);
	}
	$valuesDict = $newDict;
	$numPrunes++;
}

# get the keys ordered simply by key
sub sortKeysByKey {
	my @sortedKeys = sort { int($a) <=> int($b) } keys %{$valuesDict};
	return @sortedKeys;
}

# here we just pull in a stream of numerics and graph them, optionally graphing
# the difference between each pair of values
sub readNumerics {
	# monotonically-increasing pairs, must have at least one value
	my $lastVal = undef;

	while ($inLine = <STDIN>) {
		chomp ($inLine);
		if ($numOnly =~ /^m/i || $numOnly =~ /^d/i) {
			if (defined $lastVal) {
				$graphVal = $inLine - $lastVal;
				$totalValues += $graphVal;
				$totalObjects++;
			}
			$lastVal = $inLine;
		} else {
			$graphVal= $inLine;
			$totalValues += $inLine;
			$totalObjects++;
		}

		if ($graphVal > $maxVal) { $maxVal = $graphVal; }

		# we just build a list where the keys are line num and values are the
		# value
		if ($totalObjects > 0) {
			$valuesDict->{$totalObjects} = $graphVal;
		}
	}
}

# read in lines and build dict/map/hash object from it
sub readLinesBuildHash {
	my $pruneObjects = 0;
	while ($inLine = <STDIN>) {
		chomp($inLine);
		if ($tokenize) {
			# in this case we break the line into tokens and tally them
			foreach my $lineToken (split (/$tokenize/, $inLine)) {
				$totalObjects++;
				if ($lineToken =~ /$matchRegexp/) {
					$valuesDict->{$lineToken}++;
					$totalValues++;
					$pruneObjects++;
				}
			}
		} else {
			# in this case the entire line is the token to be tallied
			$totalObjects++;
			if ($inLine =~ /$matchRegexp/) {
				$valuesDict->{$inLine}++;
				$totalValues++;
				$pruneObjects++;
			}
		}
		if ($verbose && time() > $nextStat) {
			print STDERR "tokens/lines examined: " . addCommas($totalObjects) . "... ; hash prunes: $numPrunes" . chr(13);
			$nextStat = time() + $statInterval;
		}
		if ($pruneObjects >= $keyPruneInterval) {
			pruneKeys();
			$pruneObjects = 0;
		}
	}
}

# here is the case where we don't need to put the input into bins and tally -
# the data is pre-tallied for us
sub readPretalliedTokens {
	while ($inLine = <STDIN>) {
		chomp ($inLine);
		if ($graphValues eq 'vk') {
			if ($inLine =~ /^\s*(\d+)\s+(.+)$/) {
				$valuesDict->{$2} += $1;
				$totalValues += $1;
				if ($1 > $maxVal) { $maxVal = $1; }
				$totalObjects++;
			} else {
				print STDERR " E Input malformed+discarded (perhaps pass -g=kv?): $inLine\n";
			}
		} elsif ($graphValues eq 'kv') {
			if ($inLine =~ /^(.+?)\s+(\d+)$/) {
				$valuesDict->{$1} += $2;
				$totalValues += $2;
				if ($2 > $maxVal) { $maxVal = $2; }
				$totalObjects++;
			} else {
				print STDERR " E Input malformed+discarded (perhaps pass -g=vk?): $inLine\n";
			}
		}
	}
}

# see if there was input
sub checkValuesObjects {
	# the input may be empty. or we may have been too strict on the
	# matching regexp passed in. either way, we were left with nothing.
	if ($totalValues == 0) {
		if ($totalObjects > 0) {
			print STDERR "All input filtered! ";
		} else {
			print STDERR "No input! ";
		}
		print STDERR "No histogram for you. Sorry?\n";
		exit 255;
	}
}

# make a number filled with commas - humans hate to see a number like
# 18008675309. is that 180M or 1.8B? look again. 18B.
sub addCommas {
	my $theNumber = shift;
	$theNumber = reverse $theNumber;
	$theNumber =~ s<(\d\d\d)(?=\d)(?!\d*\.)><$1,>g;
	return reverse $theNumber;
}

# the following arrays, hashes, variables must be correct for this to work
# keyText->[]  - list of the keys
# pctText->[]  - list of the percents
# ctText->[]   - list of the counts
# barWidth->[] - list of the widths of the bars
sub outputGraph {
	# print a header with alignment from key names
	for ($j = 4; $j <= $maxKeyLen; $j++) { print STDERR " "; }
	print STDERR "Key";
	print STDERR "|Ct (Pct)";
	for ($j = 7; $j <= $maxPreBarLen; $j++) { print STDERR " "; }
	print STDERR "Histogram";

	# get ready for the output, but sorting gets hosed if we print the
	# colour code before the key, so put it on the line before
	print STDERR "$keyColour\n";

	# amount of other output reduces possible size of bar - alas
	my $maxBarWidth = $width - $maxPreBarLen - $maxKeyLen - 4;

	for ($i = 0; $i < $height; $i++) {
		# first the key that we aggregated
		for ($j = length ($keyText->[$i]); $j < $maxKeyLen; $j++) { print " "; }
		print $keyText->[$i];
		print $regularColour;
		# alignment
		# separater between keys and count/pct
		print "|";
		print $ctColour;
		print $ctText->[$i] . " ";
		print $pctColour;
		print $pctText->[$i];

		# spaces 'til time to print the bar
		for ($j = length ($ctText->[$i]) + length ($pctText->[$i]); $j <= $maxPreBarLen; $j++) { print " "; }

		print $graphColour;
		for ($j = 0; $j < int ($barWidth->[$i] * $maxBarWidth); $j++) {
			if ($charWidth < 1) {
				# print out maximum-width character (always last in array)
				print $graphChars->[scalar @$graphChars - 1];
			} else {
				# we're printing regular non-unicode characters
				if (length ($histogramChar) > 1 && !$unicode) {
					# but still we have >1 byte! so print initial byte
					# for all but the last character (printed outside loop)
					print substr ($histogramChar, 0, 1);
				} else {
					print $histogramChar;
				}
			}
		}

		# print one too many bar characters so we always see something
		if ($charWidth < 1) {
			# if we have partial-width characters, get higher resolution
			my $remainder = ($barWidth->[$i] * $maxBarWidth) - int ($barWidth->[$i] * $maxBarWidth);
			my $whichChar = int ($remainder / $charWidth);
			if ($barWidth->[$i] * $maxBarWidth > $charWidth) {
				# we have more than charWidth remainder, so print out a
				# remainder portion
				print $graphChars->[$whichChar];
			} else {
				# we had minimum remainder, so print minimum-width
				# character just print the minimum-width portion
				print $graphChars->[0];
			}
		} else {
			# we're printing regular non-unicode characters
			if (length ($histogramChar) > 1 && !$unicode) {
				# but still we have >1 byte! so print final byte of input string
				print substr ($histogramChar, -1, 1);
			} else {
				print $histogramChar;
			}
		}

		# FIXME: even with all these colour-printing antics, still one key will
		# be printed with the wrong colour on sorted output most of the time,
		# but i have no idea how to fix this other than to implement sorting of
		# the output within the script itself.
		if ($i == $height - 1) {
			# put the terminal back into a normal-colour mode on last entry
			print "$regularColour\n";
		} else {
			# we do these antics of printing $keyColour on the line before
			# the key so that piping output to sort will work
			print "$keyColour\n";
		}
	}
}

# usage
sub doArgs {
	print "\n";
	print "usage: <commandWithOutput> | $0\n";
	print "         [--rcfile=<rcFile>]\n";
	print "         [--size={sm|med|lg|full} | --width=<width> --height=<height>]\n";
	print "         [--color] [--palette=r,k,c,p,g]\n";
	print "         [--tokenize=<tokenChar>]\n";
	print "         [--graph[=[kv|vk]] [--numonly[=derivative,diff|abs,absolute,actual]]\n";
	print "         [--char=<barChars>|<substitutionString>]\n";
	print "         [--help] [--verbose]\n";
	print "  --keys=K       every $keyPruneInterval values added, prune hash to K keys (default 5000)\n";
	print "  --char=C       character(s) to use for histogram character, some substitutions follow:\n";
	print "        pl       Use 1/3-width unicode partial lines to simulate 3x actual terminal width\n";
	print "        pb       Use 1/8-width unicode partial blocks to simulate 8x actual terminal width\n";
	print "        ba       (▬) Bar\n";
	print "        bl       (Ξ) Building\n";
	print "        em       (—) Emdash\n";
	print "        me       (⋯) Mid-Elipses\n";
	print "        di       (♦) Diamond\n";
	print "        dt       (•) Dot\n";
	print "        sq       (□) Square\n";
	print "  --color        colourise the output\n";
	print "  --graph[=G]    input is already key/value pairs. vk is default:\n";
	print "        kv       input is ordered key then value\n";
	print "        vk       input is ordered value then key\n";
	print "  --height=N     height of histogram, headers non-inclusive, overrides --size\n";
	print "  --help         get help\n";
	print "  --logarithmic  logarithmic graph\n";
	print "  --match=RE     only match lines (or tokens) that match this regexp, some substitutions follow:\n";
	print "        word     ^[A-Z,a-z]+\$ - tokens/lines must be entirely alphabetic\n";
	print "        num      ^\\d+\$        - tokens/lines must be entirely numeric\n";
	print "  --numonly[=N]  input is numerics, simply graph values without labels\n";
	print "        actual   input is just values (default - abs, absolute are synonymous to actual)\n";
	print "        diff     input monotonically-increasing, graph differences (of 2nd and later values)\n";
	print "  --palette=P    comma-separated list of ANSI colour values for portions of the output\n";
	print "                 in this order: regular, key, count, percent, graph. implies --color.\n";
	print "  --rcfile=F     use this rcfile instead of \$HOME/.distributionrc - must be first argument!\n";
	print "  --size=S       size of histogram, can abbreviate to single character, overridden by --width/--height\n";
	print "        small    40x10\n";
	print "        medium   80x20\n";
	print "        large    120x30\n";
	print "        full     terminal width x terminal height (approximately)\n";
	print "  --tokenize=RE  split input on regexp RE and make histogram of all resulting tokens\n";
	print "        word     [^\\w] - split on non-word characters like colons, brackets, commas, etc\n";
	print "        white    \\s    - split on whitespace\n";
	print "  --width=N      width of the histogram report, N characters, overrides --size\n";
	print "  --verbose      be verbose\n";
	print "\n";
	print "You can use single-characters options, like so: -h=25 -w=20 -v. You must still include the =\n";
	print "\n";
	print "Samples:\n";
	print "  du -sb /etc/* | $0 --palette=0,37,34,33,32 --graph\n";
	print "  du -sk /etc/* | awk '{print \$2\" \"\$1}' | $0 --graph=kv\n";
	print "  zcat /var/log/syslog*gz | $0 --char=o --tokenize=white\n";
	print "  zcat /var/log/syslog*gz | awk '{print \$5}'  | $0 --t=word --m-word --h=15 --c=/\n";
	print "  zcat /var/log/syslog*gz | cut -c 1-9        | $0 --width=60 --height=10 --char=em\n";
	print "  find /etc -type f       | cut -c 6-         | $0 --tokenize=/ --w=90 --h=35 --c=dt\n";
	print "  cat /usr/share/dict/words | awk '{print length(\$1)}' | $0 --c=* --w=50 --h=10 | sort -n\n";
	print "\n";
}
