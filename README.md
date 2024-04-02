# Extracciones de datos con GEE

## Scripts

### Python

Esto son la base de todo. Usarlos directamente da más control, con un poco más de complejidad. Los scripts de Bash, más abajo, son alternativas simplificadas para el día a día, incluyendo los crontabs.

- **main.py**: el programa principal. Se apoya en inifun.py e calfun.py
- **insert_into_db.py**: inserta datos en la base datos\_irn

### Bash

Varios scripts dedicados a ejecutar los comandos anteriores (pero con una interfaz más simple), así como a limpieza general de los archivos.

- **run_gee_day**: corre main.py para todas las zonas y una fecha (hay que elegir 7 o 60)
- **run_absent_days.sh**: corre main.py para todas las zonas y un rango de fechas (elegir 7|60)
- **insertdb.sh**: corre insert\_into\_db.py para importar todos los datos disponibles (elegir 7|60)
- **rename_log.sh**: utilidad para el crontab (renombra archivos LOG y los guarda en la carpeta correspondiente)
- **delete_old.sh**: utilidad para el crontab (borra archivos CSV y LOG de >30 días)

### Ayuda

Todos los scripts activan una ayuda sencilla con el comando `./<script> -h`. Ejemplos:

```sh
./main.py -h
./insert_into_db.py -h
./run_gee_day.sh -h
```

## Ejemplos

### La base (**python**)

#### UNA zona - UNA fecha: `main.py`

Este script toma datos de una zona en particular, con un día en particular (que es el final de unos 30 o 2 días, según si se trata del mapa de 7 o 60 zonas).

En este caso, sería la zona 4/7 (arg. `-z`), para el día en que se ejecute el comando:

```sh
./main.py -z 4
```

Por defecto trabaja con el mapa de 7 zonas, pero esto se puede determinar con el argumento `-n`:

```sh
./main.py -z 4 -n 60
```

La fecha se puede elegir con el argumento `-e`:

```sh
./main.py -z 33 -n 60 -e 2017-06-19
```

#### INSERTAR en la BASE DE DATOS: `insert_into_db.py`

Toma archivos CSV de una carpeta cualquiera e inserta los datos en una tabla a elección de la Base de Datos (debe tener la estructura que tienen `7_zonas` y `60_zonas`).

```sh
./insert_into_db.py -b 60z/output -t 60_zonas
```

### Scripts de soporte (**bash**)

#### TODAS las zonas - UNA fecha: `run_gee_day.sh`

Hace lo mismo que el `main.py` pero para todas las zonas del mapa (según se eliga 7 o 60, con el argumento `-n`).

Estracción de datos de hoy o del 19 de junio de 2017, en todas las zonas (7):

```sh
./run_gee_day.sh -e 2017-06-19 -n 7
```

La versión para 60 zonas sería:

```sh
./run_gee_day.sh -e 2017-06-19 -n 60
```

Si no se usa el argumento `-e`, simplemente usa el día en que se hace la ejecución.

#### TODAS las zonas - MUCHAS fechas: `run_gee_day.sh`

Similar a `run_gee_day.sh`, pero para un rango de fechas. Usa 3 argumentos (fecha de inicio, fecha final y Nro. de zonas: 7 o 60):

```sh
./run_absent_days.sh 2017-01-01 2017-12-31 7  # Todo 2017, 7 zonas
```

- - -

## Sistema

Ubuntu 18.04 / Debian 11

## Instalar

- Python3
  + pip3
  + Libreria ee: `pip3 install earthengine-api --upgrade`
  + Otras librerías P3 usadas, que no sé si hay que instalar a parte: json, datetime, pprint

- gcloud


## Armar el script + crontab

Otra fuente intersante: https://medium.com/@zrowland/exporting-images-and-imagecollections-from-google-earth-engine-to-your-local-machine-412a51d05283


### Proyecto en google cloud

