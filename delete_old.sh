#!/bin/bash

SEN="[[ $0 $@ ]]"
exitval=1;
usage() {
	echo
	echo "Sentencia: $SEN"
	echo
	echo "Uso : $0 DIR [-d N]" 1>&2;
	echo
	echo "      Borra todos los archivos más antiguos que N días de la carpeta DIR"
	echo
	echo " DIR"
	echo "      Ruta a una carpeta"   
	echo
	echo " -d, --dias=N"
	echo "      Número de días de antigüedad. Archivos más antiguos serán borrados."
	echo "      En caso de estar vacío, se usa 30 días como límite."
	echo
	echo " -h, --help"
	echo "      Mostrar esta ayuda"
	echo
	echo Ejemplos:
	echo "      $0 60z/log -d 7"
	echo "      $0 7z/output/done"
	echo
	exit $exitval;
}

DIAS=30


set -- `getopt -u -o d:h --long dias:,help: -- $@`
if [ $? != 0 ]; then
	usage
fi

while [ $1 != "--" ]; do
	case $1 in
		-d|--dias)
			DIAS=$2
			;;
		-h|--help)
			exitval=0
			usage
			;;
	esac
	shift
done
shift

if [ -z $1 ]; then
	echo
	echo "ERROR: no se especificó el directorio (DIR)"
	usage
fi
echo
echo "Borrando archivos antiguos en la carpeta $1 (>$DIAS días):"

# find $1 -mtime +30
for file in $(find $1 -mtime +$DIAS);
do
	echo "  > borrando $file";
	rm $file;
done;


exit

