#!/bin/bash

DATE=$(date "+%Y-%m-%d")
./insert_into_db.py -v -b gee_60zonas -t 60_zonas > gee_60zonas/log/INSERT60_$DATE.log

