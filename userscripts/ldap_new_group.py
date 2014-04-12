#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# vim: set fileencoding=UTF-8 :

__author__ = "Thomas Juberg (thomas.juberg 'at' tihlde.org)"
__copyright__ = "Copyright (C) 2014 Trondheim Ingeniørhøgskoles Linjeforening for Dannede EDBere (TIHLDE)"
__license__ = "Apache License 2.0"

from os import sys, geteuid, path
from inspect import currentframe, getfile
currentdir = path.dirname(path.abspath(getfile(currentframe())))
parentdir = path.dirname(currentdir)
sys.path.insert(0, parentdir) 
from drift_inc import common, dldap
from drift_inc import dldap
import argparse

if geteuid() != 0:
            exit("You need to have root privileges to run this script.\nPlease try again, this time using 'sudo'. Exiting.")

parser = argparse.ArgumentParser(description='Script som finner høyeste \
        ledige brukerid (uid) eller gruppeid (gid) for en gitt tjener.')
args = parser.parse_args()

ou1 = common.read_input('Angi gruppe OU [Grupper]: ')
ou1 = ou1 or 'Grupper'

ou2 = common.read_input('Angi tjener OU [Colargol]: ')
ou2 = ou2 or 'Colargol'

group = common.read_input('Angi navn på gruppen som skal opprettes: ')

# FIXME - Error checks

cont = 0
while cont == 0:
    c = common.read_input('Verifiser og bekreft angitt data:\nDN: ou='
                          + ou1 + ',ou=' + ou2 + '\nNy gruppe: '
                          + group + '\nIs this correct?`[Y]es/[N]o: ')
    print c
    if (str(c).lower == "yes" or "y"):
        cont = 1
    elif (str(c).lower == "no" or "n"):
        cont = 2

# Until we clean things up, just exit
if cont == 2:
    print cont
    sys.exit('Run me again to try again :(')

dldap.add_group(group, ou1, ou2)
