#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

__copyright__ = u"Copyright (c), 2015, ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE (Theory and Simulation of Materials (THEOS) and National Centre for Computational Design and Discovery of Novel Materials (NCCR MARVEL)), Switzerland and ROBERT BOSCH LLC, USA and Django Software Foundation and individual contributors. All rights reserved."
__license__ = "MIT license, and Django license, see LICENSE.txt file"
__version__ = "0.4.0"
__contributors__ = "Andrea Cepellotti, Giovanni Pizzi"

if __name__ == "__main__":
    from django.core.management import execute_from_command_line
    from aiida.djsite.utils import load_dbenv

    # Copy sys.argv
    actual_argv = sys.argv[:]

    # Check if the first cmdline option is --aiida-process=PROCESSNAME
    try:
        first_cmdline_option = sys.argv[1]
    except IndexError:
        first_cmdline_option = None
    
    process_name = None # Use the default process if not specified    
    if first_cmdline_option is not None:
        cmdprefix = "--aiida-process="
        if first_cmdline_option.startswith(cmdprefix):
            process_name = first_cmdline_option[len(cmdprefix):]
            # I remove the argument I just read
            actual_argv = [sys.argv[0]] + sys.argv[2:]
            
    load_dbenv(process=process_name)
    
    execute_from_command_line(actual_argv)

