# -*- coding: UTF-8 -*-
# vim: set fileencoding=UTF-8 :

__author__ = "Christopher McDowell (christmc 'at' tihlde.org), Thomas Juberg (thomas.juberg 'at' tihlde.org)"
__copyright__ = "Copyright (C) 2014 Trondheim Ingeniørhøgskoles Linjeforening for Dannede EDBere (TIHLDE)"
__license__ = "Apache License 2.0"


# Connection to the medlemsregister database
def medlemsregister_bind():
    f = open('/home/staff/drift/passord/db-medlemsregister', 'r')
    db = MySQLdb.connect(host='localhost',
                         user='medlemsregister',
                         passwd=f.next().strip(),
                         db='medlemsregister')
    return db


# Connection to the apache database
def apachedb_bind():
    f = open('/home/staff/drift/passord/db-apache', 'r')
    db = MySQLdb.connect(host='localhost',
                         user='apache',
                         passwd=f.next().strip(),
                         db='apache')
    return db
