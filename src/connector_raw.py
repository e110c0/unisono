#!/usr/bin/env python3
'''
connector.py

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
from time import sleep
from itertools import count
from pprint import pprint

counter = 0
myID = ""

def on_result(result):
    global counter
    global myID
    counter += 1
    print("Finally, results!")
    pprint(result)
#    if counter < 10:
#        print('commit order: ' ,
#              s.commit_order(myID, {'orderid':counter, 'identifier2':'127.0.0.1', 'dataitem':'PATHMTU'}))
#        pass
#    else:
#        print('Done with all 10!')
    if "subid" in result.keys() and result["subid"] == 2:
        print("Now I cancel the order")
        s.cancel_order(myID, "0")
    return True

def on_discard(result):
    print("Discard: ", result)
    return True

def on_finished(result):
    print("Order finished:", result)
    return True
        
if __name__ == '__main__':
    orderid = count()

    # start server to get the result...
    server = SimpleXMLRPCServer(("localhost", 43222), logRequests=False)
    print("Listening on port 43222...")
    server.register_multicall_functions()
    server.register_function(on_result, 'on_result')
    server.register_function(on_discard, 'on_discard')
    server.register_function(on_finished, 'on_finished')
    thread = threading.Thread(target=server.serve_forever)
    # Exit the server thread when the main thread terminates
    thread.setDaemon(True)
    thread.start()
    
    s = xmlrpc.client.ServerProxy('http://localhost:45312/unisono')
    # Print list of available methods
    print("we do some stuff")
    print(s.system.listMethods())
    print(s.system.methodHelp('list_available_dataitems'))
    print(s.system.methodHelp('cancel_order'))
    myID = s.register_connector(43222)
    print('my ID is: ' + myID)
    print(s.list_available_dataitems())
    localip = '131.159.20.45'
    remoteip = '131.159.14.169'
#    for i in s.list_available_dataitems():
#        print('my order:', {'orderid': str(next(orderid)), 
#                                                      'identifier1':localip,
#                                                      'identifier2':remoteip,
#                                                      'type':'oneshot',
#                                                      'dataitem':i})
#        print('commit order: ' ,s.commit_order(myID, {'orderid': str(next(orderid)), 
#                                                      'identifier1':localip,
#                                                      'identifier2':remoteip,
#                                                      'type':'oneshot',
#                                                      'dataitem':i}))

    print('commit order: ' ,s.commit_order(myID, {'orderid': str(next(orderid)), 
                                                      'identifier1':localip,
                                                      'identifier2':remoteip,
                                                      'type':'oneshot',
#                                                      'parameters' : {'interval': '8', 'lifetime': '30','lower_threshold': 4000, 'upper_threshold':5500},
                                                      'dataitem':'RTT'}))
#    print('commit order: ' ,s.commit_order(myID, {'orderid': str(next(orderid)), 
#                                                      'identifier1':localip,
#                                                      'identifier2':remoteip,
#                                                      'parameters' : {'interval': '10', 'lifetime':'30', 'upper_threshold' : '', 'lower_threshold' : ''},
#                                                      'type':'triggered',
#                                                      'dataitem':'INTERFACE_TYPE'}))
#    sleep(3)
#    print('commit order: ' ,s.commit_order(myID, {'orderid': str(next(orderid)), 
#                                                  'identifier1':'193.196.31.38',
#                                                  'identifier2':remoteip,
#                                                  'type':'oneshot',
#                                                  'dataitem':'RTT_MIN'}))
#    sleep(3)
### cache testing:
#    print('check cache: ' , s.check_cache(myID, {
#                                              'identifier1':localip,
#                                              'identifier2':remoteip,
#                                              'dataitem':'INTERFACE_MAC'}))
#    print('check cache: ' , s.check_cache(myID, {
#                                              'identifier1':localip,
#                                              'identifier2':remoteip,
#                                              'dataitem':'RTT_MIN'}))

#    print('cache result:', s.cache_result({
#                                              'identifier1':localip,
#                                              'identifier2':remoteip,
#                                              'result':'123456',
#                                              'dataitem':'SWAP'}))
    ch = stdin.read(1)
    print('shutting down.')
    print(s.unregister_connector(myID))
