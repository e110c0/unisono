'''
dispatcher.py

 Created on: May 5, 2009
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
from queue import Queue
from unisono.XMLRPCListener import XMLRPCServer
from unisono.XMLRPCReplyHandler import XMLRPCReplyHandler
import logging
class Dispatcher:
    '''
    classdocs
    '''
    logger = logging.getLogger(__name__)
    logger.setLevel(DEBUG)

    def __init__(selfparams):
        '''
        Constructor
        '''
        self.eventq = Queue()
        self.startXMLRPCServer()
        self.startXMLRPCReplyHandler()
        self.initPlugins()
    
    def startXMLRPCServer(self):
        # TODO: check whether XMLRPCserver is alread running
        self.xsrv = XMLRPCServer(self.eventq)

    def startXMLRPCReplyHandler(self):
        self.replyq = Queue()
        xrh = XMLRPCReplyHandler(self.xsrv.conmap, self.replyq)
        
    def initPlugins(self):
        pass