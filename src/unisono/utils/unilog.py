'''
unilog.py

 Created on: Mar 25, 2009
 Authors: dh

 $LastChangedBy$
 $LastChangedDate$
 $Revision$

 (C) 2008-2009 by Computer Networks and Internet, University of Tuebingen

 This file is part of UNISONO Unified Information Service for Overlay
 Network Optimization.

 UNISONO is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 2 of the License, or
 (at your option) any later version.

 UNISONO is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with UNISONO.  If not, see <http://www.gnu.org/licenses/>.

'''
import logging
import sys
from os.path import expanduser
from unisono.utils import configuration

'''
global logging for unisono
usage:

import logging
logger = logging.getLogger(__name__) <-- this sets the class name in the logger
logger.setLevel(logging.INFO) <-- set the loglevel:
                                  DEBUG, INFO, WARNING, ERROR, CRITICAL
                                  global level might ommit messages!
'''
def init_logging(daemon=False):
    config = configuration.get_configparser()
    # configure the root logger
    logger = logging.getLogger()
    # root logger should accept all loglevels, handlers decide what to log
    logger.setLevel(logging.NOTSET)

    # create formatter and add it to the handlers
    logformat = logging.Formatter('%(asctime)s - %(name)-32s - %(levelname)-8s - %(message)s')
    try:
        logformat = logging.Formatter(config.get('Logging', 'log_format'))
    except:
        print('using default logformat')
    # define debug format
    debugformat = logging.Formatter('%(asctime)s - %(threadName)-10s - %(name)-32s - %(levelname)-8s - %(filename)-15s - %(lineno)4d - %(message)s')
    try:
        debugformat = logging.Formatter(config.get('Logging', 'debugformat'))
    except:
        print('using default debugformat')
    # get global loglevel
    try:
        loglevel = config.get('Logging', 'loglevel')
        loglevel = getattr(logging,loglevel.upper())
    except:
        # if config doesnt exist or is broken
        print('using default loglevel INFO')
        loglevel = logging.INFO
    # create logging handler for logfile
    if (config.get('Logging', 'uselogfile')):
        print()
        # create file handler which logs all but no debug
        fh = logging.FileHandler(expanduser(config.get('Logging','logfile')))
        fh.setLevel(loglevel)
        fh.setFormatter(logformat)
        logger.addHandler(fh)
    # create logging handler for console

    if not(config.getboolean('Logging','daemonmodelogging') or daemon):
        print('we enable console logging')
        ch = logging.StreamHandler()
        # create console handler for debugging
        if (config.getboolean('General','debug')):
            ch.setLevel(logging.DEBUG)
            ch.setFormatter(debugformat)
        else:
            ch.setLevel(loglevel)
            ch.setFormatter(logformat)
        # add the handlers to logger
        logger.addHandler(ch)
    else:
        print('we disable console logging')
    logger = logging.getLogger(__name__)
    logger.info('UNISONO logging started')