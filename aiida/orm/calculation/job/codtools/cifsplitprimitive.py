# -*- coding: utf-8 -*-
"""
Plugin to create input for scripts from cod-tools package.
This plugin is in the development stage. Andrius Merkys, 2014-10-29
"""
import os
import shutil

from aiida.orm.calculation.job.codtools.ciffilter import CiffilterCalculation
from aiida.orm.data.cif import CifData
from aiida.orm.data.parameter import ParameterData
from aiida.common.datastructures import CalcInfo
from aiida.common.exceptions import InputValidationError
from aiida.common.utils import classproperty

__copyright__ = u"Copyright (c), 2015, ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE (Theory and Simulation of Materials (THEOS) and National Centre for Computational Design and Discovery of Novel Materials (NCCR MARVEL)), Switzerland and ROBERT BOSCH LLC, USA. All rights reserved."
__license__ = "MIT license, see LICENSE.txt file"
__version__ = "0.4.0"
__contributors__ = "Andrea Cepellotti, Giovanni Pizzi"

class CifsplitprimitiveCalculation(CiffilterCalculation):
    """
    Specific input plugin for cif_cell_contents from cod-tools package.
    """

    def _init_internal_params(self):
        super(CifsplitprimitiveCalculation, self)._init_internal_params()

        self._default_parser = 'codtools.cifsplitprimitive'

        self._SPLIT_DIR = 'split'

    def _prepare_for_submission(self,tempfolder,inputdict):
        try:
            cif = inputdict.pop(self.get_linkname('cif'))
        except KeyError:
            raise InputValidationError("no CIF file is specified for this calculation")
        if not isinstance(cif, CifData):
            raise InputValidationError("cif is not of type CifData")

        parameters = inputdict.pop(self.get_linkname('parameters'), None)
        if parameters is None:
            parameters = ParameterData(dict={})
        if not isinstance(parameters, ParameterData):
            raise InputValidationError("parameters is not of type ParameterData")

        input_filename = tempfolder.get_abs_path(self._DEFAULT_INPUT_FILE)
        shutil.copy( cif.get_file_abs_path(), input_filename )

        split_dir = tempfolder.get_abs_path(self._SPLIT_DIR)
        os.mkdir(split_dir)

        commandline_params = [ '--output-dir', self._SPLIT_DIR ]
        for k in parameters.get_dict().keys():
            v = parameters.get_dict()[k]
            if v is None:
                continue
            if not isinstance(v, list):
                v = [ v ]
            key = None
            if len( k ) == 1:
                key = "-{}".format( k )
            else:
                key = "--{}".format( k )
            for val in v:
                if isinstance(val, bool) and val == False:
                    continue
                commandline_params.append( key )
                if not isinstance(val, bool):
                    commandline_params.append( val )

        calcinfo = CalcInfo()
        calcinfo.uuid = self.uuid
        calcinfo.cmdline_params = commandline_params
        calcinfo.local_copy_list = []
        calcinfo.remote_copy_list = []
        calcinfo.stdin_name  = self._DEFAULT_INPUT_FILE
        calcinfo.stdout_name = self._DEFAULT_OUTPUT_FILE
        calcinfo.stderr_name = self._DEFAULT_ERROR_FILE
        calcinfo.retrieve_list = [self._DEFAULT_OUTPUT_FILE,
                                  self._DEFAULT_ERROR_FILE,
                                  self._SPLIT_DIR]
        calcinfo.retrieve_singlefile_list = []

        return calcinfo
