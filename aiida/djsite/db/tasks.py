# -*- coding: utf-8 -*-
from aiida.common import aiidalogger
import celery
from aiida.common.exceptions import (
    LockPresent, ModificationNotAllowed, InternalError)
from aiida.djsite.settings.settings import djcelery_tasks

#from celery.utils.log import get_task_logger
## I use the aiidalogger so that the logging is managed in the same way

__copyright__ = u"Copyright (c), 2015, ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE (Theory and Simulation of Materials (THEOS) and National Centre for Computational Design and Discovery of Novel Materials (NCCR MARVEL)), Switzerland and ROBERT BOSCH LLC, USA. All rights reserved."
__license__ = "MIT license, see LICENSE.txt file"
__version__ = "0.4.0"
__contributors__ = "Andrea Cepellotti, Giovanni Pizzi, Riccardo Sabatini"

logger = aiidalogger.getChild('tasks')

LOCK_EXPIRE = 60 * 1000 # Expire time for the retriever, in seconds; should
                        # be a very large number!

def set_daemon_timestamp(task_name, when):
    """
    Set in the DB the current time associated with the given task;
    this is used to store a timestamp to know when the daemon run for the last
    time.

    :param task_name: the task for which we want to set the timestamp
      It has to be one of the keys of the
      ``aiida.djsite.settings.settings.djcelery_tasks`` dictionary.
    :param when: can either be 'start' (to call when the task started) or
      'stop' (to call when the task ended)
    """
    from aiida.common.globalsettings import set_global_setting
    from django.utils import timezone

    if when == 'start':
        verb = 'started'
    elif when == 'stop':
        verb = 'finished'
    else:
        raise ValueError("the 'when' parameter can only be 'start' or 'stop'")

    try:
        actual_task_name = djcelery_tasks[task_name]
    except KeyError:
        raise ValueError("Unknown value for 'task_name', not found in the "
                         "djcelery_tasks dictionary")

    set_global_setting('daemon|task_{}|{}'.format(when, actual_task_name),
                       timezone.now(),
                       description="The last time the daemon {} to run the "
                                    "task '{}' ({})".format(verb,
                                        task_name, actual_task_name))

def get_most_recent_daemon_timestamp():
    """
    Try to detect any last timestamp left by the daemon, for instance
    to get a hint on whether the daemon is running or not.

    :return:  a datetime.datetime object with the most recent time.
      Return None if no information is found in the DB.
    """
    import datetime
    # I go low-level here
    from aiida.djsite.db.models import DbSetting

    daemon_timestamps = DbSetting.objects.filter(key__startswith='daemon|task_')
    timestamps = []
    for timestamp_setting in daemon_timestamps:
        timestamp = timestamp_setting.getvalue()
        if isinstance(timestamp, datetime.datetime):
            timestamps.append(timestamp)

    if timestamps:
        # The most recent timestamp

        return max(timestamps)
    else:
        return None

def get_last_daemon_timestamp(task_name, when='stop'):
    """
    Return the last time stored in the DB that the daemon executed the given
    task.

    :param task_name: the task for which we want the information.
      It has to be one of the keys of the
      ``aiida.djsite.settings.settings.djcelery_tasks`` dictionary.
    :param when: can either be 'start' (to know when the task started) or
      'stop' (to know when the task ended)

    :return: a datetime.datetime object. Return None if no information is
      found in the DB.
    """
    from aiida.common.globalsettings import get_global_setting

    try:
        actual_task_name = djcelery_tasks[task_name]
    except KeyError:
        raise ValueError("Unknown value for '{}', not found in the "
                         "djcelery_tasks dictionary".format(task_name))

    try:
        return get_global_setting('daemon|task_{}|{}'.format(when,
                                                             actual_task_name))
    except KeyError: # No such global setting found
        return None


class SingleTask(celery.Task):

    abstract = True
    lock = None

    def __call__(self, *args, **kwargs):
        from aiida.djsite.utils import get_daemon_user, get_configured_user_email

        daemon_user = get_daemon_user()
        this_user = get_configured_user_email()

        if daemon_user != this_user:
            logger.error("ERROR: I detected that the daemon user ({}) is "
                         "different from the current user ({})! I do not "
                         "execute the task {}. YOU SHOULD SHUT DOWN "
                         "THE DAEMON! (I will try to do it now)"
                         "".format(daemon_user, this_user,
                                              self.name))

            from aiida.cmdline.commands.daemon import Daemon
            Daemon().kill_daemon()
            return


        from aiida.orm.lock import LockManager
        logger.debug('TASK STARTING: %s[%s]' % (self.name, self.request.id))

        try:
            self.lock = LockManager().aquire(self.name, timeout=LOCK_EXPIRE, owner=self.request.id)
            logger.debug("GOT lock for {0} by {1}".format(self.name, self.request.id))
            return self.run(*args, **kwargs)

        except LockPresent:
            logger.debug("LOCK: Another task is running, I {0} can't start.".format(self.request.id))
            self.lock = None
            return

        except InternalError:
            logger.error("ERROR: A lock went over the limit timeout, this could mine the integrity of the system. Reload the Daemon to fix the problem.")
            self.lock = None
            return

    def after_return(self, status, retval, task_id, args, kwargs, einfo):

        if not self.lock==None:

            try:
                self.lock.release(owner=self.request.id)
                logger.debug("RELEASED lock for {0} by {1}".format(self.name, self.request.id))
            except ModificationNotAllowed:
                logger.error("ERROR cannot remove the lock for {0} by {1}".format(self.lock.key, self.request.id))


@celery.task(base=SingleTask)
def submitter():
    from aiida.execmanager import submit_jobs

    set_daemon_timestamp(task_name='submitter', when='start')
    submit_jobs()
    set_daemon_timestamp(task_name='submitter', when='stop')


@celery.task(base=SingleTask)
def updater():
    from aiida.execmanager import update_jobs

    set_daemon_timestamp(task_name='updater', when='start')
    update_jobs()
    set_daemon_timestamp(task_name='updater', when='stop')

@celery.task(base=SingleTask)
def retriever():
    from aiida.execmanager import retrieve_jobs

    set_daemon_timestamp(task_name='retriever', when='start')
    retrieve_jobs()
    set_daemon_timestamp(task_name='retriever', when='stop')

@celery.task(base=SingleTask)
def workflow_stepper():
    from aiida.workflowmanager import daemon_main_loop

    set_daemon_timestamp(task_name='workflow', when='start')
    daemon_main_loop()
    set_daemon_timestamp(task_name='workflow', when='stop')

