# Sistema

Servidor: 172.20.0.57 ("google-engine")

```
jbarreneche@google-engine:~$ lsb_release -a
No LSB modules are available.
Distributor ID: Debian
Description:    Debian GNU/Linux 11 (bullseye)
Release:        11
Codename:       bullseye
```

Carpeta base en el servidor: /home/jbarreneche

# Instalar

- Python3
  + pip3
  + Libreria ee: `pip3 install earthengine-api --upgrade`
  + Otras librerías P3 usadas, que no sé si hay que instalar a parte: json, datetime, pprint

- gcloud


# Proyecto en google cloud

Hacer el proyecto (y la cuenta de servicio) en la interfaz online (https://console.cloud.google.com/iam-admin/serviceaccounts)

# Proxy

En .bashrc (ver bashrc.sh):

```sh
export http_proxy="http://172.20.2.9:8080/"
export https_proxy="http://172.20.2.9:8080/"
```

# Credenciales

## Correr script con autenticación manual

Esto es lo primero que hice (JMB). No es lo que se usa, pero lo dejo como ejemplo por las dudas.

El ejemplo básico encontrado en la documentación es ("ejemplo.py"):

```py
import ee
ee.Authenticate()
ee.Initialize()
print(ee.Image("NASA/NASADEM_HGT/001").get("title").getInfo())
```

Al correrlo en la consola (PC personal), genera esto:

```
juan@panter:~$ python3 ejemplo.py
Fetching credentials using gcloud
Your browser has been opened to visit:

    https://accounts.google.com/o/oauth2/auth?response_type=code&client_id=517222506229-vsmmajv00ul0bs7p89v5m89qs8eb9359.apps.googleusercontent.com&redirect_uri=http%3A%2F%2Flocalhost%3A8085%2F&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fearthengine+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fdevstorage.full_control+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Faccounts.reauth&state=PcASvqPUYOqeKEoVvjCgb5fEMu8uwL&access_type=offline&code_challenge=Vagt7RhdLCsBHq-t_FSLFpQwm1rpSlXG74Pd9LpHP0g&code_challenge_method=S256


Credentials saved to file: [/home/juan/.config/gcloud/application_default_credentials.json]

These credentials will be used by any library that requests Application Default Credentials (ADC).

Successfully saved authorization token.
NASADEM: NASA NASADEM Digital Elevation 30m
```

## Correr con autenticación automática

(tomado de https://developers.google.com/earth-engine/Earth_Engine_REST_API_compute_table)

Hace falta tener un archivo json con una llave, la cual se obtiene desde la consola:

```sh
# INSERT YOUR PROJECT HERE
PROJECT = 'pruebas-gee-00'

gcloud auth login --project {PROJECT}
```

Una vez logueado (ver la parte de autenticación manual), se puede ejecutar:

```sh
# INSERT YOUR SERVICE ACCOUNT HERE
SERVICE_ACCOUNT='pruebas-gee-jmb@pruebas-gee-00.iam.gserviceaccount.com'
KEY='debian-key.json'

gcloud iam service-accounts keys create {KEY} --iam-account {SERVICE_ACCOUNT}
```

Esto genera un archivo json (en este caso, `debian-key.json`).

Están en .gitignore, por las dudas. Por eso el nombre de estos archivos debe ser siempre *-key.json.

OJO: aún si el archivo json está impecable, si la fecha-hora del servidor no está bien (diferencia de 3 horas con la hora local, en el caso concreto de las pruebas que hicimos), nos va a generar problemas después, al querer ejecutar el python, específicamente porque el archivo con la llave no es "reciente" (no entendí muy bien el mensaje de error; JMB).

## Registrar el proyecto para usar Earth Engine API

Al proyecto (actualmente "pruebas-gee-00") hay que registrarlo para usar Earth Engine API. Eso se puede hacer acá: https://developers.google.com/earth-engine/guides/access#a-role-in-a-cloud-project.

(ver enlace donde dice "has been registered for use with Earth Engine."; https://code.earthengine.google.com/register)

## Scripts

Basado en ejemplos de acá: https://developers.google.com/earth-engine/Earth_Engine_REST_API_compute_table

La clave es que se usa la REST API de google. Específicamente, la que trabaja con datos para tablas (en vez de imágenes; serían feature o featureCollections).

Una versión anterior del mismo script, pero en javascript: https://code.earthengine.google.com/81598206c6a477dce405a8d7f57f1782

### Principal (Python)

Carpeta: gee_7zonas.

- `main.py`: Llama a los módulos (ver abajo), hace loggin con google cloud y escribe los outputs en CSVs

Para los cálculos utiliza todas las imágenes disponibles de Sentinel 2 de los últimos 30 días.

### Auxiliares (módulos de Python)

Carpeta: modules

- `inifun.py`: Funciones iniciales (chequeos varios y cosas así)
- `calfun.py`: Funciones de cálculos varios (ej.: modelos de clorofila, cdom y turbidez, corrección atmosférica, y más)

Para que los módulos de Python sean leídos, es preciso modificar la variable `PYTHONPATH`. Para sesiones interactivas alcanza con agregarla con el archivo .bashrc (copiado en el archivo bashrc.sh):

```sh
export PYTHONPATH="/home/jbarreneche/modules"
```

Para el crontab hay que hacer otras cosas...

## Crontab

Para que pueda conectarse a los servidores de google y además Python reconozca las librearías, hay que incluir estas líneas al inicio del crontab:

```sh
http_proxy="http://172.20.2.9:8080/"
https_proxy="http://172.20.2.9:8080/"
PYTHONPATH="/home/jbarreneche/modules"
```

(ver https://stackoverflow.com/a/10657111/1030523)

Los comandos del crontab se guardan en crontab.txt

En la consola se modifica el crontab y luego se actualiza crontab.txt con :

```sh
crontab -e # Abre crontab en editor predterminado
crontab -l > crontab.txt # Guarda conteniods de crontab en archivo txt
```

# Scripts Bash (Shell Script)


- `run_gee.sh`: ejecuta main.py con un argumento (el id_zona). Ejemplo:

```sh
./run_gee.sh 1 # Zona 1: Palmar
# o ...
/bin/bash run_gee.sh 2 # Zona 2: Andresito
```

- `rename_log.sh`: Toma el log.log (archivo de texto simple) generado por el crontab, y lo renombra según la fecha (ie: `logYYYYMMDD.log`)

# OUTPUT

Las salidas se guardan en .csv, en la carpeta gee_7zonas/output.

Se estructuran así (cortado para ahorrar espacio):

```csv
date,id_zona,zona,parameter,value,percentil
2023-04-05T13:51:49,1,PALMAR,Clorofila-a,9.490648312247684,10
2023-04-05T13:51:49,1,PALMAR,Clorofila-a,21.408959467665024,50
2023-04-05T13:51:49,1,PALMAR,Clorofila-a,54.640662657161535,90
...
2023-04-05T13:51:49,1,PALMAR,CDOM,0.8602718252064326,10
2023-04-05T13:51:49,1,PALMAR,CDOM,1.2359959729444174,50
2023-04-05T13:51:49,1,PALMAR,CDOM,3.6782969336431646,90
...
2023-04-05T13:51:49,1,PALMAR,Turbidez,9.87104861610198,10
2023-04-05T13:51:49,1,PALMAR,Turbidez,26.32665435586687,50
2023-04-05T13:51:49,1,PALMAR,Turbidez,31.6684313177501,90
```
