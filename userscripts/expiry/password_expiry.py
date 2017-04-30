# coding: utf-8
import time

import tihldelib.expiry as expirylib
import tihldelib.user_email as maillib
import tihldelib.user_ipa as ipalib


def check_password_expiry_single_user(user):
    krb_pw_expiration_pattern = '%Y%m%d%H%M%SZ'
    krb_key = 'krbpasswordexpiration'

    if krb_key in user:
        time_string = user['krbpasswordexpiration'][0]
        now = time.time()
        expiry = int(time.mktime(time.strptime(time_string, krb_pw_expiration_pattern)))
        days_till_expiry = int((expiry - now) / expirylib.SECONDS_PER_DAY)  # int division
        if days_till_expiry in [0, 7, 14]:
            # send mail om det er 0, 7 eller 14 dager til
            email = maillib.read_email_resource('password_future_expiry.txt')
            responses = maillib.send_emails(user['mail'], email.subject, email.body)
            if responses:
                print(responses)


def check_password_expiry_all():
    api = ipalib.get_ipa_api()
    for user in ipalib.get_all_users(api):
        check_password_expiry_single_user(user)


if __name__ == '__main__':
    check_password_expiry_all()
