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
echo -n "6. "
for i in `seq 1 17 3141592` ; do echo $[ $i ^ ($i + 9) ]; done | cut -c 2-6 | $distribution -width=124 -height=29 --color -c=^ --v > output006.txt 2> output106.txt


# get onto the newline
echo ""

echo "
Expected output:
 = 95e10b0882551490d9d07e45b6f28874  output001.txt
 = 2ae3621106a77cff3080ba5a240cdd69  output002.txt
 = 8228e18cb80d28cc5a983a43a1cae3d8  output003.txt
 = b29e23a97fdf88b556fdff175da8ce7e  output004.txt
 = 42446cf6f4a0f414ed27d323155ccbf7  output005.txt
 = bb2ad9bba293f3d4d938e709fa1a10e2  output006.txt

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

