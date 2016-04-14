#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from requests import Session


def login(s, username, password, debug = False):
    r = s.post("http://localhost:5000/login", data={'action': 'login', 'user': username, 'password': password })
    if debug:
        print(r.status_code, r.reason)
        print(r.text[:300] + '...')

def send_update(s, machine_id: int, machine_status: int, debug=False):
    # TODO: Use a real post request
    # TODO: Parameterize the url?
    r = s.get('http://127.0.0.1:5000/_update_status?id={0}&status={1}&pass=ajax_update'.format(
        machine_id,
        machine_status)
    )

    if debug:
        print(r.text)


if __name__ == "__main__":
    with Session() as s:
        # login(s, 'machine_update_user', 'ajax_update')
        send_update(s, 1, 3, True)
        send_update(s, 2, 2, True)