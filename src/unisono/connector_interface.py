'''
connector_interface.py

 Created on: Mar 23, 2009
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

import socketserver, threading, logging, uuid

from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from unisono.event import Event

class ConnectorMap:
    '''
    A ConnectorMap holds all known (i.e. registered) unisono connectors. It is 
    only used by the XML RPC interface, both the server and the client part.
    '''
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    def __init__(self, q):
        self.eventq = q
        self.conmap = {}
        self.lock = threading.Lock()

    def register_connector(self, conip, conport):
        '''
        Register a connector with unisono. if a connector is already registered 
        with this ip/port tuple, return its id, too
        param conip ip address of the connector (mostly 127.0.0.1 or ::1)
        param conip port of the connector
        return conid uuid for the registered connector
        '''
        with self.lock:
            # check for ip:port in conmap
            if (conip,conport) in self.conmap.values():
                conid = [ a for a in self.conmap.keys() 
                         if self.conmap[a] == (conip, conport)] 
                return conid.hex()
            else:
                conid = uuid.uuid4()
                self.conmap[conid] = (conip, conport)
                return conid.hex()

    def deregister_connector(self, conid):
        '''
        Deregister a connector from unisono. This can happen on request or due
        to timeouts while replying to the connector.
        '''
        with self.lock:
            # Trigger cancel event for this connector id
            self.eventq.put(Event('CANCEL', (conid, None)))
            # delete connector entry from the map
            del self.conmap[conid]

# Threaded XMPRPC server
class ThreadedXMLRPCserver(socketserver.ThreadingMixIn, SimpleXMLRPCServer):
    '''
    non-blocking xmlrpc-server to handle concurrent requests
    '''
    pass

class XMLRPCServer:
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    def __init__(self, q, dispatcher):
        '''
        create and start a XMLRPC server thread
        '''
        self.conmap = ConnectorMap(q)
        self.eventq = q
        self.dispatcher = dispatcher
        # Create server
        __server = ThreadedXMLRPCserver(("localhost", 45312),
                                        requestHandler=RequestHandler)
        __server.register_introspection_functions()

        # Register an instance; all the methods of the instance are
        __server.register_instance(ConnectorFunctions(self.eventq,
                                                      self.dispatcher,
                                                      self.conmap))

        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        # TODO: check whether this is no problem
        server_thread = threading.Thread(target=__server.serve_forever)
        # Exit the server thread when the main thread terminates
        server_thread.setDaemon(True)
        server_thread.start()
        self.logger.info("XMLRPC listener loop running in thread: %s",
                         server_thread.name)

class RequestHandler(SimpleXMLRPCRequestHandler):
    '''
    Restrict requests to a particular path.
    '''
    rpc_paths = ('/unisono',)

class ConnectorFunctions:
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    '''
    functions available for connectors
    most of the functions reply with a status number. Results are received via
    the listener in the connectors.
    '''
    def __init__(self, q, dispatcher, conmap):
        self.eventq = q
        self.conmap = conmap
        self.dispatcher = dispatcher
        
    def register_connector(self, port):
        '''
        register a connector to the overlay for callbacks
        we require this because XMLRPC has no persistent connection and we want
        to work asynchronous
        param port callback port for the connector requesting registration
        return connector id 
        '''
        self.logger.debug('RPC function register_connector called.')
        self.logger.debug('Connector requested registration for port %s', port)
        callerid = self.conmap.register_connector(port, '127.0.0.1')
        return callerid
    def unregister_connector(self, callerid):
        '''
        unregister a connector from unisono
        '''
        self.logger.debug('RPC function \'unregister_connector\'.')
        self.logger.debug('Connector requested deregistration: %s - Port %s',
                          callerid, port)
        status = self.conmap.deregister_connector(callerid)
        return status

    def list_available_dataitems(self):
        '''
        Lists the data items provided by the local unisono daemon

        returns string all available data items
        '''
        self.logger.debug('RPC function \'list_available_dataitems\'.')
        
        return self.dispatcher.dataitems.keys()

    def commit_order(self, paramap):
        '''
        commit an order to the daemon
        the paramap includes the complete order in key:value pairs 
        (i.e. a python dictionary)
        
        returns int the status of the request
        '''
        self.logger.debug('RPC function \'commit_order\'.')
        self.logger.debug('Order: %s', paramap)
        status = 0
        # check registration
        if paramap[connector] in self.conmap.keys():
            # create event and put it in the eventq
            self.eventq.put(Event('ORDER', paramap))
        else:
            status = - 1
        return status

    def cancel_order(self, callerid, orderid):
        '''
        cancel an already running order

        returns int the status of the request
        '''
        self.logger.debug('RPC function \'cancel_order\'.')
        #  TODO: create event and put it in the eventq
        self.eventq.put(Event('CANCEL', (callerid,orderid)))
        status = 0
        return status

    def forward_received_packet(self, packet):
        '''
        forward packets received for the unisono daemon
        this wil be used by the daemon to communicate between different hosts

        returns int the status of the request
        '''
        self.logger.debug('RPC function \'forward_received_packet\'.')
        # create event and put it in the eventq
        self.eventq.put(Event('RECEIVE', packet))
        status = 0
        return status
    
    def cache_result(self, result):
        #  TODO: create event and put it in the eventq
        self.eventq.put(Event('CACHE', result))
        return

################################################################################
# callback interface starts here
################################################################################
class XMLRPCReplyHandler:
    def __init__(self, conmap, replyq):
        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        self.replyq = replyq
        reply_thread = threading.Thread(target=self.run)
        # Exit the server thread when the main thread terminates
        reply_thread.setDaemon(True)
        reply_thread.start()
        print("XMLRPC reply handler loop running in thread:", reply_thread.name)

    def run(self):
        '''
        get events from unisono and forward them to the corresponding connector
        '''
        while True:
            self.replyq.get()
            # TODO do stuff
            
    def sendResult(self, result):
        pass
