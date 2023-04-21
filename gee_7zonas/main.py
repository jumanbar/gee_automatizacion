import sys
import os

print('=== INICIANDO main.py ===\n')

print("Carpeta de ejecucion:", os.getcwd())

from inifun import * # Archivo inifun.py

###################################################################
# ARGUMENTOS CLI
config = readArgs(sys.argv[1:])

if config['error']:
    sys.exit()

zona = config['zona']
base_folder = config['base_folder']
id_zona = config['id_zona']
asset_string = config['asset_string']
rf = rangoFechas(30)
ini_date = rf[0]
end_date = rf[1]

print('\nPARAMETROS USADOS:')
print('> zona:\t\t' + zona)
print('> id_zona:\t' + str(id_zona))
print('> fechas:\t' + rf[0] + ' al ' + rf[1])
print('> asset_string:\t' + asset_string)
print('> base_folder:\t' + base_folder)


# Existen carpetas?
print('\t>> existe carpeta?\t\t', os.path.isdir(base_folder))
print('\t>> existe carpeta output?\t', os.path.isdir(os.path.join(base_folder, 'output')))

# Archivo de salida:
filename = os.path.join(
   base_folder,
   'output', 'zona-' + str(id_zona) + '-' + end_date + '.csv'
)
print('> filename (output):\t' + filename)
print('\t>> existe?\t', os.path.isfile(filename))

if os.path.isfile(filename) and sum(1 for line in open(filename)) > 1:
   print('\n>>> Datos ya obtenidos, abortando ejecución...')
   print('\n====== FIN ======')
   sys.exit()
###################################################################

import ee
import json
import csv
from pprint import pprint
from google.auth.transport.requests import AuthorizedSession

###################################################################
# CREDENTIALS
print('\nEnviando credenciales a la nube ...')

PROJECT = 'pruebas-gee-00' # Ej: pruebas-engine-00
SERVICE_ACCOUNT = 'pruebas-gee-jmb@pruebas-gee-00.iam.gserviceaccount.com'
# KEY = os.path.join(base_folder, 'my-secret-key.json')
KEY = os.path.join(base_folder, 'debian-key.json')
rest_api_url = 'https://earthengine.googleapis.com/v1beta/projects/{}/table:computeFeatures'

print('\LLAVE:', KEY)

# PROBLEMAS ACA / INICIO
credentials = ee.ServiceAccountCredentials(SERVICE_ACCOUNT, KEY)
scoped_credentials = credentials.with_scopes(
    ['https://www.googleapis.com/auth/cloud-platform'])

session = AuthorizedSession(scoped_credentials) 
ee.Initialize(credentials)
# PROBLEMAS ACA / FIN

###################################################################
# IMPORTAR COLECCIONES ET AL
print('Importando colecciones ...')
MSI = ee.ImageCollection('COPERNICUS/S2_HARMONIZED')
S2_clouds = ee.ImageCollection('COPERNICUS/S2_CLOUD_PROBABILITY')

# Polígono:
geom = ee.FeatureCollection(asset_string).first().geometry()

###################################################################
# FUNCIONES DE CALCULOS
# Idea de acá: https://stackoverflow.com/questions/15890014/namespaces-with-module-imports
import calfun as cf # Archivo calfun.py

###################################################################
# CONSTANTES Y VARIABLES GLOBALES
p = [10, 50, 90]
cloud_perc = 25
cloud_perc2 = 25
MAX_CLOUD_PROBABILITY = 10

# COPIAR VARIABLES AL NAMESPACE DE calfun:
cf.zona = zona
cf.id_zona = id_zona
cf.geom = geom
cf.p = p
cf.cloud_perc = cloud_perc
cf.cloud_perc2 = cloud_perc2
cf.MAX_CLOUD_PROBABILITY = MAX_CLOUD_PROBABILITY
cf.end_date = end_date
cf.ini_date = ini_date

###################################################################
# INICIO
print('Iniciando procesamiento ...')

# Create an NDWI image, define visualization parameters and display.
S2_mask = MSI.filterDate(ini_date, end_date)\
    .filterBounds(geom)\
    .filterMetadata('CLOUDY_PIXEL_PERCENTAGE', "less_than", cloud_perc2)

