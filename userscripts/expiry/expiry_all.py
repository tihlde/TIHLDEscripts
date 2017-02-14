# coding: utf-8
import tihldelib.user_ipa as ipalib
from expiry import password_expiry, user_expiry


def check_password_user_expiry_all():
    api = ipalib.get_ipa_api()
    # liste over alle brukere i IPA
    all_users = api.user_find()
    password_expiry.check_password_expiry(all_users)
    user_expiry.check_user_expiry(all_users)


if __name__ == '__main__':
    check_password_user_expiry_all()


# today = math.floor(time.time() / SECONDS_PER_DAY)
# print(today)
# print(strftime('%Y.%m.%d %H:%M:%S').format(datetime.today()))
