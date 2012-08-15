#!/bin/bash

# make sure env is setup proper
if [ "xxx$distribution" == "xxx" ] ; then
	echo "To run tests, first export distribution=<pathToDistributionToTest>"
	exit 255
fi

# the tests
cat input01.txt | $distribution --graph --height=35 --width=120 --char=dt --color --verbose > output001.txt 2> output101.txt
cat input02.txt | awk '{print $4" "$5}' | $distribution --width=110 --h=30 --tokenize=word --match=word -v -c > output002.txt 2> output102.txt
grep modem input02.txt | awk '{print $1}' | $distribution --width=110 --h=15 -c='|' -v -c 2> output103.txt | sort > output003.txt
cat input03.txt | $distribution -height=8 -width=60 -t=/ -c --c=cp > output004.txt 2> output104.txt

# be sure output is proper
for i in output0*.txt ; do
	echo " = = = = = `md5sum $i` = = = = ="
	#echo "debug: `cat $i`"
done

## # the problem with output1*.txt is they have millisecond timings which
## # will change from run to run. so filter those out then repeat...
## for i in output1*.txt ; do
## 	echo " = = = = = `md5sum $i` = = = = ="
## 	#echo "debug: `cat $i`"
## done

# clean up
rm output*.txt

