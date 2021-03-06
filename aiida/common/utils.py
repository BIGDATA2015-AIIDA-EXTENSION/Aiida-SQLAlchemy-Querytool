# -*- coding: utf-8 -*-
import os.path
import string

from aiida.common.exceptions import ConfigurationError

__copyright__ = u"Copyright (c), 2015, ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE (Theory and Simulation of Materials (THEOS) and National Centre for Computational Design and Discovery of Novel Materials (NCCR MARVEL)), Switzerland and ROBERT BOSCH LLC, USA. All rights reserved."
__license__ = "MIT license, see LICENSE.txt file"
__version__ = "0.4.0"
__contributors__ = "Andrea Cepellotti, Andrius Merkys, Giovanni Pizzi"

class classproperty(object):
    """
    A class that, when used as a decorator, works as if the 
    two decorators @property and @classmethod where applied together
    (i.e., the object works as a property, both for the Class and for any
    of its instance; and is called with the class cls rather than with the 
    instance as its first argument).
    """
    def __init__(self, getter):
        self.getter= getter
    def __get__(self, instance, owner):
        return self.getter(owner)
   
def get_new_uuid():
    """
    Return a new UUID (typically to be used for new nodes).
    It uses the version of </
    """
    from aiida.djsite.settings.settings_profile import (
        AIIDANODES_UUID_VERSION)
    import uuid

    # Taken from UUIDField
    try:
        from django.utils.encoding import force_unicode     
    except ImportError:
        from django.utils.encoding import force_text as force_unicode 
    
    
    if AIIDANODES_UUID_VERSION != 4:
        raise NotImplementedError("Only version 4 of UUID supported currently")
    
    the_uuid = uuid.uuid4()
    return force_unicode(the_uuid)

def get_repository_folder(subfolder=None):
    """
    Return the top folder of the local repository.
    """
    try:
        from aiida.djsite.settings.settings import REPOSITORY_PATH
        if not os.path.isdir(REPOSITORY_PATH):
            raise ImportError
    except ImportError:
        raise ConfigurationError(
            "The REPOSITORY_PATH variable is not set correctly.")
    if subfolder is None:
        return os.path.abspath(REPOSITORY_PATH)
    elif subfolder == "sandbox":
        return os.path.abspath(os.path.join(REPOSITORY_PATH,'sandbox'))
    elif subfolder == "repository":
        return os.path.abspath(os.path.join(REPOSITORY_PATH,'repository'))
    else:
        raise ValueError("Invalid 'subfolder' passed to "
                         "get_repository_folder: {}".format(subfolder))

def escape_for_bash(str_to_escape):
    """
    This function takes any string and escapes it in a way that
    bash will interpret it as a single string.
    
    Explanation:

    At the end, in the return statement, the string is put within single
    quotes. Therefore, the only thing that I have to escape in bash is the
    single quote character. To do this, I substitute every single
    quote ' with '"'"' which means:
                 
    First single quote: exit from the enclosing single quotes

    Second, third and fourth character: "'" is a single quote character,
    escaped by double quotes
    
    Last single quote: reopen the single quote to continue the string

    Finally, note that for python I have to enclose the string '"'"'
    within triple quotes to make it work, getting finally: the complicated
    string found below.
    """
    escaped_quotes = str_to_escape.replace("'","""'"'"'""")
    return "'{}'".format(escaped_quotes)

def get_suggestion(provided_string,allowed_strings):
    """
    Given a string and a list of allowed_strings, it returns a string to print
    on screen, with sensible text depending on whether no suggestion is found,
    or one or more than one suggestions are found.

    Args:
        provided_string: the string to compare
        allowed_strings: a list of valid strings
    
    Returns:
        A string to print on output, to suggest to the user a possible valid
        value.
    """
    import difflib
    
    similar_kws = difflib.get_close_matches(provided_string,
                                            allowed_strings)
    if len(similar_kws)==1:
        return "(Maybe you wanted to specify {0}?)".format(similar_kws[0])
    elif len(similar_kws)>1:
        return "(Maybe you wanted to specify one of these: {0}?)".format(
            string.join(similar_kws,', '))
    else:
        return "(No similar keywords found...)"


