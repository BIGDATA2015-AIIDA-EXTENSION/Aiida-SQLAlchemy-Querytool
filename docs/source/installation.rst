====================================
Installation and Deployment of AiiDA
====================================

Supported architecture
++++++++++++++++++++++
AiiDA has a few strict requirements, in its current version:
first, it will run only on Unix-like systems - it
is tested (and developed) in Mac OS X and Linux (Ubuntu), but other Unix
flavours *should* work as well.

Moreover, on the clusters (computational resources) side, it expects to find
a Unix system, and the default shell is **required** to be ``bash``. 

Installing python
+++++++++++++++++

AiiDA requires python 2.7.x (only CPython has been tested).
It is probable that you already have a version of
python installed on your computer. To check, open a terminal and type::

    python -V

that will print something like this::
    
    Python 2.7.3
    
If you don't have python installed, or your version is outdated, please install
a suitable version of python (either refer to the manual of your Linux 
distribution, or for instance you can download the ActiveState Python from
ActiveState_. Choose the appropriate distribution corresponding to your 
architecture, and with version 2.7.x.x).

.. _ActiveState: http://www.activestate.com/activepython/downloads

Installation of the core dependencies
+++++++++++++++++++++++++++++++++++++

Database
--------

As a first thing, :doc:`choose and setup the database that you want to
use<database/index>`.

.. _other_core_dependencies:

Other core dependencies
-----------------------

Before continuing, you still need to install a few more programs. Some of them 
are mandatory, while others are optional (but often strongly suggested), also
depending for instance on the :doc:`type of database <database/index>`
that you plan to use.

Here is a list of packages/programs that you need to install (for each of them,
there may be a specific/easier way to install them in your distribution, as
for instance ``apt-get`` in Debian/Ubuntu -see below for the specific names
of packages to install- or ``yum`` in RedHat/Fedora).

* `git`_ (required to download the code)
* `python-pip`_ (required to automatically download and install further
  python packages required by AiiDA)
* `ipython`_ (optional, but strongly recommended for interactive usage)
* python 2.7 development files (these may be needed; refer to your distribution
  to know how to locate and install them)
* To support  SQLite:

  * `SQLite3 development files`_ (required later to compile the library,
    when configuring the python sqlite module; see below for the Ubuntu 
    module required to install these files)

* To support  PostgreSQL:

  * `PostgreSQL development files`_ (required later to compile the library,
    when configuring the python psycopg2 module; see below for the Ubuntu 
    module required to install these files)

.. _git: http://git-scm.com/
.. _python-pip: https://pypi.python.org/pypi/pip
.. _ipython: http://ipython.org/
.. _SQLite3 development files: http://www.sqlite.org/
.. _PostgreSQL development files: http://www.postgresql.org/


For Ubuntu, you can install the above packages using (tested on Ubuntu 12.04,
names may change in different releases)::

      sudo apt-get install git
      sudo apt-get install python-pip
      sudo apt-get install ipython
      sudo apt-get install python2.7-dev
      sudo apt-get install libsqlite3-dev
      sudo apt-get install postgresql-server-dev-9.1

.. note:: For the latter line, please use the same version (in the
  example above is 9.1) of the
  postgresql server that you installed (in this case, to install the server of
  the same version, use the ``sudo apt-get install postgresql-9.1`` command).
  
  If you want to use postgreSQL, use a version greater than 9.1
  (the greatest that your distribution supports).

For Mac OS X, you may either already have some of the dependencies above 
(e.g., git), or you can download binary packages to install (e.g., for
PostgreSQL you can download and install the binary package from the
official website).

Downloading the code
++++++++++++++++++++

Download the code using git in a directory of your choice (``~/git/aiida`` in
this tutorial), using the
following command::

    git clone https://USERNAME@bitbucket.org/aiida_team/aiida.git ~/git/aiida

(or use ``git@bitbucket.org:aiida_team/aiida.git`` if you are downloading
through SSH; note that this requires your ssh key to be added on the
Bitbucket account.)

Python dependencies
+++++++++++++++++++
Python dependencies are managed using ``pip``, that you have installed in the
previous steps.

As a first step, check that ``pip`` is at its most recent version.

One possible way of doing this is to update ``pip`` with itself, with
a command similar to the following::

  sudo pip install -U pip

Then, install the python dependencies is as simple as this::

      cd ~/git/aiida # or the folder where you downloaded AiiDA
      pip install --user -U -r requirements.txt

