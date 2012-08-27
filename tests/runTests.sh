#!/bin/bash

# make sure env is setup proper
if [ "xxx$distribution" == "xxx" ] ; then
	echo "To run tests, first export distribution=<pathToDistributionToTest>"
	exit 255
fi

# the tests
echo "Test #6 is designed to take several seconds."
echo -n "Running test: 1. "
cat input01.txt | $distribution --rcfile=../distributionrc --graph --height=35 --width=120 --char=dt --color --verbose > output001.txt 2> output101.txt

echo -n "2. "
cat input02.txt | awk '{print $4" "$5}' | $distribution --rcfile=../distributionrc --s=med --width=110 --tokenize=word --match=word -v -c > output002.txt 2> output102.txt

echo -n "3. "
grep modem input02.txt | awk '{print $1}' | $distribution --rcfile=../distributionrc --width=110 --h=15 -c='|' -v -c 2> output103.txt | sort > output003.txt

echo -n "4. "
cat input03.txt | $distribution --rcfile=../distributionrc --size=large -height=8 -width=60 -t=/ --pallette=0,31,33,35,37 --c='()' > output004.txt 2> output104.txt

echo -n "5. "
cat input03.txt | $distribution --rcfile=../distributionrc -c=pc --w=48 -tokenize=word -match=num -size=large -verbose 2> output105.txt | sort -n > output005.txt

echo -n "6. "
for i in `seq 1 17 3141592` ; do echo $[ $i ^ ($i + 9) ]; done | cut -c 2-6 | $distribution --rcfile=../distributionrc -width=124 -height=29 -p=0,32,34,36,31 -c=^ --v > output006.txt 2> output106.txt

echo -n "7. "
cat input04.txt | awk '{print $8}' | $distribution --rcfile=../distributionrc -s=s --w=90 --char=Ξ > output007.txt 2> output107.txt

# get onto the newline
echo ""

echo "
Expected output:
 = b2d463a3fb20df2c01fb95b1e2006784  output001.txt
 = 6e03fecd199ec6e93540fbd08afe6b94  output002.txt
 = 4edb70a142774c686c9268b88a00cb01  output003.txt
 = 5902f595bd48b5eae51e4d655b85f44e  output004.txt
 = 83332608dffc4e6692049931c9c5d5fc  output005.txt
 = f993d1b611f5d23fde36590717a0cbec  output006.txt
 = bdf7a31f8b453e9075f63b6280749021  output007.txt

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

