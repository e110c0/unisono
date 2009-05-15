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
from xmlrpc.client import ServerProxy
from queue import Queue
from unisono.event import Event

class InterfaceError(Exception):
    pass
class OutOfRangeError(InterfaceError):
    pass
class InvalidTypeError(InterfaceError):
    pass

class ConnectorMap:
    '''
    A ConnectorMap holds all known (i.e. registered) unisono connectors. It is 
    only used by the XML RPC interface, both the server and the client part.
    '''
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    def __init__(self, q):
        if isinstance(q,Queue):
            self.eventq = q
        else:
            raise InvalidTypeError('System queue invalid type error (must be of type Queue)')
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
        if not 0 < conport < 65536:
            raise OutOfRangeError("Port number out of range (must be 1..65535)")
        if not (isinstance(conport, int)):
            raise InvalidTypeError("Port number invalid type (must be int)")

        with self.lock:
            # check for ip:port in conmap
            if (conip,conport) in self.conmap.values():
                conid = [ a for a in self.conmap.keys() 
                         if self.conmap[a] == (conip, conport)] 
                return str(conid)
            else:
                conid = uuid.uuid4()
                self.logger.debug('Created this UUID: %s', conid)
                self.conmap[str(conid)] = (conip, conport)
                return str(conid)

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
#        if not (0 < port < 65536):
#            return 2 #("Port number out of range (must be 1..65535)")
#        if not (isinstance(port, int)):
#            return 1 #("Port number invalid type (must be int)")
        self.logger.debug('RPC function register_connector called.')
        self.logger.debug('Connector requested registration for port %s', port)
        callerid = self.conmap.register_connector('127.0.0.1', port)
        return callerid

    def unregister_connector(self, callerid):
        '''
        unregister a connector from unisono
        '''
#        try: 
#            uuid.UUID(callerid)
#        except ValueError:
#            return 1 # invalid type error
        self.logger.debug('RPC function \'unregister_connector\'.')
        self.logger.debug('Connector requested deregistration: %s - Port',
                          callerid)

        status = self.conmap.deregister_connector(callerid)
        return status

    def list_available_dataitems(self):
        '''
        Lists the data items provided by the local unisono daemon

        returns string all available data items
        '''
        self.logger.debug('RPC function \'list_available_dataitems\'.')
        return list(self.dispatcher.dataitems.keys())

    def commit_order(self, conid, paramap):
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
        self.logger.debug('conmap %s', self.conmap.conmap)
        if conid in self.conmap.conmap.keys():
            self.logger.debug('connector is known, putting order in the queue')
            # create event and put it in the eventq
            paramap['conid'] = conid
            self.eventq.put(Event('ORDER', paramap))
        else:
            self.logger.error('Connector %s is unknown, discarding order!', conid)
            status = -1
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

# Threaded XMPRPC server
#class ThreadedXMLRPCserver(socketserver.ThreadingMixIn, SimpleXMLRPCServer):
class ThreadedXMLRPCserver(SimpleXMLRPCServer):

    '''
    non-blocking xmlrpc-server to handle concurrent requests
    '''
    pass

class RequestHandler(SimpleXMLRPCRequestHandler):
    '''
    Restrict requests to a particular path.
    '''
    rpc_paths = ('/unisono',)

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



################################################################################
# callback interface starts here
################################################################################
class XMLRPCReplyHandler:
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    def __init__(self, conmap, replyq, eventq):
        self.conmap = conmap
        self.replyq = replyq
        self.eventq = eventq
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
            event = self.replyq.get()
            # TODO do stuff
            if event.type == 'DELIVER':
                # payload is the result
                result = event.payload
                self.logger.debug('Our result is: %s', result)
                # find requester
                self.logger.debug('host: %s port: %s',self.conmap.conmap[result['conid']][0], self.conmap.conmap[result['conid']][1] )
                uri = 'http://' + self.conmap.conmap[result['conid']][0] + ':' + str(self.conmap.conmap[result['conid']][1])
                self.logger.debug('we try to connect to ' + uri + ' now.')
                connector = ServerProxy(uri)
                try:
                    connector.on_result(result)
                except:
                    self.logger.error('Connector unreachable!')
                    self.eventq.put(Event('CANCEL',(result['conid'],None)))
                    self.conmap.deregister_connector(result['conid'])
                    
            else:
                self.logger.debug('Got an unknown event type: %s. What now?', 
                                  event.type)

    def sendResult(self, result):
        pass
