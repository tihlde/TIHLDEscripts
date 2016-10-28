# coding: utf-8
import random
import string

import pymysql

from userscripts.ipascripts.ipahttp import ipa

__author__ = 'Harald Floor Wilhelmsen'


def generate_password(pwlen):
    """
    Generates a password with lower and upper case letters and numbers.
    :param pwlen: Length of the password
    :return: The generated password as a string
    """
    lower = string.ascii_lowercase
    upper = string.ascii_uppercase
    nums = string.digits
    pw = []
    for i in range(pwlen):
        lower_index = random.randint(0, len(lower) - 1)
        pw.append(lower[lower_index])

    for i in range(int(pwlen / 2)):
        upper_index = random.randint(0, len(upper) - 1)
        pwindex = random.randint(0, pwlen - 1)
        pw[pwindex] = upper[upper_index]

    for i in range(int(pwlen / 4)):
        num_index = random.randint(0, len(nums) - 1)
        pwindex = random.randint(0, pwlen - 1)
        pw[pwindex] = nums[num_index]
    return ''.join(pw)


def get_ipa_api(uri='ipa1.tihlde.org'):
    """
    Create an api towards ipa with the given uri.
    :param uri: Uri towards an ipa-server. Will be ipa1.tihlde.org if left at None
    :return: The api
    """
    api = ipa(uri, sslverify=True)
    # username, password(second line of ipa-admin password-file)
    api.login('admin', open("/home/staff/drift/passord/ipa-admin").readlines()[1].replace('\n', '').strip())
    return api


def add_single_user(username, firstname, lastname, course, email, groupid, password=None, api=None):
    """
    Adds a single user to ipa and apache
    :param password: The password of the new user. If null, one will be generated using @generate_password
    :param api: API towards FREEIPA. This method assumes a login-request has been successful towards the IPA-server. \
    If None, one will be created towards ipa1.tihlde.org, and a login-request will be sent
    :return: The password and user id of the created user
    """
    if not api:
        api = get_ipa_api()

    if not password:
        password = generate_password(12)

    gecos = str(firstname) + ' ' + str(lastname) + ' ,' + str(email) + ' ,' + str(course)

    info = \
        {
            "givenname": firstname,
            "sn": lastname,
            "userpassword": password,
            "gecos": gecos,
            "gidnumber": groupid,
            "homedirectory": "/home/students/" + username
        }

    response = api.user_add(username, info)
    error_response = response['error']
    if error_response:
        return
    return [response['result']['result']['uidnumber'], password]


def add_user_apache():
    apache_db = pymysql.connect(host="localhost",
                                user="apache",
                                password=open("/home/staff/drift/passord/db-apache").readline().replace('\n', ''),
                                database="apache",
                                charset='utf8')
    apache_cursor = apache_db.cursor()