(this will download and install requirements that are listed in the
``requirements.txt`` file; the ``--user`` option allows to install
the packages as a normal user, without the need of using ``sudo`` or
becoming root). Check that every package is installed correctly.

.. note:: This step should work seamlessly, but there are a number of reasons
  for which problems may occur. Often googling for the error message helps in
  finding a solution. Some common pitfalls are described in the notes below.

.. note:: if the ``pip install`` command gives you this kind of error message::

    OSError: [Errno 13] Permission denied: '/usr/local/bin/easy_install'

  then try again as root::
    
    sudo pip install -U -r requirements.txt

If everything went smoothly, congratulations! Now the code is installed!
However, we need still a few steps to properly configure AiiDA for your user.

.. note:: if the ``pip install`` command gives you an error that
  resembles the one
  shown below, you might need to downgrade to an older version of pip::

	Cannot fetch index base URL https://pypi.python.org/simple/

  To downgrade pip, use the following command::

	sudo easy_install pip==1.2.1

.. note:: Several users reported the need to install also ``libqp-dev``::

    apt-get install libqp-dev
    
  But under Ubuntu 12.04 this is not needed.

.. note:: If the installation fails while installing the packages related
  to the database, you may have not installed or set up the database
  libraries as described in the section :ref:`other_core_dependencies`.

  In particular, on Mac OS X, if you installed the binary package of
  PostgreSQL, it is possible that the PATH environment variable is not
  set correctly, and you get a "Error: pg_config executable not found." error.
  In this case, discover where the binary is located, then add a line to
  your ``~/.bashrc`` file similar to the following::

    export PATH=/the/path/to/the/pg_config/file:${PATH}

  and then open a new bash shell.
  Some possible paths can be found at this
  `Stackoverflow link`_ and a non-exhaustive list of possible
  paths is the following (version number may change):

  * ``/Applications/Postgres93.app/Contents/MacOS/bin``
  * ``/Applications/Postgres.app/Contents/Versions/9.3/bin``
  * ``/Library/PostgreSQL/9.3/bin/pg_config``

  Similarly, if the package installs but then errors occur during the first
  of AiiDA (with ``Symbol not found`` errors or similar), you may need to
  point to the path where the dynamical libraries are. A way to do it is to
  add a line similar to the following to the ``~/.bashrc`` and then open
  a new shell::

    export DYLD_FALLBACK_LIBRARY_PATH=/Library/PostgreSQL/9.3/lib:$DYLD_FALLBACK_LIBRARY_PATH

  (you should of course adapt the path to the PostgreSQL libraries).

.. _Stackoverflow link: http://stackoverflow.com/questions/21079820/how-to-find-pg-config-pathlink

AiiDA configuration
+++++++++++++++++++

Path configuration
------------------

The main interface to AiiDA is through its command-line tool, called ``verdi``.
For it to work, it must be on the system path, and moreover the AiiDA python
code must be found on the python path. 

To do this, add the following to your ``~/.bashrc`` file (create it if not already present)::

      export PYTHONPATH=~/git/aiida:${PYTHONPATH}
      export PATH=~/git/aiida/bin:${PATH}

and then source the .bashrc file with the command ``source ~/.bashrc``, or login
in a new window.

.. note:: replace ``~/git/aiida`` with the path where you installed AiiDA. Note
  also that in the ``PYTHONPATH`` you simply have to specify the AiiDA path, while
  in ``PATH`` you also have to append the ``/bin`` subfolder!

.. note:: if you installed the modules with the ``--user`` parameter during the
  ``pip install`` step, you will need to add one more directory to your ``PATH``
  variable in the ``~/.bashrc`` file.
  For Linux systems, the path to add is usually ``~/.local/bin``::
  
  	export PATH=~/git/aiida/bin:~/.local/bin:${PATH}
  
  For Mac OS X systems, the path to add is usually ``~/Library/Python/2.7/bin``::
  
  	export PATH=~/git/aiida/bin:~/Library/Python/2.7/bin:${PATH}
  
  To verify if this is the correct path to add, navigate to this location and
  you should find the executable ``supervisord`` in the directory.

To verify if the path setup is OK:

* type ``verdi`` on your terminal, and check if the program starts (it should 
  provide a list of valid commands). If it doesn't, check if you correctly set
  up the ``PATH`` environmente variable above.
* go in your home folder or in another folder different from the AiiDA folder,
  run ``python`` or ``ipython`` and try to import a module, e.g. typing::

    import aiida
    
  If the setup is ok, you shouldn't get any error. If you do get an
  ``ImportError`` instead, check if you correctly set up the ``PYTHONPATH``
  environment variable in the steps above.


