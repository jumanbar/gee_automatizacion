#! /usr/bin/env python

import mariadb
import sys
import csv
import os
import glob
import irncon

verbose = False
# base_folder = os.getcwd()
base_folder = 'gee_60zonas'
table = '60_zonas'

for i, arg in enumerate(sys.argv):

    if i == 0:
        continue

    if arg == "--help" or arg == "-h":
        print("\nNOMBRE:")
        print("\tinsert_into_db.py - Importar CSV desde la carpeta 'output' a la BD 'datos_irn'i\n")
        print("SINOPSIS:")
        print("\t./insert_into_db.py [OPCIÓN]\n")
        print("DESCRIPCIÓN:")
        print("\tImporta a la Base de Datos 'datos_irn' los archivos CSV contenidos en la carpeta")
        print("\t'output', siempre y cuando sigan el patrón 'zona*csv' (ej.: zona-01de60-2016-09-27)\n")
        print("\t'-v' o '--verbose'\n\t\tImprime lista de archivos a importar y las sentencias SQL INSERT\n")
        print("\t'-h' o '--help'\n\t\tImprime esta ayuda y finaliza\n")
        print("\t'-b' o '--base-folder'\n\t\tCarpeta de base (debe incluir una carpeta llamada 'output').")
        print("\t\tPor defecto usa gee_60zonas.\n")
        print("\t'-t' o '--table'\n\t\tTabla en la que hacer los INSERTs. Por defecto usa 60_zonas.\n")
        print("EJEMPLOS:")
        print("\t./insert_into_db.py")
        print("\n\t# Los dos siguientes son equivalentes:\n")
        print("\t./insert_into_db.py -v")
        print("\t./insert_into_db.py --verbose\n")
        print("\n\t# Elegir la carpeta de base:\n")
        print("\t./insert_into_db.py -b gee_60zonas")
        print("\t./insert_into_db.py --base-folder gee_60zonas\n")
        print("\n\t# Elegir tabla en donde insertar los datos:\n")
        print("\t./insert_into_db.py -t 7_zonas")
        print("\t./insert_into_db.py -table 60_zonas\n")
        sys.exit(0)

    if arg == "--verbose" or arg == "-v":
        verbose = True

    if arg == "--base-folder" or arg == "-b":
        base_folder = sys.argv[i + 1]

    if arg == "--table" or arg == "-t":
        table = sys.argv[i + 1]

print("\n### INICIANDO " + "-"*66 + "\n")

condic = irncon.getConndetails()

if verbose:
    print("\tBase Folder: " + base_folder + "\n")
    print("\tInserciones en la tabla datos_irn." + table + "\n")

try:
    conn = mariadb.connect(
            user=condic["user"],
            password=condic["password"],
            host=condic["host"],
            port=condic["port"],
            database=condic["database"]
            )

except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

cur = conn.cursor()

csv_list = glob.glob(os.path.join(base_folder, "output", "zona*csv"))
N = len(csv_list)

print("\tNro de archivos CSV: " + str(N) + "\n")

if N == 0:
    print("\tNingun archivo para importar. Finalizando")
    print("\n### FINALIZANDO " + "-"*64 + "\n")
    sys.exit(0)

if verbose and N > 0:
    print("LISTA de CSVs:\n")
    print("- " + "\n- ".join(csv_list))
    print("\n")


# Nota: IGNORE se usa para que los casos que puedan duplicar al PRIMARY KEY sean ignorados
sql_base = "INSERT IGNORE INTO " + table +\
        "\n\t(time_start,\tvalor,\tid_zona,\tid_parametro,\tpercentil,\tfecha_insercion)" +\
        "\nVALUES\n\t" 

for i in range(len(csv_list)):

    prc = (i + 1) / N

    print("||------------ (" + str(i + 1) + " / " + str(N) + "; " + f"{prc:.1%}" + ") " + csv_list[i] +\
            " ------------||")

    with open(csv_list[i]) as csvfile:
        values = []
        reader = csv.reader(csvfile)
        next(reader)

        for row in reader:
            values.append(\
                "('"  + row[0].split("T")[0] + "',\t" + str(round(float(row[1]), 3)) + \
                ",\t" + row[2] + ",\t\t" + row[3] + \
                ",\t\t" + row[4] + ",\t\t'" + row[5] + "')")

        if len(values) == 0:
            if verbose:
                print("\n\tArchivo vacío. Continuando con archivo siguiente.\n")
        
            continue

        sql=sql_base + ",\n\t".join(values)
        if verbose:
            print("\nSQL:\n")
            print(sql)
            print("\n\n ~~ FILE END\n")

        try: cur.execute(sql)
        except mariadb.Error as e:
            print(f"Error: {e}")
        conn.commit()



# free resources
cur.close()
conn.close()
print("\n### FINALIZANDO " + "-"*64 + "\n")
sys.exit(0)

### FIN ############################################################################################

# Apuntes anteriores:

# Opcion 1: escribir el SQL completo:
sql = "INSERT INTO 60_zonas (\
         time_start, valor, id_zona, id_parametro, percentil, fecha_insercion\
       ) VALUES \
         ('2024-01-22', 3.1415, 444, 2000, 0, '2024-01-22 10:03:13.000'),\
         ('2024-01-22', 3.1415, 444, 2001, 0, '2024-01-22 10:03:13.000'),\
         ('2024-01-22', 3.1415, 444, 2002, 0, '2024-01-22 10:03:13.000'),\
         ('2024-01-22', 3.1415, 444, 2003, 0, '2024-01-22 10:03:13.000'),\
         ('2024-01-22', 3.1415, 444, 2004, 0, '2024-01-22 10:03:13.000')\
       "
try: cur.execute(sql)
except mariadb.Error as e:
    print(f"Error: {e}")


# Opcion 2: usar ? como comodines para rellenar con un array:
sql = "INSERT INTO 60_zonas (time_start, valor, id_zona, id_parametro, percentil, fecha_insercion)\
    VALUES (?, ?, ?, ?, ?, ?)"

data = [("2000-01-28", "3.1415", "10", "8888", "JMB", "2000-01-28 10:03:13.000"),
        ("2000-01-28", "3.1415", "11", "8888", "77", "2000-01-28 10:03:13.000"),
        ("2000-01-28", "3.1415", "12", "8888", "77", "2000-01-28 10:03:13.000"),
        ("2000-01-28", "3.1415", "13", "8888", "77", "2000-01-28 10:03:13.000"),
        ("2000-01-28", "3.1415", "14", "8888", "77", "2000-01-28 10:03:13.000"),
        ("2000-01-28", "3.1415", "15", "8888", "77", "2000-01-28 10:03:13.000"),
        ("2000-01-28", "3.1415", "16", "8888", "77", "2000-01-28 10:03:13.000")]

try: cur.executemany(sql, data)
except mariadb.Error as e:
    print(f"Error: {e}")

# Nota: si es una sola fila, se puede usar cur.execute, en vez de cur.executemany

conn.commit()

# free resources
cur.close()
conn.close()

