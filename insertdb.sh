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

N=$1

if [ -z $N ]; then
	echo
	echo "Error: se necesita 1 argumento"
	usage
fi

if [ $N == "-h" ]; then
	echo
	echo "Inserta datos en 7z/output o 60z/output en la base de datos"
	echo "(tablas 7_zonas y 60_zonas, respectivamente)"
	usage
fi

[ $N == 7 -o $N == 60 ] || usage



DATE=$(date "+%Y%m%d")
echo "Ejecutando:"
echo "    ./insert_into_db.py -v -b ${N}z/output -t ${N}_zonas > ${N}z/log/INSERT-$DATE.log"
./insert_into_db.py -b ${N}z/output -t ${N}_zonas > ${N}z/log/INSERT-$DATE.log

echo
echo "LOG (${N}z/log/INSERT-$DATE.log):"
echo
cat ${N}z/log/INSERT-$DATE.log

