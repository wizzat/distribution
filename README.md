distribution
============

Short, simple, direct scripts for creating ASCII graphical histograms in the
terminal.


Purpose
=======

These scripts are to generate a graphical histogram from the terminal, directly
in the terminal. At first, there will be only one script, the original written
in Perl by Tim Ellis. But if others port it to Python, Ocaml, COBOL, or
Brainfuck, then we'll include those versions here.

There are a few typical use cases:

   0. A stream of text, tokenize it, tally up the interesting tokens, and graph
      the result.
   1. A very large list of things, already one-per-line, tally up the things
      and graph them for me.
   2. A list of tokens + tallies, one-per-line, simply present a visual
      representation of the tallies for me so I can visualise the data.
   3. A list of tallies without corresponding tokens. Just present a visual
      representation of the list.

This project takes care of (the somewhat more complicated) first three cases.
For the last one, there is another project: https://github.com/holman/spark.


Options
=======

```
  --char=C       character(s) to use for histogram character, some substitutions follow:
        ba       (▬) Bar
        bl       (Ξ) Building
        em       (—) Emdash
        me       (⋯) Mid-Elipses
        di       (♦) Diamond
        dt       (•) Dot
        sq       (□) Square
        pb       Use 1/8-width unicode partial blocks to simulate 8x actual terminal width
        pc       Use 1/2-width unicode partial circles to simulate 2x actual terminal width
  --color        colourise the output
  --graph        input is already key/value pairs. vk is default:
        kv       input is ordered key then value
        vk       input is ordered value then key
  --height=N     height of histogram, headers non-inclusive, overrides --size
  --help         get help
  --match=RE     only match lines (or tokens) that match this regexp, some substitutions follow:
        word     ^[A-Z,a-z]+$ - tokens/lines must be entirely alphabetic
        num      ^\d+$        - tokens/lines must be entirely numeric
  --size         size of histogram, can abbreviate to single character, overridden by --width/--height
        small    40x10
        medium   80x20
        large    120x30
        full     terminal width x terminal height (approximately)
  --tokenize=RE  split input on regexp RE and make histogram of all resulting tokens
        word     [^\w] - split on non-word characters like colons, brackets, commas, etc
        white    \s    - split on whitespace
  --width=N      width of the histogram report, N characters, overrides --size
```


Examples
========

You can grab out parts of your syslog ask the script to tokenize on non-word
delimiters, then only match words. The verbosity gives you some stats as it
works and right before it prints the histogram.

```
$ zcat /var/log/syslog*gz | awk '{print $5" "$6}' | head -5
rsyslogd: [origin
anacron[5657]: Job
anacron[5657]: Can't
anacron[5657]: Normal
NetworkManager[1197]: SCPlugin-Ifupdown:
__________________

$ zcat /var/log/syslog*gz \
    | awk '{print $5" "$6}' \
    | distribution --tokenize=word --match=word --height=10 --verbose --char=o
 + Objects Processed: 124295.   
tokens/lines examined: 124295
 tallied in histogram: 36711
    histogram entries: 140
              runtime: 109.03ms

Val           |Ct (Pct)       Histogram
kernel        |12112 (32.99%) ooooooooooooooooooooooooooooooooooooooooooooooooo
NetworkManager|5695 (15.51%)  ooooooooooooooooooooooo
info          |5371 (14.63%)  oooooooooooooooooooooo
client        |1633 (4.45%)   ooooooo
ovpn          |1633 (4.45%)   ooooooo
daemon        |868 (2.36%)    oooo
avahi         |853 (2.32%)    oooo
dhclient      |736 (2.00%)    ooo
Trying        |667 (1.82%)    ooo
dnsmasq       |562 (1.53%)    ooo
```

You can start thinking of normal commands in new ways. For example, you can take
your "ps ax" output, get just the command portion, and do a word-analysis on it.
You might find some words are rather interesting. In this case, it appears Chrome
is doing some sort of A/B testing and their commandline exposes that.

