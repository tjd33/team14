#!/bin/bash

# Install database dependencies
sudo apt-get install postgresql postgresql-contrib libpq-dev -y

# Install Python dependencies
sudo pip3 install psycopg2
sudo pip3 install SQLalchemy
