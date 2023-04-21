import ee
import json
import os
from pprint import pprint
from google.auth.transport.requests import AuthorizedSession

###################################################################
# CREDENTIALS
print('\nEnviando credenciales a la nube ...')
base_folder = os.path.dirname(os.path.realpath(__file__))

PROJECT = 'pruebas-gee-00' # Ej: pruebas-engine-00
SERVICE_ACCOUNT = 'pruebas-gee-jmb@pruebas-gee-00.iam.gserviceaccount.com'
# KEY = base_folder + '/my-secret-key.json'

print('Trabajando en la carpeta:', base_folder)

KEY = os.path.join(base_folder, 'debian-key.json')
rest_api_url = 'https://earthengine.googleapis.com/v1beta/projects/{}/table:computeFeatures'

credentials = ee.ServiceAccountCredentials(SERVICE_ACCOUNT, KEY)
scoped_credentials = credentials.with_scopes(
    ['https://www.googleapis.com/auth/cloud-platform'])

session = AuthorizedSession(scoped_credentials) 
ee.Initialize(credentials)

# ZonasRN
palmar_rep = ee.FeatureCollection("users/brunogda/zonas_palmar_represa_dis")
andresito = ee.FeatureCollection("users/brunogda/zonas_andresito_dis")
andresitobay = ee.FeatureCollection("users/brunogda/zonas_palmar_andresito_dis")
baygorria_rep = ee.FeatureCollection("users/brunogda/zonas_baygorria_represa_dis")
baygorria_pdlt = ee.FeatureCollection("users/brunogda/zonas_baygorria_pdlt_dis")
bonete_rep = ee.FeatureCollection("users/brunogda/zonas_bonete_represa_dis")
bonete_pol = ee.FeatureCollection("users/brunogda/zonas_bonete_polanco_dis")

fusion = palmar_rep\
    .merge(andresito)\
    .merge(andresitobay)\
    .merge(baygorria_rep)\
    .merge(baygorria_pdlt)\
    .merge(bonete_rep)\
    .merge(bonete_pol)

def killgeom(f):
    f.set('geom', None)
    return f

fusionu = fusion.union().map(killgeom)

# El serializador, que parece que es necesario para el POST
serialized = ee.serializer.encode(fusionu)

print('Enviando POST a la API ...')
response = session.post(
    url = rest_api_url.format(PROJECT),
    data = json.dumps({"expression": serialized})
)

# VER ACÁ CONTINGENCIA SI ES QUE ESTO NO VIENE CON 'features' (ej: por timeout):
feat = json.loads(response.content)
pprint(feat)