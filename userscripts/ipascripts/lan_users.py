# coding: utf-8
import os
import subprocess
import sys
from os.path import expanduser

__author__ = 'Harald Floor Wilhelmsen'

# python lan_users.py useramount
# ipa user-add lan-299 --homedir=/home/lan --random --gidnumber=1002 --shell=/bin/false --first=lan --last=bruker

formatstring = 'Format: python las_users.py useramount useridstart'

args = sys.argv

# Checking if there are sufficient arguments, if not exit
if len(args) != 3:
    sys.exit('Invaild number of arguments. ' + formatstring)

# The amount of users to create
useramount = args[1].strip()

# What id to start the first user on
useridstart = args[2].strip()

# The name of the user, everything before the id
userprename = 'lan-'

# Checking if useramount and useridstart are numbers, if not exit
if not useramount.isdigit() or not useridstart.isdigit():
    sys.exit('Wrong number-format. ' + formatstring)

# Casting useramount and useridstart to ints
useramount = int(useramount)
useridstart = int(useridstart)

print('Creating ' + str(useramount) + ' users with first user id ' + str(useridstart))

# Get the home-directory of the executor
outputfile = str(expanduser("~")) + '/lan_users'

# Create outputfile if it does not exist
os.system('touch ' + outputfile)

# Loop through amount of users
for i in range(0, useramount, 1):
    # Create login-name
    newlogin = userprename + str(i + useridstart)
    # Create command to ipa
    cmd = 'ipa user-add %s --homedir=/home/lan --random --gidnumber=1002 --shell=/bin/false --first=lan --last=bruker | grep "\(login\|password\)" >> %s ' %  (newlogin, outputfile)
    # Call command to ipa
    os.system(cmd)
    print('User ' + newlogin + ' created')

print('Done. Results added to file ' + outputfile)
