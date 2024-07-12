import os
import pathlib
# from os.path import dirname, realpath
import datetime
import argparse as ap
examples = '''Ejemplos:
    ./%(prog)s -z 3 -n 7
    ./%(prog)s -z 33 -n 60
    ./%(prog)s -z 2 -n 7 -e 2024-02-06
    '''

parser = ap.ArgumentParser(
    description='Correr comandos de la API de GEE para obtener estimaciones de parámetros con imágenes satelitales. Guarda los resultados (CSV) en subcarpeta "output".',
    epilog=examples,
    formatter_class=ap.RawDescriptionHelpFormatter
    # formatter_class=ap.ArgumentDefaultsHelpFormatter
)

parser.add_argument('-z', '--id-zona', help='ID de la zona de la cual se quieren extraer los datos.',
                    required=True, type=int)
parser.add_argument('-e', '--end-date', help='La Fecha de extracción (por defecto: fecha actual). Ejemplo: 2024-01-31',
                    required=False, default=datetime.datetime.now().strftime("%Y-%m-%d"))
parser.add_argument('-n', '--nzonas', help='Define si se trabaja con 7 o 60 zonas.',
                    required=True, default=7, choices=[7, 60], type=int)
parser.add_argument('-o', '--overwrite', help='Sobreescribir resultados?',
                    required=False, action='store_true')

# ZONAS ======
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


def siono(booleano):
    return 'Sí' if booleano else 'No'


def rangoFechas(n, end_date=None):
    """
    La función `rangoFechas` devuelve una lista de dos fechas, comenzando desde hace `n` días y
    terminando en la `fecha_final` especificada o en la fecha actual si no se proporciona la
    `fecha_final`.

    :param n: El parámetro "n" representa el número de días para retroceder desde la fecha actual.
    Determina la fecha de inicio del rango de fechas
    :param end_date: El parámetro `end_date` es un parámetro opcional que especifica la fecha de
    finalización del rango de fechas. Si no se proporciona ninguna `fecha_finalización`, la fecha actual
    se utiliza como fecha de finalización
    :return: La función `rangoFechas` devuelve una lista que contiene dos elementos: la fecha inicial y
    la fecha final.
    """
    # Fechas (de ahora a 30 días para atrás)
    if (end_date is None):
        ahora = datetime.datetime.now()
        end_date = ahora.strftime("%Y-%m-%d")
    else:
        ahora = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    ini_date = ahora - datetime.timedelta(days=n)
    ini_date = ini_date.strftime("%Y-%m-%d")

    return [ini_date, end_date]


def pad(n):
    """
    La función rellena un número de un solo dígito con un cero a la izquierda.

    :param n: El parámetro "n" es un número entero que representa un número
    :return: una representación de cadena del número de entrada, con un '0' inicial si el número es
    menor que 10.
    """
    if int(n) < 10:
        return '0' + str(n)
    return str(n)


def getZona(zona):
    return asset_string_dic[zona]


def getAssetFromIdZona(id_zona):
    id_zona = int(id_zona)
    zona = ''
    idz_keys = id_zona_dic.keys()
    for i, k in enumerate(idz_keys):
        if (i + 1) == id_zona:
            return asset_string_dic[k]

    return None


def isValidZoneID(id_zona, nzonas):
    id_zona = int(id_zona)
    nzonas = int(nzonas)
    if id_zona < 0 or id_zona > nzonas:
        raise Exception('id_zona = ' + str(id_zona) + ', pero debe estar entre 1 y ' +
                        str(nzonas) + ' para el modo ' + str(nzonas) + ' ZONAS')
        return -1
    return


def getAssetFromIdZona60(n):
    """
    La función `getAssetFromIdZona60` devuelve una ruta de archivo concatenando una cadena fija con el valor
    rellenado del número de entrada y otra cadena fija.

    :param n: El parámetro `n` es un número entero que representa un número
    :return: una cadena que representa una ruta de archivo.
    """
    return 'users/brunogda/RN60/' + pad(int(n)) + '_rn'


def printZonasPosibles():
    """
    La función "printZonasPosibles" imprime una lista de zonas junto con sus números correspondientes.
    """
    print('ZONAS:')
    for i in range(1, 8):
        for k, v in id_zona_dic.items():
            if v == i:
                print('\t' + str(i) + '. ' + k)


def esZonaValida(zona):
    """
    La función "esZonaValida" comprueba si una determinada "zona" es una clave válida en el diccionario
    "id_zona_dic".

    :param zona: El parámetro "zona" representa una zona
    :return: un valor booleano que indica si la "zona" dada es una clave válida en el diccionario
    "id_zona_dic".
    """
    es = False
    idz_keys = id_zona_dic.keys()
    for i, k in enumerate(idz_keys):
        if zona == k:
            es = True
            break
    return es


def esIdZonaValido(id_zona):
    """
    La función `esIdZonaValido` comprueba si un determinado `id_zona` es válido comparándolo con los
    valores del diccionario `id_zona_dic`.

    :param id_zona: El parámetro `id_zona` es el ID de una zona cuya validez debe verificarse
    :return: un valor booleano que indica si la `id_zona` dada es válida o no.
    """
    es = False
    for t in id_zona_dic.items():
        if t[1] == id_zona:
            es = True
            break
    return es
