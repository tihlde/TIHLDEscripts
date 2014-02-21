# -*- coding: UTF-8 -*-
# vim: set fileencoding=UTF-8 :

import ldap
import string
import sys
import MySQLdb
import ldap.modlist as modlist
import re
import base64
import hashlib
import os
import random
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

notifyToEmail = 'drift@tihlde.org'
notifyFromEmail = 'noreply@tihlde.org'
ldapUsername = 'admin'
ldapServer = 'ldap://127.0.0.1:389'
myBaseDN = 'dc=tihlde,dc=org'
mySScope = ldap.SCOPE_SUBTREE
myRAttrs = None


def ldap_bind():
    try:
        global myBaseDN
        global ldapUsername
        global ldapServer
        username = 'cn=' + ldapUsername + ',' + myBaseDN
        f = open('/etc/pam_ldap.secret', 'r')  # opens the ldap-password file
        password = f.next().strip()  # reads the password from the file
                                     # and strips the whitespaces
        lcon = ldap.initialize(ldapServer)
        lcon.simple_bind_s(username, password)
    except ldap.LDAPError, e:
        print 'ldap_bind() error: ' + str(e)
        print 'Debug: ' + ldapServer + ' ' + username + ' ' + password
        sys.exit('Fatal feil. Kunne ikke koble til LDAP Tjener')
    else:
        return lcon


# Connection to the medlemsregister database
def medlemsregister_bind():
    f = open('/home/staff/drift/passord/db-medlemsregister', 'r')
    db = MySQLdb.connect(host='localhost',
                         user='medlemsregister',
                         passwd=f.next().strip(),
                         db='medlemsregister')
    return db


# Connection to the apache database
def apachedb_bind():
    f = open('/home/staff/drift/passord/db-apache', 'r')
    db = MySQLdb.connect(host='localhost',
                         user='apache',
                         passwd=f.next().strip(),
                         db='apache')
    return db


def search_ldapou(groupOU, hostOU, searchFilter, retrieveAttributes=myRAttrs, searchScope=mySScope,
                  baseDN=myBaseDN):
    try:
        lcon = ldap_bind()
        ldap_result_id = lcon.search('ou=' + groupOU + ', ou=' + hostOU + ', '
                                     + baseDN, searchScope, searchFilter,
                                     retrieveAttributes)
        result_set = []
        while 1:
            result_type, result_data = lcon.result(ldap_result_id, 0)
            if (result_data == []):
                break
            else:
                if result_type == ldap.RES_SEARCH_ENTRY:
                    result_set.append(result_data)

    except ldap.LDAPError, e:
        print ("search_ldapou error: ", e)

    lcon.unbind()
    return result_set


# Generate random password with digits, uppercase characters
# and lowercase characters
def pw_generator(size=12, chars=string.ascii_uppercase + string.digits
                 + string.ascii_lowercase):
    return ''.join(random.choice(chars) for x in range(size))


# Salts and encrypts the password with SSHA for use in ldap
def ldappassword(rawpass):
    salt = os.urandom(26)  # edit the length as you see fit
    return '{SSHA}' + base64.b64encode(hashlib.sha1(rawpass + salt).digest()
           + salt)


# Changes unicode chars to actual characters
def norify(name):
    name = re.sub(r'\xc3,', 'ø', name)
    name = re.sub(r'\xc3\x98', 'Ø', name)
    name = re.sub(r'\xc3\xa6', 'æ', name)
    name = re.sub(r'\xc3\xa5', 'å', name)
    name = re.sub(r'\xc3\x85', 'Å', name)
    return name


# Changes æøå to non-special characters
def denorify(name):
    name = re.sub('ø', 'oe', name)
    name = re.sub('å', 'aa', name)
    name = re.sub('Æ', 'AE', name)
    name = re.sub('Ø', 'OE', name)
    name = re.sub('Å', 'AA', name)
    return name


# Returns highest free id of given type on given server in given OUs of BaseDN
def highid(idType, groupOU, hostOU, searchScope=mySScope, baseDN=myBaseDN):
    lcon = ldap_bind()
    i = 0
    idNumber = 0
    idType = int(idType)

    if (idType == 1):
        retrieveAttributes = ['uidNumber']
        searchFilter = 'uidNumber=*'
    elif (idType == 2):
        if (hostOU.lower() == 'colargol'):
            idNumber = 9999
            # For å unngå framtidige problemer da det ligger grupper på
            # enkelte høye IDer per i dag, så starter vi på 10000 for
            # framtidige automatisk genererte IDer. - ThomasJ

        retrieveAttributes = ['gidNumber']
        searchFilter = 'gidNumber=*'
    else:
        sys.exit('highid() called with unknown idType. Exiting')

    # Loop for getting the highest possible idNumber in use
    while True:
        try:
            ldap_result_id = lcon.search('ou=' + groupOU + ', ou=' + hostOU
                                         + ', ' + baseDN, searchScope,
                                         searchFilter, retrieveAttributes)
            result_set = []
            while 1:
                result_type, result_data = lcon.result(ldap_result_id, 0)
                if (result_data == []):
                    break
                elif (result_type == ldap.RES_SEARCH_ENTRY):
                    result_set.append(result_data)
            while (i < len(result_set)):
                tmpid = str(result_set[i][0][1])[16: -2].replace("'", "")
                i += 1
                if (int(tmpid) > idNumber):
                    idNumber = int(tmpid)
        except ldap.LDAPError, e:
            print e
            break
        idNumber += 1  # adds one to the idNumber so it starts with a number
                       # which is not in use
        lcon.unbind()
        return idNumber


def add_group(groupName, groupOU, hostOU, baseDN=myBaseDN):
    try:
        group = groupName.lower()
        lcon = ldap_bind()
        gid = highid(2, groupOU, hostOU)
        dn = 'cn=' + group + ',ou=' + groupOU + ',ou=' + hostOU + ',' + baseDN
        print dn
        attrs = {}
        attrs['objectclass'] = ['posixGroup', 'top']
        attrs['cn'] = group
        attrs['gidNumber'] = str(gid)
        ldif = modlist.addModlist(attrs)
        lcon.add_s(dn, ldif)

    except ldap.LDAPError, e:
        print 'add_group() error: ' + str(e)
    else:
         print 'Success?'
    lcon.unbind()
