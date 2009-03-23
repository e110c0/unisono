'''
XMLRPCListener.py

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

import socketserver
import threading
from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
 
# Threaded XMPRPC server
class XMLRPCListener(socketserver.ThreadingMixIn, SimpleXMLRPCServer): 
    '''
    non-blocking xmlrpc-server to handle concurrent requests
    '''
    pass

class RequestHandler(SimpleXMLRPCRequestHandler):
    '''
    Restrict requests to a particular path.
    '''
    rpc_paths = ('/RPC2',)

class ConnectorFunctions:
    '''
    functions available for connectors
    most of the functions reply with a status number. Results are received via
    the listener in the connectors.
    '''
    def register_connector(self, callerid, port):
        '''
        register a connector to the overlay for callbacks
        we require this because XMLRPC has no persistent connection and we want 
        to work asynchronous
        '''
        # TODO: show 
        status = 0
        return status
    def list_available_dataitems(self):
        '''
        Lists the data items provided by the local unisono daemon
        
        returns string all available data items
        '''
        return "we should return something useful here"
    def commit_order(self, callerid, orderid, dataitem, identifier1,
                     identifier2 = None, type='oneshot', parameter=0,
                     accuracy=100, lifetime = 600):
        '''
        commit an order to the daemon
        
        returns int the status of the request
        '''
        status = 0
        return status
    def cancel_order(self, callerid, orderid):
        '''
        cancel an already running order
        
        returns int the status of the request
        '''
        status = 0
        return status
    def forward_received_packet(self, packet):
        '''
        forward packets received for the unisono daemon
        this wil be used by the daemon to communicate between different hosts
        
        returns int the status of the request
        '''
        status = 0
        return status

# Create server
server = XMLRPCListener(("localhost", 45312), requestHandler=RequestHandler)
#server = SimpleXMLRPCServer(("localhost", 45312),requestHandler=RequestHandler)
server.register_introspection_functions()

# Register an instance; all the methods of the instance are
# published as XML-RPC methods (in this case, just 'div').

server.register_instance(ConnectorFunctions())

# Start a thread with the server -- that thread will then start one
# more thread for each request
server_thread = threading.Thread(target=server.serve_forever)
# Exit the server thread when the main thread terminates
server_thread.setDaemon(True)
server_thread.start()
print("XMLRPC listener loop running in thread:", server_thread.name)
