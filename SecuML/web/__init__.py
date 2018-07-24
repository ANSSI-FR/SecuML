# SecuML
# Copyright (C) 2016-2017  ANSSI
#
# SecuML is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# SecuML is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with SecuML. If not, see <http://www.gnu.org/licenses/>.

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from SecuML.experiments import db_tables
from SecuML.experiments.Tools import db_tools
from SecuML.experiments.Tools import dir_exp_tools
from SecuML.experiments.config import DB_URI


user_exp = True

dir_exp_tools.checkWebLibraries()

engine, _ = db_tools.getSqlalchemySession()
db_tables.createTables(engine)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
session = SQLAlchemy(app).session

import SecuML.web.views.instances
