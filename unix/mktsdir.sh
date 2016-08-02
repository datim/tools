#!/bin/bash
# create a directory with a timestamp.  Optionally provide the directory name
# example directory name [TIMESTAMP]-[DIRECTORY NAME]

datestring=`date +"%y-%m-%d_%H-%M-%S"`

if [ $# -eq 1 ] 
then
	# input directory provided
	dir_name=$datestring"_"$1
	echo "create dir $dir_name"
	mkdir $dir_name
else
	# no directory name provided. Just make timestamp dir
	echo "create dir $datestring"
	mkdir $datestring
fi