Al final hice el proyecto (y la cuenta de servicio) en la interfaz online (https://console.cloud.google.com/iam-admin/serviceaccounts)


### Credenciales

Para obtener el archivo con las credenciales (tomado de https://developers.google.com/earth-engine/Earth_Engine_REST_API_compute_table):

```sh
# INSERT YOUR PROJECT HERE
PROJECT = 'your-project' # pruebas-gee-00

gcloud auth login --project {PROJECT}
```

Las credenciales quedan en un archivito json (en este caso, `debian-key.json`):

```sh
# INSERT YOUR SERVICE ACCOUNT HERE
SERVICE_ACCOUNT='pruebas-gee-jmb@pruebas-gee-00.iam.gserviceaccount.com'
KEY='my-secret-key.json'

gcloud iam service-accounts keys create {KEY} --iam-account {SERVICE_ACCOUNT}
```

### Registrar el proyecto para usar Earth Engine API

Pila de veces me dió el mismo error, hasta que me avivé: resulta que el proyecto (pruebas-gee-00) no estaba registrado para la Earth Engine API, y me mandaban acá: https://developers.google.com/earth-engine/guides/access#a-role-in-a-cloud-project

Y ahí solamente tenía que ir al enlace donde dice "has been registered for use with Earth Engine." (https://code.earthengine.google.com/register)

Luego de eso, ajusté el script y la cosa marchó

### Script de python

Clorofila7zonas.py

Me basé en ejemplos de acá: https://developers.google.com/earth-engine/Earth_Engine_REST_API_compute_table

La clave es que usa la REST API de google.

Hice una versión del mismo script en GEE (javascript): https://code.earthengine.google.com/81598206c6a477dce405a8d7f57f1782

### CRONTAB

Para editar el crontab:

```sh
crontab -e
```

Para consultar el crontab:

```sh
crontab -l
```

Se realizan dos crontab: uno con el usuario normal, otro con sudo

#### crontab -e

```sh
# Variables

http_proxy="http://172.20.2.9:8080/"
https_proxy="http://172.20.2.9:8080/"
PYTHONPATH="/home/jbarreneche/modules"

# m h  dom mon dow   command
56 0 * * * echo "" > log.log
00 1,2,3,4,5,6 * * * /bin/bash run_gee.sh 1 >> log.log
04 1,2,3,4,5,6 * * * /bin/bash run_gee.sh 2 >> log.log
08 1,2,3,4,5,6 * * * /bin/bash run_gee.sh 3 >> log.log
12 1,2,3,4,5,6 * * * /bin/bash run_gee.sh 4 >> log.log
16 1,2,3,4,5,6 * * * /bin/bash run_gee.sh 5 >> log.log
20 1,2,3,4,5,6 * * * /bin/bash run_gee.sh 6 >> log.log
24 1,2,3,4,5,6 * * * /bin/bash run_gee.sh 7 >> log.log
30 6 * * * /bin/bash rename_log.sh
```

#### sudo crontab

```sh
# m h  dom mon dow   command
35 6 * * * mv -f /home/jbarreneche/7z/output/*.csv /mnt/datos_irn/automatizado/
```

https://duckduckgo.com/?t=ftsa&q=exported+variable+in+.bashrc+is+not+available+in+crontab+job&atb=v163-1&ia=web

https://stackoverflow.com/questions/2229825/where-can-i-set-environment-variables-that-crontab-will-use

- - -

## Correr script con autenticación manual

Esto es lo primero que hice. No es lo que vamos a usar, pero lo dejo como legado por las dudas.

El ejemplo lo saqué de los manuales de la API, y lo puse en el archivo ee_test.py, que tiene este código:

```py
import ee
ee.Authenticate()
ee.Initialize()
print(ee.Image("NASA/NASADEM_HGT/001").get("title").getInfo())
```

Cuando corrés esto en la consola (en ubuntu, así que es bash):

```
juan@panter:~$ python3 ee_test.py
Fetching credentials using gcloud
Your browser has been opened to visit:

    https://accounts.google.com/o/oauth2/auth?response_type=code&client_id=517222506229-vsmmajv00ul0bs7p89v5m89qs8eb9359.apps.googleusercontent.com&redirect_uri=http%3A%2F%2Flocalhost%3A8085%2F&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fearthengine+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fdevstorage.full_control+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Faccounts.reauth&state=PcASvqPUYOqeKEoVvjCgb5fEMu8uwL&access_type=offline&code_challenge=Vagt7RhdLCsBHq-t_FSLFpQwm1rpSlXG74Pd9LpHP0g&code_challenge_method=S256


Credentials saved to file: [/home/juan/.config/gcloud/application_default_credentials.json]

These credentials will be used by any library that requests Application Default Credentials (ADC).

Successfully saved authorization token.
NASADEM: NASA NASADEM Digital Elevation 30m
```

- - -

```sh
jbarreneche@google-engine:~/7z$ sudo su
[sudo] password for jbarreneche:
root@google-engine:/home/jbarreneche/7z# ls
01_Palmar.py  {KEY}  my-secret-key2.json  my-secret-key.json  output  out.txt  test.py
root@google-engine:/home/jbarreneche/7z# rm \{KEY\}
root@google-engine:/home/jbarreneche/7z# cat my-secret-key2.json
root@google-engine:/home/jbarreneche/7z# rm my-secret-key2.json
root@google-engine:/home/jbarreneche/7z# ls
01_Palmar.py  my-secret-key.json  output  out.txt  test.py
root@google-engine:/home/jbarreneche/7z# gcloud auth login
Go to the following link in your browser:

    https://accounts.google.com/o/oauth2/auth?response_type=code&client_id=32555940559.apps.googleusercontent.com&redirect_uri=https%3A%2F%2Fsdk.cloud.google.com%2Fauthcode.html&scope=openid+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.email+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fcloud-platform+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fappengine.admin+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fsqlservice.login+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fcompute+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Faccounts.reauth&state=KKygtqPJwv8nr0cXkMR9kgcLgDlxJT&prompt=consent&access_type=offline&code_challenge=YcUPHea9bcOYTw8JfC1is5MkV-6ktTtqdT7FUKcAWzU&code_challenge_method=S256

Enter authorization code: 4/0AVHEtk6bdcVBAF6LEUme5c-VR5m-pfqNsCuDXUR7P6duzxJTLCxZiPXwZYQcKJc33csENg

You are now logged in as [jumanbar@gmail.com].
Your current project is [None].  You can change this setting by running:
  $ gcloud config set project PROJECT_ID
root@google-engine:/home/jbarreneche/7z# gcloud config set project pruebas-gee-00
Updated property [core/project].


PROXY
export http_proxy="http://172.20.2.9:8080/"
export https_proxy="http://172.20.2.9:8080/"
```



https://stackoverflow.com/a/10657111/1030523

```sh
root@google-engine:/home/jbarreneche/7z# timedatectl
               Local time: dom 2023-04-16 09:43:11 -03
           Universal time: dom 2023-04-16 12:43:11 UTC
                 RTC time: dom 2023-04-16 12:43:11
                Time zone: America/Montevideo (-03, -0300)
System clock synchronized: yes
              NTP service: active
          RTC in local TZ: no
```

correr esto?

```sh
sudo su

ntpd -qg
```

Fuente: https://unix.stackexchange.com/questions/605207/my-local-time-is-in-the-correct-timezone-but-isnt-actually-the-real-local-time


## VIM (colores)

"Instalé" el [codedark](https://github.com/tomasiser/vim-code-dark), así:

Bajar el archivo [**codedark.vim**](https://github.com/tomasiser/vim-code-dark/blob/master/colors/codedark.vim)

Meterlo en la carpeta /usr/share/vim/vim82/colors/

Editar el archivo /etc/vim/vimrc.local, poniendo las líneas:

```vim
set t_Co=256
set t_ut=
colorscheme codedark
```





