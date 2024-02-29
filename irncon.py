#! /usr/bin/env python

import re
from os.path import expanduser

def getConndetails():

    f = open(expanduser('~/.my.cnf'), 'r')
    lines = f.readlines()
    out = {}

    is_group = False
    grpattern = re.compile('^\[datos_irn\]')
    eqpattern = re.compile('=')
    for line in lines:
        line = line.strip()
        if grpattern.search(line):
            is_group = True
            continue

        m = eqpattern.search(line)
        if is_group and m:
            spLine = re.split('=', line)
            out[spLine[0]] = spLine[1]
        else:
            is_group = False

    return out
