# -*- coding: utf-8 -*-
import os

from aiida.orm import Data
from aiida.common.exceptions import ModificationNotAllowed

__copyright__ = u"Copyright (c), 2015, ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE (Theory and Simulation of Materials (THEOS) and National Centre for Computational Design and Discovery of Novel Materials (NCCR MARVEL)), Switzerland and ROBERT BOSCH LLC, USA. All rights reserved."
__license__ = "MIT license, see LICENSE.txt file"
__version__ = "0.4.0"
__contributors__ = "Andrea Cepellotti, Giovanni Pizzi, Nicolas Mounet"

class FolderData(Data):
    """
    Stores a folder with subfolders and files.

    No special attributes are set.
    """
    def replace_with_folder(self,folder,overwrite=True):
        """
        Replace the data with another folder, always copying and not moving the
        original files.

        Args:
            folder: the folder to copy from
            overwrite: if to overwrite the current content or not
        """

        if not os.path.isabs(folder):
            raise ValueError("folder must be an absolute path")

        # TODO: implement the logic on the folder? Or set a 'locked' flag on folders?

        if self._to_be_stored:
            self._get_folder_pathsubfolder.replace_with_folder(folder,move=False,overwrite=overwrite)
        else:
            raise ModificationNotAllowed("You cannot change the files after the node has been stored")

    def get_file_content(self, path):
        """
        Return the content of a path stored inside the folder as a string.
        
        :raise NotExistent: if the path does not exist. 
        """
        from aiida.common.exceptions import NotExistent
        
        try:
            with open(self._get_folder_pathsubfolder.get_abs_path(
                path, check_existence=True)) as f:
                return f.read()
        except (OSError, IOError):
            raise NotExistent("Error reading the file '{}' inside node with "
                "pk= {}, it probably does not exist?".format(path, self.pk))
        
