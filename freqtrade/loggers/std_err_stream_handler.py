import logging
import sys
from logging import Handler


DEBUG_SUCCESS_NUM = 1001
DEBUG_FAILED_NUM = 1002


def debug_success(self, message, *args, **kws):
    if self.isEnabledFor(DEBUG_SUCCESS_NUM):
        self._log(DEBUG_SUCCESS_NUM, message, args, **kws)


def debug_fail(self, message, *args, **kws):
    if self.isEnabledFor(DEBUG_FAILED_NUM):
        self._log(DEBUG_FAILED_NUM, message, args, **kws)


logging.addLevelName(DEBUG_SUCCESS_NUM, "SUCCESS")
logging.addLevelName(DEBUG_FAILED_NUM, "FAILED")
logging.Logger.success = debug_success
logging.Logger.fail = debug_fail


class ColorFormatter(logging.Formatter):
    """Logging Formatter to add colors and count warning / errors"""

    blue = "\x1b[34m"
    cyan = "\x1b[36;21m"
    green = "\x1b[32;21m"
    orange = "\x1b[33;21m"
    grey = "\x1b[38;21m"
    yellow = "\x1b[33;21m"
    red = "\x1b[31;21m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    time_prefix = "[%(asctime)s]"
    filename_prefix = " (%(filename)s:%(lineno)d)  "
    msg = "%(message)s"

    prefix = orange + time_prefix + reset + grey + filename_prefix + reset

    default_formatter = logging.Formatter(prefix + cyan + msg + reset)

    FORMATS = {
        logging.DEBUG: logging.Formatter(prefix + blue + msg + reset),
        logging.INFO: logging.Formatter(prefix + cyan + msg + reset),
        logging.WARNING: logging.Formatter(prefix + yellow + msg + reset),
        logging.ERROR: logging.Formatter(prefix + red + msg + reset),
        logging.CRITICAL: logging.Formatter(prefix + bold_red + msg + reset),
        DEBUG_SUCCESS_NUM: logging.Formatter(prefix + green + msg + reset),
        DEBUG_FAILED_NUM: logging.Formatter(prefix + bold_red + msg + reset),
    }

    def format(self, record):
        formatter = self.FORMATS.get(record.levelno, self.default_formatter)
        return formatter.format(record)


class FTStdErrStreamHandler(Handler):
    def flush(self):
        """
        Override Flush behaviour - we keep half of the configured capacity
        otherwise, we have moments with "empty" logs.
        """
        self.acquire()
        try:
            sys.stderr.flush()
        finally:
            self.release()

    def emit(self, record):
        try:
            msg = self.format(record)
            # Don't keep a reference to stderr - this can be problematic with progressbars.
            sys.stderr.write(msg + '\n')
            self.flush()
        except RecursionError:
            raise
        except Exception:
            self.handleError(record)
