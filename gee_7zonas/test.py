import sys
import os

print('=== INICIANDO test.py ===\n')
print("Carpeta de ejecucion:", os.getcwd())

# sys.path.append('/home/jbarreneche/modules')

import inifun as ini

print(ini.rangoFechas(10000))
print(ini.readArgs(sys.argv[1:]))

# AGREGAR MENSAJES DE ERROR PARA CUANDO LOS ARGUMENTOS INGRESADOS NO SIRVEN
# Y MENSAJES DE ADVERTENCIA CUANDO SE USAN LOS VALORES POR DEFECTO

name_of_script = sys.argv[0]
args = sys.argv[1:]
zona = 'PALMAR'
id_zona = 1
base_folder = os.path.dirname(os.path.realpath(__file__))

id_zona_dic = {
    'PALMAR': 1,
    'ANDRESITO': 2,
    'MOLLES DE PORRUA': 3,
    'BAYGORRIA': 4,
    'PASO DE LOS TOROS': 5,
    'BONETE': 6,
    'SAN GREGORIO DE POLANCO': 7
}

asset_string_dic = {
    'PALMAR': 'users/brunogda/zonas_palmar_represa_dis',
    'ANDRESITO': 'users/brunogda/zonas_andresito_dis',
    'MOLLES DE PORRUA': 'users/brunogda/zonas_palmar_andresito_dis',
    'BAYGORRIA': 'users/brunogda/zonas_baygorria_represa_dis',
    'PASO DE LOS TOROS': 'users/brunogda/zonas_baygorria_pdlt_dis',
    'BONETE': 'users/brunogda/zonas_bonete_represa_dis',
    'SAN GREGORIO DE POLANCO': 'users/brunogda/zonas_bonete_polanco_dis'
}

for i, a in enumerate(args):
    if a == '--base-folder':
        base_folder = args[i + 1]
    if a == '--zona':
        zona = args[i + 1]
    if a == '--id-zona':
        id_zona = args[i + 1]


for k, v in id_zona_dic.items():
    if str(v) == id_zona:
        if zona != k:
            print('El --id-zona (' + id_zona + ') ' + 
                'no coincide con la --zona indicada ("' + zona + '"): ' +
                'se cambia la zona a "' + k + '"')
        zona = k


print('zona:', zona)
print('base_folder:', base_folder)
print('id_zona:', id_zona)
print(os.path.isdir(base_folder)) # Para ver si existe el directorio.




"""
Comentarios 
"""