```
$ ps axww \
    | cut -c 28- \
    | distribution --tokenize=word --match=word --char='|' --width=90 --height=25
Val                     |Ct (Pct)    Histogram
usr                     |100 (6.17%) |||||||||||||||||||||||||||||||||||||||||||||||||||||
lib                     |73 (4.51%)  ||||||||||||||||||||||||||||||||||||||
browser                 |38 (2.35%)  ||||||||||||||||||||
chromium                |38 (2.35%)  ||||||||||||||||||||
P                       |32 (1.98%)  |||||||||||||||||
daemon                  |31 (1.91%)  |||||||||||||||||
sbin                    |26 (1.60%)  ||||||||||||||
gnome                   |23 (1.42%)  ||||||||||||
bin                     |22 (1.36%)  ||||||||||||
kworker                 |21 (1.30%)  |||||||||||
type                    |19 (1.17%)  ||||||||||
gvfs                    |17 (1.05%)  |||||||||
no                      |17 (1.05%)  |||||||||
en                      |16 (0.99%)  |||||||||
indicator               |15 (0.93%)  ||||||||
channel                 |14 (0.86%)  ||||||||
bash                    |14 (0.86%)  ||||||||
US                      |14 (0.86%)  ||||||||
lang                    |14 (0.86%)  ||||||||
force                   |12 (0.74%)  |||||||
pluto                   |12 (0.74%)  |||||||
ProxyConnectionImpact   |12 (0.74%)  |||||||
HiddenExperimentB       |12 (0.74%)  |||||||
ConnectBackupJobsEnabled|12 (0.74%)  |||||||
session                 |12 (0.74%)  |||||||
```

You can use very short versions of the options in case you don't like typing a
lot. The default character is "+" because it creates a type of grid system
which makes it easy for the eye to trace right/left or up/down. If the input is
already just a list of values and keys, you can pass in the "--graph" (-g)
option to graph the data without going through any parsing phase.

```
$ sudo du -sb /etc/* | distribution -w=90 -h=15 -g
Val                   |Ct (Pct)         Histogram
/etc/mateconf         |7780758 (44.60%) +++++++++++++++++++++++++++++++++++++++++++++++++
/etc/brltty           |3143272 (18.02%) ++++++++++++++++++++
/etc/apparmor.d       |1597915 (9.16%)  ++++++++++
/etc/bash_completion.d|597836 (3.43%)   ++++
/etc/mono             |535352 (3.07%)   ++++
/etc/ssl              |465414 (2.67%)   +++
/etc/ardour2          |362303 (2.08%)   +++
/etc/X11              |226309 (1.30%)   ++
/etc/ImageMagick      |202358 (1.16%)   ++
/etc/init.d           |143281 (0.82%)   +
/etc/ssh              |138042 (0.79%)   +
/etc/fonts            |119862 (0.69%)   +
/etc/sound            |112051 (0.64%)   +
/etc/xdg              |111971 (0.64%)   +
/etc/java-7-openjdk   |100414 (0.58%)   +
```

The output is separated between STDOUT and STDERR so you can sort the resulting
histogram by values. This is useful for time series or other cases where the
keys you're searching on are in some natural order.

```
$ cat NotServingRegionException-DateHour.txt \
    | distribution -v \
    | sort -n
 + Objects Processed: 1414196.   
tokens/lines examined: 1414196
 tallied in histogram: 1414196
    histogram entries: 453
              runtime: 1279.30ms

Val             |Ct (Pct)      Histogram
   2012-07-13 03|38360 (2.71%) ++++++++++++++++++++++++
   2012-07-28 21|18293 (1.29%) ++++++++++++
   2012-07-28 23|20748 (1.47%) +++++++++++++
   2012-07-29 06|15692 (1.11%) ++++++++++
   2012-07-29 07|30432 (2.15%) +++++++++++++++++++
   2012-07-29 08|76943 (5.44%) ++++++++++++++++++++++++++++++++++++++++++++++++
   2012-07-29 09|54955 (3.89%) ++++++++++++++++++++++++++++++++++
   2012-07-30 05|15652 (1.11%) ++++++++++
   2012-07-30 09|40102 (2.84%) +++++++++++++++++++++++++
   2012-07-30 10|21718 (1.54%) ++++++++++++++
   2012-07-30 16|16041 (1.13%) ++++++++++
   2012-08-01 09|22740 (1.61%) ++++++++++++++
   2012-08-02 04|31851 (2.25%) ++++++++++++++++++++
   2012-08-02 06|28748 (2.03%) ++++++++++++++++++
   2012-08-02 07|18062 (1.28%) ++++++++++++
   2012-08-02 20|23519 (1.66%) +++++++++++++++
   2012-08-03 03|21587 (1.53%) ++++++++++++++
   2012-08-03 08|33409 (2.36%) +++++++++++++++++++++
   2012-08-03 10|15854 (1.12%) ++++++++++
   2012-08-03 15|29828 (2.11%) +++++++++++++++++++
   2012-08-03 16|20478 (1.45%) +++++++++++++
   2012-08-03 17|39758 (2.81%) +++++++++++++++++++++++++
   2012-08-03 18|19514 (1.38%) ++++++++++++
   2012-08-03 19|18353 (1.30%) ++++++++++++
   2012-08-03 22|18726 (1.32%) ++++++++++++
__________________

$ cat /usr/share/dict/words \
    | awk '{print length($1)}' \
    | distribution -c=: -w=90 -h=16 \
    | sort -n
Val|Ct (Pct)       Histogram
2 |182 (0.18%)    :
3 |845 (0.85%)    ::::
4 |3346 (3.37%)   ::::::::::::::::
5 |6788 (6.84%)   :::::::::::::::::::::::::::::::
6 |11278 (11.37%) ::::::::::::::::::::::::::::::::::::::::::::::::::::
7 |14787 (14.91%) :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
8 |15674 (15.81%) ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
9 |14262 (14.38%) :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
10|11546 (11.64%) :::::::::::::::::::::::::::::::::::::::::::::::::::::
11|8415 (8.49%)   :::::::::::::::::::::::::::::::::::::::
12|5508 (5.55%)   :::::::::::::::::::::::::
13|3236 (3.26%)   :::::::::::::::
14|1679 (1.69%)   ::::::::
15|893 (0.90%)    :::::
16|382 (0.39%)    ::
17|176 (0.18%)    :
```

