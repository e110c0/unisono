#!/usr/bin/env python3
'''
connector.py

 Created on: Thu 04, 2010
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

'''
Sample to demonstrate usage of unisono client
'''

from unisono import connection

from pprint import pprint
from sys import stdin

if __name__=="__main__":
	#connect to local xml rpc server
	c = connection.Client("127.0.0.1", 45312)
	
#	localip = '85.214.236.18'
	localip = '131.159.20.45'
	remoteip = '131.159.14.169'
	
	#build normal unisono order, don't care about orderid
	order = {'identifier1':localip,
			'identifier2':remoteip,
			'type':'periodic',
			'parameters' : {'interval': '3', 'lifetime': '30'},
			'dataitem':'RTT'}
	
	
	#define a callback which will be called when our result arrives
	def callback(result):
		print("got a result:")
		pprint(result)
	
	
	ret = c.commit_order(order, callback)
	
	#could be used later ....
	orderid = ret[0]
	return_code = ret[1]
	
	print("press any key ....")
	ch = stdin.read(1)
	
	#cancel periodic order
	c.cancel_order(c.getId(), orderid)
	
	#we are done, be polite!
	c.close()


