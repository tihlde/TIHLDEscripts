#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# vim: set fileencoding=UTF-8 :

"LDAP Search"

__author__ = "Thomas Juberg (thomas.juberg 'at' tihlde.org)"
__copyright__ = "Copyright (C) 2014 Trondheim Ingeniørhøgskoles Linjeforening for Dannede EDBere (TIHLDE)"
__license__ = "Apache License 2.0"

from drift_inc import common
from drift_inc import dldap
import pprint
from os import geteuid

if geteuid() != 0:
            exit("You need to have root privileges to run this script.\nPlease try again, this time using 'sudo'. Exiting.")

ou1 = common.read_input('Angi gruppe OU [Brukere]: ')
ou1 = ou1 or 'Brukere'

ou2 = common.read_input('Angi tjener OU [Colargol]: ')
ou2 = ou2 or 'Colargol'

cont = False
while cont is False:
    attr = common.read_input('Søk på:\n1: uid\n2: navn\n')
    if (int(attr) == 1):
        streng = 'uid='
        cont = True
    elif (int(attr) == 2):
        streng = 'cn='
        cont = True
    else:
        print"Du må angi gyldig verdi"

streng = streng + common.read_input('Angi søkestreng: ')

resultat = []
resultat = dldap.search_ldapou(ou1, ou2, streng, ['shadowExpire', 'gecos', 'uid', 'gidNumber', 'uidNumber', 'cn', 'homeDirectory', 'loginShell', 'mail', 'shadowLastChange', 'shadowMax'])

for res in resultat:
    dldap.parse_ldapuser(res,ou1,ou2)

