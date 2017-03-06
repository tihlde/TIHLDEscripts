#!/usr/bin/env python3
# coding: utf-8

import json
import tihldelib.user_linux as user_linux
import tihldelib.user_ipa as user_ipa

__author__ = 'Thomas Juberg'


def main():
    user_linux.check_root()

    ipa_return = user_ipa.user_get('')
    if ipa_return is not None:
        if ipa_return['error'] is not None:
            print('An error occurred: ' + ipa_return['error']['message'])
        else:
            keys = {'krblastpwdchange', 'krbpasswordexpiration',
                    'shadowexpire', 'krbprincipalexpiration'}
            results = {}

            for element in ipa_return['result']['result']:
                uid = element['uid'][0]
                results[uid] = {}
                for key in keys:
                    if key in element:
                        results[uid][key] = element[key][0]

            with open('/tmp/root/dailyusers', 'w') as f:
                json.dump(results, f, ensure_ascii=False)


main()
