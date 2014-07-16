Developer code plugin tutorial
==============================

.. toctree::
   :maxdepth: 2

In this chapter we will give you a brief guide that will teach you how to write a plugin to support a new code.

Generally speaking, we expect that each code will have its own
peculiarity, so that sometimes a new strategy for code plugin might be
needed to be carefully thought.
Anyway, we will show you how we implemented the plugin for Quantum
Espresso, in order for you to be able to replicate the task for other
codes.
Therefore, it will be assumed that you have already tried to run an
example of QE, and you know more or less how the AiiDA interface
works.

In fact, when writing your own plugin, keep in mind that you need to
satisfy multiple users, and the interface needs to be simple (not the
code below). But always try to follow the Zen of Python:

 Simple is better than complex.
 
 Complex is better than complicated.
 
 Readability counts.

There will be two kinds of plugins, the input and the output. The
former has the purpose to convert python object in text inputs that
can be executed by external softwares. The latters will convert the
text output of these softwares back into python dictionaries/objects
that can be put back in the database.
 
InputPlugin
-----------

In abstract term, this plugin must contain these two pieces of information:

  what are the input objects of the calculation
 
  how to convert the input object in an input file

This is it, a minimal input plugin must have at least these two
things.

Create a new file, which has the same name of the class you are
creating (in this way, it will be possible to load it with
``CalculationFactory``).
Save it in a subfolder at the path ``aiida/orm/calculation``.

First define the class::

  class SubclassCalculation(Calculation):   

Take care of inheriting the Calculation class, or the plugin will not work.

Step 1: define input nodes
^^^^^^^^^^^^^^^^^^^^^^^^^^
 
First, you need to specify what are the objects that are going to be
accepted as input to the calculation class.
This is done by the class property ``_use_methods``.
An example is as follows::

    from aiida.common.utils import classproperty
  
    class SubclassCalculation(Calculation):
  
        @classproperty
        def _use_methods(cls):
            retdict = Calculation._use_methods
            retdict.update({
                "settings": {
                   'valid_types': ParameterData,
                   'additional_parameter': None,
                   'linkname': 'settings',
                   'docstring': "Use an additional node for special settings",
                   },
                "pseudo": {
                   'valid_types': UpfData,
                   'additional_parameter': 'kind',
                   'linkname': cls._get_pseudo_linkname,
                   'docstring': ("Use a remote folder as parent folder (for "
                                 "restarts and similar"),
                   },
                })
            return retdict

        @classmethod
        def _get_pseudo_linkname(cls, kind):
            """
            Return the linkname for a pseudopotential associated to a given 
            structure kind.
            """
            return "pseudo_{}".format(kind)

After this piece of code is written, we now have defined two methods
of the calculation that specify what DB object could be set as input
(and draw the graph in the DB).
Specifically, here we will find the two methods::

  calculation.use_settings(an_object)
  calculation.use_pseudo(another_object,'object_kind')

What did we do?

1. We added implicitly the two new ``use_settings`` and ``use_pseudo`` methods 
   (because the dictionary returned by ``_use_methods`` now contains a
   ``settings`` and a ``pseudo`` key)
2. We did not lose the ``use_code`` call defined in the ``Calculation`` 
   base class, because we are extending
   ``Calculation._use_methods``. Therefore: don't specify a code as
   input in the plugin!
3. ``use_settings`` will accept only one parameter, the node specifying the
   settings, since the ``additional_parameter`` value is ``None``.
4. ``use_pseudo`` will require two parameters instead, since
   ``additional_parameter`` value is *not* ``None``. If the second parameter
   is passed via kwargs, its name must be 'kind' (the value of
   ``additional_parameters``). That is, you can call ``use_pseudo`` in one of
   the two following ways::
     
     use_pseudo(pseudo_node, 'He')
     use_pseudo(pseudo_node, kind='He')

   to associate the pseudopotential node ``pseudo_node`` (that you must have
   loaded before) to helium (He) atoms.
5. The type of the node that you pass as first parameter will be checked
   against the type (or the tuple of types) specified with ``valid_types``
   (the check is internally done using the ``isinstance`` python call).
6. The name of the link is taken from the ``linkname`` value. Note that
   if ``additional_parameter`` is ``None``, this is simply a string; otherwise,
   it must be a callable that accepts one single parameter (the further
   parameter passed to the ``use_XXX`` function) and returns a string with the
   proper name. This functionality is provided to have a single ``use_XXX`` 
   method to define more than one input node, as it is the case for
   pseudopotentials, where one input pseudopotential node must be specified for
   each atomic species or kind.
7. Finally, ``docstring`` will contain the documentation of the function, 
   that the user can obtain by printing e..g. ``use_pseudo.__doc__``.






   

Step 2: prepare a text input
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

How are the input nodes used internally?
Every plugin class is required to have the following method::

  def _prepare_for_submission(self,tempfolder,inputdict):

This function is called by the daemon when it is trying to create a new calculation.

There are two arguments:

1. ``tempfolder``: is an object of kind SandboxFolder, which behaves
   exactly as a folder. In this placeholder, you are going to write
   the input files. This tempfolder is gonna be copied to the remote
   cluster.

