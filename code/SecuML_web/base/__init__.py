## SecuML
## Copyright (C) 2016-2017  ANSSI
##
## SecuML is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## SecuML is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License along
## with SecuML. If not, see <http://www.gnu.org/licenses/>.

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

user_exp = True

app = Flask(__name__)

home = os.environ['HOME']
with open(home + '/.my.cnf', 'r') as f:
    f.readline() # skip the header
    host = f.readline().split('=')[1].strip()
    user = f.readline().split('=')[1].strip()
    password = f.readline().split('=')[1].strip()
connector  = 'mysql+mysqlconnector://' + user + ':'
connector += password + '@' + host + '/'
connector += 'SecuML'
app.config['SQLALCHEMY_DATABASE_URI'] = connector
session = SQLAlchemy(app).session

import SecuML_web.base.views.instances
