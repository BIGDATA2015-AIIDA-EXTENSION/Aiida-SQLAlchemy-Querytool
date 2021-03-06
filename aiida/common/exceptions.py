# -*- coding: utf-8 -*-

__copyright__ = u"Copyright (c), 2015, ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE (Theory and Simulation of Materials (THEOS) and National Centre for Computational Design and Discovery of Novel Materials (NCCR MARVEL)), Switzerland and ROBERT BOSCH LLC, USA. All rights reserved."
__license__ = "MIT license, see LICENSE.txt file"
__version__ = "0.4.0"
__contributors__ = "Andrea Cepellotti, Giovanni Pizzi, Riccardo Sabatini"

class AiidaException(Exception):
    """
    Base class for all aiida exceptions.
    
    Each module will have its own subclass, inherited from this
    (e.g. ExecManagerException, TransportException, ...)
    """
    pass

class NotExistent(AiidaException):
    """
    Raised when the required entity does not exist.
    """
    pass

class MultipleObjectsError(AiidaException):
    """
    Raised when more than one entity is found in the DB, but only one was
    excepted.
    """
    pass
    
class RemoteOperationError(AiidaException):
    """
    Raised when an error in a remote operation occurs, as in a failed kill() 
    of a scheduler job.
    """
    pass

class ContentNotExistent(NotExistent):
    """
    Raised when trying to access an attribute, a key or a file in the result
    nodes that is not present
    """
    pass

class FailedError(AiidaException):
    """
    Raised when accessing a calculation that is in the FAILED status
    """
    pass

class ModificationNotAllowed(AiidaException):
    """
    Raised when the user tries to modify a field, object, property, ... that should not
    be modified.
    """
    pass

class UniquenessError(AiidaException):
    """
    Raised when the user tries to violate a uniqueness constraint (on the 
    DB, for instance).
    """
    pass

class MissingPluginError(AiidaException):
    """
    Raised when the user tries to use a plugin that is not available or does not exist.
    """
    pass

class InvalidOperation(AiidaException):
    """
    The allowed operation is not valid (e.g., when trying to add a non-internal attribute
    before saving the entry), or deleting an entry that is protected (e.g., 
    because it is referenced by foreign keys)
    """
    pass

class ParsingError(AiidaException):
    """
    Generic error raised when there is a parsing error
    """
    pass

class InternalError(AiidaException):
    """
    Error raised when there is an internal error of AiiDA.
    """
    pass

class PluginInternalError(InternalError):
    """
    Error raised when there is an internal error which is due to a plugin
    and not to the aiida infrastructure.
    """
    pass

class ValidationError(AiidaException):
    """
    Error raised when there is an error during the validation phase
    of a property. 
    """
    pass

class ConfigurationError(AiidaException):
    """
    Error raised when there is a configuration error in AiiDA.
    """
    pass

class DbContentError(AiidaException):
    """
    Raised when the content of the DB is not valid.
    This should never happen if the user does not play directly
    with the DB.
    """
    pass

class AuthenticationError(AiidaException):
    """
    Raised when a user tries to access a resource for which it is
    not authenticated, e.g. an aiidauser tries to access a computer
    for which there is no entry in the AuthInfo table.
    """
    pass

class InputValidationError(ValidationError):
    """
    The input data for a calculation did not validate (e.g., missing
    required input data, wrong data, ...)
    """
    pass

class WorkflowInputValidationError(ValidationError):
    """
    The input data for a workflow did not validate (e.g., missing
    required input data, wrong data, ...)
    """
    pass


class FeatureNotAvailable(AiidaException):
    """
    Raised when a feature is requested from a plugin, that is not available.
    """
    pass

class FeatureDisabled(AiidaException):
    """
    Raised when a feature is requested, but the used chose to disabled it
    (e.g., for submissions on disabled computers).
    """
    pass

class LockPresent(AiidaException):
    """
    Raised when a lock is requested, but cannot be acquired.
    """
    pass
