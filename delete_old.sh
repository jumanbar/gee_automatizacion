#!/bin/bash

# find $1/log -mtime +30

for l in $(find $1 -mtime +30);
do
	echo "Deleting $l";
	rm $l;
done;

