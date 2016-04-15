#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from requests import Session
import configparser

config = configparser.ConfigParser()
config.read('senseable_gym/sg_run/machine_updater.ini')
ip = config['SERVER']['ip']
port = config['SERVER']['port']
password = config['SERVER']['pass']


def login(s, username, password, debug = False):
    r = s.post("http://localhost:5000/login", data={'action': 'login', 'user': username, 'password': password })
    if debug:
        print(r.status_code, r.reason)
        print(r.text[:300] + '...')

def send_update(s, machine_id: int, machine_status: int, debug=False):
    # TODO: Use a real post request
    # TODO: Parameterize the url?
    r = s.get('http://{0}:{1}/_update_status?id={2}&status={3}&pass={4}'.format(
        ip,
        port,
        machine_id,
        machine_status,
        password)
    )

    if debug:
        print(r.text)


if __name__ == "__main__":
    with Session() as s:
        # login(s, 'machine_update_user', 'ajax_update')
        send_update(s, 1, 2, True)
        send_update(s, 2, 3, True)
        
        