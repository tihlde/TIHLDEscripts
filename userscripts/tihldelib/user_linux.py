# coding: utf-8
import os
import shutil
from subprocess import call

import tihldelib.user_general as user_general

__author__ = 'Harald Floor Wilhelmsen'


def is_root():
    return os.geteuid == 0


def get_group_info(group_name):
    user_groups = {'students': {'homedir_base': '/home/students', 'gid_lx': 1007, 'gid_sql': 7, 'quota': '10G'},
                   'drift': {'homedir_base': '/home/staff', 'gid_lx': 1010, 'gid_sql': 10, 'quota': '100G'},
                   'xdrift': {'homedir_base': '/home/xdrift', 'gid_lx': 1011, 'gid_sql': 11, 'quota': '100G'},
                   'hs': {'homedir_base': '/home/hs', 'gid_lx': 1006, 'gid_sql': 6, 'quota': '20G'},
                   'xhs': {'homedir_base': '/home/xhs', 'gid_lx': 1012, 'gid_sql': 12, 'quota': '20G'}}
    return user_groups[group_name]


def make_home_dir(homedir_base, username, uid, linux_groupid):
    homedir_base = user_general.format_home_basedir(homedir_base)
    new_home_dir = homedir_base + username
    # if dir exists, do nothing
    if os.path.exists(new_home_dir):
        return 'Dir already exists'

    # else, copy /etc/skel to /home/students/<username>
    shutil.copytree('/etc/skel', new_home_dir)
    # chown <uid>:<gid> /home/students/<username>
    call(['chown', '-R', uid + ':' + str(linux_groupid), new_home_dir])
    # chmod 700 /home/students/<username>
    os.chmod(path=new_home_dir, mode=0o700)


def kill_user_processes(username):
    call(['killall', '--user', username, '--signal', '[15,9]'])


def set_quota(uid, quota_value):
    """
    Sets the quota for the given user to the given GB value.
    :param uid: Username of the user to set quota for
    :param quota_value: quota value
    :return: 'ok' if everything went well. None if not.
    """
    if is_root():
        call(['zfs', 'set', 'userquota@{0}={1}'.format(uid, quota_value), ' tank/home'])
        return 'ok'
    else:
        return None
