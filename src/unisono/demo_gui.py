'''
demo_gui.py

 Created on: Jul 20, 2009
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
import threading

from unisono.utils import configuration
from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from unisono.db import DataBase
from os.path import expanduser
from os import times as os_times
from time import time

class UnisonoStats:
    '''
    class to hold the current statistics of UNISONO
    used for the Demonstrator GUI only!
    '''
    def __init__(self):
        self.entries = {}
        # get start time
        self.entries['starttime'] = time()
        # get initial load stats
        self.entries['cputimestamp'] = self.entries['starttime']
        ostimes = os_times()
        self.entries['cpusys'] = ostimes[0]
        self.entries['cpuuser'] = ostimes[1]

    def update_process_stats(self):
        '''
        update the process stats like mem usage, cpu usage etc.
        '''
        self.entries['memory'] = 1
        # load stats
        ostimes = os_times()
        now = time()
        delta = now - self.entries['cputimestamp']
        # current load stats
        self.entries['cpusys_current'] = (ostimes[0] - self.entries['cpusys']) / delta * 100
        self.entries['cpuuser_current'] = (ostimes[1] - self.entries['cpuuser']) / delta * 100
        # global load stats
        self.entries['cpusys'] = ostimes[0]
        self.entries['cpuuser'] = ostimes[1]
        self.entries['cputimestamp'] = time()
        
        self.entries['uptime'] = time() - self.entries['starttime']

    def update_db_stats(self):
        '''
        update the db stats like size, entries etc.
        '''
        self.entries['dbsize'] = 3
        self.entries['dbentrycount'] = 4

class DemoGUI:
    '''
    classdocs
    '''
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    def __init__(self, stats):
        '''
        Constructor
        '''
        self.stats = stats
        # init xmlrpcserver
        self.config = configuration.get_configparser()
        port = self.config.getint('Demo', 'xmlrpc-port')
        # Create server
        __server = SimpleXMLRPCServer(('', port),
                                      requestHandler=SimpleXMLRPCRequestHandler)
        __server.register_introspection_functions()

        # Register the functions
        __server.register_function(self.getStats)
        __server.register_function(self.getDB)
        __server.register_function(self.getLog)
        
        server_thread = threading.Thread(target=__server.serve_forever)
        # Exit the server thread when the main thread terminates
        server_thread.setDaemon(True)
        server_thread.start()
        self.logger.info("GUI listener loop running in thread: %s",
                         server_thread.name)

    def getStats(self):
        '''
        XMLRPC function to get the statistics
        '''
        self.stats.update_process_stats()
        self.stats.update_db_stats()

        return self.stats

    def getDB(self):
        '''
        XMLRPC function to get the db.
        return string sqlite dump
        '''
        dump = ""
        for i in DataBase().dbcon.iterdump():
            dump = dump + i + "\n"
        return dump

    def getLog(self):
        '''
        XMLRPC function to get the db.
        return string logfile
        '''
        return open(expanduser(self.config.get("Logging","logfile")), mode='r').read()
