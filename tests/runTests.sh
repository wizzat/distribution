#!/bin/sh

# make sure env is setup proper
if [ "xxx$distribution" == "xxx" ] ; then
	echo "To run tests, first export distribution=<pathToDistributionToTest>"
	exit 255
fi

# the tests
echo ""
printf "Running test: 1. "
cat stdin.01.txt | $distribution --rcfile=../distributionrc --graph --height=35 --width=120 --char=dt --color --verbose > stdout.01.actual.txt 2> stderr.01.actual.txt

printf "2. "
cat stdin.02.txt | awk '{print $4" "$5}' | $distribution --rcfile=../distributionrc -s=med --width=110 --tokenize=word --match=word -v -c > stdout.02.actual.txt 2> stderr.02.actual.txt

printf "3. "
grep modem stdin.02.txt | awk '{print $1}' | $distribution --rcfile=../distributionrc --width=110 -h=15 -c='|' -v -c 2> stderr.03.actual.txt | sort > stdout.03.actual.txt

printf "4. "
cat stdin.03.txt | $distribution --rcfile=../distributionrc --size=large --height=8 --width=60 -t=/ --palette=0,31,33,35,37 -c='()' > stdout.04.actual.txt 2> stderr.04.actual.txt

printf "5. "
cat stdin.03.txt | $distribution --rcfile=../distributionrc -c=pc -w=48 --tokenize=word --match=num --size=large --verbose 2> stderr.05.actual.txt | sort -n > stdout.05.actual.txt

printf "6. "
# generate a large list of deterministic but meaningless numbers
(( i=0 )) ; while [[ $i -lt 3141592 ]] ; do
	echo $(( i ^ (i+=17) ))
done | cut -c 2-6 | $distribution --rcfile=../distributionrc --width=124 --height=29 -p=0,32,34,36,31 -c=^ -v > stdout.06.actual.txt 2> stderr.06.actual.txt

printf "7. "
cat stdin.04.txt | awk '{print $8}' | $distribution --rcfile=../distributionrc -s=s -w=90 --char=Ξ > stdout.07.actual.txt 2> stderr.07.actual.txt

echo "done."

# be sure output is proper
printf "Comparing results: "
for i in 01 02 03 04 05 06 07 ; do
	printf "$i. "
	diff -w stdout.$i.expected.txt stdout.$i.actual.txt
	diff -w -I "runtime:" -I "" stderr.$i.expected.txt stderr.$i.actual.txt
done

echo "done."

# clean up
rm stdout.*.actual.txt stderr.*.actual.txt