ndwi = S2_mask.median().normalizedDifference(['B3', 'B8'])

cf.mask_ndwi = ndwi.select('nd').gte(0.2)
cf.mask_ndwi = cf.mask_ndwi.updateMask(cf.mask_ndwi)

# DEFINIR PROPIEDAD Y VALOR PARA FILTRAR S2:
prp = 'MGRS_TILE'
val = '21HVD'

if id_zona >= 4 and id_zona < 6:
  prp = 'SENSING_ORBIT_NUMBER'
  val = 124

if id_zona >= 6:
  val = '21HWD'

# FILTER Sentinel 2 collection
FC2 = MSI.filterDate(ini_date, end_date)\
    .filterMetadata('CLOUDY_PIXEL_PERCENTAGE', "less_than", cloud_perc)\
    .filterBounds(geom)\
    .filter(ee.Filter.eq(prp, val))

# Filter input collections by desired data range and region.
criteria = ee.Filter.And(ee.Filter.bounds(geom),
                         ee.Filter.date(ini_date, end_date))
FC2 = FC2.filter(criteria).map(cf.maskEdges)
S2_clouds = S2_clouds.filter(criteria)

# Join S2 SR with cloud probability dataset to add cloud mask.
FC2_with_cloud_mask = ee.Join.saveFirst('cloud_mask')\
    .apply(primary = FC2, secondary = S2_clouds,
            condition = ee.Filter.equals(
                leftField = 'system:index', rightField = 'system:index'
            ))

S2_cloud_masked = ee.ImageCollection(FC2_with_cloud_mask).map(cf.maskClouds)

# atmospheric correction
Rrs_coll = S2_cloud_masked.map(cf.s2Correction)

# Calculos:
chlor_a_coll = Rrs_coll.map(cf.chlorophyll)
cdom_coll = Rrs_coll.map(cf.cdom)
turbidez_coll = Rrs_coll.map(cf.turbidez)

# Filtered collections:
cloa_filtered_col = chlor_a_coll.select('constant')\
    .filter(ee.Filter.bounds(geom))
cdom_filtered_col = cdom_coll.select('constant')\
    .filter(ee.Filter.bounds(geom))
turb_filtered_col = turbidez_coll.select('constant')\
    .filter(ee.Filter.bounds(geom))

### Time Series #####################################
# La mejor forma que encontré de fusionar las series:
time_series_final = ee.FeatureCollection([
    cf.getPercentiles(cloa_filtered_col, 'Clorofila-a'),
    cf.getPercentiles(cdom_filtered_col, 'CDOM'),
    cf.getPercentiles(turb_filtered_col, 'Turbidez')
]).flatten()

### ENVIO EN FORMATO POST A LA REST API #############

# El serializador, que parece que es necesario para el POST
serialized = ee.serializer.encode(time_series_final)

print('Enviando POST a la API ...')
response = session.post(
    url = rest_api_url.format(PROJECT),
    data = json.dumps({"expression": serialized})
)

# VER ACÁ CONTINGENCIA SI ES QUE ESTO NO VIENE CON 'features' (ej: por timeout):
feat = json.loads(response.content)['features']

# pprint(feat)

# SALIDA EN CSV:
print('Guardando resultado en el archivo:\n\t', filename)
con = open(filename, 'w', newline='', encoding="utf-8")

# con.write('date,id_zona,zona,parameter,p10,p50,p90\n')
con.write('date,id_zona,zona,parameter,value,percentil\n')
wrt = csv.writer(con, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

for f in feat:
    r = f['properties']
    # wrt.writerow([r['date'], str(r['id_zona']), r['zona'], r['parameter'],
    #              str(r['p10']), str(r['p50']), str(r['p90'])])
    wrt.writerow([r['date'], str(r['id_zona']), r['zona'], r['parameter'],
                 str(r['p10']), '10'])
    wrt.writerow([r['date'], str(r['id_zona']), r['zona'], r['parameter'],
                 str(r['p50']), '50'])
    wrt.writerow([r['date'], str(r['id_zona']), r['zona'], r['parameter'],
                 str(r['p90']), '90'])

con.close()

print('\n====== FIN ======\n')
