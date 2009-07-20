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
from unisono.utils import configuration
from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from unisono.db import DataBase

class UnisonoStats:
    '''
    class to hold the current statistics of UNISONO
    used for the Demonstrator GUI only!
    '''
    def __init__(self):
        pass

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
        port = self.config.get('Demo', 'xmlrpc-port')
        # Create server
        __server = SimpleXMLRPCServer((None, port),
                                      requestHandler=SimpleXMLRPCRequestHandler)
        __server.register_introspection_functions()

        # Register the functions
        __server.register_function(self.getStats)
        __server.register_function(self.getDB)
        
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
        return self.stats

    def getDB(self):
        '''
        XMLRPC function to get the db.
        return string sqlite dump
        '''
        dbcon = DataBase()
        dump =  dbcon.iterdump()
        return dump
