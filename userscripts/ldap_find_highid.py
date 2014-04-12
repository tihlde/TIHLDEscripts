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
import argparse

if geteuid() != 0:
        exit("You need to have root privileges to run this script.\nPlease try again, this time using 'sudo'. Exiting.")

parser = argparse.ArgumentParser(description='Script som finner høyeste ledige brukerid (uid) eller gruppeid (gid) for en gitt tjener.')
args = parser.parse_args()

cont = False
while cont == False:
    attr = common.read_input('Angi id type:\n1: uid\n2: gid\n')
    i = int(attr)
    if (i == 1):
        ou1 = 'Brukere'
        idType = i
        cont = True
    elif (i == 2):
        ou1 = 'Grupper'
        idType = i
        cont = True
    else:
        print "Du må angi gyldig verdi"

ou2 = common.read_input('Angi tjener OU [Colargol]: ')
ou2 = ou2 or 'Colargol'


print dldap.highid(idType, ou1, ou2)
