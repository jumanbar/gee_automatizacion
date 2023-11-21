from os import getcwd
# from os.path import dirname, realpath
import datetime

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

def rangoFechas(n, end_date = None):
    # Fechas (de ahora a 30 días para atrás)
    if (end_date is None):
        ahora = datetime.datetime.now()
        end_date = ahora.strftime("%Y-%m-%d")
    else:
        ahora = datetime.datetime.strptime(end_date,'%Y-%m-%d')
    ini_date = ahora - datetime.timedelta(days=n)
    ini_date = ini_date.strftime("%Y-%m-%d")

    return [ini_date, end_date]


def pad(n):
    if n < 10:
        return '0' + str(n)
    return str(n)

def getZona60(n):
    return 'users/brunogda/RN60/' + pad(n) + '_rn'


def printZonasPosibles():
    print('ZONAS:')
    for i in range(1, 8):
        for k, v in id_zona_dic.items():
            if v == i:
                print('\t' + str(i) + '. ' + k)

def esZonaValida(zona):
    es = False
    idz_keys = id_zona_dic.keys()
    for i, k in enumerate(idz_keys):
        if zona == k:
            es = True
            break
    return es

def esIdZonaValido(id_zona):
    es = False
    for t in id_zona_dic.items():
        if t[1] == id_zona:
            es = True
            break
    return es

def readArgs(args, ndias=30):

    # AGREGAR MENSAJES DE ERROR PARA CUANDO LOS ARGUMENTOS INGRESADOS NO SIRVEN
    # Y MENSAJES DE ADVERTENCIA CUANDO SE USAN LOS VALORES POR DEFECTO

    zona = 'PALMAR'
    id_zona = 1
    # base_folder = dirname(realpath(__file__))
    base_folder = getcwd()
    end_date = None

    has_zona_arg = False
    has_id_zona_arg = False
    has_base_folder_arg = False

    for i, a in enumerate(args):
        if a == '--zona':
            has_zona_arg = True
            zona = args[i + 1]
            if not esZonaValida(zona):
                print('[[ E ]]: La --zona ingresada ("' + zona + '")' +
                      ' no está dentro de las opciones posibles:')
                printZonasPosibles()
                return { 'error': True }
        if a == '--id-zona':
            has_id_zona_arg = True
            id_zona = int(args[i + 1])
            if not esIdZonaValido(id_zona):
                print('[[ E ]]: La --id-zona ingresada (' + str(id_zona) + ')' +
                      ' no está dentro de las opciones posibles:')
                printZonasPosibles()
                return { 'error': True }
        if a == '--base-folder':
            has_base_folder_arg = True
            base_folder = args[i + 1]
        if a == '--end-date':
            end_date = args[i + 1]

    if has_id_zona_arg:
        for k, v in id_zona_dic.items():
            if v == id_zona:
                if has_zona_arg and zona != k:
                    print('[[ W ]]: El --id-zona (' + str(id_zona) + ') ' +
                          'no coincide con la --zona indicada ("' +
                          zona + '"): ' + 'se cambia la zona a "' + k + '"')
                zona = k
                break

    if not has_id_zona_arg:
        id_zona = id_zona_dic[zona]

    asset_string = asset_string_dic[zona]
    rf = rangoFechas(ndias, end_date)

    if not has_zona_arg and not has_id_zona_arg:
        print('[[ W ]]: Se usan los valores por defecto de' +
              ' --zona ("' + zona + '") e --id-zona (' + str(id_zona) + ')')

    if not has_base_folder_arg:
        print('[[ W ]]: Se usa el valor por defecto de --base-folder: ' +
              base_folder + ' (carpeta actual)')

    out = {
        'error': False,
        'zona': zona,
        'base_folder': base_folder,
        'id_zona': id_zona,
        'asset_string': asset_string,
        'rf': rf
    }

    return out

def readArgs60(args, ndias = 2):

    id_zona = 1

    base_folder = getcwd()
    end_date = None

    has_base_folder_arg = False

    for i, a in enumerate(args):
        if a == '--id-zona':
            id_zona = int(args[i + 1])
            if (id_zona < 1 or id_zona > 60):
                print('[[ E ]]: La --id-zona ingresada (' + str(id_zona) + ')' +
                      ' no está dentro de las opciones posibles: 1-60')
                return { 'error': True }

        if a == '--base-folder':
            has_base_folder_arg = True
            base_folder = args[i + 1]
        if a == '--end-date':
            end_date = args[i + 1]

    asset_string = getZona60(id_zona)

    rf = rangoFechas(ndias, end_date)

    if not has_base_folder_arg:
        print('[[ W ]]: Se usa el valor por defecto de --base-folder: ' +
              base_folder + ' (carpeta actual)')

    out = {
        'error': False,
        'base_folder': base_folder,
        'id_zona': id_zona,
        'asset_string': asset_string,
        'rf': rf
    }

    return out

