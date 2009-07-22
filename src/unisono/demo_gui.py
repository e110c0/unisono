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
import os
from os import popen




def memory(since=0.0):
    '''Return memory usage in bytes.
    '''
    return _VmB('VmSize:') - since


def resident(since=0.0):
    '''Return resident memory usage in bytes.
    '''
    return _VmB('VmRSS:') - since


def stacksize(since=0.0):
    '''Return stack size in bytes.
    '''
    return _VmB('VmStk:') - since


class UnisonoStats:
    '''
    class to hold the current statistics of UNISONO
    used for the Demonstrator GUI only!
    '''
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    def __init__(self, conmap):
        self.conmap = conmap
        self.entries = {}
        # get start time
        self.entries['starttime'] = time()
        # get initial load stats
        self.entries['cputimestamp'] = self.entries['starttime']
        ostimes = os_times()
        self.entries['cpusys'] = ostimes[0]
        self.entries['cpuuser'] = ostimes[1]
        
        self.entries['db_purge'] = self.entries['starttime']

        self.entries['orders_global'] = 0
        self.entries['aggregations_global'] = 0
        self.entries['fromcache_global'] = 0

        self.entries['orders'] = 0
        self.entries['aggregations'] = 0
        self.entries['queued_orders'] = 0

    def update_process_stats(self):
        '''
        update the process stats like mem usage, cpu usage etc.
        '''
        self.entries['memory_alloc'] = self._stat('VmSize') * 1024.0
        self.entries['memory_alloc_max'] = self._stat('VmPeak') * 1024.0
        self.entries['memory_rss'] = self._stat('VmRSS') * 1024.0
        self.entries['memory_hwn'] = self._stat('VmHWM') * 1024.0
        self.entries['threads'] = self._stat('Threads')
        # load stats
        ostimes = os_times()
        now = time()
        delta = now - self.entries['cputimestamp']
        # current load stats
        # this gives the average usage since the last update.
        self.entries['cpusys_current'] = (ostimes[0] - self.entries['cpusys']) / delta * 100
        self.entries['cpuuser_current'] = (ostimes[1] - self.entries['cpuuser']) / delta * 100
        # global load stats
        self.entries['cpusys'] = ostimes[0]
        self.entries['cpuuser'] = ostimes[1]
        self.entries['cputimestamp'] = time()
        
        self.entries['uptime'] = time() - self.entries['starttime']
        
        self.entries['identifiers'] = self._identifiers()
        self.entries['connectors'] = self._connectors()
        
    def _identifiers(self):
        identifiers = []
        for i in popen('ip a').read().splitlines():
            j = i.split()
            if 'inet' in j[0]:
                identifiers.append(j[1].split('/')[0])
        return identifiers

    def _connectors(self):
        connectors =[]
        for i in self.conmap.conmap.keys():
            connectors.append(i)
        return connectors

    def _stat(self, key):
        ''' private '''
        # get pseudo file  /proc/<pid>/status
        t = open('/proc/%d/status' % os.getpid())
        v = t.read()
        t.close()

        # get VmKey line e.g. 'VmRSS:  9999  kB\n ...'
        i = v.index(key)
        v = v[i:].split(None, 3)  # whitespace
        if len(v) < 3:
            return 0.0  # invalid format?
        # convert Vm value to bytes
        return float(v[1])

    def update_db_stats(self):
        '''
        update the db stats like size, entries etc.
        '''
        db = DataBase()
        c = db.dbcon.cursor()
        c.execute('''select name from sqlite_master where type = 'table';''')
        self.entries['dbtables'] = 0
        self.entries['dbentrycount'] = 0
        for i in c.fetchall():
            self.entries['dbtables'] = self.entries['dbtables'] + 1
            c.execute('''select * from ''' + i[0] + ''' ;''')
            rows = len(c.fetchall())
            self.logger.info('table: %s: %i', i[0], rows)
            self.entries['dbentrycount'] = self.entries['dbentrycount'] + rows
            
        c.execute('''pragma  page_count''')
        pagecount = c.fetchone()[0]
        c.execute('''pragma  freelist_count''')
        freecount = c.fetchone()[0]
        c.execute('''pragma  page_size''')
        pagesize = c.fetchone()[0]
        self.entries['dbsize'] = pagecount * pagesize
        self.entries['dbsize_unused'] = freecount * pagesize

    def increase_stats(self, key, count):
        '''
        increase a value by count
        '''
        try:
            self.entries[key] = self.entries[key] + count
        except:
            self.logger.debug('unknown key')

    def decrease_stats(self, key, count):
        '''
        decrease a value by count
        '''
        try:
            self.entries[key] = self.entries[key] - count
        except:
            self.logger.debug('unknown key')

    def update_stats(self, key, value):
        '''
        update a value with value
        '''
        try:
            self.entries[key] = value
        except:
            self.logger.debug('unknown key')

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

        return self.stats.entries

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
        return open(expanduser(self.config.get("Logging", "logfile")), mode='r').read()
