# coding: utf-8

import tihldelib.user_general as user_general
from tihldelib.ipahttp import ipa

__author__ = 'Harald Floor Wilhelmsen'


def get_ipa_api(uri='ipa1.tihlde.org'):
    """
    Create an api towards ipa with the given uri.
    :param uri: Uri towards an ipa-server. Will be ipa1.tihlde.org if left at None
    :return: The api
    """
    api = ipa(uri, sslverify=True)
    # username, password(second line of ipa-admin password-file)
    api.login('admin', open("/home/staff/drift/passord/ipa-admin").readlines()[1].replace('\n', '').strip())
    return api


def get_ipa_api_if_not_exists(api):
    if not api:
        return get_ipa_api()
    return api


def ipa_error_occurred(response):
    return response['error']


def add_user_ipa(username, firstname, lastname, groupid, homedir_base, course=None, email=None, password=None,
                 api=None):
    """
    Adds a single user to ipa
    :param homedir_base: the directory to place this user's home in. Example: /home/students/
    :param password: The password of the new user. If null, one will be generated using @generate_password
    :param api: API towards FREEIPA. This method assumes a login-request has been successful towards the IPA-server.
            If None, an ipa api object will be created towards ipa1.tihlde.org, and a login-request will be sent.
            If adding more than one user, you should get the api first, using the method @get_ipa_api and pass it
            in to all your method-calls.
    :return: The password and user id of the created user in an array; [uid, pw]
    """
    if not api:
        api = get_ipa_api()

    if not password:
        password = user_general.generate_password(12)

    homedir_base = user_general.format_home_basedir(homedir_base)

    gecos = str(firstname) + ' ' + str(lastname) + ' ,' + str(email) + ' ,' + str(course)

    info = \
        {
            "givenname": firstname,
            "sn": lastname,
            "userpassword": password,
            "gecos": gecos,
            "gidnumber": groupid,
            "homedirectory": homedir_base + username
        }

    response = api.user_add(username, info)
    error_response = response['error']
    if error_response:
        return
    return [response['result']['result']['uidnumber'], password]


def user_get(username=None, api=None):
    """
    Gets a user from the given ipa api-object.
    :param username: username of the user to get
    :param api: Api towards the ipa-server. Should be overriden if this method should be used more than once.
            If None is given this method will create it's own api-object
    :return: A dictionary with response-data from IPA. You can use @user_exists_from_output with this output-
            object to find if a user exists.
    """
    if not api:
        api = get_ipa_api()
    return api.user_find(username)


def get_all_users(api=get_ipa_api()):
    return api.user_find()['result']['result']


def user_exists_from_output(user_get_output):
    """
    Returns True or False representing if a user exists or not, based on output from @user_get.
    :param user_get_output: Output from @user_get
    :return: True if the user exists. False otherwise
    """
    return user_get_output['result']['summary'] != '0 users matched'


def user_exists(username, api=None):
    """
    Uses @user_get and @user_exists_from_output to figure out the given user exists.
    :param username: username of the user to check
    :param api: api towards ipa. If not overridden a new api-object will be created towards ipa1.tihlde.org
            for each call of this method.
    :return: True if the user exists. False otherwise
    """
    api = get_ipa_api_if_not_exists(api)
    return user_exists_from_output(user_get(username, api))


def user_get_group(username, api=None):
    """
    Gets a user groups from the given ipa api-object.
    :param username: username of the user to get
    :param api: Api towards the ipa-server. Should be overriden if this method should be used more than once.
            If None is given this method will create it's own api-object
    :return: A dictionary with response-data from IPA.
    """
    if not api:
        api = get_ipa_api()

    return api.user_show(username)['result']['result']['memberof_group']


def set_homedirectory(username, path, api=None):
    """
    Set homedirectory for user.
    :param username: username of the user to get
    :param path: path to homedirectory.
    :param api: Api towards the ipa-server. Should be overriden if this method should be used more than once.
            If None is given this method will create it's own api-object
    :return: A dictionary with response-data from IPA.
    """
    if not api:
        api = get_ipa_api()

    # if not os.path.isdir(path):
    #     return False

    return api.user_mod(username, setattrs=u'homedirectory={0}'.format(path))


def set_loginshell(username, shell_new_path, api=get_ipa_api()):
    api = get_ipa_api_if_not_exists(api)
    return api.user_mod(username, setattrs={'loginshell': shell_new_path})
