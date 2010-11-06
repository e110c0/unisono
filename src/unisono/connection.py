#!/usr/bin/env python3
'''
connection.py

 Created on: Wed 03, 2010
 Authors: cd
 
 
 (C) 2010 by I8, TUM
 
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

import socket, time, logging


class Client:
	'''
	A client to connect to the local unisono server. 
	
	commit_order is ready to use, no registering or orderid handling needed.
	
	The interface will be kept constant when unisono is changed from
	xml-rpc to json. Methods marked with *deprecated are likely to be deprecated
	when the unisono interface is changed to json.
	'''
	
	#logger = logging.getLogger(__name__)
	logger = logging.Logger(__name__)
	logger.addHandler(logging.StreamHandler())
	logger.setLevel(logging.DEBUG)
    
	def __init__(self, remote_addr, remote_port):
		self.__remote_addr = remote_addr
		self.__remote_port = remote_port
		self.__myID = ""
		self.__orderid = count()
		
		self.__callbacks_for_orderids_result = dict()
		# the following callbacks are mostly used for periodic orders
		self.__callbacks_for_orderids_discard = dict()
		self.__callbacks_for_orderids_finished = dict()
		
		# start server to get the result...
		# this is our local server, so remote unisonos can send reults back ...
		# hack hack hack -- requirement by xml rpc
		
		# used by xmp rpc for local server
		self.__local_port = 43222
		retries = 10
		while retries > 0:
			try:
				server = SimpleXMLRPCServer(("localhost", self.__local_port), logRequests=False)
				#no exception here, we got a socket!
				retries = 0
			except socket.error as e:
				if str(e) == "[Errno 98] Address already in use":
					self.__local_port += 1
					retries -= 1
				else:
					raise e
			
		self.logger.info("Listening on port %d ..." % self.__local_port)
		
		#server.register_multicall_functions()
		server.register_function(self.__on_result, 'on_result')
		server.register_function(self.__on_discard, 'on_discard')
		server.register_function(self.__on_finished, 'on_finished')
		thread = threading.Thread(target=server.serve_forever)
		# Exit the server thread when the main thread terminates
		thread.setDaemon(True)
		thread.start()
		
		server = None
		
		#remote server
		self.__remote = xmlrpc.client.ServerProxy('http://%s:%s/unisono' % 
									(self.__remote_addr, self.__remote_port))
		
		
		
		# check list of available methods
		required_commands = ["cache_result", "cancel_order", "check_cache", \
							"commit_order", "forward_received_packet", \
							"list_available_dataitems", "register_connector", \
							"unregister_connector"]
		
		provided_commands = self.__remote.system.listMethods()
		
		for r in required_commands:
			if r not in provided_commands:
				err = ("%s:%d does not know command \"%s\". I will not speak with him!" %
						(self.__remote_addr, self.__remote_port, r))
				self.logger.error(err)
				raise Exception(err)
		
		#print(self.__remote.system.methodHelp('list_available_dataitems'))
		#print(self.__remote.system.methodHelp('cancel_order'))
		
		self.__myID = self.__remote.register_connector(self.__local_port)
		self.logger.debug('my ID is: ' + self.__myID)
		
	
	def close(self):
		'''
		close connection with remote server. Many orders can be given with one
		connection.
		'''
		self.logger.debug('shutting down.')
		return self.__remote.unregister_connector(self.__myID)
	
	
	def getId(self):
		'''
		return the ID returned by register_connector
		'''
		return self.__myID
	
	def getOrderId(self):
		'''
		*deprecated - use commit order and don't care about orderids
		return a _new_ and unused orderid, safe to use for periodic orders
		'''
		return str(next(self.__orderid))
	
	def _getLocalPort(self):
		'''
		*deprecated
		'''
		return self.__local_port
	
	def list_available_dataitems(self):
		'''
		See documentation.
		'''
		return self.__remote.list_available_dataitems()
	
	
	def cache_result(self, result):
		'''
		*deprecated
		See documentation.
		'''
		return self.__remote.cache_result(result)
	
	
	def cancel_order(self, callerid, orderid):
		'''
		See documentation.
		'''
		return self.__remote.cancel_order(callerid, orderid)
	
	
	def check_cache(self, paramap):
		'''
		*deprecated
		See documentation.
		'''
		return self.__remote.check_cache(paramap)
	
	
	def forward_received_packet(self, packet):
		'''
		*deprecated
		See documentation.
		'''
		return self.__remote.forward_received_packet(packet)
	
	
	def register_connector(self, port):
		'''
		*deprecated - generate new Client
		See documentation.
		'''
		return self.__remote.register_connector(port)
	
	
	def unregister_connector(self, callerid):
		'''
		*deprecated - use close and only one connection per client
		See documentation.
		'''
		return self.__remote.unregister_connector(callerid)
		
							
	def commit_order(self, order,
				callback_result, callback_discard=None, callback_finished=None):
		'''
		See documentation.
		
		parameters
		order -	a valid unisono order. orderid will be assigned dynamically
		callback_* - the callback functions triggerd by remote
		
		!!WARNING!! return value differs from documentation
		returns tuple a tuple of (orderid, status)
		'''
		orderid = str(next(self.__orderid))
		
		if orderid in self.__callbacks_for_orderids_result:
			raise Exception("Multiple Key in on_result %s" % orderid)
			
		if orderid in self.__callbacks_for_orderids_discard:
			raise Exception("Multiple Key in on_discard %s" % orderid)
			
		if orderid in self.__callbacks_for_orderids_finished:
			raise Exception("Multiple Key in on_finished %s" % orderid)
			
		self.__callbacks_for_orderids_result[orderid] = callback_result
		self.__callbacks_for_orderids_discard[orderid] = callback_discard
		self.__callbacks_for_orderids_finished[orderid] = callback_finished
		
		order['orderid'] = orderid
		return (orderid, self.__remote.commit_order(self.__myID, order))
	
	
	def __on_result(self, result):
		'''
		callback function for xml rpc
		'''
		if result['conid'] != self.__myID:
			self.logger.error("conid doesn't match!")
			return True
		
		#call the registered callback function for this order
		self.__callbacks_for_orderids_result[result['orderid']](result)
		
		# never ever forget to return True!!
		# XMLRPC Server will cause an untrackable error
		return True
		

	def __on_discard(self, result):
		'''
		callback function for xml rpc
		'''
		if result['conid'] != self.__myID:
			self.logger.error("conid doesn't match!")
			return True
		
		if self.__callbacks_for_orderids_discard[result['orderid']] is None:
			self.logger.error("Warning: no handler for callback_discard: ", result)
		else:
			self.__callbacks_for_orderids_discard[result['orderid']](result)
		return True

	def __on_finished(self, result):
		'''
		callback function for xml rpc
		'''
		if result['conid'] != self.__myID:
			self.logger.error("conid doesn't match!")
			return True
		
		if self.__callbacks_for_orderids_finished[result['orderid']] is None:
			self.logger.error("Warning: no handler for callback_finished: ", result)
		else:
			self.__callbacks_for_orderids_finished[result['orderid']](result)
		return True




