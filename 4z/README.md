# output

Archivos .CSV con datos extraídos para 1 zona y 1 fecha. 

## output/done

Aquí se guardan los archivos CSV luego de que sus datos son insertados en la BD (`insert_into_db.py`).

# log

Archivos .LOG con registros de todas las extracciones e inserciones en la BD.




# Bruno

Hola Juan, ¿cómo estás?.


Te paso un punteo con los cambios que me parecieron necesarios para pasar del script 7 zonas Río Negro a un script para el río Santa Lucía (desde cerca de Paso Severino hasta la desembocadura con el Río de la Plata).


Por las dudas también te paso el documento que resume el desarrollo de los algoritmos.


Estamos al habla.

 

Saludos,

Bruno

- - -
 
GENERALIDADES

10% porcentaje de nubes

Ventana temporal de 1 mes

Water gte 0

'MGRS_TILE', '21HWB'

ALGORITMOS


Clorofila-a (ug/l) - MISMO ÍNDICE QUE RN


I_543 = (B3-B4+B5)/(B3+B4+B5)

y= 517.33 * x^2 - 191.1 * x + 17.05
¿x = I_543?

 

Turbidez (FTU) - MISMO ÍNDICE QUE RN

B5B6 = (B5+B6)/2

y = 2685.7 * x + 8.2333
¿x 
 

Cdom (m^-1) - CAMBIA EL ÍNDICE RESPECTO A RN


B2B4 = B2/B4

y = 33.421 * exp(-4.171 * x)

 

ASSETS SANTA LUCÍA

projects/rionegro-381613/assets/sl_zona00_santalucia

projects/rionegro-381613/assets/sl_zona01_tajes

projects/rionegro-381613/assets/sl_zona02_islas

projects/rionegro-381613/assets/sl_zona03_desembocadura

 