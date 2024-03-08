#!/bin/bash

exitval=1;
usage() {
	echo
	echo "Uso : $0 <7|60>" 1>&2;
	echo
	echo Ejemplos:
	echo 	$0 7
	echo 	$0 60
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
	echo "Cambia nombre de log7.log o log60.log (le agrega la fecha al nombre)"
	echo "y los mueve a la carpeta de logs 7z/log o 60z/log respectivamente"
	usage
fi

[ $1 == 7 -o $1 == 60 ] || usage

DATE=$(date "+%Y%m%d")

cp log$1.log log$1-$DATE.log
mv log$1-$DATE.log ${1}z/log/

