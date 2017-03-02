#!/usr/bin/env python
# -*- coding: utf-8 -*-
from os import sys, geteuid, path
from inspect import currentframe, getfile
currentdir = path.dirname(path.abspath(getfile(currentframe())))
parentdir = path.dirname(currentdir)
sys.path.insert(0, parentdir)
import urllib2
import json
import threading
from drift_inc import dldap

__author__ = "Bjørn Gilstad (bjorngi 'at' tihlde.org)"
__copyright__ = "Copyright (C) 2014 Trondheim Ingeniørhøgskoles" \
                "Linjeforening for Dannede EDBere (TIHLDE)"
__license__ = "Apache License 2.0"

# API url
if geteuid() != 0:
            exit("You need to have root privileges to run this script."
                 "\nPlease try again, this time using 'sudo'. Exiting.")

api_url = 'https://haveibeenpwned.com/api/v2/breachedaccount/'

ou1 = 'Brukere'
ou2 = 'Colargol'

resultat = dldap.search_ldapou(ou1, ou2, 'cn=*', ['mail'])
ldapaddress = []
for res in resultat:
    ldapaddress.append(dldap.parse_ldapmail(res, ou1, ou2))

emails = []
for mails in ldapaddress:
    for mail in mails:
        emails.append(mail)

testemails = ['test@test.com', 'kvhansen@online.no', 'sengir@start.no',
              'thomas.juberg@gmail.com']
breached_users = {}


def chunkIt(seq, num):
    avg = len(seq) / float(num)
    out = []
    last = 0.0

    while last < len(seq):
        out.append(seq[int(last):int(last + avg)])
        last += avg

    return out


# TODO: Gjøre noe mer fornuftig enn å skrive de ut til skjerm
def checkmail(emails):
    """checks list of emails for compromised emails"""
    for email in emails:
        lst = []
        try:
            response = urllib2.urlopen(api_url+email).read()
            json_data = json.loads(response)
            #print(email + " has been compromised in the following places: ")
            for i in json_data:
                lst.append(i.get('Name'))
                #print(i.get('Name'))
            breached_users.update({email: lst})

        except urllib2.HTTPError:
            pass

threads = []

for i in chunkIt(emails, 100):
    thread = threading.Thread(target=checkmail, args=[i])
    thread.start()
    threads.append(thread)

for thread in threads:
    thread.join()

print(breached_users)
