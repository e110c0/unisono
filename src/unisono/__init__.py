from unisono.dispatcher import Dispatcher
from unisono.utils import unilog
import logging, threading, os
from sys import stdin, exit

from optparse import OptionParser
parser = OptionParser()
parser.add_option("-d", "--daemon",
                  action="store_true", default=False,
                  help="fork to background and write pid to pidfile")
parser.add_option("--pidfile",
                  action="store", default="/var/run/unisono.pid",
                  help="pidfile to use (%default)")

def main():
    (options, args) = parser.parse_args()
    if args:
        parser.error("too many arguments")

    unilog.init_logging()
    logger = logging.getLogger(__name__)

    if options.daemon:
        pid = os.fork()
        if not pid:
            # we are the new child
            pid = os.getpid()
            logger.info("UNISONO ---- start daemon (pid: %i)"%pid)
            if options.pidfile:
                # we intentionally die on write errors here, as our callee had no way to
                # stop us otherwise
                # TODO: check if process in pidfile is alive (ie we're already running)
                try:
                    with open(options.pidfile, "w") as pidfile:
                        pidfile.write(str(pid))
                except (OSError, IOError) as e:
                    logger.error("Error writing pidfile (%s), terminating"%e)
                    exit(1)
        else:
            exit(0)
    else:
        logger.info("UNISONO ---- start in foreground")
    # init dispatcher
    dp = Dispatcher()
    dp.run()
    logger.info('shutting down.')