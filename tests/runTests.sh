#!/bin/bash

# make sure env is setup proper
if [ "xxx$distribution" == "xxx" ] ; then
	echo "To run tests, first export distribution=<pathToDistributionToTest>"
	exit 255
fi

# the tests
echo -n "test: 1. "
cat input01.txt | $distribution --graph --height=35 --width=120 --char=dt --color --verbose > output001.txt 2> output101.txt
echo -n "2. "
cat input02.txt | awk '{print $4" "$5}' | $distribution --width=110 --h=30 --tokenize=word --match=word -v -c > output002.txt 2> output102.txt
echo -n "3. "
grep modem input02.txt | awk '{print $1}' | $distribution --width=110 --h=15 -c='|' -v -c 2> output103.txt | sort > output003.txt
echo -n "4. "
cat input03.txt | $distribution -height=8 -width=60 -t=/ -c --c=cp > output004.txt 2> output104.txt
echo -n "5. "
cat input03.txt | $distribution -c=di --w=48 -tokenize=word -match=num -verbose 2> output105.txt | sort -n > output005.txt

# get onto the newline
echo ""

echo "
Expected output:
 = dfb7cbc75b73e9974d97fb68adce69f2  output001.txt
 = 5738adc4876551615ec54e639e3c36f9  output002.txt
 = 7d9c9a9e5a18a699e19f1185de7fa899  output003.txt
 = edccb59cedfb6332801f435c259a6183  output004.txt
 = e4b81d7b876398127773e5a1b0309c24  output005.txt

Actual output:"

# be sure output is proper
for i in output0*.txt ; do
	echo " = `md5sum $i`"
	#echo "debug: `cat $i`"
done

## # the problem with output1*.txt is they have millisecond timings which
## # will change from run to run. so filter those out then repeat...
## for i in output1*.txt ; do
##	echo " = `md5sum $i`"
## 	#echo "debug: `cat $i`"
## done

# clean up
rm output*.txt