2. ``inputdict``: contains all the input data nodes as a dictionary, in the
same format that is returned by the ``get_inputdata_dict()`` method,
i.e. a linkname as key, and the object as value.

.. note:: inputdict should contain all input ``Data`` nodes, but *not* the code.
  (this is what the ``get_inputdata_dict()`` method does, by the way).

In general, you simply want to do::

      inputdict = self.get_inputdata_dict()

right before calling ``_prepare_for_submission``.
The reason for having this explicitly passed is that the plugin does not have
to perform explicit database queries, and moreover this is useful to test
for submission without the need to store all nodes on the DB.    



For the sake of clarity, it's probably going to be easier looking at
an implemented example. Take a look at the ``NamelistsCalculation`` located in ``aiida.orm.calculation.quantumespresso.namelists``.



How does the method ``_prepare_for_submission`` work in practice?

1. You should start by checking if the input nodes passed in ``inputdict``
are logically sufficient to run an actual calculation. 
Remember to raise an exception (for example ``InputValidationError``) if something is missing or if something
unexpected is found. Ideally, it is better
to discover now if something is missing, rather than waiting the queue
on the cluster and see that your job has crashed.
Also, if there are some nodes left unused, you are gonna leave a DB more
complicated than what has really been, and therefore is better to stop
the calculation now.

2. create an input file (or more if needed). In the Namelist plugin is
done like::

  input_filename = tempfolder.get_abs_path(self.INPUT_FILE_NAME)
  with open(input_filename,'w') as infile:
       # Here write the information of a ParameterData inside this
       # file

Note that here it all depends on how you decided the ParameterData to
be written. In the namelists plugin we decided the convention that a ParameterData of
the format::

  ParameterData(dict={"INPUT":{'smearing':2,
                               'cutoff':30}
                      })

is written in the input file as::

  &INPUT
      smearing = 2,
      cutoff=30,
  /

Of course, it's up to you to decide a convention which defines how to convert the
dictionary to the input file.
You can also impose some default values for simplicity. For example,
the location of the scratch directory, if needed, should be imposed by
the plugin and not by the user, and similarly you can/should decide the
naming of output files.

.. note:: it is convenient to avoid hard coding of all the variables
	  that your code has. The convention stated above is
	  sufficient for all inputs structured as fortran cards,
	  without the need of knowing which variables are accepted.
	  Hard coding variable names implies that every time the
	  external software is updated, you need to modify the plugin:
	  in practice the plugin will easily become obsolete if poor maintained.
	  Easyness of maintainance here win over user comfort!

3. copy inside this folder some auxiliary files that resides on your
   local machine, like for example pseudopotentials.

4. return a ``CalcInfo`` object.

This object contains some accessory information. Here's a template of
what it may look like::

        calcinfo = CalcInfo()

        calcinfo.uuid = self.uuid
        calcinfo.cmdline_params = settings_dict.pop('CMDLINE', [])
        calcinfo.local_copy_list = local_copy_list
        calcinfo.remote_copy_list = remote_copy_list
	### Modify here and put a name for standard input/output files
        calcinfo.stdin_name = self.INPUT_FILE_NAME
        calcinfo.stdout_name = self.OUTPUT_FILE_NAME
	###        
	calcinfo.retrieve_list = []
	### Modify here !
        calcinfo.retrieve_list.append('Every file/folder you want to store back locally')
	### Modify here!
	calcinfo.retrieve_singlefile_list = []
	
        return calcinfo

There are a couple of things to be set.

1. stdin_name: the name of the standard input

2. stdin_name: the name of the standard output

3. cmdline_params: like parallelization flags, that will be used when
running the code.

