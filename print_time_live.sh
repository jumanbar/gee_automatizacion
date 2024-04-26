# Basado en
# https://stackoverflow.com/questions/1401482/yyyy-mm-dd-format-date-in-shell-script/1401495#1401495
while : 
do 
    printf "%(%Y-%m-%d %H:%M:%S)T\r" -1
    sleep 1
done

