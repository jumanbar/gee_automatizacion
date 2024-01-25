import mariadb
import sys
import csv

try:
    conn = mariadb.connect(
            user="datos_irn_gee",
            password="D4t0s1rng33",
            host="172.20.0.35",
            port=3306,
            database="datos_irn"
            )

except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

cur = conn.cursor()

# Opcion 2: usar ? como comodines para rellenar con un array:
values = []
data=[]

with open('output/zona-01de60-2016-09-27.csv') as csvfile:
    reader = csv.reader(csvfile)
    next(reader)
    for row in reader:
        # sql = sql + "('" + row[0] + "', " + row[1] + ", " + row[2] + ", " + row[3] + \
        values.append("('" + row[0].split("T")[0] + "',\t" + row[1] + ",\t" + row[2] + ",\t" + row[3] + \
                ",\t" + row[4] + ",\t'" + row[5] + "')")

sql="INSERT INTO 60_zonas (time_start, valor, id_zona, id_parametro, percentil, fecha_insercion)\nVALUES\n\t" +\
        ",\n\t".join(values)
print(sql)

try: cur.execute(sql)
except mariadb.Error as e:
    print(f"Error: {e}")

conn.commit()

# free resources
cur.close()
conn.close()
sys.exit(0)

"""
time_start,valor,id_zona,id_parametro,percentil,fecha_insercion
2016-09-26T14:01:08,7.369306466548319,1,2000,10,2023-12-07 13:56:17
2016-09-26T14:01:08,8.16949908979022,1,2000,50,2023-12-07 13:56:17
2016-09-26T14:01:08,10.0376804453081,1,2000,90,2023-12-07 13:56:17
2016-09-26T14:01:08,7.369306466545622,1,2000,10,2023-12-07 13:56:17
2016-09-26T14:01:08,8.169499089787163,1,2000,50,2023-12-07 13:56:17
2016-09-26T14:01:08,10.037680445304682,1,2000,90,2023-12-07 13:56:17
2016-09-26T14:01:08,3.724249415540617,1,2318,10,2023-12-07 13:56:17
2016-09-26T14:01:08,3.916392895111496,1,2318,50,2023-12-07 13:56:17
2016-09-26T14:01:08,4.721022124137138,1,2318,90,2023-12-07 13:56:17
2016-09-26T14:01:08,3.724249415541325,1,2318,10,2023-12-07 13:56:17
2016-09-26T14:01:08,3.916392895112238,1,2318,50,2023-12-07 13:56:17
2016-09-26T14:01:08,4.7210221241380355,1,2318,90,2023-12-07 13:56:17
2016-09-26T14:01:08,12.516296947260326,1,2035,10,2023-12-07 13:56:17
2016-09-26T14:01:08,13.774480441232143,1,2035,50,2023-12-07 13:56:17
2016-09-26T14:01:08,14.480921694939136,1,2035,90,2023-12-07 13:56:17
2016-09-26T14:01:08,12.516296947259175,1,2035,10,2023-12-07 13:56:17
2016-09-26T14:01:08,13.774480441230986,1,2035,50,2023-12-07 13:56:17
2016-09-26T14:01:08,14.480921694937981,1,2035,90,2023-12-07 13:56:17

"""

# Opcion 1: escribir el SQL completo:
sql = "INSERT INTO 60_zonas (\
         time_start, valor, id_zona, id_parametro, percentil, fecha_insercion\
       ) VALUES \
         ('2024-01-22', 3.1415, 444, 2000, 0, '2024-01-22 10:03:13.000'),\
         ('2024-01-22', 3.1415, 444, 2001, 0, '2024-01-22 10:03:13.000'),\
         ('2024-01-22', 3.1415, 444, 2002, 0, '2024-01-22 10:03:13.000'),\
         ('2024-01-22', 3.1415, 444, 2003, 0, '2024-01-22 10:03:13.000'),\
         ('2024-01-22', 3.1415, 444, 2004, 0, '2024-01-22 10:03:13.000')\
       "
try: cur.execute(sql)
except mariadb.Error as e:
    print(f"Error: {e}")


# Opcion 2: usar ? como comodines para rellenar con un array:
sql = "INSERT INTO 60_zonas (time_start, valor, id_zona, id_parametro, percentil, fecha_insercion)\
    VALUES (?, ?, ?, ?, ?, ?)"

data = [("2000-01-28", "3.1415", "10", "8888", "JMB", "2000-01-28 10:03:13.000"),
        ("2000-01-28", "3.1415", "11", "8888", "77", "2000-01-28 10:03:13.000"),
        ("2000-01-28", "3.1415", "12", "8888", "77", "2000-01-28 10:03:13.000"),
        ("2000-01-28", "3.1415", "13", "8888", "77", "2000-01-28 10:03:13.000"),
        ("2000-01-28", "3.1415", "14", "8888", "77", "2000-01-28 10:03:13.000"),
        ("2000-01-28", "3.1415", "15", "8888", "77", "2000-01-28 10:03:13.000"),
        ("2000-01-28", "3.1415", "16", "8888", "77", "2000-01-28 10:03:13.000")]

try: cur.executemany(sql, data)
except mariadb.Error as e:
    print(f"Error: {e}")

# Nota: si es una sola fila, se puede usar cur.execute, en vez de cur.executemany

conn.commit()

# free resources
cur.close()
conn.close()