def validate_list_of_string_tuples(val, tuple_length):
    """
    Check that:

    1. ``val`` is a list or tuple
    2. each element of the list:

      a. is a list or tuple
      b. is of length equal to the parameter tuple_length
      c. each of the two elements is a string

    Return if valid, raise ValidationError if invalid
    """
    from aiida.common.exceptions import ValidationError

    err_msg = ("the value must be a list (or tuple) "
               "of length-N list (or tuples), whose elements are strings; "
               "N={}".format(tuple_length))
    if not isinstance(val,(list,tuple)):
        raise ValidationError(err_msg)
    for f in val:
        if (not isinstance(f,(list,tuple)) or
              len(f)!=tuple_length or
              not all(isinstance(s,basestring) for s in f)):
            raise ValidationError(err_msg)

    return True

def conv_to_fortran(val):
    """
    :param val: the value to be read and converted to a Fortran-friendly string.
    """   
    # Note that bool should come before integer, because a boolean matches also
    # isinstance(...,int)
    if (isinstance(val,bool)):
        if val:
            val_str='.true.'
        else:
            val_str='.false.'
    elif (isinstance(val,(int,long))): 
        val_str = "{:d}".format(val)
    elif (isinstance(val,float)):
        val_str = ("{:18.10e}".format(val)).replace('e','d')
    elif (isinstance(val,basestring)):
        val_str="'{!s}'".format(val)
    else:
        raise ValueError("Invalid value passed, accepts only bools, ints, "
                         "floats and strings")

    return val_str

def get_unique_filename(filename, list_of_filenames):
    """
    Return a unique filename that can be added to the list_of_filenames.
    
    If filename is not in list_of_filenames, it simply returns the filename
    string itself. Otherwise, it appends a integer number to the filename
    (before the extension) until it finds a unique filename.

    :param filename: the filename to add
    :param list_of_filenames: the list of filenames to which filename
        should be added, without name duplicates
    
    :returns: Either filename or its modification, with a number appended
        between the name and the extension.
    """
    if filename not in list_of_filenames:
        return filename

    basename, ext = os.path.splitext(filename)

    # Not optimized, but for the moment this should be fast enough
    append_int = 1
    while True:
        new_filename = "{:s}-{:d}{:s}".format(basename, append_int, ext)
        if new_filename not in list_of_filenames:
            break
        append_int += 1
    return new_filename

def md5_file(filename, block_size_factor=128):
    """
    Open a file and return its md5sum (hexdigested).

    :param filename: the filename of the file for which we want the md5sum
    :param block_size_factor: the file is read at chunks of size
        ``block_size_factor * md5.block_size``,
        where ``md5.block_size`` is the block_size used internally by the
        hashlib module.

    :returns: a string with the hexdigest md5.

    :raises: No checks are done on the file, so if it doesn't exists it may
        raise IOError.
    """
    import hashlib
    md5 = hashlib.md5()
    with open(filename,'rb') as f:
        # I read 128 bytes at a time until it returns the empty string b''
        for chunk in iter(
            lambda: f.read(block_size_factor*md5.block_size), b''):
            md5.update(chunk)
    return md5.hexdigest()

def sha1_file(filename, block_size_factor=128):
    """
    Open a file and return its sha1sum (hexdigested).

    :param filename: the filename of the file for which we want the sha1sum
    :param block_size_factor: the file is read at chunks of size
        ``block_size_factor * sha1.block_size``,
        where ``sha1.block_size`` is the block_size used internally by the
        hashlib module.

    :returns: a string with the hexdigest sha1.

    :raises: No checks are done on the file, so if it doesn't exists it may
        raise IOError.
    """
    import hashlib
    sha1 = hashlib.sha1()
    with open(filename,'rb') as f:
        # I read 128 bytes at a time until it returns the empty string b''
        for chunk in iter(
            lambda: f.read(block_size_factor*sha1.block_size), b''):
            sha1.update(chunk)
    return sha1.hexdigest()

