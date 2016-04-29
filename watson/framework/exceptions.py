# -*- coding: utf-8 -*-
import linecache
from watson.framework import __version__
from watson.common.imports import get_qualified_name


class ApplicationError(Exception):

    """A general purpose application error.

    ApplicationError exceptions are used to redirect the user to relevant
    http status error pages.

    Attributes:
        status_code (int): The status code to be used in the response
    """
    status_code = 500

    def __init__(self, message, status_code=None):
        if status_code:
            self.status_code = status_code
        super(ApplicationError, self).__init__(message)


class NotFoundError(ApplicationError):

    """404 Not Found exception.
    """
    status_code = 404


class InternalServerError(ApplicationError):

    """500 Internal Server Error exception.
    """
    status_code = 500


class ExceptionHandler(object):

    """Processes an exception and formats a stack trace.
    """

    def __init__(self, config=None):
        self.config = config or {}

    def __call__(self, exc_info):
        code, message, cause_message, frames, type = self.__process_exception(
            exc_info)
        return {
            'code': code,
            'message': message,
            'cause_message': cause_message,
            'version': __version__,
            'frames': frames,
            'type': type,
            'debug': self.config.get('enabled', True)
        }

    def __process_exception(self, exc_info):
        try:
            code = exc_info[1].status_code
        except:
            code = 500
        exc = exc_info[1]
        message = str(exc)
        cause_message = None
        try:
            exc = exc.__cause__
            tb = exc.__traceback__
            cause_message = str(exc)
            type = get_qualified_name(exc)
        except:
            tb = exc_info[2]
            type = get_qualified_name(exc_info[0])
        frames = []
        while tb is not None:
            frame = tb.tb_frame
            line = tb.tb_lineno
            co = frame.f_code
            file = co.co_filename
            function = co.co_name
            linecache.checkcache(file)
            sourcecode = linecache.getline(file, line, frame.f_globals)
            this_frame = {
                'line': line,
                'file': file,
                'function': function,
                'code': sourcecode.strip(),
                'vars': {}
            }
            frame_vars = frame.f_locals.items()
            for var_name, value in frame_vars:
                val = None
                try:
                    val = str(value)
                except:  # pragma: no cover
                    try:
                        val = repr(value)  # pragma: no cover
                    except:
                        val = None
                this_frame['vars'][var_name] = val
            frames.append(this_frame)
            tb = tb.tb_next
        frames.reverse()
        del tb
        return code, message, cause_message, frames, type
