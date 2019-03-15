# SecuML
# Copyright (C) 2016-2019  ANSSI
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


app = None
session = None
secuml_conf = None
user_exp = None


def setApp(app_value):
    global app
    app = app_value


def setSession(session_value):
    global session
    session = session_value


def setSecuMlConf(secuml_conf_value):
    global secuml_conf
    secuml_conf = secuml_conf_value


def setUserExp(user_exp_value):
    global user_exp
    user_exp = user_exp_value