Even if you know sed/awk/grep, the built-in tokenizing/matching can be less
verbose. Say you want to look at all the URLs in your Apache logs. People will
be doing GET /a/b/c /a/c/f q/r/s q/n/p. A and Q are the most common, so you can
tokenize on / and the latter parts of the URL will be buried, statistically.

By tokenizing and matching using the script, you may also find unexpected
common portions of the URL that don't show up in the prefix.

```
$ zcat access.log*gz \
        | awk '{print $7}' \
        | distribution -t=/ -h=15
Val            |Ct (Pct)      Histogram
Art            |1839 (16.58%) +++++++++++++++++++++++++++++++++++++++++++++++++
Rendered       |1596 (14.39%) ++++++++++++++++++++++++++++++++++++++++++
Blender        |1499 (13.52%) ++++++++++++++++++++++++++++++++++++++++
AznRigging     |760 (6.85%)   ++++++++++++++++++++
Music          |457 (4.12%)   ++++++++++++
Ringtones      |388 (3.50%)   +++++++++++
CuteStance     |280 (2.52%)   ++++++++
Traditional    |197 (1.78%)   ++++++
Technology     |171 (1.54%)   +++++
CreativeExhaust|134 (1.21%)   ++++
Fractals       |127 (1.15%)   ++++
robots.txt     |125 (1.13%)   ++++
RingtoneEP1.mp3|125 (1.13%)   ++++
Poetry         |108 (0.97%)   +++
RingtoneEP2.mp3|95 (0.86%)    +++
```


To-Do List
==========

This script is 1.0 after only about a week of life. New features should be
carefully considered and weighed against their likelihood of causing bugs.
That is to say, new features are unlikely to be added, as the existing
functionality already arguably is a superset of what's necessary.  Still, there
are some things that need to be done.

 * No Time::HiRes Perl module? Don't die. Much harder than it should be. Invalidated by next to-do.
 * Get script included in package managers.
 * Configuration file (~/.distributionrc) for default behaviours and colours.
 * On large files it might be slow. Speed enhancements nice.


Porting
=======

Perl is fairly common, but I'm not sure 100% of systems out there have it. A
Python and C/C++ port would be most welcome.

If you write a port, send me a pull request so I can include it in this repo.

Port requirements: from the user's point of view, it's the exact same script.
They pass in the same options in the same way, and get the same output,
byte-for-byte if possible. This means you'll need (Perl) regexp support in your
language of choice. Also a hash map structure makes the implementation simple,
but more-efficient methods are welcome.

I imagine, in order of nice-to-haveness:

 * C or C++
 * Python
 * Java
 * Ruby
 * Lisp
 * Ocaml
 * Brainfuck

Brainfuck I want as a point of geek pride. Please don't make me learn it. Give
me a port!

