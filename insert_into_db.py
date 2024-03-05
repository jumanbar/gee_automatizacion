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
    ./%(prog)s -b gee_60zonas/output -t 60_zonas
    ./%(prog)s --csv-folder gee_60zonas/output -t 60_zonas

    # Elegir tabla en donde insertar los datos:
    ./%(prog)s -t 7_zonas -b gee_7zonas/output
    ./%(prog)s -table 60_zonas -b gee_7zonas/output
    '''

parser = ap.ArgumentParser(
        description = 'Importar CSVs desde una carpeta (--csv-folder) hacia la BD "datos_irn". Los CSVs son luego movidos a una subcarpeta: "{--csv-folder}/done"',
        epilog = examples,
        formatter_class = ap.RawDescriptionHelpFormatter
        )
parser.add_argument('-v', '--verbose', help = 'Imprime lista de archivos a importar y las sentencias SQL INSERT.', action = 'store_true')
parser.add_argument('-t', '--table', help = 'Tabla en la que hacer los INSERTs. Por ejemplo: "60_zonas"', required = True) # , default = '60_zonas')
parser.add_argument('-b', '--csv-folder', help = 'Carpeta en donde se guardan los CSV. Por ejemplo: "gee_60zonas/output"', required = True) # , default = 'gee_60zonas/output')

args = parser.parse_args()
# print(args)
# Namespace(verbose=True, table='60_zonas', csv_folder='gee_60zonas/')
# sys.exit(0)

print('\n### INICIANDO ' + '-'*66 + '\n')

condic = irncon.getConndetails()

if args.verbose:
    print('\tCSV Folder: ' + args.csv_folder + '\n')
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

csv_list = glob.glob(os.path.join(args.csv_folder, 'zona*csv'))
N = len(csv_list)

print('\tNro de archivos CSV: ' + str(N) + '\n')

if N == 0:
    print('\tNingun archivo para importar. Finalizando')
    print('\n### FINALIZANDO ' + '-'*64 + '\n')
    sys.exit(0)

if args.verbose and N > 0:
    print('LISTA de CSVs:\n')
    print('- ' + '\n- '.join(csv_list))
    print('\n')

if not os.path.isdir(os.path.join(args.csv_folder, 'done')):
    os.mkdir(os.path.join(args.csv_folder, 'done'))

# Nota: IGNORE se usa para que los casos que puedan duplicar al PRIMARY KEY sean ignorados
sql_base = 'INSERT IGNORE INTO ' + args.table +\
        '\n\t(time_start,\tvalor,\tid_zona,\tid_parametro,\tpercentil,\tfecha_insercion)' +\
        '\nVALUES\n\t'

for i in range(len(csv_list)):

    prc = (i + 1) / N

    print('||------------ (' + str(i + 1) + ' / ' + str(N) + '; ' + f'{prc:.1%}' + ') ' + csv_list[i] +\
            ' ------------||')

    with open(csv_list[i]) as csvfile:
        values = []
        reader = csv.reader(csvfile)
        next(reader)

        for row in reader:
            values.append(\
                '("'  + row[0].split('T')[0] + '",\t' + str(round(float(row[1]), 3)) + \
                ',\t' + row[2] + ',\t\t' + row[3] + \
                ',\t\t' + row[4] + ',\t\t"' + dt.today().strftime('%Y-%m-%d %H:%M:%S.%f') + '")')

        if len(values) == 0:
            shutil.move(csv_list[i], os.path.join(args.csv_folder, 'done'))
            if args.verbose:
                print('\n\tArchivo vacío. Continuando con archivo siguiente.\n')
            continue

        sql=sql_base + ',\n\t'.join(values)
        if args.verbose:
            print('\nSQL:\n')
            print(sql)
            print('\n\n ~~ FILE END\n')

        try: cur.execute(sql)
        except mariadb.Error as e:
            print(f'Error: {e}')
        conn.commit()

    shutil.move(csv_list[i], os.path.join(args.csv_folder, 'done'))


# free resources
cur.close()
conn.close()
print('\n### FINALIZANDO ' + '-'*64 + '\n')
sys.exit(0)

