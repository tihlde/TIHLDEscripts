# coding: utf-8
import random
import string

from termcolor import colored

from tihldelib.email import Email

__author__ = 'Harald Floor Wilhelmsen'


def generate_password(password_length):
    """
    Generates a password with lower and upper case letters and numbers.
    :param password_length: Length of the password
    :return: The generated password as a string
    """
    lower = string.ascii_lowercase
    upper = string.ascii_uppercase
    nums = string.digits
    pw = []
    for i in range(password_length):
        lower_index = random.randint(0, len(lower) - 1)
        pw.append(lower[lower_index])

    for i in range(int(password_length / 2)):
        upper_index = random.randint(0, len(upper) - 1)
        pwindex = random.randint(0, password_length - 1)
        pw[pwindex] = upper[upper_index]

    for i in range(int(password_length / 4)):
        num_index = random.randint(0, len(nums) - 1)
        pwindex = random.randint(0, password_length - 1)
        pw[pwindex] = nums[num_index]
    return ''.join(pw)


def color(text, c):
    text = '[{0}]'.format(text)
    return colored(text, c)


def format_home_basedir(homedir_base):
    if homedir_base[-1] != '/':
        homedir_base += '/'
    return homedir_base


def read_email_resource(filename, prefix_res=True):
    if prefix_res:
        filename = 'resources/' + filename
    with open(filename, encoding='utf8') as file:
        subject = file.readline()
        body = ''.join(line for line in file)
        return Email(subject, body)
