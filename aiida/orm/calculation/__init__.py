# -*- coding: utf-8 -*-
from aiida.orm import Node
from aiida.common.datastructures import calc_states
from aiida.common.exceptions import ModificationNotAllowed
from aiida.common.utils import classproperty

__copyright__ = u"Copyright (c), 2015, ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE (Theory and Simulation of Materials (THEOS) and National Centre for Computational Design and Discovery of Novel Materials (NCCR MARVEL)), Switzerland and ROBERT BOSCH LLC, USA. All rights reserved."
__license__ = "MIT license, see LICENSE.txt file"
__version__ = "0.4.0"
__contributors__ = "Andrea Cepellotti, Giovanni Pizzi, Marco Dorigo, Nicolas Mounet, Riccardo Sabatini"

def _parse_single_arg(function_name, additional_parameter,
                     args, kwargs):
    """
    Verifies that a single additional argument has been given (or no
    additional argument, if additional_parameter is None). Also
    verifies its name.
    
    :param function_name: the name of the caller function, used for
        the output messages
    :param additional_parameter: None if no additional parameters
        should be passed, or a string with the name of the parameter
        if one additional parameter should be passed.
    
    :return: None, if additional_parameter is None, or the value of 
        the additional parameter
    :raise TypeError: on wrong number of inputs
    """
    # Here all the logic to check if the parameters are correct.
    if additional_parameter is not None:
        if len(args) == 1:                        
            if kwargs:
                raise TypeError("{}() received too many args".format(
                    function_name))
            additional_parameter_data = args[0]
        elif len(args) == 0:
            kwargs_copy = kwargs.copy()
            try:
                additional_parameter_data = kwargs_copy.pop(
                    additional_parameter)
            except KeyError:
                if kwargs_copy:
                    raise TypeError("{}() got an unexpected keyword "
                        "argument '{}'".format(
                        function_name, kwargs_copy.keys()[0]))
                else:
                    raise TypeError("{}() requires more "
                        "arguments".format(function_name))
            if kwargs_copy:
                raise TypeError("{}() got an unexpected keyword "
                    "argument '{}'".format(
                    function_name, kwargs_copy.keys()[0]))  
        else:
            raise TypeError("{}() received too many args".format(
                function_name))
        return additional_parameter_data
    else:
        if kwargs:
            raise TypeError("{}() got an unexpected keyword "
                            "argument '{}'".format(
                                function_name, kwargs.keys()[0]))
        if len(args) != 0:
            raise TypeError("{}() received too many args".format(
                function_name))
            
        return None


