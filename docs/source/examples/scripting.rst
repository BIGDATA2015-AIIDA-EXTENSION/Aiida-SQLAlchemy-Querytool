Scripting with AiiDA
====================

While many common functionalities are provided by either command-line tools 
(via ``verdi``) or the web interface, for fine tuning (or automatization) 
it is useful to directly access the python objects and call their methods.

This is possible in two ways, either via an interactive shell, or writing and 
running a script. Both methods are described below.

``verdi shell``
---------------
By running ``verdi shell`` on the terminal, a new interactive 
`IPython <http://ipython.org/>`_ shell will be opened (this requires that
IPython is installed on your computer).

Note that simply opening IPython and loading the AiiDA modules will not work
(unless you perform the operations described in the
:ref:`following section <writing_python_scripts_for_aiida>`) because
the database settings are not loaded by default and AiiDA does not know how to
access the database.

Moreover, by calling ``verdi shell``, you have the additional advantage that
some classes and modules are automatically loaded, in particular at start-up 
the following modules are loaded, as described
:ref:`here <verdi_shell_description>`.

A further advantage is that bash completion is enabled, allowing to press the 
``TAB`` key to see available submethods of a given object (see for instance
the documentation of the :doc:`ResultManager <../parsers/resultmanager>`).

.. _writing_python_scripts_for_aiida:

Writing python scripts for AiiDA
--------------------------------
Alternatively, if you do not need an interactive shell but you prefer to write
a script and then launch it from the command line, you can just write a 
standard python ``.py`` file. The only modification that you need to do is
to add, at the beginning of the file and before loading any other AiiDA module,
the following two lines::
  
  from aiida import load_dbenv
  load_dbenv()
  
that will load the database settings and allow AiiDA to reach your database.
Then, you can load as usual python and AiiDA modules and classes, and use them.
If you want to have the same environment of the ``verdi shell`` interactive
shell, you can also add (below the ``load_dbenv`` call) the following lines::

  
  from aiida.orm import Calculation, Code, Computer, Data, Node
  from aiida.orm import CalculationFactory, DataFactory
  from aiida.djsite.db import models
  
or simply import the only modules that you will need in the script.

While this method will work, we strongly suggest to use instead the
``verdi run`` command, described here below.

The ``verdi run`` command and the ``runaiida`` executable
.........................................................

In order to simplify the procedure described above, it is possible to 
execute a python file using ``verdi run``: this command will accept
as parameter the name of a file, and will execute it after having
loaded the modules described above.

The command ``verdi run`` has
the additional advantage of adding all stored nodes to suitable special
groups, of type ``autogroup.run``, for later usage. 
You can get the list of all these groups with the command::

  verdi group list -t autogroup.run

Some further command line options of ``verdi run`` allow the user
to fine-tune the autogrouping behavior;
for more details, refer to the output of ``verdi run -h``.
Note also that further command line parameters to ``verdi run`` are
passed to the script as ``sys.argv``.

Finally, we also defined a ``runaiida`` command, that simply will 
pass all its parameters to ``verdi run``. The reason for this is that
one can define a new script to be run with ``verdi run``, add as the
first line the shebang command ``#!/usr/bin/env runaiida``, and give
to the file execution permissions, and the file will become an
executable that is run using AiiDA. A simple example could be::

  #!/usr/bin/env runaiida
  import sys

  pk = int(sys.argv[1])
  node = load_node(pk)
  print "Node {} is: {}".format(pk, repr(node))

  import aiida
  print "AiiDA version is: {}".format(aiida.get_version())



 
