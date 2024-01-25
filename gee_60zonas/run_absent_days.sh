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
# ini_date=$(date -d "2023-06-01" "+%Y-%m-%d")
# fin_date=$(date -d "2023-06-02" "+%Y-%m-%d")
ini_date=$(date -d $1 "+%Y-%m-%d")
fin_date=$(date -d $2 "+%Y-%m-%d")

echo "FECHA INICIAL: $ini_date"
echo "FECHA FINAL: $fin_date"
# echo "FECHA INICIAL NUM: $(date -d ${ini_date} +%s)"
# echo "FECHA FINAL NUM: $(date -d ${fin_date} +%s)"


for j in {1..60};
do
	DATE=$ini_date
	while [ $(date -d ${DATE} +%s) -le $(date -d ${fin_date} +%s) ]
	do
		echo "id_zona: $(pad $j) / 60 | FECHA: $DATE / $fin_date"
		python3 main.py --id-zona $(pad $j) --end-date $DATE > log/log-z-$(pad $j)-$DATE.log
		DATE=$(date -d "${DATE} +1 days" "+%Y-%m-%d")
	done;
done;

# if [ $A -lt 10 ] ; then echo "0$A"; fi
# date '+%Y-%m-%d' -d '-1 days'
# $(date "+%Y-%m-%d" -d "-${!A} days")
# date -d "2023-11-11" "+%Y-%m-%d"
# date -d $fin_date -d "-1000 days"

# python3 main.py --id-zona 1 --end-date 2023-11-25