class Calculation(Node):
    """
    This class provides the definition of an "abstract" AiiDA calculation.
    A calculation in this sense is any computation that converts data into data.
    
    You will typically use one of its subclasses, often a JobCalculation for
    calculations run via a scheduler.
    """    
        
    # Nodes that can be added as input using the use_* methods
    @classproperty
    def _use_methods(cls):
        """
        Return the list of valid input nodes that can be set using the
        use_* method. 
        
        For each key KEY of the return dictionary, the 'use_KEY' method is
        exposed.
        Each value must be a dictionary, defining the following keys:
        * valid_types: a class, or tuple of classes, that will be used to
          validate the parameter using the isinstance() method
        * additional_parameter: None, if no additional parameters can be passed
          to the use_KEY method beside the node, or the name of the additional
          parameter (a string)
        * linkname: the name of the link to create (a string if
          additional_parameter is None, or a callable if additional_parameter is
          a string. The value of the additional parameter will be passed to the
          callable, and it should return a string.
        * docstring: a docstring for the function
        
        .. note:: in subclasses, always extend the parent class, do not
          substitute it!
        """
        from aiida.orm import Code
        
        return {
            "code": {
               'valid_types': Code,
               'additional_parameter': None,
               'linkname': 'code',
               'docstring': "Choose the code to use",
               },
            }

    @property
    def logger(self):
        """
        Get the logger of the Calculation object, so that it also logs to the
        DB.
        
        :return: LoggerAdapter object, that works like a logger, but also has
          the 'extra' embedded
        """
        import logging
        from aiida.djsite.utils import get_dblogger_extra
        
        return logging.LoggerAdapter(logger=self._logger,
                                     extra=get_dblogger_extra(self))

    def __dir__(self):
        """
        Allow to list all valid attributes, adding also the use_* methods
        """
        return sorted(dir(type(self)) + list(['use_{}'.format(k)
                                 for k in self._use_methods.iterkeys()]))

    def __getattr__(self,name):
        """
        Expand the methods with the use_* calls. Note that this method only 
        gets called if 'name' is not already defined as a method. Returning
        None will then automatically raise the standard AttributeError 
        exception.
        """
        class UseMethod(object):
            """
            Generic class for the use_* methods. To know which use_* methods
            exist, use the ``dir()`` function. To get help on a specific method,
            for instance use_code, use::
              ``print use_code.__doc__``
            """
            
            def __init__(self, node, actual_name, data):
                from aiida.common.exceptions import InternalError
                
                self.node = node
                self.actual_name = actual_name
                self.data = data
                try:
                    self.__doc__ = data['docstring']
                except KeyError:
                    # Forgot to define the docstring! Use the default one
                    pass
                            
            def __call__(self, parent_node, *args, **kwargs):
                import collections
                
                # Not really needed, will be checked in get_linkname
                # But I do anyway in order to raise an exception as soon as
                # possible, with the most intuitive caller function name
                additional_parameter = _parse_single_arg(
                    function_name='use_{}'.format(self.actual_name),
                    additional_parameter=self.data['additional_parameter'],
                    args=args, kwargs=kwargs)
                 
                # Type check   
                if isinstance(self.data['valid_types'], collections.Iterable):
                    valid_types_string = ",".join([_.__name__ for _ in 
                                                   self.data['valid_types']])
                else:
                    valid_types_string = self.data['valid_types'].__name__
                if not isinstance(parent_node, self.data['valid_types']):
                    raise TypeError("The given node is not of the valid type "
                                    "for use_{}. Valid types are: {}, while "
                                    "you provided {}".format(
                                    self.actual_name, valid_types_string,
                                    parent_node.__class__.__name__))
                
                # Get actual link name
                actual_linkname = self.node.get_linkname(actual_name, *args,
                                                         **kwargs)
                # Checks that such an argument exists have already been
                # made inside actual_linkname
                    
                # Here I do the real job
                self.node._replace_link_from(parent_node, actual_linkname)
                
        prefix = 'use_'
        valid_use_methods = list(['{}{}'.format(prefix, k)
                                 for k in self._use_methods.iterkeys()])
        
        if name in valid_use_methods:
            actual_name = name[len(prefix):]
            return UseMethod(node=self, actual_name=actual_name,
                             data=self._use_methods[actual_name])
        else:
            raise AttributeError("'{}' object has no attribute '{}'".format(
                self.__class__.__name__, name))
             
    def get_linkname(self, link, *args, **kwargs):
        """
        Return the linkname used for a given input link

        Pass as parameter "NAME" if you would call the use_NAME method.
        If the use_NAME method requires a further parameter, pass that
        parameter as the second parameter.
        """
        from aiida.common.exceptions import InternalError

        try:
            data = self._use_methods[link]
        except KeyError:
            raise ValueError("No '{}' link is defined for this "
                "calculation".format(link))

        # Raises if the wrong # of parameters is passed
        additional_parameter = _parse_single_arg(
            function_name='get_linkname',
            additional_parameter=data['additional_parameter'],
            args=args, kwargs=kwargs)
                      
        if data['additional_parameter'] is not None:
            # Call the callable to get the proper linkname
            actual_linkname = data['linkname'](additional_parameter)
        else:
            actual_linkname = data['linkname']
        
        return actual_linkname
        
    def _can_link_as_output(self,dest):
        """
        An output of a calculation can only be a data.

        :param dest: a Data object instance of the database
        :raise: ValueError if a link from self to dest is not allowed.
        """
        from aiida.orm import Data

        if not isinstance(dest, Data):
            raise ValueError(
                "The output of a calculation node can only be a data node")

        return super(Calculation, self)._can_link_as_output(dest)

    def _add_link_from(self,src,label=None):
        '''
        Add a link with a code as destination. 
        
        You can use the parameters of the base Node class, in particular the
        label parameter to label the link.
        
        :param src: a node of the database. It cannot be a Calculation object.
        :param str label: Name of the link. Default=None
        '''
        
        from aiida.orm.data import Data
        from aiida.orm.code import Code
        
        if not isinstance(src,(Data, Code)):
            raise ValueError("Nodes entering in calculation can only be of "
                             "type data or code")
        
        return super(Calculation,self)._add_link_from(src, label)

    def _replace_link_from(self,src,label):
        '''
        Replace a link. 
        
        :param src: a node of the database. It cannot be a Calculation object.
        :param str label: Name of the link. 
        '''
        
        from aiida.orm.data import Data
        from aiida.orm.code import Code
        
        if not isinstance(src,(Data, Code)):
            raise ValueError("Nodes entering in calculation can only be of "
                             "type data or code")
        
        return super(Calculation,self)._replace_link_from(src, label)

    def get_code(self):
        """
        Return the code for this calculation, or None if the code
        was not set.
        """
        from aiida.orm import Code
        
        return dict(self.get_inputs(type=Code, also_labels=True)).get(
            self._use_methods['code']['linkname'], None)
                        
