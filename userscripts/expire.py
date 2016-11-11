# coding: utf-8
import calendar
import time

from datetime import datetime
from time import strftime

import math

__author__ = 'Harald Floor Wilhelmsen'

# liste over alle brukere i IPA
#   sjekk shadow-expire
#   sjekk shadow-expire
#       er det 30 14 eller 7 dager til brukeren gaar ut: send mail om det til brukeren
#       har brukeren gaatt ut: Er expired shell ikke satt, sett expired shell
#   password expire
#       send mail om det er 0, 7 eller 14 dager til

SECONDS_PER_DAY = 86400

today = math.floor(time.time() / SECONDS_PER_DAY)

print(today)
print(strftime('%Y.%m.%d %H:%M:%S').format(datetime.today()))
