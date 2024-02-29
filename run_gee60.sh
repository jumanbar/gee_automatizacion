#!/bin/bash

# Ejemplos
#   ./run_gee60.sh 2024-01-24
#   ./run_gee60.sh

# $1 = argumento 1 (FECHA)
# Ejemplo ./run_gee.sh 2024-01-24 # Indica que corra el script para la fecha 24 de enero de 2024

function pad () {
	if [ $1 -lt 10 ]; then
		echo "0$1"
	else
		echo $1
	fi
}

echo
echo ==========================================================================
echo Iniciando LOOP
echo

# Chequear si se invocó el script con o sin argumentos:
if [ $# -eq 0 ]; then
	echo "Sin argumentos: se usa la fecha actual"
	DATE=$(date "+%Y-%m-%d")
else
	DATE=$(date -d $1 "+%Y-%m-%d")
fi

bf=/home/jbarreneche/gee_60zonas
echo "	 --end-date: DATE"
echo "--base-folder: $bf"

echo
echo "FECHA: $(date '+%A %d de %B de %Y | %H:%M:%S')"
echo

SUMA=0
for z in {1..60};
do
	echo -n "id_zona: $(pad $z) / 60 | FECHA: $DATE"
	HOUR=$(date "+%H%M%S")
	./gee_60zonas/main.py --id-zona $(pad $z) --end-date $DATE\
		--base-folder $bf > $bf/log/log-z-$(pad $z)-$DATE-$HOUR.log

	E=$(grep EXITO $bf/log/log-z-$(pad $z)-$DATE-$HOUR.log | sed "s/EXITO: //")
	SUMA=$((SUMA + E))
	echo " | Exito: $E | Total: $SUMA"
done;

echo "Total de extracciones exitosas: $SUMA"

# cat $bf/log/log-z-$(pad $z)-$DATE-$HOUR.log
