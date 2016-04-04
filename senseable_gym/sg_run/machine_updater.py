#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests


def send_update(machine_id: int, machine_status: int):
    r = requests.get('http://127.0.0.1:5000/_update_status/{0}/{1}'.format(
        machine_id,
        machine_status)
    )
    print(r.text)

send_update(1, 2)
send_update(2, 3)
