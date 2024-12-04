#! /usr/bin/env python

import sys
import os
import datetime
from inifun import *  # Archivo inifun.py

###################################################################
# ARGUMENTOS CLI ======
config = parser.parse_args()
id_zona = int(config.id_zona)
nzonas = int(config.nzonas)
isValidZoneID(id_zona, nzonas)
root_folder = os.path.dirname(os.path.realpath(__file__))
base_folder = os.path.join(root_folder, str(nzonas) + "z")
ow = config.overwrite

ndias = 30 if nzonas <= 7 else 2
asset_string = getAssetFromIdZona(config.id_zona, nzonas)

rf = rangoFechas(ndias, config.end_date)
ini_date = rf[0]
ini_date_o3 = rangoFechas(30, config.end_date)[0]
end_date = rf[1]
###################################################################

print("\n\n=== INICIANDO / " + str(nzonas) + " ZONAS ===\n")

print("Carpeta de ejecucion:", os.path.realpath(os.getcwd()))


# Archivo de salida:
filename = os.path.join(
    base_folder,
    "output",
    "zona-" + pad(id_zona) + "de" + str(pad(nzonas)) + "-" + end_date + ".csv",
)
print("\n RESUMEN")
print("+-------+")
print("> working dir.:\t" + os.path.realpath(os.getcwd()))
print("> id_zona:\t" + pad(id_zona))
print("> fechas:\t" + ini_date + " al " + end_date)
print("> fechas (O3):\t" + ini_date_o3 + " al " + end_date)
print("> asset_string:\t" + asset_string)
print("> base_folder:\t" + base_folder)
print("> outfile:\t" + filename)

# Existen carpetas / outfile?
print("\t>> existe carpeta?\t\t", siono(os.path.isdir(base_folder)))
print(
    "\t>> existe carpeta output?\t",
    siono(os.path.isdir(os.path.join(base_folder, "output"))),
)
print("\t>> existe outfile?\t\t", siono(os.path.isfile(filename)))
print("\t>> sobreescribir resultados?\t", siono(ow))

if not ow and os.path.isfile(filename) and sum(1 for line in open(filename)) > 1:
    print("\n>>> Datos ya obtenidos, abortando ejecución...")
    print("EXITO: 0")
    print("\n====== FIN ======")
    sys.exit()
###################################################################

import ee
import json
import csv
from pprint import pprint
from google.auth.transport.requests import Request
from google.auth.transport.requests import AuthorizedSession

###################################################################
# CREDENTIALS =======

print("\nEnviando credenciales a la nube ...")

PROJECT = "pruebas-gee-00"  # Ej: pruebas-engine-00
SERVICE_ACCOUNT = "pruebas-gee-jmb@pruebas-gee-00.iam.gserviceaccount.com"
KEY = os.path.join(os.getcwd(), "debian-key.json")
rest_api_url = (
    "https://earthengine.googleapis.com/v1beta/projects/{}/table:computeFeatures"
)

print("\LLAVE:", KEY)

# PROBLEMAS ACA / INICIO

# Estimate Google's server time
google_server_time = get_google_server_time()
d = google_server_time - datetime.datetime.utcnow();
diff = d.total_seconds()
# diff = d.total_seconds() - 3 * 60 * 60

credentials = ee.ServiceAccountCredentials(SERVICE_ACCOUNT, KEY)
# pprint(credentials)
credentials._now = lambda: datetime.datetime.utcnow() + datetime.timedelta(seconds=diff)
credentials.refresh(Request())

print("Google: ")
print(google_server_time)
print("VM: ")
print(datetime.datetime.utcnow())
print("credentials._now(): ")
print(credentials._now())

# pprint(credentials)

scoped_credentials = credentials.with_scopes(
    ["https://www.googleapis.com/auth/cloud-platform"]
)

session = AuthorizedSession(scoped_credentials)
ee.Initialize(credentials)
# PROBLEMAS ACA / FIN

###################################################################
# IMPORTAR COLECCIONES ET AL =====
print("Importando colecciones ...")
MSI = ee.ImageCollection("COPERNICUS/S2_HARMONIZED")
S2_clouds = ee.ImageCollection("COPERNICUS/S2_CLOUD_PROBABILITY")

# Polígono:
geom = ee.FeatureCollection(asset_string).first().geometry()

###################################################################
# FUNCIONES DE CALCULOS =====
# Idea de acá: https://stackoverflow.com/questions/15890014/namespaces-with-module-imports
import calfun as cf  # Archivo calfun.py

###################################################################
# CONSTANTES Y VARIABLES GLOBALES =====
p = [10, 50, 90]
MAX_CLOUD_PROBABILITY = 10
cloud_perc = 25
cloud_perc2 = 25
if nzonas == 4:
    cloud_perc = 10
    cloud_perc2 = 10