4. retrieve_list: a list of relative file pathnames, that will be copied
from the cluster to the aiida server, after the calculation has run on
cluster.
Note that all the file names you need to modify are not absolute path names (you don't know the name of the folder where it will be created) but rather the path relative to the scratch folder.

5. local_copy_list: a list of length-two-tuples: (localabspath,
relativedestpath). Copies files sitting on the aiida server to the cluster

6. remote_copy_list: a list of tuples: (remotemachinename, remoteabspath,
relativedestpath). Copies a file/folder from a remote source to a
remote destination, sitting both on the same machine.

7. retrieve_singlefile_list: a list of triplets, in the form
["linkname_from calc to singlefile","subclass of
singlefile","filename"]. If this is specified, at the end of the
calculation it will be created a SinglefileData-like object in the
Database, children of the calculation, if of course the file is found
on the cluster.

If you need to change other settings to make the plugin work, you
likely need to add more information to the calcinfo than what we
showed here.
For the full definition of ``CalcInfo()``, refer to the source
``aiida.common.datastructures``.


That's what is needed to write an input plugin.
To test that everythin is done properly, remember to use the
``calculation.submit_test()`` method, which creates locally the folder
to be sent on cluster, without submitting the calculation on the cluster.



OutputPlugin
------------

Well done! You were able to have a successful input plugin.
Now we are going to see what you need to do for an output plugin.
First of all let's create a new folder:
``$path_to_aiida/aiida/parsers/plugins/the_name_of_new_code``, and put there an empty ``__init__.py`` file.
Here you will write in a new python file the output parser class.
It is actually a rather simple class, performing only a few (but tedious) tasks.

After the calculation has been computed and retrieved from the
cluster, that is, at the moment when the parser is going to be called,
the calculation has two children: a RemoteData and a FolderData.
The RemoteData is an object which represents the scratch folder on the
cluster: you don't need it for the parsing phase.
The FolderData is the folder in the AiiDA server which contains the
files that have been retrieved from the cluster.
Moreover, if you specified a retrieve_singlefile_list, at this stage
there is also going to be some children of SinglefileData kind.

Let's say that you copied the standard output in the FolderData.
The parser than has just a couple of tasks:

1. open the files in the FolderData
2. read them
3. convert the information into objects that can be saved in the
   Database
4. return the objects and the linkname. 

.. note:: The parser should not save any object in the DB, that is
	  a task of the daemon: never use a ``.store()`` method!

Basically, you just need to specify an ``__init__()`` method, and a
function ``parse_from_calc(calc)__``, which does the actual work.

The difficult and long part is the point 3), which is the actual
parsing stage, which convert text into python objects.
Here, you should try to parse as much as you can from the output files.
The more you will write, the better it will be.
*Note also that not only you should parse physical values, a very
important thing that could be used by workflows are exceptions or
others errors occurring in the calculation. 
You could save them in a dedicated key of the dictionary (say
'warnings'), later a  workflow can easily read the exceptions from the
results and perform a dedicated correction!*

In principle, you can save the information in an arbitrary number of
objects.
The most useful classes to store the information back into the DB are:

1. ParameterData. 
This is the DB representation of a python dictionary. If you put
everything in a single ParameterData, then this could be easily
accessed from the calculation with the ``.res`` method. If you have to
store arrays / large lists or matrices, consider using ArrayData instead.

2. ArrayData. If you need to store large arrays of values, for
   example, a list of points or a molecular dynamic trajectory, we
   strongly encourage you to use this class.
   At variance with ParameterData, the values are not stored in the
   DB, but are written to a file (mapped back in the DB). If instead
   you store large arrays of numbers in the DB with ParameterData, you might soon realise
   that: a) the DB grows large really rapidly; b) the time it takes to
   save an object in the DB gets very large.

3. StructureData. If your code relaxes an input structure, you can end up
  with an output structure.

Of course, you can create new classes to be stored in the DB, and use
them at your own advantage.

A kind of template for writing such parser for the calculation class
``NewCalculation`` is as follows::

    class NewParser(Parser):
        """
        A doc string
        """

        def __init__(self,calc):
            """
            Initialize the instance of NewParser
            """
            # check for valid input
	    if not isinstance(calc,NewCalculation):
	        raise ParsingError("Input must calc must be a NewCalculation")
        
	    super(NewParser, self).__init__(calc)

        def parse_from_calc(self):
            """
            Parses the calculation-output datafolder, and stores
            results.
            """           
	    # load the error logger
	    from aiida.common import aiidalogger
	    from aiida.djsite.utils import get_dblogger_extra
	    parserlogger = aiidalogger.getChild('newparser')
	    logger_extra = get_dblogger_extra(self._calc)

	    # check the calc status, not to overwrite anything
            state = calc.get_state()
            if state != calc_states.PARSING:
                raise InvalidOperation("Calculation not in {} state"
                                       .format(calc_states.PARSING) )

	    # retrieve the whole list of input links
	    calc_input_parameterdata = self._calc.get_inputs(type=ParameterData,
                                                         also_labels=True)
            # then look for parameterdata only
	    input_param_name = self._calc.get_linkname('parameters')
	    params = [i[1] for i in calc_input_parameterdata if i[0]==input_param_name]
	    if len(params) != 1:
	        parserlogger.error("Found {} input_params instead of one"
                                  .format(params),extra=logger_extra)
                successful = False
            calc_input = params[0]

            # check what is inside the folder
            list_of_files = out_folder.get_path_list()
            # at least the stdout should exist
            if not calc.OUTPUT_FILE_NAME in list_of_files:
                raise QEOutputParsingError("Standard output not found")
            # get the path to the standard output
            out_file = os.path.join( out_folder.get_abs_path('.'), 
                                     calc.OUTPUT_FILE_NAME )

	    # read the file
	    with open(out_file) as f:
	        out_file_lines = f.readlines()

            # call the raw parsing function. Here it was thought to return a
            # dictionary with all keys and values parsed from the out_file (i.e. enery, forces, etc...)
            # and a boolean indicating whether the calculation is successfull or not
	    # In practice, this is the function deciding the final status of the calculation
            parsed_ditionary,successful = parse_raw_output(out_file_lines)
            
            # convert the dictionary into an AiiDA object, here a
	    # ParameterData for instance
            output_params = ParameterData(dict=out_dict)

	    # prepare the list of output nodes to be returned
	    new_nodes_list = [ ['linkname',output_params] ]

	    # if false, the calculation status will be flagged as failed, to finished if true
            return successful, new_nodes_list


