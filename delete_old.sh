#!/bin/bash

exitval=1;
usage() {
	echo
	echo "Uso : $0 <directorio>" 1>&2;
	echo
	echo Ejemplos:
	echo 	$0 60z/log
	echo 	$0 7z/output/done
	echo
	exit $exitval;
}

if [ -z $1 ]; then
	echo
	echo "Error: se necesita 1 argumento"
	usage
fi
if [ $1 == "-h" ]; then
	echo
	echo "Borra archivos de más de 30 días de antigüedad en una carpeta CUALQUIERA"
	usage
fi

# find $1 -mtime +30
for file in $(find $d -mtime +30);
do
	echo "Deleting $file";
	rm $file;
done;

