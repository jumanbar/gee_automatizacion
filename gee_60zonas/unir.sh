#!/bin/bash

# Uso:
#
# ./unir.sh output

function pad () {
	if [ $1 -lt 10 ]
	then
		echo "0$1"
	else
		echo $1
	fi

}

if [ $(find -name "unir_files") ];
then
	echo "Borrando la carpeta 'unir_files'"
	rm -rf unir_files
fi

echo "Creando la carpeta 'unir_files'"

mkdir unir_files

for i in {1..60};
do
	# echo "va";
	N=$(pad $i)
	FILENAME=unir_files/zona-$N-todo.csv
	echo "Creando $FILENAME"

	# if [ $(ls $FILENAME) ];
	# then
		# rm $FILENAME
	# fi
	touch $FILENAME 

	head $(ls $1/zona-$N*.csv | head -n 1) -n 1 >> $FILENAME

	for a in $(ls $1/zona-$N*.csv);
	do
		# echo $a;
		tail $a -n +2 >> $FILENAME
	done;
done;

