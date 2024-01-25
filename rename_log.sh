
FECHA=`date +%Y%m%d`

cp log.log log$FECHA.log
cp log60.log log60$FECHA.log

mv log$FECHA.log gee_7zonas/log/
mv log60$FECHA.log gee_60zonas/log/

