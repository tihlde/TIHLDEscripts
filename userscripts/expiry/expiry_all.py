# coding: utf-8
import datetime

import tihldelib.user_ipa as ipalib
from expiry import password_expiry, user_expiry


def format_krb_expiry(expiry_string):
    # example 20170715
    return datetime.datetime.strptime(expiry_string[:8], '%Y%m%d')


def get_all_users(api=ipalib.get_ipa_api()):
    return api.user_find()['result']['result']


def check_password_user_expiry_all():
    api = ipalib.get_ipa_api()
    # liste over alle brukere i IPA
    all_users = get_all_users(api)
    for user in all_users:
        user_expiry.check_expire_single_user(user, api)
        password_expiry.check_password_expiry(user)


if __name__ == '__main__':
    check_password_user_expiry_all()


# today = math.floor(time.time() / SECONDS_PER_DAY)
# print(today)
# print(strftime('%Y.%m.%d %H:%M:%S').format(datetime.today()))
