# coding: utf-8
import datetime

import tihldelib.user_ipa as ipalib
from expiry import password_expiry, user_expiry


def check_expiry_all():
    api = ipalib.get_ipa_api()
    # liste over alle brukere i IPA
    all_users = ipalib.get_all_users(api)
    for user in all_users:
        user_expiry.check_expire_single_user(user, api)
        password_expiry.check_password_expiry_single_user(user)


if __name__ == '__main__':
    check_expiry_all()


# today = math.floor(time.time() / SECONDS_PER_DAY)
# print(today)
# print(strftime('%Y.%m.%d %H:%M:%S').format(datetime.today()))
