# -*- coding: utf-8 -*-
"""
This file was copied and edited from Django 1.7.4, and modified to allow to define default loads in ipython.

.. note: Only ipython and bpython do the auto import, not the plain shell.

.. note: This command should be updated when we upgrade to a more recent version of django.

.. todo: Move the list of commands to import from here (method get_start_namespace) to
    the settings.py module, probably.
"""
from optparse import make_option
import os
from django.core.management.base import NoArgsCommand

__copyright__ = u"Copyright (c), 2015, ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE (Theory and Simulation of Materials (THEOS) and National Centre for Computational Design and Discovery of Novel Materials (NCCR MARVEL)), Switzerland and ROBERT BOSCH LLC, USA and Django Software Foundation and individual contributors. All rights reserved."
__license__ = "MIT license, and Django license, see LICENSE.txt file"
__version__ = "0.4.0"
__contributors__ = "Andrea Cepellotti, Andrius Merkys, Giovanni Pizzi, Nicolas Mounet"

default_modules_list = [
            #    ("aiida.djsite.db.models","DbNode","DbNode"),
                        ("aiida.orm","Node","Node"),
                        ("aiida.orm","Calculation","Calculation"),
                        ("aiida.orm","JobCalculation","JobCalculation"),
                        ("aiida.orm","Code","Code"),
                        ("aiida.orm","Data","Data"),
                        ("aiida.orm","CalculationFactory","CalculationFactory"),
                        ("aiida.orm","DataFactory","DataFactory"),
                        ("aiida.orm","Computer","Computer"),
                        ("aiida.orm","Group","Group"),
                        ("aiida.orm","load_node","load_node"),
                        ("aiida.orm.workflow","Workflow","Workflow"),
                        ("aiida.orm","load_workflow","load_workflow"),
                        ("aiida.djsite.db","models","models"),
                        ]


class Command(NoArgsCommand):
    shells = ['ipython', 'bpython']

    option_list = NoArgsCommand.option_list + (
        make_option('--plain', action='store_true', dest='plain',
            help='Tells Django to use plain Python, not IPython or bpython.'),
        make_option('--no-startup', action='store_true', dest='no_startup',
            help='When using plain Python, ignore the PYTHONSTARTUP environment variable and ~/.pythonrc.py script.'),
        make_option('-i', '--interface', action='store', type='choice', choices=shells,
                    dest='interface',
            help='Specify an interactive interpreter interface. Available options: "ipython" and "bpython"'),

    )
    help = "Runs a Python interactive interpreter. Tries to use IPython or bpython, if one of them is available."
    requires_system_checks = False

    def get_start_namespace(self):
        user_ns = {}
        for app_mod, model_name, alias in default_modules_list:
            user_ns[alias] = getattr(__import__(app_mod, {}, {}, model_name), model_name)
        
        return user_ns

    def _ipython_pre_011(self):
        """Start IPython pre-0.11"""
        from IPython.Shell import IPShell
        user_ns = self.get_start_namespace()
        if user_ns:
            shell = IPShell(argv=[],user_ns=user_ns)
        else:
            shell = IPShell(argv=[])
        shell.mainloop()

    def _ipython_pre_100(self):
        """Start IPython pre-1.0.0"""
        from IPython.frontend.terminal.ipapp import TerminalIPythonApp
        app = TerminalIPythonApp.instance()
        app.initialize(argv=[])
        user_ns = self.get_start_namespace() 
        if user_ns:
            app.shell.user_ns.update(user_ns) 
        app.start()

    def _ipython(self):
        """Start IPython >= 1.0"""
        from IPython import start_ipython
        user_ns = self.get_start_namespace()
        if user_ns:
            start_ipython(argv=[],user_ns=user_ns)
        else:
            start_ipython(argv=[])

    def ipython(self):
        """Start any version of IPython"""
        for ip in (self._ipython, self._ipython_pre_100, self._ipython_pre_011):
            try:
                ip()
            except ImportError:
                pass
            else:
                return
        # no IPython, raise ImportError
        raise ImportError("No IPython")

    def bpython(self):
        import bpython
        user_ns = self.get_start_namespace()
        if user_ns:
            bpython.embed(user_ns)
        else:
            bpython.embed()

    def run_shell(self, shell=None):
        available_shells = [shell] if shell else self.shells

        for shell in available_shells:
            try:
                return getattr(self, shell)()
            except ImportError:
                pass
        raise ImportError

    def handle_noargs(self, **options):
        use_plain = options.get('plain', False)
        no_startup = options.get('no_startup', False)
        interface = options.get('interface', None)

        try:
            if use_plain:
                # Don't bother loading IPython, because the user wants plain Python.
                raise ImportError

            self.run_shell(shell=interface)
        except ImportError:
            import code
            # Set up a dictionary to serve as the environment for the shell, so
            # that tab completion works on objects that are imported at runtime.
            # See ticket 5082.
            imported_objects = {}
            try:  # Try activating rlcompleter, because it's handy.
                import readline
            except ImportError:
                pass
            else:
                # We don't have to wrap the following import in a 'try', because
                # we already know 'readline' was imported successfully.
                import rlcompleter
                readline.set_completer(rlcompleter.Completer(imported_objects).complete)
                readline.parse_and_bind("tab:complete")

            # We want to honor both $PYTHONSTARTUP and .pythonrc.py, so follow system
            # conventions and get $PYTHONSTARTUP first then .pythonrc.py.
            if not no_startup:
                for pythonrc in (os.environ.get("PYTHONSTARTUP"), '~/.pythonrc.py'):
                    if not pythonrc:
                        continue
                    pythonrc = os.path.expanduser(pythonrc)
                    if not os.path.isfile(pythonrc):
                        continue
                    try:
                        with open(pythonrc) as handle:
                            exec(compile(handle.read(), pythonrc, 'exec'), imported_objects)
                    except NameError:
                        pass
            code.interact(local=imported_objects)