if nzonas == 60:
    cloud_perc = 1.1
    cloud_perc2 = 1.1

# COPIAR VARIABLES AL NAMESPACE DE calfun:
cf.zona = "RN60Z"
cf.id_zona = id_zona
cf.geom = geom
cf.p = p
cf.cloud_perc = cloud_perc
cf.cloud_perc2 = cloud_perc2
cf.MAX_CLOUD_PROBABILITY = MAX_CLOUD_PROBABILITY
cf.end_date = end_date
cf.ini_date = ini_date
cf.ini_date_o3 = ini_date_o3

###################################################################
# INICIO =====
print("Iniciando procesamiento ...")

print("Valores de Cloud Percentage y max. cloud prob. ...")
print("\tcloud_perc            : " + str(cloud_perc))
print("\tcloud_perc2           : " + str(cloud_perc2))
print("\tMAX_CLOUD_PROBABILITY : " + str(MAX_CLOUD_PROBABILITY))

# Create an NDWI image, define visualization parameters and display.
S2_mask = (
    MSI.filterDate(ini_date, end_date)
    .filterBounds(geom)
    .filterMetadata("CLOUDY_PIXEL_PERCENTAGE", "less_than", cloud_perc2)
)

ndwi = S2_mask.median().normalizedDifference(["B3", "B8"])

cf.mask_ndwi = ndwi.select("nd").gte(0.2)

cf.mask_ndwi = cf.mask_ndwi.updateMask(cf.mask_ndwi)

# DEFINIR PROPIEDAD Y VALOR PARA FILTRAR S2:
prp = "MGRS_TILE"
val = "21HVD"

if nzonas == 4:
    val = "21HWB"

elif nzonas == 7:
    if id_zona >= 4 and id_zona < 6:
        prp = "SENSING_ORBIT_NUMBER"
        val = 124
    elif id_zona >= 6:
        val = "21HWD"

elif nzonas == 60:
    if id_zona >= 1 and id_zona < 18:
        val = "21HVD"
    elif id_zona == 18:
        val = "21HWD"
    elif id_zona >= 19 and id_zona < 37:
        prp = "SENSING_ORBIT_NUMBER"
        val = 124
    elif id_zona >= 37 and id_zona < 56:
        val = "21HWD"
    elif id_zona >= 56 and id_zona < 59:
        val = "21HXD"
    elif id_zona >= 59 and id_zona <= 60:
        val = "21HXE"

print("Valores para filtro de Propertie & Value ...")
print("\tprp : " + str(prp))
print("\tval : " + str(val))

# FILTER Sentinel 2 collection
FC2 = (
    MSI.filterDate(ini_date, end_date)
    .filterMetadata("CLOUDY_PIXEL_PERCENTAGE", "less_than", cloud_perc)
    .filterBounds(geom)
    .filter(ee.Filter.eq(prp, val))
)

# Filter input collections by desired data range and region.
criteria = ee.Filter.And(ee.Filter.bounds(geom), ee.Filter.date(ini_date, end_date))
FC2 = FC2.filter(criteria).map(cf.maskEdges)
S2_clouds = S2_clouds.filter(criteria)

# Join S2 SR with cloud probability dataset to add cloud mask.
FC2_with_cloud_mask = ee.Join.saveFirst("cloud_mask").apply(
    primary=FC2,
    secondary=S2_clouds,
    condition=ee.Filter.equals(leftField="system:index", rightField="system:index"),
)

S2_cloud_masked = ee.ImageCollection(FC2_with_cloud_mask).map(cf.maskClouds)

# atmospheric correction
Rrs_coll = S2_cloud_masked.map(cf.s2Correction)

# Calculos:
if nzonas == 4:
    chlor_a_coll = Rrs_coll.map(cf.chlorophyll_sl)
    cdom_coll = Rrs_coll.map(cf.cdom_sl)
    turbidez_coll = Rrs_coll.map(cf.turbidez_sl)
else:
    chlor_a_coll = Rrs_coll.map(cf.chlorophyll)
    cdom_coll = Rrs_coll.map(cf.cdom)
    turbidez_coll = Rrs_coll.map(cf.turbidez)

# Filtered collections:
cloa_filtered_col = chlor_a_coll.select("constant").filter(ee.Filter.bounds(geom))
cdom_filtered_col = cdom_coll.select("constant").filter(ee.Filter.bounds(geom))
turb_filtered_col = turbidez_coll.select("constant").filter(ee.Filter.bounds(geom))

#####################################################
# Time Series =====
# La mejor forma que encontré de fusionar las series:
time_series_final = ee.FeatureCollection(
    [
        cf.getPercentiles(cloa_filtered_col, "Clorofila-a", False),
        cf.getPercentiles(cdom_filtered_col, "CDOM", False),
        cf.getPercentiles(turb_filtered_col, "Turbidez", False),
    ]
).flatten()

