#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# vim: set fileencoding=UTF-8 :

from drift_inc import common
from drift_inc import dldap
import argparse
from os import geteuid

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
