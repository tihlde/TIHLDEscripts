# coding: utf-8
import subprocess
import sys

__author__ = 'Harald Floor Wilhelmsen'

# python lan_users.py useramount
# ipa user-add lan-299 --homedir=/home/lan --random --gidnumber=1002 --shell=/bin/false --first=lan --last=bruker

args = str(sys.argv).split(' ')

useramount = args[0].strip()
useridstart = args[1].strip()
userprename = 'lan-'

if not useramount.isdigit() or not useridstart.isdigit():
    sys.exit('Wrong format. Format: python las_users.py useramount useridstart')

useramount = int(useramount)
useridstart = int(useridstart)

print('Creating ' + str(useramount) + ' users with first user id ' + str(useridstart))

executorHome = subprocess.Popen('echo $HOME').stdout.read(300)
outputfile = executorHome + '/lan_users'

for i in range(0, useramount, 1):
    newlogin = userprename + str(i + useridstart)
    subprocess.Popen(['ipa user-add ', newlogin, ' --homedir=/home/lan --random --gidnumber=1002 --shell=/bin/false --first=lan --last=bruker '
                                         '| egrep \(User login\|Random password\) > ', outputfile])

print('Done. Results added to file ' + outputfile)
