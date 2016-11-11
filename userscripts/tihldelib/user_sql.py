# coding: utf-8
import pymysql

__author__ = 'Harald Floor Wilhelmsen'


def mysql_connect(host, username, password, database_name, charset='utf8'):
    """
    Returns a connection-object to a MySQL database.
    :param host: host with database
    :param username: username to authenticate towards mysql
    :param password: password to authenticate towards mysql
    :param database_name: name of database
    :param charset: charset of communications between you and the database. Should not be overridden.
    :return: The connection object
    """
    return pymysql.connect(host=host,
                           user=username,
                           password=password,
                           database=database_name,
                           charset=charset)


def add_user_apache(username, groupid, apache_conn=None, apache_cursor=None, commit_and_close=True):
    """
    Inserts a single user into the apache database
    :param username: The username of the user to add to the database
    :param groupid: Group id of the new user. In sql style. E. g. students us '7'
    :param apache_conn: PyMySQL connection object. If None a new one will be created
    :param apache_cursor: PyMySQL cursor-object. If None a new one will be
    :param commit_and_close: Set to False if this method should NOT commit the query and
            close the cursor and connection to the database. Default if True
    :return: None if successful. An error-message if not.
    """
    if not apache_cursor:
        if not apache_conn:
            apache_pw = open("/home/staff/drift/passord/db-apache").readline().rstrip('\n')
            apache_conn = mysql_connect("localhost", "apache", apache_pw, "apache")
        apache_cursor = apache_conn.cursor()
    try:
        apache_cursor.execute(
            "INSERT INTO `apache`.`brukere` (`id`, `brukernavn`, `gruppe`, `expired`, `deaktivert`, `webdav`, `kommentar`) "
            "VALUES (NULL, '{0}', '{1}', 'false', 'false', 'false', '');".format(username, str(groupid)))
        if commit_and_close:
            apache_conn.commit()
            apache_cursor.close()
            apache_conn.close()
        return
    except pymysql.Error as err:
        return 'Error when pushing user {0} to the apache database:\n{1}' \
            .format(username, err)
