#!/bin/bash

set -e

mysql -e 'CREATE DATABASE secuml;'
psql -c 'create database secuml;' -U postgres
python3 travis_tools/generate_travis_secuml_conf.py $TRAVIS_BUILD_DIR

mkdir output_data
