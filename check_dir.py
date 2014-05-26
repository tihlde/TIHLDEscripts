#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os


def check_dir_ifempty(dir):
    try:
        if not os.listdir(dir):
            print "empty"
        else:
            print "not empty"
    except Exception, e:
        print e
