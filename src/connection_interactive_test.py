#!/usr/bin/env python3
'''
connection_interactive_test.py

 Created on: Sat 06, 2010
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
from unisono.connection import Client
import unittest

class ClientUnittest(unittest.TestCase):
	#def __init__(self, a):
	#	super().__init__(a)
	
	def setUp(self):
		self.count = 0
		self.c = Client("127.0.0.1", 45312)	
		
		self.localip = '127.0.0.1'
		#self.localip = '131.159.14.169'
		self.remoteip = '131.159.14.169'
		#self.remoteip = '134.2.172.172'
		
	def tearDown(self):
		self.c.close()
	
	
	def test_periodic_orders(self):
		'''
		We generate a periodic order which will be executed 10 times.
		Hit enter when at least 3 answers arrived
		'''
		order = {'orderid': None, # the Client class will care about this!
				  'identifier1':self.localip,
				  'identifier2':self.remoteip,
				  'type':'periodic',
				  'parameters' : {'interval': '3', 'lifetime': '30'},
				  'dataitem':'RTT'}
		
		
		def callback(result):
			print("callback function: %s" % result)
			self.assertEquals(result['identifier1'], self.localip)
			self.assertEquals(result['identifier2'], self.remoteip)
			self.count +=1
			print("%d outstanding answers" % (3-self.count))
		
		#for the lulz: skip one oderderid
		self.assertEquals(self.c.getOrderId(), '0')
		
		ret = self.c.commit_order(order, callback)
		#orderid is now '1', return code should be 0 (no error)
		self.assertEquals(ret, ('1',0))
		
		orderid = ret[0]
		
		print("press any key ....")
		ch = stdin.read(1)
		
		self.assertTrue(self.count >= 3)
		
		self.assertEqual(self.c.cancel_order(self.c.getId(), orderid), 0)
	
	def test_make_7_orders(self):
		'''make 7 oneshot orders'''
		order = {'orderid': None, # the Client class will care about this!
				  'identifier1':self.localip,
				  'identifier2':self.remoteip,
				  'type':'oneshot',
				  'dataitem':'RTT'}
		
		
		def callback(result):
			print("callback function: %s" % result)
			self.assertEquals(result['identifier1'], self.localip)
			self.assertEquals(result['identifier2'], self.remoteip)
			self.count +=1
			print("%d outstanding answers" % (7-self.count))
		
		self.assertEquals(self.c.commit_order(order, callback), ('0',0))
		sleep(1)
		self.assertEquals(self.c.commit_order(order, callback), ('1',0))
		self.assertEquals(self.c.commit_order(order, callback), ('2',0))
		self.assertEquals(self.c.commit_order(order, callback), ('3',0))
		self.assertEquals(self.c.commit_order(order, callback), ('4',0))
		
		#skip one oderderid
		self.assertEquals(self.c.getOrderId(), '5')
		
		self.assertEquals(self.c.commit_order(order, callback), ('6',0))
		self.assertEquals(self.c.commit_order(order, callback), ('7',0))
		
		print("press any key ....")
		ch = stdin.read(1)
		
		self.assertEquals(self.count, 7)
	
	def test_some_datasets(self):
		'''query the datasets defined im commands'''
		commands = ['CPU_CORE_COUNT', 'CPU_SPEED', 'CPU_TYPE']
		for i in commands:
			self.assertTrue(i in self.c.list_available_dataitems())

		self.commands = commands
		
		def callback(result):
			print("test_some_datasets callback function: %s" % result)
			self.assertEquals(result['identifier1'], self.localip)
			self.assertEquals(result['identifier2'], self.remoteip)
			found = False
			for i in self.commands:
				if i in result:
					self.commands.remove(i)
					found = True
			if not found:
				print("unknown field in result %s" % result)
				self.assertTrue(False)
			
		for i in commands:
			#invalid orderird fixed in Client
			order = {'orderid': 'invalid', 'identifier1':self.localip,
					'identifier2':self.remoteip, 'type':'oneshot',
					'dataitem':i}
			self.c.commit_order(order, callback)
		
		print("press any key ....")
		ch = stdin.read(1)
		
		self.assertEquals(self.commands, [])
	
	def test_connect_disconnect(self):
		'''unregister an reregister, *deprecated'''
		self.c.unregister_connector(self.c.getId())
		self.c.register_connector(self.c._getLocalPort())
	
		
	
if __name__ == '__main__':
	unittest.main()
	
