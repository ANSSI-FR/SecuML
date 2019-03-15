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


from celery import Celery
from celery.bin import worker

# instantiate Celery object
app = Celery(include=['secuml.exp.active_learning.celery_tasks'])

# import celery config file
app.config_from_object('secuml.exp.celery_app.conf')

secumlworker = worker.worker(app=app)

if __name__ == '__main__':
    app.start()