#####################################################
# POST =====

# El serializador, que parece que es necesario para el POST
serialized = ee.serializer.encode(time_series_final)

print("Enviando POST a la API ...")
response = session.post(
    url=rest_api_url.format(PROJECT), data=json.dumps({"expression": serialized})
)

# VER ACÁ CONTINGENCIA SI ES QUE ESTO NO VIENE CON 'features' (ej: por timeout):

import pickle

# with open('res_sin_features_z' + id_zona + 'fecha' + end_date + '.pkl', 'wb') as outp:
#     pickle.dump(response, outp, pickle.HIGHEST_PROTOCOL)
# with open('response.pkl', 'rb') as inp:
#     response = pickle.load(inp)

if response.ok:
    print("> Solicitud exitosa!")
    rcontent = json.loads(response.content)
    if "features" not in rcontent:
        archivito = "res_sin_features_z" + str(id_zona) + "fecha" + end_date + ".pkl"
        archivito = os.path.join(base_folder, "log", archivito)
        print(
            '> Respuesta vacía (sin features)\n  Guardando archivo: \n\t"'
            + archivito
            + '"'
        )
        with open(archivito, "wb") as outp:
            pickle.dump(response, outp, pickle.HIGHEST_PROTOCOL)
        print("EXITO: 0")
        print("\n====== FIN ======\n")
        sys.exit()
    else:
        feat = rcontent["features"]

else:
    print(
        "[[ E ]]: la solicitud dió un error (código "
        + str(response.status_code)
        + "; razón: "
        + response.reason
        + ")"
    )
    pprint(response)
    pprint(json.loads(response.content))
    print("EXITO: 0")
    print("\n====== FIN ======\n")
    sys.exit()

# {'error': {'code': 400,
#            'message': "Image.normalizedDifference: No band named 'B3'. "
#                       'Available band names: [].',
#            'status': 'INVALID_ARGUMENT'}}
# Traceback (most recent call last):
#   File "/home/jbarreneche/gee_60zonas/main.py", line 212, in <module>
#     feat = json.loads(response.content)['features']
# KeyError: 'features'

# El intérprete de órdenes devolvió 1

# pprint(feat)

# SALIDA EN CSV: =====
print("\nGuardando resultado en el archivo:\n\t", filename)

ign_arr = []
# ign_file = open('fechas_ignorar.txt', 'r')
ign_file = open(os.path.join(root_folder, "fechas_ignorar.txt"), "r")
for line in ign_file:
    line_stripped = line.strip()
    if line_stripped != "":
        ign_arr.append(line_stripped)

ign_file.close()
print("\nFechas a ignorar:")
[print("\t" + x) for x in ign_arr]
print("")

con = open(filename, "w", newline="", encoding="utf-8")
con.write("time_start,valor,id_zona,id_parametro,percentil,fecha_insercion\n")
wrt = csv.writer(con, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)

for f in feat:
    stop = False
    r = f["properties"]
    id_parametro = None

    for ign in ign_arr:
        if ign == r["date"][:10] == ign:
            print(
                "Ignorando la fecha:\t" + r["date"][:10] + " (" + r["parameter"] + ")"
            )
            stop = True
            break

    if stop:
        continue

    if r["parameter"] == "Clorofila-a":
        id_parametro = 2000
    elif r["parameter"] == "CDOM":
        id_parametro = 2318
    elif r["parameter"] == "Turbidez":
        id_parametro = 2035

    fecha_insercion = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        p10 = r["p10"]
    except KeyError:
        continue

    wrt.writerow(
        [
            r["date"],
            str(r["p10"]),
            str(r["id_zona"]),
            id_parametro,
            "10",
            fecha_insercion,
        ]
    )
    wrt.writerow(
        [
            r["date"],
            str(r["p50"]),
            str(r["id_zona"]),
            id_parametro,
            "50",
            fecha_insercion,
        ]
    )
    wrt.writerow(
        [
            r["date"],
            str(r["p90"]),
            str(r["id_zona"]),
            id_parametro,
            "90",
            fecha_insercion,
        ]
    )

con.close()

with open(filename) as f:
    nlineas = 0
    for line in f:
        nlineas += 1

if nlineas == 1:
    os.remove(filename)
    print(
        "\nLa petición fue exitosa pero no se encontraron datos para estas fechas"
        + "\n(posiblemente por alta cobertura de nubes en la zona en cuestión)\n"
    )
    print(f"\nSe elimina el archivo csv:\n\t{filename}")
    print("\nEXITO: 0")
    print("\n====== FIN ======\n")
    sys.exit()

print("\nEXITO: 1")
print("\n====== FIN ======\n")
