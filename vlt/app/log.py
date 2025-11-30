import os
import datetime
import warnings
from .. import file as vlt_file

class Log:
    """
    vlt.app.log: A logger for system and/or error messages by a Python application or package.
    """

    def __init__(self, system_logfile=None, error_logfile=None, debug_logfile=None,
                 system_verbosity=1.0, error_verbosity=1.0, debug_verbosity=1.0,
                 log_name='', log_error_behavior='warning'):

        cwd = os.getcwd()
        self.system_logfile = system_logfile if system_logfile else os.path.join(cwd, 'system.log')
        self.error_logfile = error_logfile if error_logfile else os.path.join(cwd, 'error.log')
        self.debug_logfile = debug_logfile if debug_logfile else os.path.join(cwd, 'debug.log')

        self.system_verbosity = system_verbosity
        self.error_verbosity = error_verbosity
        self.debug_verbosity = debug_verbosity
        self.log_name = log_name

        self.seterrorbehavior(log_error_behavior)
        self.touch()

    def seterrorbehavior(self, log_error_behavior):
        """
        Set the error behavior of a LOG object.
        """
        behavior = log_error_behavior.lower()
        if behavior in ['nothing', 'warning', 'error']:
            self.log_error_behavior = behavior
        else:
            raise ValueError(f"Unknown error behavior: {log_error_behavior}.")

    def touch(self):
        """
        Create all log files if they do not already exist.
        """
        paths = [self.system_logfile, self.error_logfile, self.debug_logfile]
        for path in paths:
            vlt_file.touch(path)

    def msg(self, type_, priority, message):
        """
        Write a log message to the log.
        Returns True if successful, False otherwise (or raises error based on behavior).
        """
        b = True
        errormsg = ''

        # Timestamp
        timestamp = datetime.datetime.now(datetime.timezone.utc).strftime('%d-%b-%Y %H:%M:%S')

        themsg = f"{timestamp} [{self.log_name}] {type_.upper()} {message}"

        type_upper = type_.upper()

        if type_upper == 'SYSTEM':
            if priority >= self.system_verbosity:
                b, errormsg = vlt_file.addline(self.system_logfile, themsg)
        elif type_upper == 'ERROR':
            if priority >= self.error_verbosity:
                b, errormsg = vlt_file.addline(self.error_logfile, themsg)
        elif type_upper == 'DEBUG':
            if priority >= self.debug_verbosity:
                b, errormsg = vlt_file.addline(self.debug_logfile, themsg)
        else:
            raise ValueError(f"Invalid log type: {type_}; expected SYSTEM, ERROR, or DEBUG")

        if not b:
            if self.log_error_behavior == 'nothing':
                pass
            elif self.log_error_behavior == 'warning':
                warnings.warn(errormsg)
            elif self.log_error_behavior == 'error':
                raise Exception(errormsg)

        return b
