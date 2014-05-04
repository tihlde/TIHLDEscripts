#!/bin/bash


DIR=$1
if [[ $DIR == "" ]]; then
    echo "Dir-argument emtpy!"
    exit 1
fi

if [ ! -d $DIR ];then
    echo "Not a dir"
    exit 1
fi

let kilobyte=1024
let megabyte=$(($kilobyte*1024))
let gigabyte=$(($megabyte*1024))
let terabyte=$(($gigabyte*1024))

find $DIR -type f -print0 | xargs -0 ls -l | awk '{print $3 " " $5}' | sort > tempfile1

for user in `cat tempfile1 | awk '{print $1}' | sort | uniq`; do
    bytes=$(cat tempfile1 | grep $user | awk '{print $2}' | paste -sd+ | bc)
    if (($bytes < $kilobyte)); then
        echo -n $bytes $bytes" B" >> tempfile2
    elif (($bytes < $megabyte)); then
        echo -n $bytes $(($bytes/$kilobyte))" KB" >> tempfile2
    elif (($bytes < $gigabyte)); then
        echo -n $bytes $(($bytes/$megabyte))" MB" >> tempfile2
    elif (($bytes < $terabyte)); then
        echo -n $bytes $(($bytes/$gigabyte))" GB" >> tempfile2
    else
        echo -n $bytes $(($bytes/$terabyte))" TB" >> tempfile2
    fi
    echo " uploaded by $user" >> tempfile2
done

cat tempfile2 | sort -nr | awk '{for (i=2;i<=NF;i++) printf $i" "; print '\n' }'

rm tempfile1 tempfile2

exit 0