def str_timedelta(dt, max_num_fields=3, short=False, negative_to_zero = False):
    """
    Given a dt in seconds, return it in a HH:MM:SS format.

    :param dt: a TimeDelta object
    :param max_num_fields: maximum number of non-zero fields to show
        (for instance if the number of days is non-zero, shows only
        days, hours and minutes, but not seconds)
    :param short: if False, print always ``max_num_fields`` fields, even
        if they are zero. If True, do not print the first fields, if they
        are zero.
    :param negative_to_zero: if True, set dt = 0 if dt < 0.
    """        
    if max_num_fields <= 0:
        raise ValueError("max_num_fields must be > 0")
    
    s = dt.total_seconds() # Important to get more than 1 day, and for 
                           # negative values. dt.seconds would give
                           # wrong results in these cases, see
                           # http://docs.python.org/2/library/datetime.html
    s = int(s)
    
    if negative_to_zero:
        if s < 0:
            s = 0

    negative = (s < 0)
    s = abs(s)
    
    negative_string = " in the future" if negative else " ago"
    
    # For the moment stay away from months and years, difficult to get
    days, remainder = divmod(s, 3600*24)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    all_fields = [(days,'D'), (hours, 'h'), (minutes, 'm'), (seconds,'s')]
    fields = []
    start_insert = False
    counter = 0
    for idx, f in enumerate(all_fields):
        if f[0] != 0:
            start_insert = True
        if (len(all_fields) - idx) <= max_num_fields:
            start_insert = True
        if start_insert:
            if counter >= max_num_fields:
                break
            fields.append(f)
            counter += 1
            
    if short:
        while len(fields)>1: # at least one element has to remain
            if fields[0][0] != 0:
                break
            fields.pop(0) # remove first element
            
    # Join the fields
    raw_string = ":".join(["{:02d}{}".format(*f) for f in fields])
    
    if raw_string.startswith('0'):
        raw_string = raw_string[1:]
    
    # Return the resulting string, appending a suitable string if the time
    # is negative
    return "{}{}".format(raw_string, negative_string)

def create_display_name(field):
    """
    Given a string, creates the suitable "default" display name: replace 
    underscores with spaces, and capitalize each word.
    
    :return: the converted string
    """
    return ' '.join(_.capitalize() for _ in field.split('_'))

def get_class_string(obj):
    """
    Return the string identifying the class of the object (module + object name,
    joined by dots).

    It works both for classes and for class instances.
    """
    import inspect
    if inspect.isclass(obj):
        return "{}.{}".format(
            obj.__module__,
            obj.__name__)     
    else:
        return "{}.{}".format(
            obj.__module__,
            obj.__class__.__name__)


def get_object_from_string(string):
    """
    Given a string identifying an object (as returned by the get_class_string
    method) load and return the actual object.
    """
    import importlib

    the_module, _, the_name = string.rpartition('.')
    
    return getattr(importlib.import_module(the_module), the_name)

def export_shard_uuid(uuid):
    """
    Sharding of the UUID for the import/export
    """
    return os.path.join(uuid[:2], uuid[2:4], uuid[4:])

def grouper(n, iterable):
    """
    Given an iterable, returns an iterable that returns tuples of groups of
    elements from iterable of length n, except the last one that has the
    required length to exaust iterable (i.e., there is no filling applied).
    
    :param n: length of each tuple (except the last one,that will have length
       <= n
    :param iterable: the iterable to divide in groups
    """
    import itertools
    
    it = iter(iterable)
    while True:
        chunk = tuple(itertools.islice(it, n))
        if not chunk:
            return
        yield chunk

def gzip_string(string):
    """
    Gzip string contents.

    :param string: a string
    :return: a gzipped string
    """
    import tempfile,gzip
    with tempfile.NamedTemporaryFile() as f:
        g = gzip.open(f.name,'wb')
        g.write(string)
        g.close()
        return f.read()

def gunzip_string(string):
    """
    Gunzip string contents.

    :param string: a gzipped string
    :return: a string
    """
    import tempfile,gzip
    with tempfile.NamedTemporaryFile() as f:
        f.write(string)
        f.flush()
        g = gzip.open(f.name,'rb')
        return g.read()

class EmptyContextManager(object):
    def __enter__(self):
        pass
    
    def __exit__(self, exc_type, exc_value, traceback):
        pass

