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

import socketserver, threading, logging, uuid, socket
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
        if isinstance(q, Queue):
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
        try:
            socket.getaddrinfo(conip, None)
        except socket.gaierror:
            raise InvalidTypeError('provided IP not valid')
        with self.lock:
            # check for ip:port in conmap
            if (conip, conport) in self.conmap.values():
                conid = [a for a in self.conmap.keys() 
                        if self.conmap[a] == (conip, conport)]
                self.logger.info('Connector already known under UUID %s', conid)
                return conid[0]
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
        self.logger.debug('Trying to deregister connector %s', conid)
        self.logger.debug('currently registered: %s', self.conmap)
        with self.lock:
            # Trigger cancel event for this connector id
            self.eventq.put(Event('CANCEL', (conid, None)))
            # delete connector entry from the map
            del self.conmap[conid]
            self.logger.debug('now: %s', self.conmap)
        return 0;

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
        Register a connector to the overlay for callbacks. This is required
        because XMLRPC has no persistent connection and UNISONO must be able to
        work asynchronous and to reply several times on one request (e.g. for
        periodic measurements).
        parameters:
        port - callback port for the connector requesting registration (int)
        
        return string - connector id (UUID) 
        '''
        if not (0 < port < 65536):
            return 2 #("Port number out of range (must be 1..65535)")
        if not (isinstance(port, int)):
            return 1 #("Port number invalid type (must be int)")
        self.logger.debug('RPC function register_connector called.')
        self.logger.debug('Connector requested registration for port %s', port)
        callerid = self.conmap.register_connector('127.0.0.1', port)
        self.logger.debug('CallerID: %s', callerid)
        return callerid

    def unregister_connector(self, callerid):
        '''
        Unregister a connector from unisono.
        This will also cancel all orders for this connector immediately.
        parameters:
        callerid - the id of the connector (UUID as string) 
        
        return status, 0 if everything went fine. (int)
        '''
        try: 
            uuid.UUID(callerid)
        except ValueError:
            return 1 # invalid type error
        self.logger.debug('RPC function \'unregister_connector\'.')
        self.logger.debug('Connector requested deregistration: %s', callerid)

        status = self.conmap.deregister_connector(callerid)
        self.logger.debug('dereg status: %s', status)
        return status

    def list_available_dataitems(self):
        '''
        Lists the data items provided by the local unisono daemon

        return string - all available data items
        '''
        self.logger.debug('RPC function \'list_available_dataitems\'.')
        return sorted(list(self.dispatcher.dataitems.keys()))

    def commit_order(self, conid, paramap):
        '''
        Commit an order.
        
        parameters
        conid   - UUID of the connector (string)
        paramap - the paramap includes the complete order in key:value pairs 
        (i.e. a python dictionary)
        
        returns int the status of the request
        '''
        self.logger.debug('RPC function \'commit_order\'.')
        self.logger.debug('Order: %s', paramap)
        status = 0
        # sanity checks
        for i in ['orderid']:
            if i not in paramap.keys():
                self.logger.error('Order is incomplete (missing %s), discarding', i)
                status = 400
                #order['errortext'] = 'Order incomplete, missing ' + i
                #self.replyq.put(Event('DISCARD', order))
                return status;
        # TODO: check for orderid clashes here??
        # check registration
        self.logger.debug('conmap %s', self.conmap.conmap)
        if conid in self.conmap.conmap.keys():
            self.logger.debug('connector is known, putting order in the queue')
            # create event and put it in the eventq
            paramap['conid'] = conid
            self.eventq.put(Event('ORDER', paramap))
        else:
            self.logger.error('Connector %s is unknown, discarding order!', conid)
            status = 401
        return status

    def cancel_order(self, callerid, orderid):
        '''
        Cancel an already running order.

        parameters:
        callerid - UUID of the caller (string) 
        orderid - ID of the order (string), must be unique!
        
        returns int the status of the request
        '''
        self.logger.debug('RPC function \'cancel_order\'.')
        #  TODO: create event and put it in the eventq
        self.eventq.put(Event('CANCEL', (callerid, orderid)))
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
        '''
        Cache a result from a remote request.
        In order to benefit from remote results, these results are cached in 
        UNISONO.
        
        parameters
        result - a paramap including the order parameters as well as the result
        (similar to the commit_order() paramap)
        '''
        #  TODO: create event and put it in the eventq
        self.eventq.put(Event('CACHE', result))
        return

    def check_cache(self, paramap):
        '''
        with check_cache() it is possible to get a result from UNISONO cache if
        any exists. This should primarily be used to check for results cached
        from remote hosts.
        The used syntax is similar to commit_order() but it directly returns the
        result if available.
        
        parameters
        conid   - UUID of the connector (string)
        paramap - the paramap includes the complete order in key:value pairs 
        (i.e. a python dictionary)
        
        return struct the paramap extended with the result
        '''
        # TODO: really check the cache as soon as it is implemented.
        paramap['error'] = 404
        paramap['errortext'] = 'Data item not found in cache'
        return paramap

#class CorrelationInterface:
#    def correlate_this(self, ditype, parameter1, parameter2):
#        pass

# Threaded XMPRPC server
#class ThreadedXMLRPCserver(socketserver.ThreadingMixIn, SimpleXMLRPCServer):
class ThreadedXMLRPCserver(SimpleXMLRPCServer):

    '''
    non-blocking xmlrpc-server to handle concurrent requests
    WARNING: We changed this to a blocking XMLRPCServer which handles only 1
    request at a time. This is slightly (~10%) faster than threaded. If this
    blocks too long, we can change this back to a threaded approach.
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
        #__server.register_instance(CorrelationInterface())

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

    def find_requester(self,conid):
        uri = 'http://' + self.conmap.conmap[conid][0] + ':' + str(self.conmap.conmap[conid][1]) + "/RPC2"
        connector = ServerProxy(uri)
        return connector

    def run(self):
        '''
        get events from unisono and process them.
        currently, the handler processes the following events:

        DELIVER: deliver a result to the corresponding connector
                 the result structure is a dictionary (or XMLRPC struct) with
                 the following structure:
                 * all entries of the original order (including orderid,
                   requested data item etc.
                 * a key:value pair for each data item, e.g.
                   RTT = 123
                 * error: the error code of the measurement
                 * errortext: a specific error text for the error code
                 * result: the result of the first requested data item. This
                   entry is deprecated, it can not handle orders with more then
                   one data item.
        DISCARD: discard an order if UNISONO isn't able to process it.
                 the result structure is a dictionary (or XMLRPC struct) with
                 the following structure:
                 * orderid of the discarded order
                 * error: the error code of the measurement
                 * errortext: a specific error text for the error code
        '''
        while True:
            event = self.replyq.get()
            # TODO do stuff
            self.logger.debug('got event %s',event.type)
            if event.type == 'DELIVER':
                # payload is the result
                result = event.payload
                self.logger.debug('Our result is: %s', result)
                # find requester
                try:
                    connector = self.find_requester(result['conid'])
                except KeyError:
                    self.logger.error('Unknown connector %s, discarding order', result['conid'])
                    self.eventq.put(Event('CANCEL', (result['conid'], result['orderid'])))
                    continue
                try:
                    connector.on_result(result)
                except:
                    self.logger.error('Connector %s unreachable!', result['conid'])
                    self.eventq.put(Event('CANCEL', (result['conid'], None)))
                    self.conmap.deregister_connector(result['conid'])
            elif event.type == 'DISCARD':
                # prepare paramap
                paramap = dict( ((k,v) for (k,v) in event.payload.items() 
                                if k in ('orderid','error','errortext') ))
                self.logger.debug('Discarding: %s', paramap)
                # find requester
                try:
                    connector = self.find_requester(event.payload['conid'])
                except KeyError:
                    self.logger.error('Unknown connector %s, discarding order', event.payload['conid'])
                    self.eventq.put(Event('CANCEL', (event.payload['conid'], event.payload['orderid'])))
                    continue
                try:
                    connector.on_discard(paramap)
                except:
                    self.logger.error('Connector %s unreachable!', event.payload['conid'])
                    self.conmap.deregister_connector(event.payload['conid'])
            else:
                self.logger.debug('Got an unknown event type: %s. What now?',
                                  event.type)

