#!/usr/bin/env python3
'''
file_name

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

from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
import xmlrpc.client
import threading
from sys import stdin

counter = 0
myID = ""

def on_result(result):
    global counter
    global myID
    counter +=1
    print("Oh yeah, got my result: %s",result)
#    if counter < 10:
#        print('commit order: ' ,
#              s.commit_order(myID, {'orderid':counter, 'identifier2':'127.0.0.1', 'dataitem':'PATHMTU'}))
#        pass
#    else:
#        print('Done with all 10!')
    return True

if __name__ == '__main__':

    # start server to get the result...
    server = SimpleXMLRPCServer(("localhost", 43222),logRequests=False)
    print("Listening on port 43222...")
    server.register_multicall_functions()
    server.register_function(on_result,'on_result')
    thread = threading.Thread(target=server.serve_forever)
    # Exit the server thread when the main thread terminates
    thread.setDaemon(True)
    thread.start()
    
    s = xmlrpc.client.ServerProxy('http://localhost:45312/unisono')
    # Print list of available methods
    print("we do some stuff")
    print(s.system.listMethods())
    print(s.system.methodHelp('list_available_dataitems'))
    myID = s.register_connector(43222)
    print('my ID is: ' + myID)
    print(s.list_available_dataitems())
    orderid = 0

    for i in s.list_available_dataitems():
        print('my order:', {'orderid': str(orderid), 
                                                      'identifier1':'10.192.128.43',
                                                      'identifier2':'10.192.128.43',
                                                      'dataitem':i})
        print('commit order: ' ,s.commit_order(myID, {'orderid': str(orderid), 
                                                      'identifier1':'10.192.128.43',
                                                      'identifier2':'10.192.128.43',
                                                      'dataitem':i}))

        orderid = orderid+1
    ch = stdin.read(1)
    print('shutting down.')
    print(s.unregister_connector(myID))
