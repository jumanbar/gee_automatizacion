#!/bin/bash

## Ejemplo:
# ./run_absent_days.sh 2016-09-01 2016-12-31

function pad () {
	if [ $1 -lt 10 ]; then
		echo "0$1"
	else
		echo $1
	fi

}

# FECHAS:
ini_date=$(date -d $1 "+%Y-%m-%d")
fin_date=$(date -d $2 "+%Y-%m-%d")

echo "FECHA INICIAL: $ini_date"
echo "FECHA FINAL: $fin_date"

# https://www.cyberciti.biz/faq/bash-for-loop/
for j in {1..60};
do
	DATE=$ini_date
	while [ $(date -d ${DATE} +%s) -le $(date -d ${fin_date} +%s) ]
	do
		echo "id_zona: $(pad $j) / 60 | FECHA: $DATE / $fin_date"
		HOUR=$(date "+%H%M%S")
		./main.py --id-zona $(pad $j) --end-date $DATE > log/log-z-$(pad $j)-$DATE-$HOUR.log
		# ./main.py --id-zona $(pad $j) --end-date $DATE > log/log-z-$(pad $j)-$DATE-$HOUR.log
		DATE=$(date -d "${DATE} +1 days" "+%Y-%m-%d")
	done;
done;
