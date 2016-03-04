# coding: utf-8
import os
import subprocess
import sys
from os.path import expanduser

__author__ = 'Harald Floor Wilhelmsen'

# python lan_users.py useramount
# ipa user-add lan-299 --homedir=/home/lan --random --gidnumber=1002 --shell=/bin/false --first=lan --last=bruker

args = sys.argv

useramount = args[1].strip()
useridstart = args[2].strip()
userprename = 'lan-'

if not useramount.isdigit() or not useridstart.isdigit():
    sys.exit('Wrong format. Format: python las_users.py useramount useridstart')

useramount = int(useramount)
useridstart = int(useridstart)

print('Creating ' + str(useramount) + ' users with first user id ' + str(useridstart))

process = subprocess.Popen(['echo', '$HOME'], stdout=subprocess.PIPE, shell=True)
(executorHome, err) = process.communicate()
outputfile = str(expanduser("~")) + '/lan_users'

os.system('touch ' + outputfile)

for i in range(0, useramount, 1):
    newlogin = userprename + str(i + useridstart)
    cmd = 'ipa user-add %s --homedir=/home/lan --random --gidnumber=1002 --shell=/bin/false --first=lan --last=bruker | grep "\(login\|password\)" >> %s ' %  (newlogin, outputfile)
    os.system(cmd)

print('Done. Results added to file ' + outputfile)
