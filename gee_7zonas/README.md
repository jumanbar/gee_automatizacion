# Ejemplo de ejecucion manual

```sh
python3 main.py --id-zona 1                       # Fecha actual
python3 main.py --id-zona 1 --end-date 2023-04-16 # Fecha elegida
```

# Llenar fechas vacías

Ver el script `run_absent_days.sh`:

```sh
for j in {2..7};
do
	for i in 05 06 07 08 09 {10..30}; 
	do
		python3 main.py --id-zona $j --end-date 2023-09-$i; 
		sleep 1; 
	done;

	for i in 01 02; 
	do
		python3 main.py --id-zona $j --end-date 2023-10-$i; 
		sleep 1; 
	done;
done
```

