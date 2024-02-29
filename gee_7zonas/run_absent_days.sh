#!/bin/bash

## Ejemplo:
# ./run_absent_days.sh 2016-09-01 2016-12-31

# FECHAS:
ini_date=$(date -d $1 "+%Y-%m-%d")
fin_date=$(date -d $2 "+%Y-%m-%d")

echo "FECHA INICIAL: $ini_date"
echo "FECHA FINAL: $fin_date"

# https://www.cyberciti.biz/faq/bash-for-loop/
for j in {1..7};
do
	DATE=$ini_date
	while [ $(date -d ${DATE} +%s) -le $(date -d ${fin_date} +%s) ]
	do
		echo "id_zona: $j / 60 | FECHA: $DATE / $fin_date"
		HOUR=$(date "+%H%M%S")
		./main.py --id-zona $j --end-date $DATE > log/log-z-$j-$DATE-$HOUR.log
		DATE=$(date -d "${DATE} +1 days" "+%Y-%m-%d")
	done;
done;

