#!/bin/bash

# https://stackoverflow.com/a/34531699/1030523
exitval=1;
usage() {
	echo
	echo "Uso :  $0 [-f <AAAA-MM-DD>] -n <7|60>" 1>&2;
	echo
	echo " -f    Fecha (i.e.: --end-date). Ej. 2024-10-31."
	echo "       Opcional. Por defecto, fecha corriente"
	echo
	echo " -n    Nro de zonas: 7 o 60"
	echo 
	echo " -h    Ayuda"
	echo
        echo Ejemplos:
        echo "   $0 -n 7"
	echo "   $0 -f 2024-01-24 -n 7"
	echo
	exit $exitval;
}

DATE=$(date "+%Y-%m-%d")
while getopts ":f:n:h" o; do
    case $o in
        f)  DATE=$OPTARG ;;
        n)  ZFOLDER=${OPTARG}z
	    N=$OPTARG
	    [ $N == 7 -o $N == 60 ] || usage ;;
	h)  exitval=0;
	    usage ;;
	:)  echo "Error: la opción -$OPTARG no puede estar vacía"
	    exitval=2
	    usage ;;
	?)  echo "Error: la opción -$OPTARG no existe"
	    exitval=3
	    usage ;;
	*)  usage ;;
    esac
done

if [ -z "${ZFOLDER}" ]; then
    echo
    echo "Error: no se indicó el argumento -n (7 o 60)"
    usage
fi

function pad () {
	if [ $1 -lt 10 ]; then
		echo "0$1"
	else
		echo $1
	fi
}

echo
echo ==========================================================================
echo Iniciando LOOP: $N ZONAS
echo

bf=$HOME/gee_automatizacion/$ZFOLDER
echo "  --end-date:    $DATE"
echo "  --base-folder: $bf"

echo
echo "FECHA: $(date '+%A %d de %B de %Y | %H:%M:%S')"
echo

SUMA=0

for (( z=1; z<=$N; z++ ));
do
	echo -n "id_zona: $(pad $z) / $(pad $N) | FECHA: $DATE"
	HOUR=$(date "+%H%M%S")
	./main.py -n $N --id-zona $(pad $z) --end-date $DATE > $bf/log/log-z-$(pad $z)-$DATE-$HOUR.log

	E=$(grep EXITO $bf/log/log-z-$(pad $z)-$DATE-$HOUR.log | sed "s/EXITO: //")
	SUMA=$((SUMA + E))
	echo " | Exito: $E | Total: $SUMA"
done;

echo "Total de extracciones exitosas: $SUMA"
echo
echo "FIN de la extracción: $(date '+%A %d de %B de %Y | %H:%M:%S')"

# cat $bf/log/log-z-$(pad $z)-$DATE-$HOUR.log

