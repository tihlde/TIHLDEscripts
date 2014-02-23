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
#import smtplib
#from email.MIMEMultipart import MIMEMultipart
#from email.MIMEText import MIMEText
from datetime import datetime
import calendar
from pprint import pprint

notifyToEmail = 'drift@tihlde.org'
notifyFromEmail = 'noreply@tihlde.org'
ldapUsername = 'admin'
ldapServer = 'ldap://127.0.0.1:389'
myBaseDN = 'dc=tihlde,dc=org'
mySScope = ldap.SCOPE_SUBTREE
myRAttrs = None

SECONDS_IN_DAY = 86400
ANSI_TAB = '\011'
ANSI_BOLD = '\033[1m'
ANSI_RED = '\033[31m'
ANSI_BLINK = '\033[5m'
ANSI_RESET = '\033[0m'


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
        #print 'Debug: ' + ldapServer + ' ' + username + ' ' + password
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


def search_ldapou(groupOU, hostOU, searchFilter, retrieveAttributes=myRAttrs,
                  searchScope=mySScope, baseDN=myBaseDN):
    try:
        lcon = ldap_bind()
        string = ''
        if groupOU is not None:
            string += 'ou={},'.format(groupOU)
        if hostOU is not None:
            string += 'ou={},'.format(hostOU)
        string += '{}'.format(baseDN)
        ldap_result_id = lcon.search(string, searchScope, searchFilter,
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


# Parse ldap result and return human readable form
def parse_ldapuser(user, group_ou=None, base_dn=myBaseDN):
    ret = ''
    for u in user:
        u = u[1]
        # cn
        if 'cn' in u and u['cn'][0] is not None:
            ret += 'Name:{}{}\n'.format(ANSI_TAB, u['cn'][0])
        # gecos
        if 'gecos' in u and u['gecos'][0] is not None:
                ret += 'Gecos:{}{}\n'.format(ANSI_TAB, u['gecos'][0])
        # uid
        if 'uid' in u and u['uid'][0] is not None:
            ret += 'User:{}{}\n'.format(ANSI_TAB, u['uid'][0])
        # uidNumber
        if 'uidNumber' in u and u['uidNumber'][0] is not None:
            ret += 'Uid:{}{}\n'.format(ANSI_TAB, u['uidNumber'][0])
        # gidNumber
        if 'gidNumber' in u and u['gidNumber'][0] is not None:
            ret += 'Groups:'
            for gid,gname in ldap_find_group_membership(u['uid'][0], None, base_dn).iteritems():
                ret += '{}{} ({})\n'.format(ANSI_TAB, gname, gid)
            #ret += 'Gid:{}{}\n'.format(ANSI_TAB, u['gidNumber'][0])
            #if 'uid' in u and u['uid'][0] is not None:
            #    ret += 'Groups:{}'.format(ldap_find_group_membership(u['uid'][0], None, base_dn))
        # homeDirectory
        if 'homeDirectory' in u and u['homeDirectory'][0] is not None:
            ret += 'Home:{}{}\n'.format(ANSI_TAB,
                                        u['homeDirectory'][0])
        # loginShell
        if 'loginShell' in u and u['loginShell'][0] is not None:
            ret += 'Shell:{}{}\n'.format(ANSI_TAB,
                                         u['loginShell'][0])
        # mail
        if 'mail' in u and u['mail'][0] is not None:
            ret += 'EMail: '
            for mail in u['mail']:
                ret += '{}{}\n'.format(ANSI_TAB,
                                       mail)
        # shadowExpire
        if 'shadowExpire' in u and u['shadowExpire'][0] is not None:
            ret += 'Expire:{}'.format(ANSI_TAB)
            expired = ldap_is_timestamp_expired(u['shadowExpire'][0])
            if expired:
                ret += ANSI_BOLD + ANSI_RED + ANSI_BLINK
            ret += '{}'.format(ldap_timestamp_to_date(float(u['shadowExpire'][0])))
            if expired:
                ret += ANSI_RESET
            ret += '\n'
        else:
            ret += 'Expire:{}No expiry\n'.format(ANSI_TAB)
        # sadowLasteChange
        if 'shadowLastChange' in u and u['shadowLastChange'][0] is not None:
            ret += 'Passwd:{}'.format(ANSI_TAB)
            expired = ldap_is_timestamp_expired(int(u['shadowLastChange'][0]) + int(u['shadowMax'][0]))
            if expired:
                ret += ANSI_BOLD + ANSI_RED + ANSI_BLINK
            ret += '{}'.format(ldap_timestamp_to_date(float(int(u['shadowLastChange'][0]) + int(u['shadowMax'][0]))))
            if expired:
                ret += ANSI_RESET
            ret += '\n'
    print(ret)


def ldap_timestamp_to_date(timestamp):
    return (datetime.utcfromtimestamp(int(timestamp) * SECONDS_IN_DAY).strftime('%d/%m %Y'))


# Return todays date in LDAP
def ldap_timestamp_today():
    return (calendar.timegm(datetime.today().utctimetuple()) / SECONDS_IN_DAY)


# return timestamp with number of years added
def ldap_timestamp_add_years(timestamp, years):
    return int(timestamp) + (years * 365)

# return a dictionaru with group names and ids a username is member of.
# first entry will be the primary membership
def ldap_find_group_membership(uid, group_ou=None, base_dn=myBaseDN):
    result = search_ldapou(group_ou, base_dn, 'uid={}'.format(uid), ['gidNumber'])
    gid = result[0][0][1]['gidNumber'][0]
    result = search_ldapou(group_ou, base_dn, '(&(objectClass=posixGroup)(gidNumber={}))'.format(gid))
    gname = result[0][0][1]['cn'][0]
    ret = {gid: gname}
    #ret = '{}{} ({}) (primary)\n'.format(ANSI_TAB, gname, gid)
    result = search_ldapou(group_ou, base_dn, '(&(objectClass=posixGroup)(memberUid={}))'.format(uid))
    for group in result:
        group = group[0][1]
        ret[group['gidNumber'][0]] = group['cn'][0]
        #ret += '{}{} ({})\n'.format(ANSI_TAB, group[0][1]['cn'][0], group[0][1]['gidNumber'][0])
    #pprint(ret)
    return ret

# Simple function to compare timestamp against NOW and return true if its older.
def ldap_is_timestamp_expired(timestamp):
    if int(timestamp) < ldap_timestamp_today():
        return True
    return False
