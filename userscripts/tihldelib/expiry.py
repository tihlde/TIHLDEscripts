import datetime

SECONDS_PER_DAY = 86400


def krb_expiry_to_datetime(expiry_string):
    # example 20170715
    return datetime.datetime.strptime(expiry_string[:8], '%Y%m%d')


def epochdays_to_datetime(epoch_days):
    return datetime.datetime.utcfromtimestamp(epoch_days * SECONDS_PER_DAY)