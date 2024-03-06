#!/bin/bash

# Ejemplos
#   ./run_gee.sh 2024-01-24
#   ./run_gee.sh

# $1 = argumento 1 (FECHA)
# Ejemplo ./run_gee.sh 2024-01-24 # Indica que corra el script para la fecha 24 de enero de 2024

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

bf=$HOME/gee_automatizacion/gee_7zonas
echo "--end-date:    $DATE"
echo "--base-folder: $bf"

echo
echo "FECHA: $(date '+%A %d de %B de %Y | %H:%M:%S')"
echo

SUMA=0

for z in {1..7};
do
	echo -n "id_zona: $z / 7 | FECHA: $DATE"
	HOUR=$(date "+%H%M%S")
	./gee_7zonas/main.py --id-zona $z --end-date $DATE\
		--base-folder $bf > $bf/log/log-z-$z-$DATE-$HOUR.log

	E=$(grep EXITO $bf/log/log-z-$z-$DATE-$HOUR.log | sed "s/EXITO: //")
	SUMA=$((SUMA + E))
	echo " | Exito: $E | Total: $SUMA"
done;

echo
echo "Total de extracciones exitosas: $SUMA"
echo

# cat $bf/log/log-z-$(pad $z)-$DATE-$HOUR.log
