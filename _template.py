#!/usr/bin/env python3                                                                                                                                                                                                                   i
# -*- coding: UTF-8 -*-
# vim: set fileencoding=UTF-8 :

__author__ = "Name (Name 'at' Domain)"
__copyright__ = "Copyright (C) 2014 Trondheim Ingeniørhøgskoles Linjeforening for Dannede EDBere (TIHLDE)"
__license__ = "Apache License 2.0"

from os import sys, geteuid, path
from inspect import currentframe, getfile
currentdir = path.dirname(path.abspath(getfile(currentframe())))
parentdir = path.dirname(currentdir)
sys.path.insert(0, parentdir)
