#!/bin/bash

DATE=$(date "+%Y-%m-%d")
./insert_into_db.py -v -b gee_7zonas/output -t 7_zonas > gee_7zonas/log/INSERT_$DATE.log

