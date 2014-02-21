import urllib2
import ldap
from os import geteuid

<<<<<<< HEAD
# API url
=======
if geteuid() != 0:
            exit("You need to have root privileges to run this script.\nPlease try again, this time using 'sudo'. Exiting.")

>>>>>>> bd49d3def3123c5b04dfe2c77759efddab206938
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


