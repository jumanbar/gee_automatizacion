#!/bin/bash

exitval=1;
usage() {
    echo
    echo "Uso :  $0 <AAAA-MM-DD> <AAAA-MM-DD> <4|7|60>" 1>&2;
    echo
    echo "Ejemplos:"
    echo "       $0 2024-03-01 2024-03-31 4  #  4 zonas (Santa Lucía)"
    echo "       $0 2024-01-01 2024-01-31 7  #  7 zonas (Río Negro)"
    echo "       $0 2024-02-06 2024-02-07 60 # 60 zonas (Río Negro)"
    echo
    exit $exitval;
}

while getopts "h" o; do
    case $o in
	h)  echo
	    echo "Corre el main.py para los días indicados por el usuario,"
	    echo "con fechas de inicio y fin."
	    usage ;;
    esac
done

if [ $# -lt 3 ]; then
    echo
    echo "Error: se necesitan dos fechas y un número (4, 7 o 60)  para correr el script."
    usage
fi

# FECHAS:
ini_date=$(date -d $1 "+%Y-%m-%d")
fin_date=$(date -d $2 "+%Y-%m-%d")
N=$3

echo "FECHA INICIAL: $ini_date"
echo "FECHA FINAL: $fin_date"
echo "MODO: $N ZONAS"

function pad () {
	if [ $1 -lt 10 ]; then
		echo "0$1"
	else
		echo $1
	fi
}

SUMA=0
# https://www.cyberciti.biz/faq/bash-for-loop/
for (( z=1; z<=$N; z++ ));
do
	DATE=$ini_date
	while [ $(date -d ${DATE} +%s) -le $(date -d ${fin_date} +%s) ]
	do
		echo -n "id_zona: $(pad $z) / $(pad $N) | FECHA: $DATE / $fin_date"
		HOUR=$(date "+%H%M%S")
		./main.py -n $N --id-zona $(pad $z) --end-date $DATE > ${N}z/log/log-z-$(pad $z)-$DATE-$HOUR.log
		E=$(grep EXITO ${N}z/log/log-z-$(pad $z)-$DATE-$HOUR.log | sed "s/EXITO: //") 
		SUMA=$((SUMA + E))
		DATE=$(date -d "${DATE} +1 days" "+%Y-%m-%d")
		echo " | Exito: $E | Total: $SUMA"
	done;
done;
echo "Total de extracciones exitosas: $SUMA"
exit

# cat $bf/log/log-z-$(pad $z)-$DATE-$HOUR.log

