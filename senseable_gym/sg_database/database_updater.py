#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#  Standard imports
import sched
import time

# Senseable Gym Imports
from senseable_gym.sg_database.database import DatabaseModel


# Setup scheduler
s = sched.scheduler(time.time, time.sleep)


def update_all_machine_statuses(db: DatabaseModel) -> None:
    machines = db.get_machines()

    for machine in machines:
        current_status = db.query_current_status(machine)
        print(machine.machine_id, current_status)