Bash completion
^^^^^^^^^^^^^^^

``verdi`` fully supports bash completion (i.e., the possibility to press the
``TAB`` of your keyboard to get a list of sensible commands to type.
We strongly suggest to enable bash completion by adding also the following
line to your ``.bashrc``, **after** the previous lines::
   
   eval "$(verdi completioncommand)"

If you feel that the bash loading time is becoming too slow, you can instead
run the::

    verdi completioncommand
    
on a shell, and copy-paste the output directly inside your ``.bashrc`` file,
**instead** of the ``eval "$(verdi completioncommand)"`` line.
    
Remember, after any modification to the ``.bashrc`` file, to source it,
or to open a new shell window. 

.. note:: remember to check that your ``.bashrc`` is sourced also from your
  ``.profile`` or ``.bash_profile`` script. E.g., if not already present,
  you can add to your ``~/.bash_profile`` the following lines::

    if [ -f ~/.bashrc ] 
    then
        . ~/.bashrc
    fi



AiiDA first setup
-----------------

Run the following command::

    verdi install
    
to configure AiiDA. The command will guide you through a process to configure
the database, the repository location, and it will finally (automatically) run 
<<<<<<< HEAD
a django ``migrate`` command, if needed, that creates the required tables
=======
a django ``syncdb`` command, if needed, that creates the required tables
>>>>>>> 5bdba659b4b8732bd54ced1951fcaba5a0dd14d1
in the database and installs the database triggers.

The first thing that will be asked to you is the timezone, extremely important
to get correct dates and times for your calculations.

AiiDA will do its best to try and understand the local timezone (if properly
configured on your machine), and will suggest a set of sensible values.
Choose the timezone that fits best to you (that is, the nearest city in your 
timezone - for Lausanne, for instance, we choose ``Europe/Zurich``) and type
it at the prompt.

If the automatic zone detection did not work for you,  type instead another 
valid string.
A list of valid strings can be found at
http://en.wikipedia.org/wiki/List_of_tz_database_time_zones
but for the definitive list of timezones supported by your system, open
a python shell and type::

  import pytz
  print pytz.all_timezones

as AiiDA will not accept a timezone string that is not in the above list.

As a second parameter to input during the ``verdi install`` phase,
the "Default user email" is asked.

We suggest here to use your institution email, that will be used to associate
the calculations to you.
 
.. note:: In AiiDA, the user email is used as 
  username, and also as unique identifier when importing/exporting data from 
  AiiDA.
   
.. note:: Even if you choose an email different from the default one
  (``aiida@localhost``), a user with email ``aiida@localhost`` will be
  set up,
  with its password set to ``None`` (disabling access via this user
  via API or Web interface).
  
  The existence of a default user is internally useful for multi-user
  setups, where only one user 
  runs the daemon, even if many users can simultaneously access the DB.
  See the page on :ref:`setting up AiiDA in multi-user mode<aiida_multiuser>`
  for more details (only for advanced users).

.. note:: The password, in the current version of AiiDA, is not used (it will
    be used only in the REST API and in the web interface). If you leave the
    field empty, no password will be set and no access will be granted to the
    user via the REST API and the web interface.

Then, the following prompts will help you configure the database. Typical settings are::

	Insert your timezone: Europe/Zurich
	Default user email: richard.wagner@leipzig.de
	Database engine: sqlite3
	AiiDA Database location: /home/wagner/.aiida/aiida.db
	AiiDA repository directory: /home/wagner/.aiida/repository/
	[...]
	Configuring a new user with email 'richard.wagner@leipzig.de'
	First name: Richard
	Last name: Wagner
	Institution: BRUHL, LEIPZIG
	The user has no password, do you want to set one? [y/N] y
	Insert the new password:
	Insert the new password (again):


.. note:: When the "Database engine" is asked, use 'sqlite3' **only if** you want
  to try out AiiDA without setting up a database.
  
  **However, keep in mind that for serious use, SQLite has serious
  limitations!!** For instance, when many calculations are managed at the same
  time, the database file is locked by SQLite to avoid corruption, but this
  can lead to timeouts that do not allow to AiiDA to properly store the
  calculations in the DB.
  
  **Therefore, for production use of AiiDA, we strongly suggest to setup a
  "real" database** as PostgreSQL or MySQL. Then, in the "Database engine"
  field, type either 'postgres' or 'mysql' according to the database you 
  chose to use. See :doc:`here<database/index>` for the documentation
  to setup such databases (including info on how to proceed with ``verdi install``
  in this case). 

At the end, AiiDA will also ask to configure your user, if you set up a user
different from ``aiida@localhost``.

If something fails, there is a high chance that you may have misconfigured
the database. Double-check your settings before reporting an error.

Start the daemon
-----------------
If you configured your user account with your personal email (or if in
general there are more than just one user) you will not be able to
start the daemon with the command ``verdi daemon start`` before its configuration.
  
  *If you are working in a single-user mode, and you are sure that nobody else
  is going to run the daemon*, you can configure your user as the (only)
  one who can run the daemon.
  
To configure the deamon, run::
    
    verdi daemon configureuser
   
and (after having read and understood the warning text that appears) insert
the email that you used above during the ``verdi install`` phase.
  

To try AiiDA and start the daemon, run::

    verdi daemon start

If everything was done correctly, the daemon should start.
You can inquire the daemon status using::

    verdi daemon status

and, if the daemon is running, you should see something like::

  * aiida-daemon[0]        RUNNING    pid 12076, uptime 0:39:05
  * aiida-daemon-beat[0]   RUNNING    pid 12075, uptime 0:39:05


To stop the daemon, use::

    verdi daemon stop

A log of the warning/error messages of the daemon
can be found in ``in ~/.aiida/daemon/log/``, and can also be seen using
the ``verdi daemon logshow`` command. The daemon is 
a fundamental component of AiiDA, and it is in charge of submitting new
calculations, checking their status on the cluster, retrieving and parsing
the results of finished calculations, and managing the workflow steps.

**Congratulations, your setup is complete!**

Before going on, however, you will need to setup *at least one computer* (i.e.,
on computational resource as a cluster or a supercomputer, on which you want 
to run your calculations) *and one code*. The documentation for these steps can
be found :doc:`here<setup/computerandcodes>`.


Optional dependencies
+++++++++++++++++++++

CIF manipulation
----------------

For the manipulation of `Crystallographic Information Framework (CIF) files`_,
following dependencies are required to be installed:

* `PyCifRW`_
* `jmol`_
* `Atomic Simulation Environment (ASE)`_
* :doc:`cod-tools<plugins/codtools/index>`

First two can be installed from the default repositories::

    sudo pip install pycifrw==3.6.2
    sudo apt-get install jmol

ASE has to be installed from source::

    curl https://wiki.fysik.dtu.dk/ase-files/python-ase-3.8.1.3440.tar.gz > python-ase-3.8.1.3440.tar.gz
    gunzip python-ase-3.8.1.3440.tar.gz
    tar -xvf python-ase-3.8.1.3440.tar
    cd python-ase-3.8.1.3440
    setup.py build
    setup.py install
    export PYTHONPATH=$(pwd):$PYTHONPATH

For the setting up of cod-tools please refer to
:ref:`installation of cod-tools<codtools_installation>`.

.. _Crystallographic Information Framework (CIF) files: http://www.iucr.org/resources/cif
.. _Atomic Simulation Environment (ASE): https://wiki.fysik.dtu.dk/ase/
.. _PyCifRW: https://pypi.python.org/pypi/PyCifRW/3.6.2
.. _jmol: http://jmol.sourceforge.net

Further comments and troubleshooting
++++++++++++++++++++++++++++++++++++

* For some reasons, on some machines (notably often on Mac OS X) there is no
  default locale defined, and when you run ``verdi install`` for the first
  time it fails (see also `this issue`_ of django).  To solve the problem, first
  remove the sqlite database that was created. 
  
  Then, run in your terminal (or maybe even better, add to your ``.bashrc``, but
  then remember to open a new shell window!)::
  
     export LANG="en_US.UTF-8"
     export LC_ALL="en_US.UTF-8"

  and then run ``verdi install`` again.

.. _this issue: https://code.djangoproject.com/ticket/16017

* [*Only for developers*] The developer tests of the *SSH* transport plugin are 
  performed connecting to ``localhost``. The tests will fail if 
  a passwordless ssh connection is not set up. Therefore, if you want to run
  the tests:

  + make sure to have a ssh server. On Ubuntu, for instance, you can install
    it using::

       sudo apt-get install openssh-server

  + Configure a ssh key for your user on your machine, and then add
    your public key to the authorized keys of localhsot.
    The easiest way to achieve this is to run::

       ssh-copy-id localhost

    (it will ask your password, because it is connecting via ssh to ``localhost``
    to install your public key inside ~/.ssh/authorized_keys).
