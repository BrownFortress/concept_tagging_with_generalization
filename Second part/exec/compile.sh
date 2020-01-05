#!/bin/bash
#Produce different models
# Input: lexicon and data
lex=$1
data=$2
outputfolder=$3
subfolder=$4

farcompilestrings --symbols=$lex.txt --unknown_symbol="<unk>"  $data.txt > $data.far

declare -a arr=("witten_bell" "absolute" "katz" "kneser_ney" "presmoothed")



for i in `seq 1 4`;
   do
	rm -rf $outputfolder/$subfolder/$i
	mkdir -p $outputfolder/$subfolder/$i
        ngramcount --order=$i --require_symbols=false $data.far > $data$i.cnts
	for smooth in "${arr[@]}";
		do
		 ngrammake --method=$smooth $data$i.cnts > $outputfolder/$subfolder/$i/$smooth.lm
		done
   done
rm bin/*.far bin/*.cnts bin/*.lm
