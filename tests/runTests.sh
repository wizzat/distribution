#!/bin/bash

# make sure env is setup proper
if [ "xxx$distribution" == "xxx" ] ; then
	echo "To run tests, first export distribution=<pathToDistributionToTest>"
	exit 255
fi

# the tests
echo -n "Running test: 1. "
cat input01.txt | $distribution --graph --height=35 --width=120 --char=dt --color --verbose > output001.txt 2> output101.txt

echo -n "2. "
cat input02.txt | awk '{print $4" "$5}' | $distribution --s=med --width=110 --tokenize=word --match=word -v -c > output002.txt 2> output102.txt

echo -n "3. "
grep modem input02.txt | awk '{print $1}' | $distribution --width=110 --h=15 -c='|' -v -c 2> output103.txt | sort > output003.txt

echo -n "4. "
cat input03.txt | $distribution --size=large -height=8 -width=60 -t=/ -c --c=cp > output004.txt 2> output104.txt

echo -n "5. "
cat input03.txt | $distribution -c=di --w=48 -tokenize=word -match=num -size=large -verbose 2> output105.txt | sort -n > output005.txt

echo -n "6. "
for i in `seq 1 17 3141592` ; do echo $[ $i ^ ($i + 9) ]; done | cut -c 2-6 | $distribution -width=124 -height=29 --color -c=^ --v > output006.txt 2> output106.txt

echo -n "7. "
cat input04.txt | awk '{print $8}' | $distribution -s=s --w=90 --char=Ξ > output007.txt 2> output107.txt

# get onto the newline
echo ""

echo "
Expected output:
 = b2d463a3fb20df2c01fb95b1e2006784  output001.txt
 = e296b1664d48339aed963268b34adc20  output002.txt
 = 4edb70a142774c686c9268b88a00cb01  output003.txt
 = bf5d4acdd4e711ea392feb9969af4303  output004.txt
 = 42446cf6f4a0f414ed27d323155ccbf7  output005.txt
 = 2e53cae32394f7da53fdaf62a5ae98c5  output006.txt
 = b78314f12f57f215628ef2dedf3114de  output007.txt

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

