#! /usr/bin/env python

import mariadb
import sys
import csv
import os
import shutil
from datetime import datetime as dt
import glob
import irncon
import argparse as ap

examples = '''Ejemplos:
    # Elegir la carpeta de base:
    ./%(prog)s -d 60z/output -t 60_zonas
    ./%(prog)s --data-folder 60z/output -t 60_zonas

    # Elegir tabla en donde insertar los datos:
    ./%(prog)s -t 7_zonas -d 7z/output
    ./%(prog)s --table 7_zonas -d 7z/output
    '''

parser = ap.ArgumentParser(
    description="""
    Importar CSVs desde una carpeta (--data-folder) hacia la BD "datos_irn".
    Los CSVs son luego movidos a una subcarpeta: "{--data-folder}/done"
    """,
    epilog=examples,
    formatter_class=ap.RawDescriptionHelpFormatter
)
parser.add_argument(
    '-v', '--verbose',
    action='store_true',
    help="""
        Imprime lista de archivos a importar y las sentencias SQL INSERT.
    """)
parser.add_argument(
    '-t', '--table',
    help="""Tabla en la que hacer los INSERTs. Por ejemplo: "60_zonas".""",
    required=True, choices=['4_zonas', '7_zonas', '60_zonas'])
parser.add_argument(
    '-d', '--data-folder',
    help="""
        Carpeta en donde se guardan los CSV. Por ejemplo: "60z/output".
        """,
    required=True)
parser.add_argument(
    '-k', '--keep-data-in-place',
    help="""
    A menos que se use `-k`, los archivos ya leídos y procesados se mueven a
    una subcarpeta: `--data-folder`/done.
    """,
    required=False, action='store_true')

args = parser.parse_args()
move = not args.keep_data_in_place

# Inicio --------
print('\n### INICIANDO ' + '-'*66 + '\n')

condic = irncon.getConndetails()

if args.verbose:
    print('\tCSV Folder: ' + args.data_folder + '\n')
    print('\tInserciones en la tabla: datos_irn.' + args.table + '\n')

try:
    conn = mariadb.connect(
        user=condic['user'],
        password=condic['password'],
        host=condic['host'],
        port=int(condic['port']),
        database=condic['database']
    )

except mariadb.Error as e:
    print(f'Error connecting to MariaDB Platform: {e}')
    sys.exit(1)

cur = conn.cursor()

csv_list = glob.glob(os.path.join(args.data_folder, 'zona*csv'))
N = len(csv_list)

print('\tNro de archivos CSV: ' + str(N) + '\n')
if N == 0:
    print('\tNingun archivo para importar. Finalizando')
    print('\n### FINALIZANDO ' + '-'*64 + '\n')
    sys.exit(0)

if move:
    print('\tMover a subcarpeta? Sí')
    print('\t\tDestino : ', os.path.join(args.data_folder, 'done'), '\n')
else:
    print('\tMover a subcarpeta? No\n')

if args.verbose and N > 0:
    print('LISTA de CSVs:\n')
    print('- ' + '\n- '.join(csv_list))
    print('\n')

if move and not os.path.isdir(os.path.join(args.data_folder, 'done')):
    os.mkdir(os.path.join(args.data_folder, 'done'))

sql_base = f"""
    INSERT IGNORE INTO {args.table}
    (time_start,\tvalor,\tid_zona,\tid_parametro,\tpercentil,\tfecha_insercion)
    \nVALUES
    """

total = str(N)
for i in range(len(csv_list)):

    ncurr = str(i + 0).rjust(len(total), ' ')
    prc = (i + 1) / N

    print(f'||------------ ({ncurr} / {total}; {prc:.1%}) {csv_list[i]}',
          '------------||')

    with open(csv_list[i]) as csvfile:
        values = []
        reader = csv.reader(csvfile)
        next(reader)

        for row in reader:
            insertdate = dt.today().strftime('%Y-%m-%d %H:%M:%S.%f')
            values.append(
                f'("{row[0].split("T")[0]}",\t{float(row[1]): .03f},' +
                f'\t{row[2]},\t\t{row[3]},\t\t{row[4]},\t\t"{insertdate}")'
            )

        if len(values) == 0:
            if move:
                shutil.move(csv_list[i], os.path.join(
                    args.data_folder, 'done'))
            if args.verbose:
                print('\n\tArchivo vacío. Continuando con el siguiente.\n')
            continue

        sql = sql_base + ',\n\t'.join(values)
        if args.verbose:
            print('\nSQL:\n')
            print(sql)
            print('\n\n ~~ FILE END\n')

        try:
            cur.execute(sql)
        except mariadb.Error as e:
            print(f'Error: {e}')
        conn.commit()

    if move:
        shutil.move(csv_list[i], os.path.join(
            args.data_folder, 'done', os.path.split(csv_list[i])[1]))


# free resources
cur.close()
conn.close()
print('\n### FINALIZANDO ' + '-'*64 + '\n')
sys.exit(0)
