import urllib2
import ldap
from os import geteuid

__author__ = "Bjørn Gilstad (bjorngi 'at' tihlde.org)"
__copyright__ = "Copyright (C) 2014 Trondheim Ingeniørhøgskoles Linjeforening for Dannede EDBere (TIHLDE)"
__license__ = "Apache License 2.0"

# API url
if geteuid() != 0:
            exit("You need to have root privileges to run this script.\nPlease try again, this time using 'sudo'. Exiting.")

api_url = 'https://haveibeenpwned.com/api/v2/breachedaccount/'

#Initiation email array
emails = []
emails.append('test@test.com')
emails.append('test2@test.com')

breached_users = []

for x in emails:
    try:
        response = urllib2.urlopen(api_url+email).read()
        print(response)

    except urllib2.HTTPError:
        print('Not found')


